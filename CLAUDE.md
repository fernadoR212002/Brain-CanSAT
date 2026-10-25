# CanSat Brain · reglas para Claude

Second brain del equipo para la competencia académica CanSat, con el patrón LLM Wiki: fuentes inmutables (`raw/`), una wiki que escribe Claude y este archivo de reglas. Líder del frente de control y dueño del brain: Angel Fernando Revelo Narvaez. Cubre la misión completa a nivel de resumen y el control a fondo. Cómo lo usan las personas: [GUIA.md](GUIA.md).

> [!WARNING]
> **Pendiente** — integrantes y frentes, alcance completo de control, si el repo es solo del líder de control o de todo el equipo, y qué fechas valen (la guía se contradice). Ver [estado.md](estado.md).

## Capas

| Capa | Carpeta | Quién escribe |
|---|---|---|
| Fuentes inmutables | `raw/` | nadie edita; todo entra por `raw/inbox/` |
| Derivados | `derivados/` | solo scripts (pdftotext, OCR, limpieza); nunca a mano |
| Wiki | `Mision/` `Control/` `Subsistemas/` `Decisiones/` `Pruebas/` `Riesgos/` `Conceptos/` `Entregas/` `Plantillas/` | Claude |
| Simulación | `sim/` + `sim/requirements.txt` | scripts reproducibles: modelos, simulaciones, telemetría |
| Herramientas | `scripts/` | matriz de requisitos y lint del brain |
| Exportaciones | `salida/` | solo productos listos: matriz CSV, PDF o PPTX de revisión, figuras |
| Memoria | `index.md` · `log.md` · `estado.md` | Claude |

- Subcarpetas de `raw/`: `mision/` (guía, reglas, calendario y aclaraciones oficiales, texto literal) · `revisiones/` (plantillas y comentarios de jueces) · `datasheets/` · `pruebas/` (datos crudos) · `vuelos/` (telemetría cruda) · `reuniones/` (actas, fotos de tablero) · `lecturas/` · `datos/`. Archivos grandes en Drive: solo el enlace, en `raw/LINKS.md`.
- Las subcarpetas de `raw/` no llevan README: el catálogo de fuentes es `index.md` (columna `procesado`: no · parcial · sí).
- Todas las demás carpetas llevan `README.md` con una línea por nota. Al crear una nota se agrega su línea.

## IDs (estables; nunca se reutilizan; el 000 es de las plantillas)

| ID | Qué es | Nota en |
|---|---|---|
| RQ-NNN | requisito de la competencia, texto literal. Si la guía los numera con enteros, se conserva su número; si la numeración es jerárquica, va en `ref_oficial` | `Mision/` |
| RC-NNN | requisito derivado de control, con su RQ de origen en `requisitos` | `Control/` |
| DEC-NNN | decisión o trade study | `Decisiones/` |
| TST-NNN | prueba (un vuelo también es una prueba) | `Pruebas/` |
| RSK-NNN | riesgo | `Riesgos/` |
| ICD-NNN | interfaz entre subsistemas | `Subsistemas/` |
| DS-NN | hoja de datos (`raw/datasheets/`) | `Subsistemas/` |
| L-NN | lectura (`raw/lecturas/`) | `Conceptos/` |
| ACT-AAAA-MM-DD | acta (`raw/reuniones/`) | `Decisiones/` |
| REV-PDR, REV-CDR, REV-PFR… | entrega de revisión | `Entregas/` |

- Siguiente número libre: el mayor de `index.md` y `log.md` más uno. Un ID borrado o reemplazado no se vuelve a usar.
- Enunciados dentro de cada nota: **P** principio físico · **C** criterio o requisito citado · **D** definición · **S** supuesto · **M** medición. Se numeran por nota (`**M2.**`) y se citan como `TST-004·M2`.

## Trazabilidad (regla central)

Cadena: RQ → RC → DEC → TST → evidencia en `raw/` → REV.

- Cada RQ y RC lleva en el frontmatter `metodo` (I inspección, A análisis, D demostración, T prueba), `responsable` y `verificacion` (pendiente · en curso · verificado · fallido).
- Un RC cita su RQ de origen en `requisitos`. DEC, TST, RSK, ICD y REV listan en `requisitos` los RQ y RC que tocan; cada TST lista sus datos crudos en `evidencia`.
- La matriz se calcula desde el frontmatter: `python3 scripts/matriz-requisitos.py` → `salida/matriz-requisitos.csv`. Nunca se edita a mano.
- Un requisito pasa a `verificado` solo con evidencia en `raw/` y, si hay números, con un script en `sim/`.

## Formato

- Markdown de GitHub. Enlaces relativos: `[alcance](Control/alcance.md)`. Prohibidos los enlaces de doble corchete (wikilinks).
- Avisos: `[!NOTE]` `[!TIP]` `[!IMPORTANT]` `[!WARNING]` `[!CAUTION]`. El marcador va solo en su línea (si no, GitHub no lo muestra como aviso):
  `> [!WARNING]` y en la línea siguiente `> **Pendiente** — …` o `> **Sin fuente en raw/** — …`.
