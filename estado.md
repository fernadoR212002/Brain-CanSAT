# Estado del CanSat Brain

_Actualizado: 2026-10-25 (America/Bogota). Lo reescribe la skill `estado`; una página como máximo._

**Próximo paso:** seguir descubriendo el lazo con el acelerómetro (la inclinación) y la fusión de sensores.

## Resumen

| Indicador | Valor |
|---|---|
| Próxima revisión | PDR: 28-ene-2027 a las 23:59:59 UTC (18:59 en Bogotá), según el calendario (p. 56); la tabla 1 (p. 37) dice 30-ene |
| Días restantes | 95 |
| Requisitos de control verificados | 0 de 0 (los RQ aún no están cargados) |
| Riesgos altos abiertos | 0 registrados |
| Archivos en `raw/inbox/` por procesar | 0 |
| Último lint | 2026-10-25 · 0 errores y 1 aviso (TST-001 es exploratoria y no tiene requisito) |

Ya resuelto con la guía ([ficha](Mision/guia-mision-2027.md)): la competencia es la CanSat Competition 2027 en formato PocketQube, y las fechas son las del calendario oficial.

## Pendientes

> [!WARNING]
> **Pendiente**
> 1. Integrantes del equipo y frente de cada uno.
> 2. Alcance completo de «control». El primer frente es la estabilización de video (C8, C11, PQ15–PQ18).
> 3. Si el repositorio es solo del líder de control o de todo el equipo.
> 4. Confirmar con la organización tres cosas: qué fechas valen (la guía se contradice), el sitio de lanzamiento y si el norte es el verdadero o el magnético.
> 5. Las 4 capturas de [TST-001](Pruebas/tst-001-exploracion-sensores-celular.md) faltan en la subpágina de Notion: la red del entorno bloquea `api.notion.com`, así que hay que arrastrarlas a mano.

## Tres próximos pasos

1. Seguir con el acelerómetro y la fusión de sensores ([nota de sensores](Conceptos/sensores-giroscopio-magnetometro.md)); en Notion, la página es [Sensores de rumbo](https://app.notion.com/p/404d9b500e34818c9d42dfebb09d3367).
2. Diseñar el experimento y, con él, exportar los CSV de phyphox para analizarlos con un script.
3. «requisitos»: crear los RQ literales y los RC del lazo de rumbo (C8, C11, PQ15–PQ18, PQ28, PQ30), después de decidir cómo se numeran los RQ.
