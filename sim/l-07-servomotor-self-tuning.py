#!/usr/bin/env python3
"""Ejemplo del servomotor DC self-tuning (L-07): reproducción y análisis del cero de muestreo.

Reproduce los números de Conceptos/l-07-servomotor-self-tuning.md.
Uso (desde la raíz del repo):  python3 sim/l-07-servomotor-self-tuning.py
Escribe:
  derivados/l-07-modelos-discretos.csv   discretización ZOH de los tres regímenes frente a la fuente
  derivados/l-07-reproduccion-str.csv    parámetros estimados al final de cada régimen frente a la tabla 1
  derivados/l-07-cero-de-muestreo.csv    RST fijo: cancelar el cero de muestreo frente a conservarlo
  salida/figuras/l-07-reproduccion-str.png   salida, modelo de referencia y voltaje (como las figuras 6 y 10)
  salida/figuras/l-07-cero-de-muestreo.png   voltaje y salida con y sin cancelar el cero (régimen t >= 20 s)

Fuente: L-07 (raw/LINKS.md). Supuestos que la fuente no da (S1 a S5 en la nota):
  S1 modelo de referencia con xi = 0,7 y omega_n = 65 rad/s, leídos a ojo de la figura 7
  S2 SBPA de 8 registros, 0,05 rad de amplitud y un bit por muestra
  S3 P(0) = 1000 I y parámetros iniciales en cero (esto último sí lo dice la fuente)
  S4 mientras |b1 estimado| < 1e-3 se aplica u = y_r (la fuente no dice cómo arranca)
  S5 la recursión del RST usa el voltaje ya saturado
Las ecuaciones (9) a (13) de la fuente no tienen factor de olvido (lambda = 1). La reproducción
se corre literal y, como variante marcada, con lambda = 0,995 y 0,99.
"""
import csv
import math
from pathlib import Path

import control as ct
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
DER = RAIZ / "derivados"
SAL = RAIZ / "salida" / "figuras"

T = 0.01                      # periodo de muestreo de la fuente (s)
DURACION = 30.0
REGIMENES = [(0.0, 30.0, 0.1), (10.0, 60.0, 0.1), (20.0, 60.0, 0.5)]  # (desde t, K_c, tau_c)
U_MAX = 30.0                  # límite del actuador en la fuente (V)
XI, WN = 0.7, 65.0            # S1
A_SBPA = 0.05                 # S2
P0 = 1000.0                   # S3
B1_MIN = 1e-3                 # S4
LAMBDAS = (1.0, 0.995, 0.99)  # 1 = ecuaciones de la fuente; los otros, variante con factor de olvido
SUBPASOS = 20                 # para ver la salida continua entre muestras

# Valores impresos en la fuente: (a1D, a0D, b1D, b0D)
FUENTE = {
    "ec. (17), 0 < t < 10": (-1.9048, 0.9048, 0.0145, 0.014),
    "ec. (18), 10 <= t < 20": (-1.9048, 0.9048, 0.029, 0.0281),
    "ec. (19), t >= 20": (-1.9048, 0.9048, 0.0145, 0.014),
}
TABLA1_REAL = [(-1.9048, 0.9048, 0.0145, 0.014), (-1.9048, 0.9048, 0.029, 0.0281), (-1.9802, 0.9802, 0.0060, 0.0059)]
TABLA1_EST = [(-1.9050, 0.9048, 0.0146, 0.014), (-1.9050, 0.9047, 0.029, 0.0280), (-1.9800, 0.9803, 0.0059, 0.0059)]

# Colores (paleta de referencia validada de la skill dataviz, superficie clara)
AZUL, NARANJA = "#2a78d6", "#eb6834"
TINTA, TINTA_2, REJILLA, FONDO = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def discreto(K: float, tau: float, h: float = T) -> tuple:
    """Planta K/(s(tau s + 1)) con ZOH: devuelve (a1, a0, b1, b0) y las matrices exactas Phi, Gamma."""
    p = math.exp(-h / tau)
    b1 = K * (h - tau * (1 - p))
    b0 = K * (tau * (1 - p) - h * p)
    Phi = np.array([[1.0, tau * (1 - p)], [0.0, p]])
    Gam = K * np.array([h - tau * (1 - p), 1 - p])
    return (-(1 + p), p, b1, b0), Phi, Gam


