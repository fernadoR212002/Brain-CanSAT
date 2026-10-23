# Índice del CanSat Brain

Catálogo de todo lo que hay en el brain. La skill `subir` agrega las fuentes y cada skill que crea una nota la agrega aquí y en el README de su carpeta.

## Fuentes (`raw/`)

`procesado`: **no** (solo catalogada) · **parcial** (algunas secciones; se dice cuáles) · **sí** (texto extraído y notas escritas).

| ID | Archivo | Tipo | Fecha | Procesado | Derivado | Nota |
|---|---|---|---|---|---|---|
| — | _(sin fuentes todavía)_ | | | | | |

Enlaces a archivos grandes en Drive: [raw/LINKS.md](raw/LINKS.md) _(sin enlaces todavía)_.

## Wiki

| Carpeta | Notas |
|---|---|
| [Mision/](Mision/README.md) | _(sin notas)_ |
| [Control/](Control/README.md) | [alcance.md](Control/alcance.md): alcance del frente de control (con pendientes) |
| [Subsistemas/](Subsistemas/README.md) | _(sin notas)_ |
| [Decisiones/](Decisiones/README.md) | _(sin notas)_ |
| [Pruebas/](Pruebas/README.md) | _(sin notas)_ |
| [Riesgos/](Riesgos/README.md) | _(sin notas)_ |
| [Conceptos/](Conceptos/README.md) | _(sin notas)_ |
| [Entregas/](Entregas/README.md) | _(sin notas)_ |
| [Plantillas/](Plantillas/README.md) | [requisito](Plantillas/requisito.md) · [decision](Plantillas/decision.md) · [prueba](Plantillas/prueba.md) · [riesgo](Plantillas/riesgo.md) · [interfaz](Plantillas/interfaz.md) · [acta](Plantillas/acta.md) · [entrega](Plantillas/entrega.md) |

## IDs asignados

Último número usado por tipo (el siguiente es este más uno; nunca se reutilizan).

| RQ | RC | DEC | TST | RSK | ICD | DS | L | ACT | REV |
|---|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — | — | — |

## Derivados (`derivados/`)

_(ninguno todavía)_

## Simulación y herramientas

- [sim/requirements.txt](sim/requirements.txt): entorno de simulación. Scripts de `sim/`: _(ninguno todavía)_.
- [scripts/matriz-requisitos.py](scripts/matriz-requisitos.py) · [scripts/lint.py](scripts/lint.py) · [scripts/brain.py](scripts/brain.py).

## Salidas (`salida/`)

- [matriz-requisitos.csv](salida/matriz-requisitos.csv): matriz de trazabilidad (vacía, con encabezados).

## Memoria, guías y configuración

- [README.md](README.md) · [GUIA.md](GUIA.md) · [CLAUDE.md](CLAUDE.md) · [estado.md](estado.md) · [log.md](log.md)
- `.claude/settings.json` (permisos y hook) · `.claude/hooks/session-start.sh` · `.claude/skills/` (10 skills)
