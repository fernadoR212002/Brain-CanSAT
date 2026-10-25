# sim/

Scripts de Python reproducibles: modelos de planta, simulaciones de control y análisis de datos de pruebas y de telemetría. Las herramientas del brain (matriz, lint) están en [scripts/](../scripts/README.md).

- Entorno: [requirements.txt](requirements.txt) (numpy, scipy, pandas, matplotlib, control). En la nube lo instala el hook `SessionStart`; en local: `python3 -m pip install -r sim/requirements.txt`.
- Nombre: el ID de la nota a la que sirve: `sim/tst-004-analisis.py`, `sim/rc-003-descenso.py`.
- Cada script lee solo de `raw/` o `derivados/`, fija sus parámetros al inicio (con la fuente de cada uno), usa semilla fija si hay azar, escribe los CSV en `derivados/` y las figuras en `salida/figuras/`, e imprime las métricas. En el código y los CSV se usa punto decimal.
- Se corre desde la raíz del repo: `python3 sim/<script>.py`.

## Scripts

- [campo-geomagnetico.py](campo-geomagnetico.py) — Campo magnético de la Tierra (WMM2025) en Bogotá, Medellín y Monterey (Virginia): intensidad, inclinación, declinación y sensibilidad del rumbo. Escribe `derivados/campo-geomagnetico.csv`.