def modelo_referencia() -> tuple:
    gd = ct.c2d(ct.tf([WN**2], [1, 2 * XI * WN, WN**2]), T, "zoh")
    num = np.atleast_1d(np.squeeze(gd.num[0][0]))
    den = np.atleast_1d(np.squeeze(gd.den[0][0]))
    num, den = num[-2:] / den[0], den / den[0]
    return float(num[0]), float(num[1]), float(den[1]), float(den[2])   # b1m, b0m, a1m, a0m


def sbpa(n: int) -> np.ndarray:
    """Señal binaria pseudoaleatoria de 8 registros (polinomio x^8 + x^6 + x^5 + x^4 + 1, periodo 255)."""
    reg = [1, 0, 0, 0, 0, 0, 0, 0]
    out = np.empty(n)
    for k in range(n):
        out[k] = 1.0 if reg[7] else -1.0
        reg = [reg[7] ^ reg[5] ^ reg[4] ^ reg[3]] + reg[:7]
    return out


def cuadrada(n: int) -> np.ndarray:
    """Tren de pulsos de ±1 rad con periodo de 1 s, empezando en -1 (figura 7 de la fuente)."""
    return np.array([-1.0 if (k % 100) < 50 else 1.0 for k in range(n)])


def regimen(k: int) -> int:
    t = k * T
    return max(i for i, (t0, _, _) in enumerate(REGIMENES) if t >= t0 - 1e-12)


def modelos_discretos() -> None:
    filas = []
    for i, (t0, K, tau) in enumerate(REGIMENES):
        (a1, a0, b1, b0), _, _ = discreto(K, tau)
        gd = ct.c2d(ct.tf([K], [tau, 1, 0]), T, "zoh")      # comprobación con python-control
        num = np.squeeze(gd.num[0][0]); den = np.squeeze(gd.den[0][0])
        assert np.allclose([a1, a0, b1, b0], [den[1] / den[0], den[2] / den[0], num[-2] / den[0], num[-1] / den[0]], rtol=1e-9)
        nombre, impreso = list(FUENTE.items())[i]
        calculado = (round(a1, 4), round(a0, 4), round(b1, 4), round(b0, 4))
        filas.append({
            "regimen": nombre, "K_c": K, "tau_c_s": tau,
            "a1D": calculado[0], "a0D": calculado[1], "b1D": calculado[2], "b0D": calculado[3],
            "cero_de_muestreo": round(-b0 / b1, 4),
            "impreso_en_la_fuente": " ".join(str(v) for v in impreso),
            "tabla1_real": " ".join(str(v) for v in TABLA1_REAL[i]),
            "coincide_con_la_ecuacion": "sí" if np.allclose(calculado, impreso, atol=6e-4) else "no (errata)",
            "coincide_con_la_tabla1": "sí" if np.allclose(calculado, TABLA1_REAL[i], atol=6e-4) else "no",
        })
    escribir(DER / "l-07-modelos-discretos.csv", filas)


def simular(n: int, yr: np.ndarray, controlador, K_tau=None, fino: bool = False) -> dict:
    """Simula la planta continua con ZOH. controlador(k, y, u, yr) devuelve u(k) sin saturar."""
    x = np.zeros(2)
    y = np.zeros(n); u = np.zeros(n)
    t_fino, th_fino = [], []
    for k in range(n):
        K, tau = K_tau if K_tau else REGIMENES[regimen(k)][1:]
        y[k] = x[0]
        u[k] = float(np.clip(controlador(k, y, u, yr), -U_MAX, U_MAX))
        if fino:
            _, Phi_h, Gam_h = discreto(K, tau, T / SUBPASOS)
            for j in range(SUBPASOS):
                t_fino.append((k + j / SUBPASOS) * T); th_fino.append(x[0])
                x = Phi_h @ x + Gam_h * u[k]
        else:
            _, Phi, Gam = discreto(K, tau)
            x = Phi @ x + Gam * u[k]
    return {"y": y, "u": u, "t_fino": np.array(t_fino), "th_fino": np.array(th_fino)}


def salida_modelo(yr: np.ndarray, b1m: float, b0m: float, a1m: float, a0m: float) -> np.ndarray:
    ym = np.zeros(len(yr))
    for k in range(2, len(yr)):
        ym[k] = -a1m * ym[k - 1] - a0m * ym[k - 2] + b1m * yr[k - 1] + b0m * yr[k - 2]
    return ym


