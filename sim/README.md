# sim/

Scripts de Python reproducibles: modelos de planta, simulaciones de control y análisis de datos de pruebas y de telemetría. Las herramientas del brain (matriz, lint) están en [scripts/](../scripts/README.md).

- Entorno: [requirements.txt](requirements.txt) (numpy, scipy, pandas, matplotlib, control, pygeomag, sympy). En la nube lo instala el hook `SessionStart`; en local: `python3 -m pip install -r sim/requirements.txt`.
- Nombre: el ID de la nota a la que sirve: `sim/tst-004-analisis.py`, `sim/rc-003-descenso.py`.
- Cada script lee solo de `raw/` o `derivados/`, fija sus parámetros al inicio (con la fuente de cada uno), usa semilla fija si hay azar, escribe los CSV en `derivados/` y las figuras en `salida/figuras/`, e imprime las métricas. En el código y los CSV se usa punto decimal.
- Se corre desde la raíz del repo: `python3 sim/<script>.py`.

## Scripts

- [campo-geomagnetico.py](campo-geomagnetico.py) — Campo magnético de la Tierra (WMM2025) en Bogotá, Medellín y Monterey (Virginia): intensidad, inclinación, declinación y sensibilidad del rumbo. Escribe `derivados/campo-geomagnetico.csv`.
- [caracterizacion-sensores.py](caracterizacion-sensores.py) — Error de rumbo que deja cada fuente del giróscopo y del magnetómetro (sesgo, ruido, cuantización, hierro, inclinación, rotación de la Tierra), por sitio, y cumplimiento de PQ28 y PQ30. Escribe `derivados/caracterizacion-sensores.csv`.
- [modelo-rumbo.py](modelo-rumbo.py) — Comprobación simbólica (sympy) del modelo del lazo de rumbo: matrices, funciones de transferencia, rangos de controlabilidad y observabilidad, filtro complementario, discretización, cero de muestreo y error ante un giro constante del cuerpo. Escribe `derivados/modelo-rumbo.txt` y dos CSV.
- [l-07-servomotor-self-tuning.py](l-07-servomotor-self-tuning.py) — Reproducción del ejemplo L-07 (RLS + RST con la planta cambiando) y comparación entre cancelar y conservar el cero de muestreo. Escribe tres CSV `derivados/l-07-*.csv` y dos figuras en `salida/figuras/`.
- [servo-prueba-futaba.m](servo-prueba-futaba.m) — Prueba de banco del servomotor en MATLAB: barre los extremos (0 y 180 grados) y lo deja en el ángulo pedido, con pulso de 0,6 a 2,4 ms. Usa `servo_futaba` del brain de tesis del líder (fuera de este repo). No escribe archivos.
