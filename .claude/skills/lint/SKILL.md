---
name: lint
description: Revisión de salud del brain, cada dos semanas. Busca enlaces rotos, wikilinks, notas huérfanas, requisitos sin método o sin verificar, pruebas sin requisito, unidades sin declarar y contradicciones entre notas. Úsala con «lint» o «revisa el brain», o cuando la última entrada lint de log.md tenga más de 14 días.
---

# lint

## Entrada

Todo el repo, menos el contenido de `raw/` y `derivados/`, que no se corrige.

## Proceso

1. **Revisión mecánica:** `python3 scripts/lint.py`. Detecta:
   - errores: wikilinks, enlaces rotos, notas sin frontmatter completo, IDs duplicados, README faltantes;
   - avisos: notas huérfanas o fuera del README de su carpeta, requisitos sin método o sin responsable, requisitos sin verificar, pruebas sin requisito, avisos mal formados, posibles puntos decimales en notas, fuentes sin catalogar, matriz desactualizada, rutas inexistentes en el frontmatter.
2. **Revisión con criterio** (la hace Claude leyendo las notas):
   - **Unidades:** cada número físico lleva unidad SI; coma decimal en notas y punto en CSV y código.
   - **Contradicciones:** una misma magnitud con valores distintos en dos notas; un RQ cuyo texto no coincide con su derivado; un `estado.md` que no cuadra con la matriz; un DEC aceptado que contradice otro.
   - **Trazabilidad:** RQ de control sin RC, RC sin DEC ni TST cerca de una revisión, requisitos `verificado` sin evidencia en `raw/`.
   - **Vigencia:** notas `borrador` con más de 30 días y pendientes que ya tienen fuente.
3. **Corregir lo trivial** en la wiki: enlaces, líneas de README que faltan, formato de avisos. Nunca toques `raw/` ni `derivados/` a mano. Las contradicciones y los cambios de contenido se reportan y se preguntan; no se resuelven solos.
4. **Registrar** en `log.md`: `## AAAA-MM-DD · lint · N errores, M avisos`, con lo corregido y lo pendiente.

## Salida

Un informe corto con errores, avisos, lo que se corrigió y lo que necesita decisión del usuario. `scripts/lint.py` debe terminar sin errores antes de abrir un PR.
