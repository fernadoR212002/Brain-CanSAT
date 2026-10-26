# salida/

Solo exportaciones listas para entregar o compartir. Todo lo de aquí sale de un script o de una skill; no se edita a mano.

## Archivos

- [matriz-requisitos.csv](matriz-requisitos.csv) — Matriz de trazabilidad RQ → RC → DEC → TST → evidencia → entrega. La regenera `python3 scripts/matriz-requisitos.py`. Punto decimal, separador coma, UTF-8.
- `figuras/` — figuras de simulaciones y pruebas:
  - [l-07-reproduccion-str.png](figuras/l-07-reproduccion-str.png): reproducción del ejemplo L-07, salida frente al modelo de referencia y voltaje (`sim/l-07-servomotor-self-tuning.py`).
  - [l-07-cero-de-muestreo.png](figuras/l-07-cero-de-muestreo.png): voltaje y salida con y sin cancelar el cero de muestreo (mismo script).
- `rev-xxx-AAAA-MM-DD.pdf` o `.pptx` — documentos de revisión exportados por la skill `revision`.
