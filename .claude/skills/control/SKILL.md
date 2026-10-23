---
name: control
description: Diseña y evalúa una solución de control a partir de un requisito. Plantea el modelo de planta con sus supuestos, el controlador, una simulación reproducible en sim/ y las métricas (sobrepaso, tiempo de establecimiento, error en estado estacionario, márgenes), y escribe la nota en Control/, con un DEC si se elige una opción. Úsala cuando el usuario diga «control», pida modelar una planta, diseñar o sintonizar un controlador, o simular un lazo.
argument-hint: RC-NNN
---

# control

## Entrada

- Un RC-NNN (`$ARGUMENTS`) o, si no lo hay, un RQ de control. Sin RC no se diseña: primero corre la skill `requisitos`.
- Las notas relacionadas: el RQ de origen, las hojas de datos (DS) de sensores y actuadores, y las pruebas (TST) y decisiones (DEC) previas.

## Proceso

1. **Especificación:** convierte el RC en metas numéricas con unidad, por ejemplo $M_p \le$ …, $t_s \le$ … s, $|e_{ss}| \le$ …, margen de fase $\ge$ … °. Lo que el RC no fije queda como **Pendiente**: no se inventa.
2. **Modelo de planta:**
   - ecuaciones de movimiento como enunciados **P**;
   - parámetros con su fuente (`DS-03 p. 12`, `TST-004·M2`);
   - supuestos **S** numerados, con la linealización y el punto de operación;
   - un diagrama de bloques en mermaid.

   Un parámetro sin fuente se marca `> [!WARNING]` + `> **Sin fuente en raw/** — …`, y se dice cómo medirlo (propón una prueba).
3. **Controlador:** al menos dos candidatos razonables para la planta (por ejemplo PID, adelanto-atraso o realimentación de estados), con la sintonía justificada. Si el problema es de secuencia, una máquina de estados en mermaid (`stateDiagram-v2`).
4. **Simulación:** `sim/rc-NNN-<tema>.py`, con python-control, scipy y numpy:
   - parámetros al inicio, cada uno con su fuente en un comentario;
   - semilla fija si hay azar;
   - límites de saturación del actuador tomados de su DS;
   - figuras en `salida/figuras/rc-NNN-*.png` y métricas en `derivados/rc-NNN-metricas.csv`;
   - imprime las métricas.

   Se corre con `python3 sim/rc-NNN-<tema>.py`.
5. **Métricas** (definiciones en [Control/alcance.md](../../../Control/alcance.md)): sobrepaso, tiempo de establecimiento (2 %), error en estado estacionario, margen de ganancia y de fase, esfuerzo de control frente a la saturación, y robustez ante la variación de los parámetros inciertos. Todos los números salen del script.
6. **Nota** `Control/diseno-<tema>.md` (frontmatter: `type: diseno-control`, `requisitos: [RC-NNN]`, `source`), con estas secciones:
   - especificación;
   - planta (P y S);
   - controladores;
   - resultados (enunciados **M** con coma decimal y unidad);
   - tabla de metas frente a resultados;
   - cómo reproducirlo.
7. **Decidir:** si hay que elegir entre candidatos, sigue la skill `decision` (DEC-NNN, con los criterios ligados al RC) y propón la prueba que lo confirme (skill `prueba`).
8. **Actualizar** `Control/README.md`, `sim/README.md`, `index.md` y `log.md` (`## AAAA-MM-DD · control · …`); regenera la matriz si hubo DEC y corre el lint.

## Salida

- Script en `sim/`, figuras en `salida/figuras/`, métricas en `derivados/`, nota en `Control/` y, si se eligió, un DEC.
- Al usuario: la tabla de metas frente a resultados, el candidato recomendado y por qué, y los supuestos más débiles que habría que medir.
