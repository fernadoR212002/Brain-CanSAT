#!/usr/bin/env python3
"""Modelo de rumbo en espacio de estados: comprobación simbólica de matrices, rangos y discretización.

Reproduce las afirmaciones de Control/modelo-rumbo-espacio-estados.md.
Uso (desde la raíz del repo):  python3 sim/modelo-rumbo.py
Escribe derivados/modelo-rumbo.txt (resultados simbólicos), derivados/modelo-rumbo-cero-de-muestreo.csv
y derivados/modelo-rumbo-giro-maximo.csv.

No usa parámetros físicos del equipo (inercias, fricciones, constantes del motor):
todavía no se han medido. Todo se comprueba con símbolos positivos, así que vale
para cualquier valor físico. Lo único numérico es la tabla del cero de muestreo,
que solo depende del cociente T/tau.
"""
import csv
import math
from pathlib import Path

import sympy as sp

RAIZ = Path(__file__).resolve().parent.parent
TXT = RAIZ / "derivados" / "modelo-rumbo.txt"
CSV = RAIZ / "derivados" / "modelo-rumbo-cero-de-muestreo.csv"

s, z = sp.symbols("s z")
lineas: list[str] = []


def informe(texto: str = "") -> None:
    print(texto)
    lineas.append(texto)


def matriz_ctrb(A: sp.Matrix, B: sp.Matrix) -> sp.Matrix:
    return sp.Matrix.hstack(*[A**k * B for k in range(A.shape[0])])


def matriz_obsv(A: sp.Matrix, C: sp.Matrix) -> sp.Matrix:
    return sp.Matrix.vstack(*[C * A**k for k in range(A.shape[0])])


def rango(M: sp.Matrix) -> int:
    return M.rank(simplify=True)


def tf(A: sp.Matrix, B: sp.Matrix, C: sp.Matrix) -> sp.Expr:
    """Función de transferencia escalar C (sI - A)^-1 B."""
    return sp.factor(sp.simplify((C * (s * sp.eye(A.shape[0]) - A).inv() * B)[0, 0]))


def comprobar(nombre: str, expr: sp.Expr) -> None:
    """Afirma que expr se simplifica a cero y lo deja escrito."""
    ok = sp.simplify(expr) == 0
    informe(f"  [{'ok' if ok else 'FALLA'}] {nombre}")
    if not ok:
        raise SystemExit(f"Falla la comprobación: {nombre}")


def cuerpo() -> None:
    informe("1. Cuerpo del PocketQube en guiñada (N0): x = [psi_b, omega_b]")
    J_b, b_b, k_r = sp.symbols("J_b b_b k_r", positive=True)
    A = sp.Matrix([[0, 1], [-k_r / J_b, -b_b / J_b]])
    B = sp.Matrix([0, 1 / J_b])
    C_mag, C_gir = sp.Matrix([[1, 0]]), sp.Matrix([[0, 1]])
    informe(f"  A = {A.tolist()}   B = E = {B.T.tolist()}^T   D = 0")
    comprobar("psi_b/tau = 1/(J_b s^2 + b_b s + k_r)", tf(A, B, C_mag) - 1 / (J_b * s**2 + b_b * s + k_r))
    informe(f"  rango de [B AB] = {rango(matriz_ctrb(A, B))} (de 2): controlable si hay par de control sobre el cuerpo")
    for k_val, etiqueta in ((0, "con destorcedor (k_r = 0)"), (k_r, "sin destorcedor (k_r > 0)")):
        A_k = A.subs(k_r, k_val)
        informe(f"  {etiqueta}: rango O(giróscopo) = {rango(matriz_obsv(A_k, C_gir))}, "
                f"rango O(magnetómetro) = {rango(matriz_obsv(A_k, C_mag))}")
    T = sp.symbols("T", positive=True)
    Phi, Gam = sp.Matrix([[1, T], [0, 1]]), sp.Matrix([T**2 / 2, T])  # ZOH exacto con b_b = k_r = 0
    G = sp.factor(sp.simplify((C_mag * (z * sp.eye(2) - Phi).inv() * Gam)[0, 0]))
    comprobar("doble integrador con ZOH: T^2 (z+1) / (2 (z-1)^2), cero en z = -1", G - T**2 * (z + 1) / (2 * (z - 1) ** 2))
    informe()


