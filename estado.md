# Estado del CanSat Brain

_Actualizado el 25 de noviembre de 2026 (America/Bogota)._

## Resumen

| Indicador | Valor |
|---|---|
| Próxima revisión | PDR el 28 de enero de 2027 a las 18:59:59 de Bogotá, en 64 días. La tabla 1 de la guía señala el 30 de enero. [Calendario](Mision/guia-mision-2027.md) |
| Requisitos de control verificados | 0 de 0. Sigue pendiente cargar los RQ y RC en la [matriz](salida/matriz-requisitos.csv). |
| Riesgos abiertos | Uno alto por la [calibración del magnetómetro](Riesgos/rsk-002-calibracion-magnetometro.md) y uno medio por el [recorrido del servo](Riesgos/rsk-001-rango-servo-camara.md). |
| Entrada de fuentes | Dos archivos para procesar, `Servos.pdf` y `Rumbo de cámara CanSat.html`. Hay además dos carpetas de la ingesta anterior, una con restos de PlatformIO y otra vacía. |
| Última revisión automática | 25 de noviembre de 2026, al cerrar TST-004. |

[TST-004](Pruebas/tst-004-salida-pwm-actuador.md) simuló la salida PWM del ESP32 al actuador, en Simulink y en una réplica de Codex en Python. Con motor DC y puente H, el RST L3 cumple C8 con 8 a 11 bits de PWM, pero solo si se compensa la zona muerta del motor. El servo de hobby de 180° con L0 no cumple con ninguna resolución, por falta de recorrido. El flujo de validación está en [este diagrama](.archify/workflow-validacion-pwm-actuador-20261125-142605/validacion-pwm-actuador.html).

## Pendientes

> [!WARNING]
> **Pendiente**
> 1. Integrantes del equipo y frente de cada uno.
> 2. Alcance completo de «control». El primer frente es la estabilización de video (C8, C11, PQ15–PQ18).
> 3. Si el repositorio es solo del líder de control o de todo el equipo.
> 4. Confirmar con la organización tres cosas: qué fechas valen (la guía se contradice), el sitio de lanzamiento y si el norte es el verdadero o el magnético.
> 5. Las 4 capturas de [TST-001](Pruebas/tst-001-exploracion-sensores-celular.md) y las 2 figuras de L-07 faltan en Notion: la red del entorno bloquea `api.notion.com`, así que hay que arrastrarlas a mano.
> 6. Las hojas de datos oficiales del BNO055 y del LIS3MDL (L-08 y L-09): la red del entorno bloquea esos dominios. Hay que subirlas por `raw/inbox/` para confirmar los valores no validados de la caracterización.
> 7. La decisión del actuador y de la ley de control (DEC-001): faltan los pesos del equipo. TST-004 agrega dos criterios, la zona muerta medida del motor y la reducción. El servo de 180° tiene el riesgo [RSK-001](Riesgos/rsk-001-rango-servo-camara.md).
> 8. Los CSV de TST-003, el sitio de la prueba y la tarjeta de vuelo: el ESP32 clásico funcionó, y la base Hardware dice ESP32-S3.
> 9. Según el aviso de MATLAB del 25 de noviembre, la licencia vence en 5 días. Hay que renovarla antes de correr TST-004 en banco.

## Tres próximos pasos

1. Registrar los RQ y RC del lazo de rumbo a partir de C8, C11, PQ15–PQ18, PQ28 y PQ30 para documentar su verificación en el PDR (`requisitos`).
2. Elegir el actuador con DEC-001. Después, ejecutar la parte de banco de [TST-004](Pruebas/tst-004-salida-pwm-actuador.md): medir el PWM, la zona muerta, $K_c$ y $\tau_c$, y re-simular con lo medido (`subir` para `Servos.pdf`, `decision`, `prueba TST-004`).
3. Recuperar los CSV de TST-003 y ejecutar [TST-002](Pruebas/tst-002-guia-datos-estacionarios-sensores.md) a 100 Hz con el montaje final, para medir el error tras calibrar el magnetómetro (`subir`, `prueba`).
