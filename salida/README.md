# salida/

Solo exportaciones listas para entregar o compartir. Todo lo de aquí sale de un script o de una skill; no se edita a mano.

## Archivos

- [matriz-requisitos.csv](matriz-requisitos.csv) — Matriz de trazabilidad RQ → RC → DEC → TST → evidencia → entrega. La regenera `python3 scripts/matriz-requisitos.py`. Punto decimal, separador coma, UTF-8.
- `figuras/` — figuras de simulaciones y pruebas:
  - [l-07-reproduccion-str.png](figuras/l-07-reproduccion-str.png): reproducción del ejemplo L-07, salida frente al modelo de referencia y voltaje (`sim/l-07-servomotor-self-tuning.py`).
  - [l-07-cero-de-muestreo.png](figuras/l-07-cero-de-muestreo.png): voltaje y salida con y sin cancelar el cero de muestreo (mismo script).
- [presentacion-control-camara/](presentacion-control-camara/index.html) — presentación para el equipo, 7 diapositivas con three.js: el control con la regla de colores del modelo, el trabajo con el BNO055 y lo que sigue. La escribió Claude (no la genera un script) con los números de `derivados/` y de TST-003; `img/` trae copias de las capturas originales y `lazo-camara-colores.html` es el diagrama de archify. Se ve mejor publicada como Artifact privado: https://claude.ai/artifact/7NkQKFxgatcrG7yPeDGqz4.
- [presentacion-control-camara.html](presentacion-control-camara.html) — la misma presentación en un solo archivo, para enviar por WhatsApp, correo o Drive: imágenes en base64 y el diagrama de archify adentro. La escena 3D y las tipografías se cargan de internet; sin JavaScript (la vista previa de WhatsApp en iPhone) se leen el texto y las imágenes, pero no se mueven las animaciones. La regenera `python3 scripts/exportar-presentacion.py` después de cualquier cambio en la carpeta.
- `rev-xxx-AAAA-MM-DD.pdf` o `.pptx` — documentos de revisión exportados por la skill `revision`.