def reproduccion(ref: tuple, lam: float) -> tuple:
    b1m, b0m, a1m, a0m = ref
    n = int(round(DURACION / T))
    yr = cuadrada(n) + A_SBPA * sbpa(n)
    est = np.zeros((n, 4))
    estado = {"th": np.zeros(4), "P": P0 * np.eye(4), "rst": None}

    def str_rls(k, y, u, yr):
        if k >= 2:   # mínimos cuadrados recursivos, ecuaciones (9) a (11) de la fuente (lam = 1)
            phi = np.array([-y[k - 1], -y[k - 2], u[k - 1], u[k - 2]])
            Pphi = estado["P"] @ phi
            g = Pphi / (lam + phi @ Pphi)
            estado["th"] = estado["th"] + g * (y[k] - phi @ estado["th"])
            estado["P"] = (estado["P"] - np.outer(g, Pphi)) / lam
        est[k] = estado["th"]
        a1, a0, b1, b0 = estado["th"]
        if abs(b1) >= B1_MIN:   # diseño RST en línea, pasos 1 a 6 de la fuente
            estado["rst"] = (b0 / b1, (a1m - a1) / b1, (a0m - a0) / b1, b1m / b1, b0m / b1)
        if estado["rst"] is None:
            return yr[k]          # S4
        r0, s1, s0, t1, t0 = estado["rst"]
        return -r0 * u[k - 1] + t1 * yr[k] + t0 * yr[k - 1] - s1 * y[k] - s0 * y[k - 1]

    sim = simular(n, yr, str_rls)
    ym = salida_modelo(yr, b1m, b0m, a1m, a0m)
    filas = []
    for i, (t0, K, tau) in enumerate(REGIMENES):
        k_fin = int(round((REGIMENES[i + 1][0] if i + 1 < len(REGIMENES) else DURACION) / T)) - 1
        k_ini = int(round(t0 / T))
        ventana = slice(k_ini + 300, k_fin + 1)     # descarta 3 s de adaptación tras cada cambio
        filas.append({
            "lambda": lam,
            "regimen": f"{t0:g} s en adelante" if i == 2 else f"{t0:g} a {REGIMENES[i + 1][0]:g} s",
            "a1D_est": round(float(est[k_fin, 0]), 4), "a0D_est": round(float(est[k_fin, 1]), 4),
            "b1D_est": round(float(est[k_fin, 2]), 4), "b0D_est": round(float(est[k_fin, 3]), 4),
            "tabla1_estimado": " ".join(str(v) for v in TABLA1_EST[i]),
            "max_dif_con_tabla1_estimado": round(float(np.max(np.abs(est[k_fin] - TABLA1_EST[i]))), 4),
            "max_dif_con_tabla1_real": round(float(np.max(np.abs(est[k_fin] - TABLA1_REAL[i]))), 4),
            "error_rms_seguimiento_rad": round(float(np.sqrt(np.mean((sim["y"][ventana] - ym[ventana]) ** 2))), 4),
            "fraccion_saturada": round(float(np.mean(np.abs(sim["u"][k_ini:k_fin + 1]) >= U_MAX - 1e-9)), 3),
            "rms_du_V": round(float(np.sqrt(np.mean(np.diff(sim["u"][k_ini:k_fin + 1]) ** 2))), 2),
        })
    filas[0]["minimo_inicial_theta_rad"] = round(float(np.min(sim["y"][:50])), 2)
    return filas, {"t": np.arange(n) * T, "y": sim["y"], "ym": ym, "u": sim["u"], "est": est}


def disenos_fijos(K: float, tau: float, ref: tuple) -> dict:
    """RST con los parámetros verdaderos: A) cancela el cero, como la fuente; B) lo conserva."""
    b1m, b0m, a1m, a0m = ref
    (a1, a0, b1, b0), _, _ = discreto(K, tau)
    A_cancela = (b0 / b1, (a1m - a1) / b1, (a0m - a0) / b1, b1m / b1, b0m / b1)
    ao = 0.0   # observador A_o = z
    M = np.array([[1, b1, 0], [a1, b0, b1], [a0, 0, b0]])
    r0, s1, s0 = np.linalg.solve(M, [a1m - ao - a1, a0m - a1m * ao - a0, -a0m * ao])
    K_m = (1 + a1m + a0m) / (b1 + b0)          # B_m = K_m B^-, con G_m(1) = 1
    B_conserva = (r0, s1, s0, K_m, -K_m * ao)
    # Polos de U/Y_r = A T / (A R + B S)
    polos = {}
    for nombre, (r0_, s1_, s0_, _, _) in (("cancela", A_cancela), ("conserva", B_conserva)):
        car = np.polyadd(np.polymul([1, a1, a0], [1, r0_]), np.polymul([b1, b0], [s1_, s0_]))
        polos[nombre] = np.roots(car)
    return {"cancela": A_cancela, "conserva": B_conserva, "polos": polos, "K_m": K_m, "b": (b1, b0), "a": (a1, a0)}


