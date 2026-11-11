# Estado del CanSat Brain

_Actualizado: 2026-11-11 (America/Bogota). Lo reescribe la skill `estado`; una página como máximo._

**Próximo paso:** conseguir los CSV de TST-003 y calibrar el magnetómetro con el montaje final, que ahora es la ruta crítica de C8 ([RSK-002](Riesgos/rsk-002-calibracion-magnetometro.md)). Después, cerrar el DEC-001 e identificar el actuador en banco.

## Resumen

| Indicador | Valor |
|---|---|
| Próxima revisión | PDR: 28-ene-2027 a las 23:59:59 UTC (18:59 en Bogotá), según el calendario (p. 56); la tabla 1 (p. 37) dice 30-ene |
| Días restantes | 78 |
| Requisitos de control verificados | 0 de 0 (los RQ aún no están cargados) |
| Riesgos altos abiertos | 1: [RSK-002](Riesgos/rsk-002-calibracion-magnetometro.md), calibración del magnetómetro en vuelo (además, 1 medio: [RSK-001](Riesgos/rsk-001-rango-servo-camara.md), recorrido del servo) |
| Archivos en `raw/inbox/` por procesar | 2 (`Servos.pdf` y `Rumbo de cámara CanSat.html`), más los restos de PlatformIO (`.pio`, `.vscode`) que esperan autorización para borrarse |
| Último lint | 2026-11-11 · 0 errores y 3 avisos (TST-001 a TST-003 no tienen RQ: los RQ aún no están cargados) |

Avance de control listo, en el brain y en Notion ([Sensores de rumbo](https://app.notion.com/p/404d9b500e34818c9d42dfebb09d3367)):

- la caracterización de los sensores ([nota](Conceptos/sensores-giroscopio-magnetometro.md), parte 4);
- el modelo en espacio de estados ([nota](Control/modelo-rumbo-espacio-estados.md));
- el ejemplo del seguidor de referencia ([L-07](Conceptos/l-07-servomotor-self-tuning.md)).

Código de prueba del servo en MATLAB: [servo-prueba-futaba.m](sim/servo-prueba-futaba.m).

Nuevo:

- [TST-003](Pruebas/tst-003-bno055-sin-calibrar-esp32-matlab.md) es la primera lectura del BNO055 real sin calibrar (ESP32 clásico, MATLAB en vivo). Llegaron solo capturas, sin CSV. A ojo, el rumbo sin calibrar se desvía del orden de 20°. La ley L3 no cambia, pero la calibración del magnetómetro pasa a ser la ruta crítica, y el lazo debe ir a 100 Hz ([sección 9 del diseño](Control/diseno-estabilizacion-camara.md)).
- Réplica de L3 en Simulink con colores por función: [simulink_lazo_camara_l3.m](sim/simulink_lazo_camara_l3.m) → [lazo_camara_l3.slx](sim/lazo_camara_l3.slx). Da 3,01° en S1 y 2,60° en S2, y cuadra con Python.
- Presentación para el equipo, 7 diapositivas con three.js: el control explicado con los colores del modelo, el trabajo de Luis con el BNO055 y la prueba con el recovery que falta ([fuente](salida/presentacion-control-camara/index.html) · [Artifact](https://claude.ai/artifact/7NkQKFxgatcrG7yPeDGqz4)).

Antes: [TST-002](Pruebas/tst-002-guia-datos-estacionarios-sensores.md), guía de laboratorio para que eléctrica tome datos estacionarios del BNO055 y el LIS3MDL reales y mida la interferencia del servo ([PDF](salida/tst-002-guia-laboratorio-sensores.pdf)).

También: [opciones de control del lazo de la cámara](Control/diseno-estabilizacion-camara.md). Se recomienda un RST con integrador que conserva el cero de muestreo, más prealimentación del giróscopo. Error de control ≤ 0,27° en simulación; el cuello de botella es el estimador de rumbo.

## Pendientes

> [!WARNING]
> **Pendiente**
> 1. Integrantes del equipo y frente de cada uno.
> 2. Alcance completo de «control». El primer frente es la estabilización de video (C8, C11, PQ15–PQ18).
> 3. Si el repositorio es solo del líder de control o de todo el equipo.
> 4. Confirmar con la organización tres cosas: qué fechas valen (la guía se contradice), el sitio de lanzamiento y si el norte es el verdadero o el magnético.
> 5. Las 4 capturas de [TST-001](Pruebas/tst-001-exploracion-sensores-celular.md) y las 2 figuras de L-07 faltan en Notion: la red del entorno bloquea `api.notion.com`, así que hay que arrastrarlas a mano.
> 6. Las hojas de datos oficiales del BNO055 y del LIS3MDL (L-08 y L-09): la red del entorno bloquea esos dominios. Hay que subirlas por `raw/inbox/` para confirmar los valores no validados de la caracterización.
> 7. La decisión del actuador y de la ley de control (DEC-001): faltan los pesos del equipo. El servo de 180° tiene el riesgo [RSK-001](Riesgos/rsk-001-rango-servo-camara.md).
> 8. Los CSV de TST-003, el sitio de la prueba y la tarjeta de vuelo: el ESP32 clásico funcionó, y la base Hardware dice ESP32-S3.

## Tres próximos pasos

1. Subir los CSV de TST-003 y analizarlos con un script. Ejecutar TST-002 a 100 Hz, con datos crudos y con el LIS3MDL, y calibrar el magnetómetro con elipsoide. Procesar `Servos.pdf` con `subir`. Después, acordar los pesos y cerrar el DEC-001 del actuador y la ley de control (skill `decision`), y subir las hojas de datos.
2. Identificar el servo ($K_c$, $\tau_c$) en banco y medir el giro del PocketQube bajo el paracaídas con una caída desde dron (skill `prueba`).
3. «requisitos»: crear los RQ literales y los RC del lazo de rumbo (C8, C11, PQ15–PQ18, PQ28, PQ30); después, el acelerómetro, el filtro complementario y el RST que conserva el cero de muestreo, con acción integral.
