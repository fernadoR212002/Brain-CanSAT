"""Compara seis estimadores de rumbo con las lecturas del simulador de cámara.

Ejecutar desde la raíz con python3 sim/filtro-kalman-rumbo.py.
Los estados internos usan radianes y segundos. Cada error compara la salida
con el cuerpo en el instante de entrega, incluida la latencia del sensor.
Las desviaciones de Kalman son posteriores y describen su modelo de ruido.
"""

import importlib.util
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from scipy.linalg import solve_discrete_are

matplotlib.use("Agg")
from matplotlib import pyplot as plt


RUTA_BASE = Path(__file__).resolve().with_name("diseno-estabilizacion-camara.py")
RAIZ = RUTA_BASE.parent.parent
especificacion = importlib.util.spec_from_file_location("estabilizacion_camara", RUTA_BASE)
base = importlib.util.module_from_spec(especificacion)
# Cargar la fuente inmutable sin crear archivos auxiliares en el repositorio.
escritura_previa = sys.dont_write_bytecode
try:
    sys.dont_write_bytecode = True
    especificacion.loader.exec_module(base)
finally:
    sys.dont_write_bytecode = escritura_previa

T, NSUB, TF = base.T, base.NSUB, base.TF  # Fuente: mallas de simulate() y body_profile().
D2R, R2D, wrap, body_profile = base.D2R, base.R2D, base.wrap, base.body_profile
SEMILLA = 1  # Fuente: valor por defecto de body_profile() y simulate().
SEMILLA_SENSORES = SEMILLA + 100  # Fuente: generador de simulate().
SESGO_REAL = 0.5 * D2R  # rad/s. Sin fuente en raw/: supuesto de simulate().
SIGMA_G = 0.1 * D2R  # rad/s por muestra. Sin fuente en raw/: supuesto de simulate().
PASO_G = D2R / 16  # rad/s. Fuente: simulate() y L-10 (BNO055, sin validar).
SIGMA_M = 0.9 * D2R  # rad. Fuente: simulate(), redondeo para Monterey de caracterizacion-sensores.csv.
ERROR_FIJO = 1.5 * D2R  # rad. Sin fuente en raw/: supuesto de simulate().
ERROR_AMPLITUD = 2.0 * D2R  # rad. Sin fuente en raw/: supuesto de simulate().
ERROR_FRECUENCIA = 0.4  # Hz. Sin fuente en raw/: supuesto de simulate().
WE, ZE = 0.5, 0.7  # rad/s y adimensional. Fuente: observador de simulate().
L1, L2 = 2 * ZE * WE, WE**2  # Fuente: polos del complementario de simulate().
CAMINATA_SESGO = 0.01 * D2R  # (rad/s)/√s. Sin fuente en raw/: supuesto de sintonía.
SIGMA_SESGO_INICIAL = 1.0 * D2R  # rad/s. Fuente: Conceptos/sensores-giroscopio-magnetometro.md, L-15 (BMI088, sin validar).
SESGO_INICIAL = 0.0  # rad/s. Fuente: inicialización solicitada y simulate().
F = np.array([[1.0, -T], [0.0, 1.0]])  # Fuente: predicción discreta solicitada.
H = np.array([[1.0, 0.0]])  # Fuente: observación solicitada del rumbo.
Q = np.diag([(T * SIGMA_G)**2, CAMINATA_SESGO**2 * T])  # Fuente: modelo de proceso solicitado.
R = SIGMA_M**2  # Fuente: modelo de ruido blanco solicitado para el magnetómetro.
P0 = np.diag([R, SIGMA_SESGO_INICIAL**2])  # Fuente: incertidumbre inicial solicitada.
UMBRAL_COMPUERTA = 9.0  # Fuente: criterio solicitado para la innovación normalizada al cuadrado.
TOL_RICCATI = 1e-6  # Fuente: tolerancia relativa solicitada para cada ganancia.
FIN_ARRANQUE = 5.0  # s. Fuente: ventana de métricas solicitada.
INSTANTES_SESGO = (2.0, 5.0)  # s. Fuente: revisión de Claude; reemplaza la banda de convergencia de 0.05 °/s, que el ruido cruzaba al azar.
INICIO_PULSO, FIN_PULSO = 20.0, 23.0  # s. Fuente: perturbación solicitada, intervalo [inicio, fin).
PULSO = 20.0 * D2R  # rad. Sin fuente en raw/: supuesto ilustrativo del motor solicitado.
FIN_VENTANA = 26.0  # s. Fuente: último instante incluido en la métrica de perturbación.
MUESTRAS_ARRANQUE = (0.0, 14.75, 0.25)  # s. Fuente: inicio, fin y paso del CSV solicitado.
MUESTRAS_PULSO = (18.0, 26.85, 0.15)  # s. Fuente: inicio, fin y paso del CSV solicitado.
EQUIVALENTE = "complementario_con_ganancias_de_kalman"


