#!/usr/bin/env python3
"""Campo geomagnético (modelo WMM2025) en los sitios de prueba y en el sitio de lanzamiento.

Reproduce los valores de Conceptos/sensores-giroscopio-magnetometro.md.
Uso (desde la raíz del repo):  python3 sim/campo-geomagnetico.py
Escribe derivados/campo-geomagnetico.csv e imprime la tabla.

Fuentes: modelo WMM2025 de NOAA (raw/LINKS.md, L-01) mediante pygeomag (L-02).
Supuestos: las coordenadas son el centro aproximado de cada ciudad; el sitio de
lanzamiento (Monterey, Virginia) viene de L-03, una fuente no validada.
"""
import csv
import math
from datetime import date
from pathlib import Path

from pygeomag import GeoMag

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "derivados" / "campo-geomagnetico.csv"

# (sitio, latitud en grados, longitud en grados, altitud en km, fecha de uso)
SITIOS = [
    ("Bogotá", 4.711, -74.072, 2.6, date(2026, 10, 25)),               # pruebas en Colombia
    ("Medellín", 6.244, -75.581, 1.5, date(2026, 10, 25)),             # pruebas en Colombia
    ("Monterey, Virginia", 38.4126, -79.5806, 0.9, date(2027, 6, 12)),  # día del lanzamiento
]


def anio_decimal(d: date) -> float:
    """Año decimal al mediodía del día dado, como lo pide el WMM."""
    inicio = date(d.year, 1, 1)
    dias_del_anio = (date(d.year + 1, 1, 1) - inicio).days
    return d.year + ((d - inicio).days + 0.5) / dias_del_anio


def main() -> None:
    geo = GeoMag(coefficients_file="wmm/WMM_2025.COF")
    filas = []
    for sitio, lat, lon, alt_km, fecha in SITIOS:
        r = geo.calculate(glat=lat, glon=lon, alt=alt_km, time=anio_decimal(fecha))
        tan_i = math.tan(math.radians(r.i))
        filas.append({
            "sitio": sitio,
            "fecha": fecha.isoformat(),
            "latitud_deg": lat,
            "longitud_deg": lon,
            "altitud_km": alt_km,
            "total_uT": round(r.f / 1000, 1),
            "horizontal_uT": round(r.h / 1000, 1),
            "vertical_uT": round(r.z / 1000, 1),
            "inclinacion_deg": round(r.i, 1),
            "declinacion_deg": round(r.d, 1),
            "tan_inclinacion": round(tan_i, 2),
            # Error de rumbo que deja 1° de error de inclinación sobre el eje norte–sur.
            "error_rumbo_por_1deg_de_inclinacion_deg": round(
                math.degrees(math.atan(tan_i * math.sin(math.radians(1.0)))), 2),
            # Perturbación magnética transversal que produce 1° de error de rumbo (1 µT = 10 mG).
            "perturbacion_para_1deg_de_rumbo_mG": round(r.h / 100 * math.tan(math.radians(1.0)), 1),
        })

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with SALIDA.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)

    print(f"{'sitio':20s} {'fecha':10s} {'total':>7s} {'horiz':>7s} {'vert':>7s} {'incl':>6s} {'decl':>6s} {'tanI':>5s} {'err/1°':>7s} {'mG/1°':>6s}")
    for f in filas:
        print(f"{f['sitio']:20s} {f['fecha']:10s} {f['total_uT']:7.1f} {f['horizontal_uT']:7.1f} {f['vertical_uT']:7.1f} "
              f"{f['inclinacion_deg']:6.1f} {f['declinacion_deg']:6.1f} {f['tan_inclinacion']:5.2f} "
              f"{f['error_rumbo_por_1deg_de_inclinacion_deg']:7.2f} {f['perturbacion_para_1deg_de_rumbo_mG']:6.1f}")
    print(f"(campo en µT, ángulos en grados) → {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
