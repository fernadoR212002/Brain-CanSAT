# CanSat Brain

Second brain del equipo para la competencia académica CanSat: fuentes inmutables en `raw/`, una wiki que escribe Claude y reglas en [CLAUDE.md](CLAUDE.md). Cubre la misión completa a nivel de resumen y el frente de control a fondo (líder: Angel Fernando Revelo Narvaez).

**¿Primera vez?** Lee la [GUIA.md](GUIA.md): cómo subir información (navegador, celular, chat) y cómo sacarla.

<!-- estado:inicio · lo reescribe la skill estado -->
## Estado

_Actualizado el 25 de noviembre de 2026 (America/Bogota)._

| Indicador | Valor |
|---|---|
| Competencia | CanSat Competition 2027, formato PocketQube |
| Próxima revisión | PDR el 28 de enero de 2027 a las 18:59:59 de Bogotá. Faltan 64 días. La tabla 1 de la [guía](Mision/guia-mision-2027.md) señala el 30 de enero. |
| Requisitos de control verificados | 0 de 0 registrados en la [matriz](salida/matriz-requisitos.csv). |
| Riesgos altos abiertos | 1 por la [calibración del magnetómetro](Riesgos/rsk-002-calibracion-magnetometro.md). |
| Último avance | [TST-004](Pruebas/tst-004-salida-pwm-actuador.md): salida PWM del ESP32 al actuador, simulada en Simulink y en Python. |

Los siguientes pasos son registrar los requisitos de rumbo, elegir el actuador y medirlo en banco con TST-004, y calibrar el magnetómetro. [Estado y pendientes](estado.md)

<!-- estado:fin -->

## Hitos

| Hito | Fecha (America/Bogota) | Estado |
|---|---|---|
| Montaje del brain | 2026-10-22 | hecho |
| Guía de misión en `raw/` | 2026-10-25 | hecho (procesada en parte) |
| Entrega del PDR | 2027-01-28, 23:59:59 UTC (la tabla 1 dice 30-ene) | pendiente |
| Entrega del CDR | 2027-04-01, 23:59:59 UTC (la tabla 1 dice 27-mar) | pendiente |
| Documento de pruebas ambientales | 2027-05-21 (la tabla 1 dice 22-may) | pendiente |
| Revisión de vuelo (FRR) y lanzamiento | 2027-06-11 y 2027-06-12 | pendiente |
| PFR | 2027-06-13 (la tabla 1 dice 7-jun) | pendiente |

## Navegación

| Dónde | Qué hay |
|---|---|
| [GUIA.md](GUIA.md) | cómo subir y sacar información |
| [CLAUDE.md](CLAUDE.md) | reglas del brain (capas, IDs, trazabilidad, formato) |
| [estado.md](estado.md) · [index.md](index.md) · [log.md](log.md) | estado actual · catálogo de todo · diario |
| [raw/](raw/README.md) | fuentes inmutables; entrada única: `raw/inbox/` |
| [derivados/](derivados/README.md) | texto extraído, CSV limpios y figuras intermedias (solo scripts) |
| [Mision/](Mision/README.md) | la misión a nivel de resumen y los requisitos RQ |
| [Control/](Control/README.md) | el frente de control a fondo: [alcance](Control/alcance.md), RC, diseños |
| [Subsistemas/](Subsistemas/README.md) | subsistemas, hojas de datos (DS) e interfaces (ICD) |
| [Decisiones/](Decisiones/README.md) | decisiones (DEC) y actas (ACT) |
| [Pruebas/](Pruebas/README.md) | pruebas y vuelos (TST) |
| [Riesgos/](Riesgos/README.md) | riesgos (RSK) |
| [Conceptos/](Conceptos/README.md) | teoría y lecturas (L) |
| [Entregas/](Entregas/README.md) | revisiones (REV) |
| [Plantillas/](Plantillas/README.md) | plantillas de nota |
| [sim/](sim/README.md) | simulación y análisis de telemetría (Python) |
| [scripts/](scripts/README.md) | matriz de requisitos y lint |
| [salida/](salida/README.md) | exportaciones listas, como la [matriz de requisitos](salida/matriz-requisitos.csv) |
