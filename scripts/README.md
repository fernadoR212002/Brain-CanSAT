# scripts/

Herramientas del brain. Solo usan la biblioteca estándar de Python, así que funcionan sin instalar nada. Se corren desde la raíz del repo.

## Scripts

- [brain.py](brain.py) — Funciones comunes: recorre la wiki, lee el frontmatter y construye la matriz de requisitos.
- [matriz-requisitos.py](matriz-requisitos.py) — Regenera `salida/matriz-requisitos.csv` desde el frontmatter e imprime el resumen («requisitos de control verificados X de Y»). Con `--check` solo comprueba que la matriz esté al día.
- [lint.py](lint.py) — Revisa wikilinks, enlaces rotos, frontmatter, IDs, notas huérfanas, requisitos sin método o sin verificar, pruebas sin requisito, avisos mal formados, posibles puntos decimales en notas y fuentes sin catalogar. Termina con un código de error si encuentra errores.
- [exportar-presentacion.py](exportar-presentacion.py) — Empaca `salida/presentacion-control-camara/` (la fuente del Artifact) en `salida/presentacion-control-camara.html`, un solo archivo para enviar: mete las imágenes como data URI y el diagrama de archify por `srcdoc`, y cambia el enlace al diagrama por un botón de pantalla completa. Se corre de nuevo después de cada cambio en la presentación.
