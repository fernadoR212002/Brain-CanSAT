# Estado del CanSat Brain

_Actualizado: 2026-11-05 (America/Bogota). Lo reescribe la skill `estado`; una página como máximo._

**Próximo paso:** subir las hojas de datos del BNO055 y del LIS3MDL, decidir el actuador de la cámara e identificar el servo.

## Resumen

| Indicador | Valor |
|---|---|
| Próxima revisión | PDR: 28-ene-2027 a las 23:59:59 UTC (18:59 en Bogotá), según el calendario (p. 56); la tabla 1 (p. 37) dice 30-ene |
| Días restantes | 95 |
| Requisitos de control verificados | 0 de 0 (los RQ aún no están cargados) |
| Riesgos altos abiertos | 0 registrados |
| Archivos en `raw/inbox/` por procesar | 0 |
| Último lint | 2026-10-25 · 0 errores y 1 aviso (TST-001 es exploratoria y no tiene requisito) |

Avance de control listo, en el brain y en Notion ([Sensores de rumbo](https://app.notion.com/p/404d9b500e34818c9d42dfebb09d3367)):

- la caracterización de los sensores ([nota](Conceptos/sensores-giroscopio-magnetometro.md), parte 4);
- el modelo en espacio de estados ([nota](Control/modelo-rumbo-espacio-estados.md));
- el ejemplo del seguidor de referencia ([L-07](Conceptos/l-07-servomotor-self-tuning.md)).

Código de prueba del servo en MATLAB: [servo-prueba-futaba.m](sim/servo-prueba-futaba.m).

## Pendientes

> [!WARNING]
> **Pendiente**
> 1. Integrantes del equipo y frente de cada uno.
> 2. Alcance completo de «control». El primer frente es la estabilización de video (C8, C11, PQ15–PQ18).
> 3. Si el repositorio es solo del líder de control o de todo el equipo.
> 4. Confirmar con la organización tres cosas: qué fechas valen (la guía se contradice), el sitio de lanzamiento y si el norte es el verdadero o el magnético.
> 5. Las 4 capturas de [TST-001](Pruebas/tst-001-exploracion-sensores-celular.md) y las 2 figuras de L-07 faltan en Notion: la red del entorno bloquea `api.notion.com`, así que hay que arrastrarlas a mano.
> 6. Las hojas de datos oficiales del BNO055 y del LIS3MDL (L-08 y L-09): la red del entorno bloquea esos dominios. Hay que subirlas por `raw/inbox/` para confirmar los valores no validados de la caracterización.
> 7. La decisión del actuador: servo de hobby o motor DC con codificador, si además se gira el cuerpo y dónde va el IMU.

## Tres próximos pasos

1. Subir las hojas de datos y tomar la decisión del actuador (skill `decision`).
2. Identificar el servo ($K_c$, $\tau_c$) en banco y medir el giro del PocketQube bajo el paracaídas con una caída desde dron (skill `prueba`).
3. «requisitos»: crear los RQ literales y los RC del lazo de rumbo (C8, C11, PQ15–PQ18, PQ28, PQ30); después, el acelerómetro, el filtro complementario y el RST que conserva el cero de muestreo, con acción integral.