def lecturas(escenario):
    """Reproduce incluso el orden de extracción del ruido de simulate()."""
    tiempo_fino, rumbo, velocidad, _ = body_profile(escenario, seed=SEMILLA)
    i0 = np.arange(round(TF / T)) * NSUB
    j = np.maximum(i0 - NSUB, 0)
    t = tiempo_fino[i0]
    ruido_g, ruido_m = np.random.default_rng(SEMILLA_SENSORES).standard_normal((len(t), 2)).T
    w = np.round((velocidad[j] + SESGO_REAL + SIGMA_G * ruido_g) / PASO_G) * PASO_G
    residuo = ERROR_FIJO + ERROR_AMPLITUD * np.sin(2 * np.pi * ERROR_FRECUENCIA * t)
    mag_nominal = rumbo[j] + residuo + SIGMA_M * ruido_m
    mag_blanco = rumbo[j] + SIGMA_M * ruido_m
    return t, rumbo[i0], w, mag_nominal, mag_blanco


def complementario(w, mag, l1, l2):
    """Replica la actualización de simulate(), incluida la primera muestra."""
    rumbo, sesgo = mag[0], SESGO_INICIAL
    rumbos, sesgos = np.empty_like(w), np.empty_like(w)
    for k in range(len(w)):
        innovacion = wrap(mag[k] - rumbo)
        rumbo += T * (w[k] - sesgo + l1 * innovacion)
        sesgo -= T * l2 * innovacion
        rumbos[k], sesgos[k] = rumbo, sesgo
    return rumbos, sesgos


def ganancia(previa):
    """Calcula K y la varianza escalar S para H = [1, 0]."""
    varianza = previa[0, 0] + R
    return previa[:, 0] / varianza, varianza


def joseph(previa, k):
    """Covarianza posterior en forma de Joseph."""
    resto = np.eye(2) - k[:, None] @ H
    return resto @ previa @ resto.T + R * np.outer(k, k)


def kalman(w, mag, compuerta=False):
    """Corrige con la lectura retrasada y luego predice hasta el instante actual.

    El giróscopo y el magnetómetro de la muestra k describen el instante k-1 (una
    muestra de latencia). Por eso se corrige primero el rumbo predicho para k-1 y
    después se avanza una muestra con el giróscopo: la salida es el rumbo actual,
    en el mismo orden que el complementario de simulate(). Si se predijera antes
    de corregir, la salida quedaría una muestra atrás del cuerpo.
    """
    estados = np.empty((len(w), 2))
    ganancias, desviaciones = np.empty_like(estados), np.empty_like(estados)
    estado = np.array([mag[0], SESGO_INICIAL])
    p = P0.copy()
    for i in range(len(w)):
        if i == 0:
            # La primera lectura inicializa el rumbo: peso efectivo 1, sin corrección del sesgo.
            # Las filas 0 y 1 describen el mismo instante (latencia con j = max(i0 - NSUB, 0)),
            # así que aquí no se predice: el ciclo de corrección y predicción empieza en i = 1.
            # Hallazgo de la revisión de Codex.
            ganancias[0] = (1.0, 0.0)
            desviaciones[0] = np.sqrt(np.diag(p))
            estados[0] = estado
            continue
        else:
            k, varianza = ganancia(p)
            innovacion = wrap(mag[i] - estado[0])
            if compuerta and innovacion**2 / varianza > UMBRAL_COMPUERTA:
                ganancias[i] = 0.0
            else:
                estado = estado + k * innovacion
                p = joseph(p, k)
                ganancias[i] = k
        desviaciones[i] = np.sqrt(np.diag(p))   # posterior, como en estacionario()
        # Predicción hasta el instante actual con el giróscopo (la parte predictiva).
        estado = F @ estado
        estado[0] += T * w[i]
        p = F @ p @ F.T + Q
        estados[i] = estado
    return estados.T, ganancias, desviaciones