- Ecuaciones con `$$ … $$` (en línea, `$ … $`). Diagramas mermaid para máquinas de estado y lazos de control.
- Frontmatter YAML en toda nota de la wiki: `type, status, id, tags, created, source, requisitos` y los campos propios de su plantilla.
- Archivos en minúsculas, con guiones y el ID delante: `tst-004-caida-desde-dron.md`, `act-2026-10-22-arranque.md`.
- Unidades SI siempre junto al número. En las notas, coma decimal (9,81 m/s²; en LaTeX, `9{,}81`). En CSV y código, punto decimal (9.81).
- Tiempos de los datos en UTC (ISO 8601: `2026-10-22T14:03:05Z`). Fechas del calendario en America/Bogota.
- Español, con el término técnico en inglés entre paréntesis la primera vez: tiempo de establecimiento (settling time).

## Reglas

1. No inventar datos, requisitos ni resultados. Lo que no esté en `raw/` va marcado con `> [!WARNING]` + `> **Sin fuente en raw/** — …`; lo que nadie sabe todavía, con `> **Pendiente** — …`.
2. El texto oficial de la competencia no se altera; lo propio va aparte y marcado como interpretación.
3. Cada fuente se lee una vez: `pdftotext -layout` a `derivados/` (OCR si no hay capa de texto) y después se trabaja sobre el derivado. Si un PDF pasa de 30 páginas (`pdfinfo`), preguntar qué secciones procesar.
4. Todo resultado numérico de una prueba sale de un script en `sim/` que se puede volver a correr sobre `raw/`. Nada de números a mano.
5. Con «debatamos» o «paso a paso»: solo conversar, sin escribir en el repo.
6. Si un cambio toca más de 5 archivos, mostrar antes el plan en 5 líneas.
7. Repo privado. No subir datos de terceros (datos personales, material de otros equipos, contenido con licencia) sin preguntar.
8. Trabajo en rama y Pull Request hacia `main`. Al cerrar: `estado.md`, entrada en `log.md`, lint, push y enlace al PR.
9. Conectores. Google Drive: solo lectura. Notion: lectura, y escritura solo para crear o editar páginas dentro de CANSAT cuando el líder lo pida; nunca borrar ni mover. Lo escrito en Notion es una copia: la fuente de verdad es el brain. Lo que se use de un conector se congela antes de citarlo: copia por `raw/inbox/` o enlace en `raw/LINKS.md`.
10. Fecha real siempre con `TZ=America/Bogota date`; nunca suponerla.

## Permisos y nube

- `.claude/settings.json` niega `Edit` (que cubre también `Write`) en `raw/mision`, `revisiones`, `datasheets`, `pruebas`, `vuelos`, `reuniones`, `lecturas` y `datos`. `raw/inbox/` y `raw/LINKS.md` quedan libres.
- Ingesta: `git mv raw/inbox/<archivo> raw/<subcarpeta>/<id>-<nombre>`, sin opciones y como comando aparte (el `git add` va en otro). La regla `allow` `Bash(git mv raw/inbox/* raw/*)` lo aprueba sin preguntar. Cualquier otro cambio dentro de `raw/` se pide al usuario y nunca se rodea con otro comando o script.
- Drive tiene negadas sus herramientas de escritura. En Notion solo se permite crear y editar páginas y subir archivos; siguen negados borrar, mover y duplicar, y tocar bases de datos, vistas o comentarios. La red del entorno bloquea `api.notion.com`, así que las imágenes no se pueden subir a Notion desde la nube.
- Hook `SessionStart` (`.claude/hooks/session-start.sh`): en la nube instala `sim/requirements.txt` (numpy, scipy, pandas, matplotlib, control).

## Skills (`.claude/skills/`)

| Skill | Para qué |
|---|---|
| `inicio` | abrir la sesión: pull, reglas, estado, log, fecha, inbox, próxima revisión |
| `subir` | procesar `raw/inbox/`; si llega la guía de misión, encadena `requisitos` |
| `requisitos` | RQ literales, marca de control, RC derivados y matriz |
| `control` | requisito → planta → controlador → simulación → métricas → nota y DEC |
| `prueba TST-NNN` | plan de prueba y, con datos, análisis reproducible y veredicto |
| `decision` | trade study → DEC-NNN |
| `pregunta` | responder solo desde el brain, citando RQ, DS (página), TST y DEC |
| `revision PDR\|CDR\|PFR` | entregable con la plantilla oficial, cobertura y exportación |
| `estado` | reescribir `estado.md` y el resumen del README |
| `lint` | revisión de salud cada dos semanas |

## Memoria

- `index.md`: catálogo de todo (fuentes con `procesado`, notas, derivados, salidas).
- `log.md`: diario que solo crece. Cada entrada se agrega al final con el encabezado `## AAAA-MM-DD · tipo · título`.
- `estado.md`: una página como máximo; la reescribe la skill `estado`.