def comparar(K: float, tau: float, ref: tuple, etiqueta: str, duracion: float = 3.0) -> tuple:
    b1m, b0m, a1m, a0m = ref
    n = int(round(duracion / T))
    yr = cuadrada(n)
    d = disenos_fijos(K, tau, ref)
    filas, curvas = [], {}
    for nombre in ("cancela", "conserva"):
        r0, s1, s0, t1, t0 = d[nombre]

        def ley(k, y, u, yr, r0=r0, s1=s1, s0=s0, t1=t1, t0=t0):
            if k == 0:
                return t1 * yr[0] - s1 * y[0]
            return -r0 * u[k - 1] + t1 * yr[k] + t0 * yr[k - 1] - s1 * y[k] - s0 * y[k - 1]

        sim = simular(n, yr, ley, K_tau=(K, tau), fino=True)
        if nombre == "cancela":
            ym = salida_modelo(yr, b1m, b0m, a1m, a0m)
        else:
            b1, b0 = d["b"]
            ym = salida_modelo(yr, d["K_m"] * b1, d["K_m"] * b0, a1m, a0m)
        # Ventanas de reposo: los últimos 0,2 s de cada medio periodo, cuando la salida ya debería estar quieta
        reposo = np.array([(k % 50) >= 30 and k >= 50 for k in range(n)])
        du = np.diff(sim["u"], prepend=sim["u"][0])
        k_fino = (sim["t_fino"] / T + 1e-9).astype(int)
        # Oscilación pico a pico de la salida continua en cada ventana de reposo (desde la segunda)
        osc = max(np.ptp(sim["th_fino"][(k_fino >= k0) & (k_fino < k0 + 20)]) for k0 in range(80, n, 50))
        polo_min = min(d["polos"][nombre], key=lambda p: p.real)
        filas.append({
            "planta": etiqueta, "diseno": "A: cancela el cero (fuente)" if nombre == "cancela" else "B: conserva el cero",
            "r0": round(float(r0), 4), "s1": round(float(s1), 2), "s0": round(float(s0), 2),
            "t1": round(float(t1), 2), "t0": round(float(t0), 2) + 0.0,
            "polo_mas_negativo_de_U_sobre_Yr": round(float(polo_min.real), 4),
            "u_max_V": round(float(np.max(np.abs(sim["u"]))), 1),
            "fraccion_saturada": round(float(np.mean(np.abs(sim["u"]) >= U_MAX - 1e-9)), 3),
            "rms_du_V": round(float(np.sqrt(np.mean(np.diff(sim["u"]) ** 2))), 2),
            "error_max_en_muestras_rad": round(float(np.max(np.abs(sim["y"][20:] - ym[20:]))), 4),
            "rms_du_en_reposo_V": round(float(np.sqrt(np.mean(du[reposo] ** 2))), 3),
            "oscilacion_theta_en_reposo_mrad": round(float(1000 * osc), 3),
        })
        curvas[nombre] = (np.arange(n) * T, sim, ym)
    return filas, curvas


def escribir(ruta: Path, filas: list) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    campos = list(dict.fromkeys(c for f in filas for c in f))
    with ruta.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, lineterminator="\n")
        w.writeheader()
        w.writerows(filas)
    print(f"-> {ruta.relative_to(RAIZ)}")
    for fila in filas:
        print("   ", fila)


def estilo(ax, ylabel: str) -> None:
    ax.set_facecolor(FONDO)
    ax.grid(True, color=REJILLA, linewidth=0.6)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(REJILLA)
    ax.tick_params(colors=TINTA_2, labelsize=8)
    ax.set_ylabel(ylabel, color=TINTA_2, fontsize=9)


