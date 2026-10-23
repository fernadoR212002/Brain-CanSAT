# raw/ · fuentes inmutables

Lo que llega de fuera, tal cual: nunca se edita. Si algo está mal en una fuente, se corrige en la nota de la wiki y se marca como interpretación.

- **Entrada única:** `inbox/`. Aquí se sueltan los archivos (desde GitHub, el celular o el chat) y la skill `subir` los clasifica y los mueve con `git mv` a su subcarpeta, con el ID delante.
- **Catálogo:** las subcarpetas no llevan README; todo se cataloga en [index.md](../index.md), con la columna `procesado`.
- **Protección:** `.claude/settings.json` niega a Claude editar o escribir en las subcarpetas (todas menos `inbox/`).
- **Archivos grandes (más de 25 MB):** van a Google Drive y aquí solo queda el enlace, en [LINKS.md](LINKS.md).

| Subcarpeta | Qué va | ID |
|---|---|---|
| `inbox/` | entrada única; se vacía con `subir` | — |
| `mision/` | guía, reglas, calendario y aclaraciones oficiales (texto literal) | — (genera RQ) |
| `revisiones/` | plantillas oficiales de revisión y comentarios de jueces | — (alimenta REV) |
| `datasheets/` | hojas de datos de componentes | DS-NN |
| `pruebas/` | datos crudos de pruebas | TST-NNN |
| `vuelos/` | telemetría cruda de vuelos | TST-NNN |
| `reuniones/` | actas, fotos de tablero, notas de reunión | ACT-AAAA-MM-DD |
| `lecturas/` | artículos, libros, tutoriales | L-NN |
| `datos/` | otros datos de referencia (tablas, mapas, modelos) | — |
