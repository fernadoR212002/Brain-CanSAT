---
name: prueba
description: Planifica o analiza una prueba TST-NNN (un vuelo también es una prueba). Sin datos, escribe el plan con objetivo, montaje y criterios ligados a RQ y RC. Con los datos crudos en raw/, hace el análisis con un script en sim/, deja las figuras en salida/ y da el veredicto. Úsala con «prueba TST-NNN», «prueba nueva», «planear una prueba», «llegaron los datos de la prueba» o «analiza el vuelo».
argument-hint: TST-NNN | nueva
---

# prueba

## Entrada

- `$ARGUMENTS`: un TST-NNN existente o «nueva».
- Los requisitos que se quieren verificar (RQ, RC) y, para el análisis, los datos crudos en `raw/pruebas/` o `raw/vuelos/` (llegan con la skill `subir`).

## Proceso

**Modo plan** (la prueba no existe o todavía no tiene datos):

1. Siguiente TST libre (`index.md`) y nota `Pruebas/tst-NNN-nombre.md` con [la plantilla](../../../Plantillas/prueba.md), `status: planificada`.
2. Objetivo y la decisión que depende del resultado.
3. Criterios de aceptación: un **C** por requisito, con umbral y unidad SI, y el RQ o RC en `requisitos`. Un umbral sin fuente es **Pendiente**.
4. Montaje con los instrumentos y su DS, procedimiento y datos a registrar: variables, unidades, frecuencia, tiempo en UTC y formato del archivo.
5. Riesgos de la prueba (RSK) si los hay.

**Modo análisis** (hay datos en `raw/`):

1. Pon las rutas de los datos en `evidencia` y `status: ejecutada`.
2. Script `sim/tst-NNN-analisis.py`:
   - lee solo `raw/`;
   - escribe el CSV limpio en `derivados/tst-NNN-limpio.csv` y las figuras en `salida/figuras/tst-NNN-*.png`;
   - imprime las métricas;
   - convierte los tiempos a UTC si no lo están, y lo dice.

   Se corre con `python3 sim/tst-NNN-analisis.py`.
3. Resultados como enunciados **M**, copiados de la salida del script (coma decimal, unidad SI).
4. Veredicto por criterio (pasa · falla · no concluyente) y `veredicto` en el frontmatter.
5. Actualiza `verificacion` de cada RQ o RC: `verificado` solo si todos sus criterios pasan con evidencia en `raw/`; `fallido` si alguno falla; `en curso` si falta algo.
6. `python3 scripts/matriz-requisitos.py`.

**En los dos modos:** actualiza `Pruebas/README.md`, `index.md` y `log.md` (`## AAAA-MM-DD · prueba · …`) y corre el lint.

## Salida

- Plan: la nota TST lista para ejecutar, con los criterios ligados a RQ y RC.
- Análisis: script reproducible, CSV limpio, figuras, enunciados M, veredicto y estados de verificación y matriz al día.
- Al usuario: veredicto por criterio y qué requisitos cambiaron de estado.