def camara() -> tuple:
    informe("2. Cámara sobre un servomotor DC, en coordenadas relativas al cuerpo: x = [theta_g, omega_g, i_a]")
    J_c, B_v, k_t, k_v, R_a, L_a, N = sp.symbols("J_c B_v k_t k_v R_a L_a N", positive=True)
    A = sp.Matrix([[0, 1, 0], [0, -B_v / J_c, N * k_t / J_c], [0, -N * k_v / L_a, -R_a / L_a]])
    B = sp.Matrix([0, 0, 1 / L_a])
    E = sp.Matrix([0, -1, 0])  # w = aceleración angular del cuerpo (la base)
    C = sp.Matrix([[1, 0, 0]])
    informe(f"  A = {A.tolist()}")
    informe(f"  B = {B.T.tolist()}^T   E = {E.T.tolist()}^T   C = {C.tolist()}   D = 0")
    den = s * ((J_c * s + B_v) * (L_a * s + R_a) + N**2 * k_t * k_v)
    comprobar("theta_g/u = N k_t / (s[(J_c s + B_v)(L_a s + R_a) + N^2 k_t k_v])", tf(A, B, C) - N * k_t / den)
    comprobar("theta_g/w = -J_c (L_a s + R_a) / (s[...])", tf(A, E, C) + J_c * (L_a * s + R_a) / den)
    # Transmisión pasiva del giro del cuerpo a la cámara (u = 0): psi_c/psi_b = 1 + s^2 theta_g/w
    trans = sp.simplify(1 + s**2 * tf(A, E, C))
    informe(f"  psi_c/psi_b con u = 0: {sp.factor(trans)}  -> en s = 0 vale {sp.simplify(trans.subs(s, 0))}")
    informe(f"  rango de [B AB A^2B] = {rango(matriz_ctrb(A, B))} (de 3)")
    informe(f"  rango O con codificador (theta_g medido) = {rango(matriz_obsv(A, C))} (de 3)")
    # Modelo reducido: L_a -> 0
    red = sp.limit(N * k_t / den, L_a, 0)
    K_c = N * k_t / (B_v * R_a + N**2 * k_t * k_v)
    tau_c = J_c * R_a / (B_v * R_a + N**2 * k_t * k_v)
    comprobar("con L_a -> 0: theta_g/u = K_c / (s (tau_c s + 1))", red - K_c / (s * (tau_c * s + 1)))
    comprobar("con N = 1, K_c y tau_c son las ecuaciones (7) y (8) del ejemplo",
              (K_c - k_t / (B_v * R_a + k_t * k_v)).subs(N, 1) + (tau_c - J_c * R_a / (B_v * R_a + k_t * k_v)).subs(N, 1))
    K, tau = sp.symbols("K_c tau_c", positive=True)
    A_r = sp.Matrix([[0, 1], [0, -1 / tau]])
    B_r = sp.Matrix([0, K / tau])
    C_r = sp.Matrix([[1, 0]])
    comprobar("modelo reducido A_r, B_r, C_r da K_c/(s(tau_c s + 1))", tf(A_r, B_r, C_r) - K / (s * (tau * s + 1)))
    informe(f"  A_r = {A_r.tolist()}   B_r = {B_r.T.tolist()}^T   E_r = [[0, -1]]^T   C_r = [[1, 0]]   D_r = 0")
    informe()
    return A_r, B_r, C_r, K, tau