def estacionario():
    """La Riccati dual da la covarianza previa. Joseph da la posterior."""
    previa = solve_discrete_are(F.T, H.T, Q, np.array([[R]]))
    k, _ = ganancia(previa)
    desv = np.sqrt(np.diag(joseph(previa, k))) * R2D
    l1, l2 = k[0] / T, -k[1] / T
    frecuencia = np.sqrt(l2)
    base_actual = "sim/diseno-estabilizacion-camara.py: simulate()"
    filas = [
        ("K_rumbo", k[0], "1", "Riccati discreta, ganancia de corrección"),
        ("K_sesgo", k[1], "1/s", "Riccati discreta, ganancia de corrección"),
        ("l1_eq", l1, "1/s", "K_rumbo / T"),
        ("l2_eq", l2, "1/s²", "-K_sesgo / T"),
        ("frecuencia_natural_eq", frecuencia, "rad/s", "raíz cuadrada de l2_eq"),
        ("amortiguamiento_eq", l1 / (2 * frecuencia), "1", "l1_eq / (2 · frecuencia_natural_eq)"),
        ("desviacion_rumbo", desv[0], "°", "covarianza posterior estacionaria"),
        ("desviacion_sesgo", desv[1], "°/s", "covarianza posterior estacionaria"),
        ("l1_actual", L1, "1/s", base_actual),
        ("l2_actual", L2, "1/s²", base_actual),
        ("frecuencia_natural_actual", WE, "rad/s", base_actual),
    ]
    return k, l1, l2, pd.DataFrame(filas, columns=["magnitud", "valor", "unidad", "fuente"])


def error_sesgo(sesgo, instante):
    """Error absoluto del sesgo estimado en un instante, en grados por segundo."""
    if sesgo is None:
        return np.nan
    return abs(sesgo[round(instante / T)] - SESGO_REAL) * R2D


def indices(malla):
    """Selecciona muestras por su índice entero e incluye el extremo final."""
    inicio, fin, paso = (round(s / T) for s in malla)
    return np.arange(inicio, fin + 1, paso)


def exportar(nombre, tabla):
    """Escribe e imprime la tabla completa con punto decimal y vacíos para NaN."""
    contenido = tabla.to_csv(index=False, float_format="%.12g", lineterminator="\n")
    ruta = RAIZ / "derivados" / f"filtro-kalman-rumbo-{nombre}.csv"
    ruta.write_text(contenido, encoding="utf-8")
    print(ruta.relative_to(RAIZ))
    print(contenido)


def figura(arranque, perturbacion):
    """Dibuja las trazas a resolución completa en las ventanas de los dos CSV."""
    fig, (sesgo, peso, error) = plt.subplots(3, 1, figsize=(11, 10), layout="constrained")
    t = arranque.t_s
    sesgo.plot(t, arranque.sesgo_complementario_deg_s, color="tab:blue", label="Complementario, error magnético nominal")
    sesgo.plot(t, arranque.sesgo_kalman_deg_s, color="tab:orange", label="Kalman, error magnético nominal")
    sesgo.plot(t, arranque.sesgo_complementario_blanco_deg_s, color="tab:blue", ls="--",
               label="Complementario, solo ruido blanco")
    sesgo.plot(t, arranque.sesgo_kalman_blanco_deg_s, color="tab:orange", ls="--", label="Kalman, solo ruido blanco")
    sesgo.axhline(SESGO_REAL * R2D, color="black", linestyle=":", label="Sesgo verdadero")
    sesgo.set(title="Estimación del sesgo durante el arranque", ylabel="Sesgo (grados por segundo)")
    peso.semilogy(t, arranque.ganancia_rumbo_kalman, color="tab:orange", label="Kalman")
    peso.semilogy(t, arranque.ganancia_rumbo_complementario, color="tab:blue", label="Complementario actual")
    peso.set(title="Peso de la lectura magnética en el rumbo durante el arranque",
             ylabel="Ganancia de rumbo (adimensional)")
    for eje in (sesgo, peso):
        eje.set_xlim(*MUESTRAS_ARRANQUE[:2])
    t = perturbacion.t_s
    error.plot(t, perturbacion.err_solo_magnetometro_deg, color="0.6", lw=0.9, label="Solo magnetómetro")
    error.plot(t, perturbacion.err_complementario_deg, label="Complementario actual")
    error.plot(t, perturbacion.err_kalman_deg, label="Kalman")
    error.plot(t, perturbacion.err_kalman_compuerta_deg, label="Kalman con compuerta")
    error.axvspan(INICIO_PULSO, FIN_PULSO, color="tab:red", alpha=0.08, label="Perturbación aplicada")
    error.set(title="Error de rumbo ante la perturbación magnética", ylabel="Error de rumbo (grados)",
              xlim=MUESTRAS_PULSO[:2])
    for eje in (sesgo, peso, error):
        eje.set_xlabel("Tiempo (segundos)")
        eje.grid(axis="y", alpha=0.25)
    for eje in (sesgo, peso):
        eje.legend(loc="best", ncol=2)
    error.legend(loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=3)
    fig.savefig(RAIZ / "salida/figuras/filtro-kalman-rumbo.png", dpi=150)
    plt.close(fig)


