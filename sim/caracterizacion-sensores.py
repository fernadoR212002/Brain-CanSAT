#!/usr/bin/env python3
"""Caracterización del giróscopo y del magnetómetro: cuánto error de rumbo deja cada fuente.

Reproduce las tablas de la parte 4 de Conceptos/sensores-giroscopio-magnetometro.md.
Uso (desde la raíz del repo):  python3 sim/caracterizacion-sensores.py
Usa los mismos sitios y el mismo modelo WMM2025 que sim/campo-geomagnetico.py (sin redondear)
y escribe derivados/caracterizacion-sensores.csv, en formato largo: sitio, magnitud, valor, unidad, fuente.

Cada parámetro lleva su fuente. Los marcados «no validado» salen de resúmenes de buscador
o de foros (raw/LINKS.md) y hay que confirmarlos con las hojas de datos oficiales.
"""
import csv
import importlib.util
import math
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "derivados" / "caracterizacion-sensores.csv"

# Requisitos de la guía (raw/mision/cansat-mission-guide-2027-r1.1.pdf)
PQ28_DEG_S = 0.1          # resolución del giróscopo, p. 15
PQ30_MG = 1.0             # resolución del magnetómetro, p. 15
C8_DEG = 10.0             # rotación máxima del video, p. 9
T_COMANDO_S = 30.0        # el comando de giro de 90° llega a los 30 s de vuelo, p. 6

# Parámetros de los sensores: (valor, unidad, fuente)
LIS3MDL_LSB_MG = (1000 / 6842, "mG", "raw/datos/notion-hardware-2026-10-25.md (0.146 mG/LSB en ±4 G); 6842 LSB/G en L-12, no validado")
LIS3MDL_RUIDO_MG = (3.2, "mG rms (ejes X e Y)", "L-13, no validado")
BNO055_MAG_LSB_MG = (3.0, "mG (≈ 0.3 µT)", "L-11, no validado")
BNO055_GIR_LSB = (1 / 16, "°/s (16 LSB por °/s)", "L-10, no validado")
GIR_DENSIDAD = (0.014, "°/s/√Hz", "L-14: valor del BMI055, no del BNO055; no validado")
GIR_SESGOS = ((1.0, "°/s", "L-15: desfase típico del BMI088, no validado"),
              (0.1, "°/s", "supuesto: sesgo residual tras calibrar"),
              (0.01, "°/s", "supuesto: sesgo residual tras calibrar bien"))
OMEGA_TIERRA = 7.292115e-5   # rad/s, rotación de la Tierra (constante del WGS84)
TIEMPOS_S = (30.0, 60.0, 120.0, 180.0)   # 30 s: comando de giro; 2–3 min: descenso según raw/datos
INCLINACIONES_DEG = (1.0, 2.0, 5.0, 10.0)
R_MOTOR_SIN_BRAZO_MM = 30.0   # supuesto ilustrativo: magnetómetro junto al motor, sin brazo
R_BRAZO_MM = 220.0            # PQ10, p. 13


def campo_por_sitio() -> list[dict]:
    """Campo WMM2025 sin redondear, con los sitios de sim/campo-geomagnetico.py."""
    spec = importlib.util.spec_from_file_location("campo", RAIZ / "sim" / "campo-geomagnetico.py")
    campo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(campo)
    geo = campo.GeoMag(coefficients_file="wmm/WMM_2025.COF")
    sitios = []
    for nombre, lat, lon, alt_km, fecha in campo.SITIOS:
        r = geo.calculate(glat=lat, glon=lon, alt=alt_km, time=campo.anio_decimal(fecha))
        sitios.append({"sitio": nombre, "latitud_deg": lat, "H_mG": r.h / 100, "F_mG": r.f / 100, "I_deg": r.i})
    return sitios


