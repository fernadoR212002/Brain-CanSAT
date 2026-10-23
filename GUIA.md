# Guía de uso del CanSat Brain

Cómo meter información al brain y cómo sacarla, desde el computador, el celular o el chat con Claude. Las reglas completas están en [CLAUDE.md](CLAUDE.md).

## La idea en tres líneas

1. Todo lo que llega de fuera (guía, datasheets, datos de pruebas, fotos del tablero) entra por **`raw/inbox/`** y luego no se edita nunca.
2. Claude lo clasifica, le pone un ID y escribe las notas de la wiki cuando le dices **«subir»**.
3. Tú preguntas, decides y revisas los Pull Requests; Claude mantiene la wiki, la matriz de requisitos y el estado.

## Subir información

### Desde el navegador (computador)

1. Abre el repo en GitHub y entra a la carpeta `raw/inbox/`.
2. **Add file → Upload files**, arrastra los archivos y, abajo, **Commit changes** directo a `main` (solo agrega archivos al inbox; no toca nada más).
3. Abre una sesión de Claude Code sobre el repo y di **«inicio»** y luego **«subir»**.

Consejos:

- Un nombre que diga qué es ayuda: `2026-10-22-guia-mision.pdf`, `prueba-caida-telemetria.csv`. Claude lo renombra con el ID al moverlo.
- Si es una aclaración oficial que llegó por correo, guarda el correo completo (con fecha y remitente) como PDF o pega el texto en el chat (ver abajo).

### Desde el celular

- **Archivos y fotos (tablero, montaje, pantalla del osciloscopio):** en el navegador del celular abre el repo en GitHub, entra a `raw/inbox/` y usa **Add file → Upload files**. Si el botón no aparece, activa **Ver versión para computador** en el menú del navegador. La app de GitHub sirve para leer, comentar y fusionar PR; para subir archivos usa el navegador.
- **Texto (notas rápidas, una aclaración de los jueces, una idea):** ábrelo en el chat de Claude (abajo).
- **Fusionar el PR que dejó Claude:** app de GitHub → Pull requests → el PR → **Merge**.

### Desde el chat con Claude (app o claude.ai/code)

- **Texto:** pégalo y di «guárdalo en el inbox y súbelo». Claude lo guarda **literal** en `raw/inbox/AAAA-MM-DD-tema.md`, con una línea de procedencia (quién, cuándo, de dónde), y lo procesa.
- **Imagen o archivo adjunto:** Claude lo ve. Si la sesión lo recibe como archivo, lo guarda en `raw/inbox/`; si solo lo ve como imagen, súbelo también por el navegador para que quede como fuente. Sin archivo en `raw/` no hay fuente.
- **Algo en Google Drive o Notion:** pásale el enlace. Claude lo lee en modo solo lectura y lo congela: copia por `raw/inbox/` o enlace en `raw/LINKS.md`.

### Archivos de más de 25 MB

GitHub no acepta por el navegador archivos de más de 25 MB, y git rechaza los de más de 100 MB. Para videos de vuelos, telemetría larga o PDF muy pesados:

1. Súbelos a la carpeta del equipo en **Google Drive**.
2. Pide a Claude «agrega este enlace a LINKS.md: <enlace> — <qué es>», o edita `raw/LINKS.md` en GitHub (lápiz ✏️): una fila con descripción, fecha, tamaño y enlace.
3. Si hace falta trabajar con el contenido, sube al inbox una versión reducida de menos de 25 MB: el recorte de la telemetría del vuelo, el CSV en lugar del XLSX, el PDF solo con las secciones útiles o las fotos comprimidas.

## Sacar información

| Quiero… | Haz esto |
|---|---|
| saber cómo vamos | lee [estado.md](estado.md) o el inicio del [README](README.md); para actualizarlo, di «estado» |
| encontrar algo | [index.md](index.md) cataloga fuentes, notas y salidas |
| una respuesta con fuentes | di «pregunta: …». Claude responde solo desde el brain y cita RQ, DS (con página), TST y DEC |
| la matriz de requisitos | `salida/matriz-requisitos.csv` → en GitHub, **Download raw file**. En Google Sheets: Archivo → Importar. En Excel: Datos → Desde texto/CSV (UTF-8) |
| el documento de una revisión | di «revision PDR» (o CDR, PFR); queda en `salida/` |
| ver qué cambió | [log.md](log.md) (diario) y los Pull Requests en GitHub |

En el celular, la app de GitHub muestra bien las notas; los diagramas mermaid se ven mejor en el navegador.

## Palabras clave

| Di | Qué hace Claude |
|---|---|
| «inicio» | trae lo nuevo de `main`, lee reglas, estado y log, revisa el inbox y te dice cuántos días faltan para la próxima revisión |
| «subir» | procesa `raw/inbox/`: clasifica, asigna ID, extrae texto, escribe la nota y actualiza índice, README y log |
| «requisitos» | extrae o actualiza los RQ, marca los de control, deriva los RC y regenera la matriz |
| «control» | requisito → modelo de planta → controlador → simulación → métricas → nota (y DEC si se elige) |
| «prueba TST-004» | plan de la prueba; con datos, análisis con script, figuras y veredicto |
| «decision» | trade study con opciones, criterios y pesos → DEC |
| «pregunta: …» | respuesta citando las notas |
| «revision PDR» | arma el entregable con la plantilla oficial y lo exporta |
| «estado» | reescribe `estado.md` y el resumen del README |
| «lint» | revisión de salud del brain (cada dos semanas) |
| «debatamos» o «paso a paso» | solo conversa; no escribe nada en el repo |

También puedes escribirlas como comando: `/inicio`, `/subir`, `/prueba TST-004`, `/revision PDR`.

## Ciclo de una sesión

1. «inicio».
2. Trabajo: «subir», «requisitos», «control», «prueba…».
3. Al cerrar, Claude actualiza `estado.md` y `log.md`, corre el lint, hace push a su rama y te da el enlace del PR.
4. Revisas el PR y lo fusionas en `main`. Las sesiones siguientes parten de `main`.

## Sesiones en la nube

- Cada sesión parte de un clon nuevo de `main`. Lo que no esté fusionado en `main` no lo ve la sesión siguiente: fusiona los PR.
- Al arrancar, el hook instala el entorno de simulación. La primera vez tarda cerca de 1 min; después, segundos.
- La protección de `raw/` y el hook viven en `.claude/settings.json`; se aplican en las sesiones abiertas sobre este repo, no en los hilos de un proyecto de claude.ai.