def combinado() -> None:
    informe("3. Modelo combinado: x = [psi_b, omega_b, theta_g, omega_g, i_a, b_g] (sensores en el cuerpo)")
    J_b, b_b, k_r, J_c, B_v, k_t, k_v, R_a, L_a, N = sp.symbols(
        "J_b b_b k_r J_c B_v k_t k_v R_a L_a N", positive=True)
    A = sp.Matrix([
        [0, 1, 0, 0, 0, 0],
        [-k_r / J_b, -b_b / J_b, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0],
        [k_r / J_b, b_b / J_b, 0, -B_v / J_c, N * k_t / J_c, 0],
        [0, 0, 0, -N * k_v / L_a, -R_a / L_a, 0],
        [0, 0, 0, 0, 0, 0],
    ])
    B = sp.Matrix([0, 0, 0, 0, 1 / L_a, 0])
    filas = {"giróscopo": [0, 1, 0, 0, 0, 1], "magnetómetro": [1, 0, 0, 0, 0, 0], "codificador": [0, 0, 1, 0, 0, 0]}
    informe(f"  rango de la matriz de controlabilidad desde u = {rango(matriz_ctrb(A, B))} (de 6): "
            "el cuerpo y el sesgo no se controlan con el servo")
    casos = [("giróscopo", "magnetómetro", "codificador"), ("giróscopo", "magnetómetro"), ("giróscopo", "codificador")]
    for caso in casos:
        C = sp.Matrix([filas[f] for f in caso])
        for k_val, etiqueta in ((0, "k_r = 0"), (k_r, "k_r > 0")):
            r = rango(matriz_obsv(A.subs(k_r, k_val), C))
            informe(f"  rango O con {' + '.join(caso)} ({etiqueta}) = {r} (de 6)")
    informe()


def estimador() -> None:
    informe("4. Estimador de rumbo con el giróscopo como entrada: x_e = [psi_b, b_g], u_e = y_g, y = y_psi")
    A = sp.Matrix([[0, -1], [0, 0]])
    C = sp.Matrix([[1, 0]])
    informe(f"  A_e = {A.tolist()}   B_e = [[1, 0]]^T   C_e = {C.tolist()}   D_e = 0")
    informe(f"  rango O con el magnetómetro = {rango(matriz_obsv(A, C))} (de 2): rumbo y sesgo observables")
    l1, l2, b = sp.symbols("l_1 l_2 b", positive=True)
    Psi = sp.Function("Psi")(s)
    F_m = (l1 * s + l2) / (s**2 + l1 * s + l2)
    F_g = s / (s**2 + l1 * s + l2)
    comprobar("filtro complementario: F_m + s F_g = 1", F_m + s * F_g - 1)
    err2 = sp.simplify(F_m * Psi + F_g * (s * Psi + b / s) - Psi)
    informe(f"  error con sesgo constante (2.º orden): {err2};  valor final = {sp.limit(s * err2, s, 0)}")
    err1 = sp.simplify(l1 / (s + l1) * Psi + 1 / (s + l1) * (s * Psi + b / s) - Psi)
    informe(f"  error con sesgo constante (1.er orden, sin estado de sesgo): {err1};  valor final = {sp.limit(s * err1, s, 0)}")
    informe()


def discretizacion(A_r, B_r, C_r, K, tau) -> None:
    informe("5. Discretización con retenedor de orden cero (ZOH) del modelo reducido")
    T, sig = sp.symbols("T sigma", positive=True)
    Phi = sp.simplify((A_r * T).exp())
    Gam = sp.simplify(sp.integrate((A_r * sig).exp() * B_r, (sig, 0, T)))
    p = sp.exp(-T / tau)
    comprobar("Phi = [[1, tau(1-p)], [0, p]]", (Phi - sp.Matrix([[1, tau * (1 - p)], [0, p]])).norm())
    comprobar("Gamma = K [T - tau(1-p), 1 - p]^T", (Gam - K * sp.Matrix([T - tau * (1 - p), 1 - p])).norm())
    G = sp.simplify((C_r * (z * sp.eye(2) - Phi).inv() * Gam)[0, 0])
    b1 = K * (T - tau * (1 - p))
    b0 = K * (tau * (1 - p) - T * p)
    comprobar("G(z) = (b1 z + b0) / ((z - 1)(z - p))", G - (b1 * z + b0) / ((z - 1) * (z - p)))
    h = sp.symbols("h", positive=True)
    z0 = sp.simplify((-b0 / b1).subs(T, h * tau))
    informe(f"  cero de muestreo z0(h = T/tau) = {z0}")
    informe(f"  límite h -> 0: {sp.limit(z0, h, 0)};  serie: {sp.series(z0, h, 0, 2).removeO()}")
    filas = []
    for T_val in (0.01, 0.25):
        for tau_val in (0.05, 0.1, 0.2, 0.5, 1.0):
            hv = T_val / tau_val
            z0v = float(z0.subs(h, hv))
            muestras = -1 / math.log(abs(z0v))
            filas.append({"T_s": T_val, "tau_s": tau_val, "T_sobre_tau": round(hv, 4), "cero_z0": round(z0v, 4),
                          "muestras_para_caer_a_1_sobre_e": round(muestras, 1), "segundos": round(muestras * T_val, 3)})
    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(filas)
    informe(f"  tabla del cero de muestreo -> {CSV.relative_to(RAIZ)}")
    for f in filas:
        informe(f"    T = {f['T_s']} s, tau = {f['tau_s']} s: z0 = {f['cero_z0']}, "
                f"el modo (z0)^k cae a 1/e en {f['muestras_para_caer_a_1_sobre_e']} muestras ({f['segundos']} s)")
    informe()


