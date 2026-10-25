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
- Rama `claude/fervent-gauss-1zksw8` → [PR #1](https://github.com/fernadoR212002/Brain-CanSAT/pull/1) hacia `main` (el repo estaba vacío: `main` se creó con el README como primer commit).

## 2026-10-22 · ajuste · Regla allow para git mv desde raw/inbox/

- El líder de control aprobó agregar a `.claude/settings.json` la regla `allow` `Bash(git mv raw/inbox/* raw/*)`. Resuelve el bloqueo de la ingesta que quedó pendiente en la entrada anterior.
- Comprobado: `git mv raw/inbox/prueba-permiso.md raw/mision/prueba-permiso.md` pasa sin preguntar y editar el archivo ya movido sigue negado. El archivo de prueba se borró sin llegar a ningún commit.
- La regla solo cubre `git mv` con origen en `raw/inbox/` y destino en `raw/`. Un `git mv` con opciones delante (`-f`) o con otro origen no coincide y se pide al usuario.
- Actualizados `CLAUDE.md` (permisos y nube) y la skill `subir` (paso 3: `git add` y `git mv` en comandos separados).

## 2026-10-25 · subir · Guía de misión 2027, capturas de phyphox y copia de la base Hardware de Notion

- La guía oficial pasó de `raw/inbox/` a `raw/mision/cansat-mission-guide-2027-r1.1.pdf`, con su texto en `derivados/`. Quedó procesada en parte (lo del lazo de rumbo); ficha en `Mision/guia-mision-2027.md`.
- Las 4 capturas de phyphox del líder de control pasaron a `raw/pruebas/tst-001-*.png`.
- La base «Hardware» de Notion se leyó en modo solo lectura y se guardó como copia literal en `raw/datos/notion-hardware-2026-10-25.md` (regla 9). Los componentes elegidos que importan aquí son el BNO055, el LIS3MDL y la cámara Cyclops 3 V3.
- Enlaces web L-01 a L-06 agregados a `raw/LINKS.md`. L-03, L-04 y L-05 quedan como no validados.
- Hallazgos: la guía se contradice en las fechas (tabla 1 frente al calendario), y el LIS3MDL podría estar descontinuado (L-05, sin validar).

## 2026-10-25 · prueba · TST-001: exploración del giróscopo y el magnetómetro con un celular

- Prueba exploratoria, sin requisito, con valores leídos a ojo de las capturas: el giróscopo solo cambia mientras hay giro, y el magnetómetro queda en el valor nuevo y muestra distorsión de hierro duro y efecto del entorno.
- Pendiente: exportar los CSV de phyphox para analizarlos con un script (regla 4) y anotar la fecha y el lugar.

## 2026-10-25 · control · Nota de concepto: giróscopo y magnetómetro

- `Conceptos/sensores-giroscopio-magnetometro.md` tiene tres partes: cómo funcionan, Bogotá–Medellín–Virginia y las leyes físicas con los requisitos de la guía.
- `sim/campo-geomagnetico.py` (WMM2025 con `pygeomag`, agregado a `sim/requirements.txt`) da la inclinación: 26,5° en Bogotá, 29,3° en Medellín y 64,7° en Monterey. Allí, cada grado de inclinación mal estimada pesa unas 4 veces más que en Colombia.

## 2026-10-25 · ajuste · Escritura en Notion: bloqueada

- El líder aprobó permitir crear y editar páginas dentro de CANSAT en Notion, sin borrar ni mover nada.
- El clasificador del modo automático bloqueó que Claude editara `.claude/settings.json` (automodificación de permisos). El cambio queda en manos del líder; la regla 9 se ajusta cuando se aplique.
