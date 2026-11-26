---
name: subir
description: Procesa lo que hay en raw/inbox/. Clasifica cada archivo, le asigna ID, lo mueve con git mv a su subcarpeta de raw/, extrae el texto a derivados/, escribe la nota de la wiki y actualiza index.md, el README de la carpeta y log.md. Si llega la guía de misión, encadena la skill requisitos. Úsala cuando el usuario diga «subir», «procesa el inbox» o «ya subí…», o cuando pegue un documento para guardarlo como fuente.
---

# subir

## Entrada

- Archivos en `raw/inbox/`.
- O texto o archivos que el usuario pegó o adjuntó en el chat. Guárdalos primero en `raw/inbox/AAAA-MM-DD-tema.md` (texto literal), con una línea inicial de procedencia: quién lo envió, cuándo y por qué medio.

## Proceso

Para cada archivo del inbox (sin contar `.gitkeep`):

1. **Revisar antes de mover.**
   - Tamaño de más de 25 MB: no va a git. Pide subirlo a Drive y agrega una fila en `raw/LINKS.md`.
   - Datos de terceros (datos personales, material de otros equipos, contenido con licencia): pregunta antes de seguir (regla 7).
2. **Clasificar e identificar.**

   | Si es… | Subcarpeta | ID | Nota |
   |---|---|---|---|
   | guía, reglas, calendario o aclaración oficial | `mision/` | — | `Mision/` (resumen, calendario); luego la skill `requisitos` |
   | plantilla de revisión o comentarios de jueces | `revisiones/` | — | `Entregas/rev-xxx.md` |
   | hoja de datos | `datasheets/` | DS-NN | `Subsistemas/ds-NN-componente.md` |
   | datos crudos de una prueba | `pruebas/` | TST-NNN (el de su prueba) | `Pruebas/tst-NNN-….md`; si no existe, la skill `prueba` |
   | telemetría de vuelo | `vuelos/` | TST-NNN | igual que una prueba |
   | acta, foto de tablero, notas de reunión | `reuniones/` | ACT-AAAA-MM-DD | `Decisiones/act-AAAA-MM-DD-tema.md` |
   | artículo, libro, tutorial | `lecturas/` | L-NN | `Conceptos/l-NN-tema.md` |
   | otros datos de referencia | `datos/` | — | solo en `index.md`, o en la nota que lo use |

   Siguiente número libre: el mayor de `index.md` (tabla «IDs asignados») y de `log.md`, más uno. Nunca reutilices un número.
3. **Mover**, en dos comandos separados:
   - `git add raw/inbox/<archivo>` (si no estaba en git);
   - `git mv raw/inbox/<archivo> raw/<subcarpeta>/<id-en-minúsculas>-<nombre-corto>.<ext>`, en minúsculas y con guiones, sin opciones y sin encadenarlo con `&&`.

   Así coincide con la regla `allow` `Bash(git mv raw/inbox/* raw/*)` y no pide permiso. Si aun así se bloquea, detente y pide al usuario que lo apruebe. No lo rodees con otro comando ni con un script.
4. **Extraer el texto, una sola vez:**
   - PDF: `pdfinfo` para contar páginas; si pasa de 30, pregunta qué secciones procesar (y marca `procesado: parcial`). Luego `pdftotext -layout raw/<…>.pdf derivados/<mismo-nombre>.txt`.
   - PDF sin capa de texto o foto con texto: OCR (`pdftoppm -r 300 -png` + `tesseract -l spa+eng`; si `tesseract` no está, avisa y deja `procesado: no`).
   - DOCX o PPTX: `pandoc -t plain` a `derivados/`. XLSX: CSV con pandas a `derivados/`.
   - CSV o telemetría: queda cruda; la limpieza la hace un script de `sim/` (skill `prueba`).
5. **Escribir la nota** con la plantilla que corresponda (`Plantillas/`). Si no hay plantilla (DS, L, resumen de guía), usa este frontmatter: `type` (datasheet · lectura · guia · calendario), `status: borrador`, `id`, `tags`, `created`, `source: [raw/…]`, `requisitos: []`. El cuerpo lleva:
   - qué es y de dónde viene;
   - los datos clave como enunciados **C** con su página (`DS-03 p. 12`);
   - lo que falta por leer.

   Nada sin fuente. El texto oficial va literal.
6. **Actualizar:**
   - `index.md`: fila de la fuente con `procesado` y su derivado, y la tabla de IDs.
   - El README de la carpeta de la nota: una línea.
   - `log.md`: entrada `## AAAA-MM-DD · subir · …`.
7. **Encadenar:** si llegó la guía de misión o una aclaración oficial, sigue con la skill `requisitos`.
8. **Comprobar:** `python3 scripts/lint.py`.

## Salida

- Fuentes movidas a `raw/<subcarpeta>/` con su ID, texto en `derivados/`, notas nuevas y `index.md`, README y `log.md` al día.
- Al usuario: una tabla con archivo, ID asignado, nota creada y `procesado`, y lo que quedó pendiente (secciones sin leer, preguntas).