def giro_del_cuerpo() -> None:
    informe("6. Giro constante del cuerpo (rampa a la salida) con el RST que cancela el cero (ejemplo L-07)")
    p, T, Om, r0, a1m, a0m = sp.symbols("p T Omega r_0 a_1m a_0m", positive=True)
    A = (z - 1) * (z - p)
    R = Bmas = z + r0                       # diseño de la fuente: R = B+ (R1 = 1), A_o = 1
    Am = z**2 + a1m * z + a0m
    sens = A * R / (Bmas * Am)              # S = A R / (A R + B S), con A R + B S = B+ A_m A_o
    rampa = Om * T * z / (z - 1) ** 2
    e_ss = sp.simplify(sp.limit((z - 1) * sens * rampa, z, 1))
    comprobar("error estacionario = (1 - p) T Omega / A_m(1)", e_ss - (1 - p) * T * Om / (1 + a1m + a0m))
    tau, s1, s2, wn = sp.symbols("tau_c s_1 s_2 omega_n", positive=True)
    aprox = sp.limit((1 - sp.exp(-T / tau)) * T / ((1 - sp.exp(-s1 * T)) * (1 - sp.exp(-s2 * T))), T, 0)
    informe(f"  con T -> 0 y A_m(1) = (1 - e^(-s1 T))(1 - e^(-s2 T)): error/Omega -> {aprox}  (s1 s2 = omega_n^2)")
    informe("  con acción integral en el controlador, R(1) = 0 y el error estacionario es cero")
    filas = []
    T_v, xi = 0.01, 0.7
    for tau_v in (0.1, 0.5):
        for wn_v in (5.0, 10.0, 20.0, 65.0):
            raices = [complex(-xi * wn_v, sgn * wn_v * math.sqrt(1 - xi**2)) for sgn in (1, -1)]
            Am1 = ((1 - complex(math.e) ** (raices[0] * T_v)) * (1 - complex(math.e) ** (raices[1] * T_v))).real
            seg = (1 - math.exp(-T_v / tau_v)) * T_v / Am1          # segundos de error por cada rad/s de giro
            filas.append({"T_s": T_v, "tau_c_s": tau_v, "omega_n_rad_s": wn_v, "xi": xi,
                          "error_por_cada_grado_por_segundo_deg": round(seg, 5),
                          "giro_maximo_para_10deg_deg_s": round(10.0 / seg, 1)})
    ruta = RAIZ / "derivados" / "modelo-rumbo-giro-maximo.csv"
    with ruta.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(filas)
    informe(f"  giro máximo del cuerpo que deja 10° de error sin acción integral -> {ruta.relative_to(RAIZ)}")
    for f in filas:
        informe(f"    tau_c = {f['tau_c_s']} s, omega_n = {f['omega_n_rad_s']} rad/s: "
                f"{f['error_por_cada_grado_por_segundo_deg']}° por cada °/s; 10° con {f['giro_maximo_para_10deg_deg_s']} °/s")
    informe()


def main() -> None:
    informe("Modelo de rumbo: comprobación simbólica (sympy). Generado por sim/modelo-rumbo.py; no editar a mano.")
    informe()
    cuerpo()
    A_r, B_r, C_r, K, tau = camara()
    combinado()
    estimador()
    discretizacion(A_r, B_r, C_r, K, tau)
    giro_del_cuerpo()
    TXT.parent.mkdir(parents=True, exist_ok=True)
    TXT.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"-> {TXT.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
