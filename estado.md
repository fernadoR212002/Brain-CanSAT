# Estado del CanSat Brain

_Actualizado: 2026-11-10 (America/Bogota). Lo reescribe la skill `estado`; una página como máximo._

**Próximo paso:** acordar los pesos del DEC-001 (ley de control y actuador de la cámara), medir el giro del PocketQube con una caída desde dron e identificar el actuador en banco.

## Resumen

| Indicador | Valor |
|---|---|
| Próxima revisión | PDR: 28-ene-2027 a las 23:59:59 UTC (18:59 en Bogotá), según el calendario (p. 56); la tabla 1 (p. 37) dice 30-ene |
| Días restantes | 79 |
| Requisitos de control verificados | 0 de 0 (los RQ aún no están cargados) |
| Riesgos altos abiertos | 0 (1 medio: [RSK-001](Riesgos/rsk-001-rango-servo-camara.md), recorrido del servo) |
| Archivos en `raw/inbox/` por procesar | 2 (`Servos.pdf` y `Rumbo de cámara CanSat.html`) |
| Último lint | 2026-11-10 · 0 errores y 2 avisos (TST-001 y TST-002 no tienen RQ: los RQ aún no están cargados) |

Avance de control listo, en el brain y en Notion ([Sensores de rumbo](https://app.notion.com/p/404d9b500e34818c9d42dfebb09d3367)):

- la caracterización de los sensores ([nota](Conceptos/sensores-giroscopio-magnetometro.md), parte 4);
- el modelo en espacio de estados ([nota](Control/modelo-rumbo-espacio-estados.md));
- el ejemplo del seguidor de referencia ([L-07](Conceptos/l-07-servomotor-self-tuning.md)).

Código de prueba del servo en MATLAB: [servo-prueba-futaba.m](sim/servo-prueba-futaba.m).

Nuevo: [TST-002](Pruebas/tst-002-guia-datos-estacionarios-sensores.md), guía de laboratorio para que eléctrica tome datos estacionarios del BNO055 y el LIS3MDL reales y mida la interferencia del servo ([PDF](salida/tst-002-guia-laboratorio-sensores.pdf)).

Antes: [opciones de control del lazo de la cámara](Control/diseno-estabilizacion-camara.md). Se recomienda un RST con integrador que conserva el cero de muestreo, más prealimentación del giróscopo. Error de control ≤ 0,27° en simulación; el cuello de botella es el estimador de rumbo.

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

## Tres próximos pasos

1. Ejecutar TST-002 (datos estacionarios de los sensores reales) y procesar `Servos.pdf` con `subir`. Después, acordar los pesos y cerrar el DEC-001 del actuador y la ley de control (skill `decision`), y subir las hojas de datos.
2. Identificar el servo ($K_c$, $\tau_c$) en banco y medir el giro del PocketQube bajo el paracaídas con una caída desde dron (skill `prueba`).
3. «requisitos»: crear los RQ literales y los RC del lazo de rumbo (C8, C11, PQ15–PQ18, PQ28, PQ30); después, el acelerómetro, el filtro complementario y el RST que conserva el cero de muestreo, con acción integral.
