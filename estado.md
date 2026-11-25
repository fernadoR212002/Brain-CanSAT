# Estado del CanSat Brain

_Actualizado el 19 de noviembre de 2026 (America/Bogota)._

## Resumen

| Indicador | Valor |
|---|---|
| Próxima revisión | PDR el 28 de enero de 2027 a las 18:59:59 de Bogotá, en 70 días. La tabla 1 de la guía señala el 30 de enero. [Calendario](Mision/guia-mision-2027.md) |
| Requisitos de control verificados | 0 de 0. Sigue pendiente cargar los RQ y RC en la [matriz](salida/matriz-requisitos.csv). |
| Riesgos abiertos | Uno alto por la [calibración del magnetómetro](Riesgos/rsk-002-calibracion-magnetometro.md) y uno medio por el [recorrido del servo](Riesgos/rsk-001-rango-servo-camara.md). |
| Entrada de fuentes | Dos archivos para procesar, `Servos.pdf` y `Rumbo de cámara CanSat.html`. Hay además dos carpetas de la ingesta anterior, una con restos de PlatformIO y otra vacía. |
| Última revisión automática | 19 de noviembre de 2026. Tres avisos corresponden a las pruebas que esperan sus RQ. |

La [animación para el equipo](salida/antares-control-15s.mp4) resume el trabajo sobre el control de la cámara y la adquisición de datos con el BNO055. La [prueba de banco TST-003](Pruebas/tst-003-bno055-sin-calibrar-esp32-matlab.md) aportó capturas del sensor. En el [modelo de Simulink](Control/diseno-estabilizacion-camara.md), el máximo error absoluto de rumbo fue de 3,01° en S1 y 2,60° en S2, excluidos el arranque y la maniobra de 90°.

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

1. Recuperar los CSV de TST-003, analizarlos y ejecutar [TST-002](Pruebas/tst-002-guia-datos-estacionarios-sensores.md) a 100 Hz con el montaje final para medir el error tras calibrar el magnetómetro (`subir`, `prueba`).
2. Registrar los RQ y RC del lazo de rumbo a partir de C8, C11, PQ15–PQ18, PQ28 y PQ30 para documentar su verificación en el PDR (`requisitos`).
3. Procesar la documentación de los servos, acordar los criterios de DEC-001, identificar el actuador en banco y medir el giro bajo el paracaídas con el equipo de recuperación (`subir`, `decision`, `prueba`).
