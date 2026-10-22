# Log del CanSat Brain

Diario del brain. **Solo crece:** cada entrada se agrega al final con el encabezado `## AAAA-MM-DD · tipo · título` (fecha America/Bogota). Tipos: creacion, subir, requisitos, control, prueba, decision, revision, estado, lint, reunion, ajuste.

## 2026-10-22 · creacion · Montaje inicial del brain

- Capas: `raw/` (`inbox/` y 8 subcarpetas, más `LINKS.md`), `derivados/`, wiki (9 carpetas), `sim/`, `scripts/` y `salida/`, cada una con su README (las subcarpetas de `raw/` no lo llevan; el catálogo es `index.md`).
- Memoria y guías: `CLAUDE.md`, `GUIA.md`, `README.md`, `index.md`, `estado.md` y este log.
- 7 plantillas (requisito, decisión, prueba, riesgo, interfaz, acta, entrega) y `Control/alcance.md`, sin datos de misión.
- 10 skills en `.claude/skills/`: inicio, subir, requisitos, control, prueba, decision, pregunta, revision, estado y lint.
- `.claude/settings.json`: niega `Edit` (cubre `Write`) en las 8 subcarpetas de `raw/`, deja libre `raw/inbox/`, niega las herramientas de escritura de Drive y Notion y registra el hook `SessionStart`. Comprobado en esta sesión: escribir en `raw/mision/` falla (con la herramienta Write y con una redirección de Bash) y en `raw/inbox/` funciona; la regla aplicó sin reiniciar.
- Ingesta: el `git mv` de prueba de `raw/inbox/` a `raw/mision/` lo bloqueó el clasificador del modo automático (no la regla). Queda pendiente que el líder decida si se agrega una regla `allow` solo para `git mv raw/inbox/…`; mientras tanto, `subir` pide aprobación para cada movimiento.
- Hook `SessionStart`: instala `sim/requirements.txt` (numpy 2.5.3, scipy 1.18.1, pandas 3.0.5, matplotlib 3.11.2, control 0.10.2). Instalación limpia en un entorno nuevo: 53 s, sin errores.
- `scripts/matriz-requisitos.py` genera `salida/matriz-requisitos.csv` (solo encabezados) y `scripts/lint.py` pasa sin errores.
- Pendiente: competencia y edición, integrantes y frentes, alcance de control, fechas, propiedad del repo.
- Rama `claude/fervent-gauss-1zksw8` → PR hacia `main` (el repo estaba vacío: `main` se creó con el README como primer commit).
