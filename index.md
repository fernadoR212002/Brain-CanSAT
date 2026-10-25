# Índice del CanSat Brain

Catálogo de todo lo que hay en el brain. La skill `subir` agrega las fuentes y cada skill que crea una nota la agrega aquí y en el README de su carpeta.

## Fuentes (`raw/`)

`procesado`: **no** (solo catalogada) · **parcial** (algunas secciones; se dice cuáles) · **sí** (texto extraído y notas escritas).

| ID | Archivo | Tipo | Fecha | Procesado | Derivado | Nota |
|---|---|---|---|---|---|---|
| — | [raw/mision/cansat-mission-guide-2027-r1.1.pdf](raw/mision/cansat-mission-guide-2027-r1.1.pdf) | guía oficial de misión, 56 p. | 2026-08-03 (Rev 1.1) | parcial: lo del lazo de rumbo, ver la ficha | [texto](derivados/cansat-mission-guide-2027-r1.1.txt) | [guia-mision-2027](Mision/guia-mision-2027.md) |
| TST-001 | [raw/pruebas/tst-001-1-giroscopio-giro.png](raw/pruebas/tst-001-1-giroscopio-giro.png) | captura de phyphox: giróscopo durante un giro | Pendiente (hora 1:28) | sí (lectura visual) | — | [TST-001](Pruebas/tst-001-exploracion-sensores-celular.md) |
| TST-001 | [raw/pruebas/tst-001-2-magnetometro-giro.png](raw/pruebas/tst-001-2-magnetometro-giro.png) | captura de phyphox: magnetómetro durante un giro | Pendiente (hora 1:31) | sí (lectura visual) | — | [TST-001](Pruebas/tst-001-exploracion-sensores-celular.md) |
| TST-001 | [raw/pruebas/tst-001-3-giroscopio-quieto.png](raw/pruebas/tst-001-3-giroscopio-quieto.png) | captura de phyphox: giróscopo quieto | Pendiente (hora 1:44) | sí (lectura visual) | — | [TST-001](Pruebas/tst-001-exploracion-sensores-celular.md) |
| TST-001 | [raw/pruebas/tst-001-4-magnetometro-absoluto.png](raw/pruebas/tst-001-4-magnetometro-absoluto.png) | captura de phyphox: magnitud total del campo | Pendiente (hora 1:46) | sí (lectura visual) | — | [TST-001](Pruebas/tst-001-exploracion-sensores-celular.md) |
| — | [raw/datos/notion-hardware-2026-10-25.md](raw/datos/notion-hardware-2026-10-25.md) | copia de la base «Hardware» de Notion (31 componentes) | 2026-10-25 | sí | — | [sensores-giroscopio-magnetometro](Conceptos/sensores-giroscopio-magnetometro.md) |

Enlaces externos ([raw/LINKS.md](raw/LINKS.md)): L-01 modelo WMM2025 (NOAA) · L-02 pygeomag · L-03 sitio de lanzamiento 2027 (no validada) · L-04 giróscopos MEMS (no validada) · L-05 LIS3MDL de ST (no validada) · L-06 phyphox.

## Wiki

| Carpeta | Notas |
|---|---|
| [Mision/](Mision/README.md) | [guia-mision-2027.md](Mision/guia-mision-2027.md): ficha de la guía oficial (procesada en parte) |
| [Control/](Control/README.md) | [alcance.md](Control/alcance.md): alcance del frente de control (con pendientes) |
| [Subsistemas/](Subsistemas/README.md) | _(sin notas)_ |
| [Decisiones/](Decisiones/README.md) | _(sin notas)_ |
| [Pruebas/](Pruebas/README.md) | [tst-001-exploracion-sensores-celular.md](Pruebas/tst-001-exploracion-sensores-celular.md): TST-001, giróscopo y magnetómetro con un celular |
| [Riesgos/](Riesgos/README.md) | _(sin notas)_ |
| [Conceptos/](Conceptos/README.md) | [sensores-giroscopio-magnetometro.md](Conceptos/sensores-giroscopio-magnetometro.md): qué miden, Bogotá–Medellín–Virginia, leyes físicas y requisitos |
| [Entregas/](Entregas/README.md) | _(sin notas)_ |
| [Plantillas/](Plantillas/README.md) | [requisito](Plantillas/requisito.md) · [decision](Plantillas/decision.md) · [prueba](Plantillas/prueba.md) · [riesgo](Plantillas/riesgo.md) · [interfaz](Plantillas/interfaz.md) · [acta](Plantillas/acta.md) · [entrega](Plantillas/entrega.md) |

## IDs asignados

Último número usado por tipo (el siguiente es este más uno; nunca se reutilizan).

| RQ | RC | DEC | TST | RSK | ICD | DS | L | ACT | REV |
|---|---|---|---|---|---|---|---|---|---|
| — | — | — | TST-001 | — | — | — | L-06 | — | — |

## Derivados (`derivados/`)

- [cansat-mission-guide-2027-r1.1.txt](derivados/cansat-mission-guide-2027-r1.1.txt): texto de la guía (`pdftotext -layout`).
- [campo-geomagnetico.csv](derivados/campo-geomagnetico.csv): campo WMM2025 en Bogotá, Medellín y Monterey (lo escribe `sim/campo-geomagnetico.py`).

## Simulación y herramientas

- [sim/requirements.txt](sim/requirements.txt): entorno de simulación. Scripts de `sim/`: [campo-geomagnetico.py](sim/campo-geomagnetico.py).
- [scripts/matriz-requisitos.py](scripts/matriz-requisitos.py) · [scripts/lint.py](scripts/lint.py) · [scripts/brain.py](scripts/brain.py).

## Salidas (`salida/`)

- [matriz-requisitos.csv](salida/matriz-requisitos.csv): matriz de trazabilidad (vacía, con encabezados).

## Memoria, guías y configuración

- [README.md](README.md) · [GUIA.md](GUIA.md) · [CLAUDE.md](CLAUDE.md) · [estado.md](estado.md) · [log.md](log.md)
- `.claude/settings.json` (permisos y hook) · `.claude/hooks/session-start.sh` · `.claude/skills/` (10 skills)