def main():
    k_inf, l1_eq, l2_eq, tabla_estacionaria = estacionario()
    filas = []
    for escenario in ("S1", "S2"):
        t, verdad, w, mag_nominal, mag_blanco = lecturas(escenario)
        casos = {f"{escenario}_nominal": mag_nominal}
        if escenario == "S2":
            pulso = (t >= INICIO_PULSO) & (t < FIN_PULSO)
            casos.update(S2_sin_error_mag=mag_blanco, S2_perturbado=mag_nominal + PULSO * pulso)
        for caso, mag in casos.items():
            estados, ganancias, desv = kalman(w, mag)
            diferencia_relativa = np.abs((ganancias[-1] - k_inf) / k_inf)
            assert np.all(diferencia_relativa < TOL_RICCATI), (caso, diferencia_relativa)
            con_compuerta, _, _ = kalman(w, mag, compuerta=True)
            # La primera lectura fija el origen; w[k] integra el intervalo que termina en t[k].
            integrado = mag[0] + T * np.r_[0.0, np.cumsum(w[1:])]
            actual = complementario(w, mag, L1, L2)
            estimaciones = {
                "solo_giroscopo": (integrado, None),
                "solo_magnetometro": (mag, None),
                "complementario_actual": actual,
                "kalman": estados,
                EQUIVALENTE: complementario(w, mag, l1_eq, l2_eq),
                "kalman_con_compuerta": con_compuerta,
            }
            errores = {}
            regimen = t >= FIN_ARRANQUE
            ventana = (t >= INICIO_PULSO) & (t <= FIN_VENTANA)
            for nombre, (rumbo, sesgo) in estimaciones.items():
                error = wrap(rumbo - verdad) * R2D
                errores[nombre] = error
                filas.append(dict(
                    caso=caso, estimador=nombre,
                    max_abs_err_deg=np.max(np.abs(error[regimen])),
                    rms_err_deg=np.sqrt(np.mean(error[regimen]**2)),
                    max_abs_err_arranque_deg=np.max(np.abs(error[~regimen])),
                    err_sesgo_2s_deg_s=error_sesgo(sesgo, INSTANTES_SESGO[0]),
                    err_sesgo_5s_deg_s=error_sesgo(sesgo, INSTANTES_SESGO[1]),
                    max_abs_err_ventana_deg=np.max(np.abs(error[ventana])) if caso == "S2_perturbado" else np.nan,
                ))
            if caso == "S2_nominal":
                diferencia = wrap(estimaciones[EQUIVALENTE][0] - estados[0])
                avance = T * (w - SESGO_REAL)
                print(f"S2 nominal desde {FIN_ARRANQUE:g} s: diferencia media de rumbo "
                      f"(complementario equivalente menos Kalman) {diferencia[regimen].mean() * R2D:.4f} grados; "
                      f"avance medio por muestra {avance[regimen].mean() * R2D:.4f} grados.")
                arranque = pd.DataFrame(dict(
                    t_s=t, sesgo_complementario_deg_s=actual[1] * R2D, sesgo_kalman_deg_s=estados[1] * R2D,
                    ganancia_rumbo_kalman=ganancias[:, 0], ganancia_sesgo_kalman=ganancias[:, 1],
                    desviacion_rumbo_kalman_deg=desv[:, 0] * R2D, desviacion_sesgo_kalman_deg_s=desv[:, 1] * R2D,
                    ganancia_rumbo_complementario=T * L1,
                ))
            if caso == "S2_sin_error_mag":
                # Mismo arranque con el error magnético como ruido blanco: el modelo del filtro es correcto.
                arranque["sesgo_complementario_blanco_deg_s"] = actual[1] * R2D
                arranque["sesgo_kalman_blanco_deg_s"] = estados[1] * R2D
            if caso == "S2_perturbado":
                perturbacion = pd.DataFrame(dict(
                    t_s=t, err_complementario_deg=errores["complementario_actual"], err_kalman_deg=errores["kalman"],
                    err_kalman_compuerta_deg=errores["kalman_con_compuerta"],
                    err_solo_magnetometro_deg=errores["solo_magnetometro"],
                ))
    print(f"Máxima diferencia relativa final de las ganancias frente a Riccati: {max(diferencia_relativa):.3e}")
    exportar("metricas", pd.DataFrame(filas))
    exportar("estacionario", tabla_estacionaria)
    exportar("arranque", arranque.iloc[indices(MUESTRAS_ARRANQUE)])
    exportar("perturbacion", perturbacion.iloc[indices(MUESTRAS_PULSO)])
    figura(arranque, perturbacion)


if __name__ == "__main__":
    main()