def main() -> None:
    sitios = campo_por_sitio()
    filas = []

    def fila(sitio, magnitud, valor, unidad, fuente):
        filas.append({"sitio": sitio, "magnitud": magnitud, "valor": valor, "unidad": unidad, "fuente": fuente})

    # 1. Requisitos de resolución (no dependen del sitio)
    q_g = BNO055_GIR_LSB[0]
    fila("todos", "resolucion_giroscopio_BNO055", round(q_g, 4), "°/s", BNO055_GIR_LSB[2])
    fila("todos", "cumple_PQ28_0.1_deg_s", "sí" if q_g <= PQ28_DEG_S else "no", "", "comparación con PQ28 (p. 15)")
    fila("todos", "resolucion_magnetometro_LIS3MDL", round(LIS3MDL_LSB_MG[0], 3), "mG", LIS3MDL_LSB_MG[2])
    fila("todos", "cumple_PQ30_1_mG_LIS3MDL", "sí" if LIS3MDL_LSB_MG[0] <= PQ30_MG else "no", "", "comparación con PQ30 (p. 15)")
    fila("todos", "resolucion_magnetometro_BNO055", BNO055_MAG_LSB_MG[0], "mG", BNO055_MAG_LSB_MG[2])
    fila("todos", "cumple_PQ30_1_mG_BNO055", "sí" if BNO055_MAG_LSB_MG[0] <= PQ30_MG else "no", "", "comparación con PQ30 (p. 15)")
    fila("todos", "ruido_cuantizacion_giroscopio", round(q_g / math.sqrt(12), 4), "°/s rms", "q/√12 con la resolución de L-10")

    # 2. Giróscopo: deriva por sesgo y caminata aleatoria del ángulo
    for b, unidad, fuente in GIR_SESGOS:
        fila("todos", f"tiempo_hasta_10deg_con_sesgo_{b}_deg_s", round(C8_DEG / b, 1), "s", fuente)
        for t in TIEMPOS_S:
            fila("todos", f"deriva_por_sesgo_{b}_deg_s_en_{int(t)}_s", round(b * t, 2), "°", fuente)
    for t in TIEMPOS_S:
        fila("todos", f"caminata_aleatoria_en_{int(t)}_s", round(GIR_DENSIDAD[0] * math.sqrt(t), 3), "° (1 sigma)",
             GIR_DENSIDAD[2] + "; sigma = N·√t, con un factor √2 según la convención de densidad")

    # Error de factor de escala: un giro de 90° (C11) medido con un error de escala del 1 % (supuesto)
    fila("todos", "error_por_factor_de_escala_1pct_en_giro_de_90deg", round(0.01 * 90.0, 2), "°",
         "s_g · delta_psi con s_g = 1 % (supuesto) y el giro de 90° de C11")

    # 3. Factor de reducción de la interferencia por el brazo (dipolo, 1/r^3)
    fila("todos", "reduccion_interferencia_dipolo_brazo", round((R_BRAZO_MM / R_MOTOR_SIN_BRAZO_MM) ** 3, 0), "veces",
         f"(220/{R_MOTOR_SIN_BRAZO_MM:.0f})^3; 220 mm de PQ10 y {R_MOTOR_SIN_BRAZO_MM:.0f} mm supuesto")

    # 4. Magnetómetro y giróscopo, por sitio
    for s in sitios:
        nombre = s["sitio"]
        H_mG = s["H_mG"]
        F_mG = s["F_mG"]
        incl = math.radians(s["I_deg"])
        lat = math.radians(float(s["latitud_deg"]))
        fila(nombre, "campo_total_esperado_tras_calibrar", round(F_mG, 0), "mG", "WMM2025 (L-01, L-02)")
        fila(nombre, "campo_horizontal", round(H_mG, 0), "mG", "WMM2025 (L-01, L-02)")
        fila(nombre, "ruido_rumbo_LIS3MDL_por_muestra",
             round(math.degrees(LIS3MDL_RUIDO_MG[0] / H_mG), 3), "° rms", "sigma_psi = sigma_B / H con " + LIS3MDL_RUIDO_MG[2])
        fila(nombre, "cuantizacion_rumbo_LIS3MDL",
             round(math.degrees(LIS3MDL_LSB_MG[0] / (math.sqrt(12) * H_mG)), 4), "° rms", "q / (√12 H)")
        fila(nombre, "cuantizacion_rumbo_telemetria_1_mG",
             round(math.degrees(PQ30_MG / (math.sqrt(12) * H_mG)), 4), "° rms", "q / (√12 H) con la resolución de PQ30")
        fila(nombre, "cuantizacion_rumbo_BNO055",
             round(math.degrees(BNO055_MAG_LSB_MG[0] / (math.sqrt(12) * H_mG)), 4), "° rms", "q / (√12 H) con " + BNO055_MAG_LSB_MG[2])
        for err in (1.0, 5.0, C8_DEG):
            fila(nombre, f"perturbacion_transversal_para_{err:g}deg", round(H_mG * math.tan(math.radians(err)), 1), "mG",
                 "delta_h = H tan(delta_psi), perturbación perpendicular a H")
        for d in INCLINACIONES_DEG:
            dpsi = math.degrees(math.atan(math.tan(incl) * math.sin(math.radians(d))))
            fila(nombre, f"error_rumbo_por_inclinacion_{d:g}deg", round(dpsi, 2), "°",
                 "atan(tan I · sin delta), peor caso: inclinación sobre el eje del campo horizontal")
        delta_max = math.degrees(math.asin(min(1.0, math.tan(math.radians(C8_DEG)) / math.tan(incl))))
        fila(nombre, "inclinacion_sin_compensar_que_agota_10deg", round(delta_max, 2), "°",
             "delta = asin(tan 10° / tan I)")
        w_v = OMEGA_TIERRA * math.sin(lat)
        fila(nombre, "rotacion_tierra_sobre_la_vertical", round(math.degrees(w_v), 5), "°/s", "Omega_T · sin(latitud)")
        fila(nombre, "deriva_por_rotacion_tierra_en_180_s", round(math.degrees(w_v) * 180, 3), "°", "Omega_T · sin(latitud) · 180 s")

    with SALIDA.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(filas)

    ancho = max(len(r["magnitud"]) for r in filas)
    for r in filas:
        print(f"{r['sitio']:20s} {r['magnitud']:{ancho}s} {str(r['valor']):>9s} {r['unidad']}")
    print(f"-> {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