def figura_reproduccion(r: dict) -> None:
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 5.2), sharex=True, facecolor=FONDO)
    a1.plot(r["t"], r["y"], color=AZUL, lw=1.2, label="salida del servomotor θ")
    a1.plot(r["t"], r["ym"], color=NARANJA, lw=1.2, label="modelo de referencia y_m")
    estilo(a1, "ángulo (rad)")
    a1.set_ylim(-3, 2)
    a1.legend(loc="lower right", fontsize=8, frameon=False, labelcolor=TINTA)
    a1.set_title("Reproducción del ejemplo L-07 en Python (T = 0,01 s, factor de olvido λ = 0,99)",
                 color=TINTA, fontsize=10, loc="left")
    a2.plot(r["t"], r["u"], color=AZUL, lw=0.5)
    estilo(a2, "voltaje u (V)")
    a2.set_xlabel("tiempo (s)", color=TINTA_2, fontsize=9)
    fig.tight_layout()
    fig.savefig(SAL / "l-07-reproduccion-str.png", dpi=150, facecolor=FONDO)
    plt.close(fig)
    print(f"-> {(SAL / 'l-07-reproduccion-str.png').relative_to(RAIZ)}")


def figura_cero(curvas: dict) -> None:
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 5.2), sharex=True, facecolor=FONDO)
    t, simA, ymA = curvas["cancela"]
    _, simB, _ = curvas["conserva"]
    lim = t <= 1.5
    a1.step(t[lim], simA["u"][lim], where="post", color=AZUL, lw=1.0, label="A: cancela el cero (como la fuente)")
    a1.step(t[lim], simB["u"][lim], where="post", color=NARANJA, lw=1.4, label="B: conserva el cero")
    estilo(a1, "voltaje u (V)")
    a1.legend(loc="lower right", fontsize=8, frameon=False, labelcolor=TINTA)
    a1.set_title("RST fijo con la planta de t ≥ 20 s (cero de muestreo en z = −0,993)", color=TINTA, fontsize=10, loc="left")
    limf = simA["t_fino"] <= 1.5
    a2.plot(simA["t_fino"][limf], simA["th_fino"][limf], color=AZUL, lw=1.0, label="θ continua, diseño A")
    a2.plot(simB["t_fino"][limf], simB["th_fino"][limf], color=NARANJA, lw=1.4, label="θ continua, diseño B")
    estilo(a2, "ángulo (rad)")
    a2.set_xlabel("tiempo (s)", color=TINTA_2, fontsize=9)
    a2.legend(loc="upper left", fontsize=8, frameon=False, labelcolor=TINTA)
    fig.tight_layout()
    fig.savefig(SAL / "l-07-cero-de-muestreo.png", dpi=150, facecolor=FONDO)
    plt.close(fig)
    print(f"-> {(SAL / 'l-07-cero-de-muestreo.png').relative_to(RAIZ)}")


def main() -> None:
    ref = modelo_referencia()
    print(f"Modelo de referencia discreto (S1): B_m = {ref[0]:.5f} z + {ref[1]:.5f}, A_m = z^2 + {ref[2]:.5f} z + {ref[3]:.5f}")
    modelos_discretos()
    filas_rep, curvas_rep = [], {}
    for lam in LAMBDAS:
        f, curvas_rep[lam] = reproduccion(ref, lam)
        filas_rep += f
    escribir(DER / "l-07-reproduccion-str.csv", filas_rep)
    r = curvas_rep[0.99]   # la variante que reproduce la tabla 1 y las figuras 6 y 10
    filas = []
    curvas_t20 = None
    for (t0, K, tau), etiqueta in zip(REGIMENES, ("K_c = 30; tau_c = 0.1 s", "K_c = 60; tau_c = 0.1 s", "K_c = 60; tau_c = 0.5 s")):
        f, curvas = comparar(K, tau, ref, etiqueta)
        filas += f
        if tau == 0.5:
            curvas_t20 = curvas
    # Sensibilidad al supuesto S1: el zumbido del diseño A no depende de omega_n
    for wn in (40.0, 90.0):
        gd = ct.c2d(ct.tf([wn**2], [1, 2 * XI * wn, wn**2]), T, "zoh")
        num = np.squeeze(gd.num[0][0]); den = np.squeeze(gd.den[0][0])
        ref_w = (num[-2] / den[0], num[-1] / den[0], den[1] / den[0], den[2] / den[0])
        f, _ = comparar(60.0, 0.5, ref_w, f"K_c = 60; tau_c = 0.5 s; omega_n = {wn:g} rad/s")
        filas += f
    escribir(DER / "l-07-cero-de-muestreo.csv", filas)
    SAL.mkdir(parents=True, exist_ok=True)
    figura_reproduccion(r)
    figura_cero(curvas_t20)


if __name__ == "__main__":
    main()
