---
name: decision
description: Hace un trade study y lo registra como DEC-NNN, con opciones, criterios con pesos ligados a requisitos, puntuación, sensibilidad, elección y requisitos afectados. Úsala cuando el usuario diga «decision», «trade study» o «comparemos opciones», o cuando haya que elegir un componente, una arquitectura o un controlador.
---

# decision

## Entrada

- La pregunta que hay que decidir y los requisitos (RQ, RC) que la motivan.
- Los datos de las opciones que ya estén en el brain: DS, TST, L, diseños de `Control/`.

## Proceso

1. **Pregunta y alcance:** formula la decisión en una línea y lista los RQ y RC afectados.
2. **Opciones:** al menos dos, cada una con sus datos clave y su fuente (`DS-03 p. 4`, `TST-002·M1`). Un dato que falte es **Pendiente** y se dice cómo conseguirlo.
3. **Criterios y pesos:** propón criterios ligados a requisitos o restricciones (masa, consumo, costo, plazo, riesgo). **Los pesos los acuerda el usuario**: pregúntaselos y deben sumar 1.
4. **Puntuación:** de 1 a 5 por opción y criterio, con una justificación y su fuente en cada celda; $S_j = \sum_i w_i\, s_{ij}$. Haz la sensibilidad: ¿cambia la ganadora si un peso varía ± 0,10? Si la cuenta es larga, hazla con un `python3 -c` o un script y deja el comando en la nota.
5. **Nota** `Decisiones/dec-NNN-tema.md` con [la plantilla](../../../Plantillas/decision.md), `status: propuesta`. Claude recomienda; el equipo decide. Pasa a `aceptada` (con `fecha_decision` y `responsable`) solo cuando el usuario lo confirme.
6. **Consecuencias:**
   - pon los RQ y RC en `requisitos`;
   - anota los riesgos nuevos (crea el RSK si hace falta) y las pruebas que confirmarán la decisión (TST);
   - si reemplaza otra decisión, llena `reemplaza` y pon la anterior en `status: reemplazada`.
7. **Actualizar** `Decisiones/README.md`, `index.md` (notas e IDs) y `log.md` (`## AAAA-MM-DD · decision · …`). Regenera la matriz y corre el lint.

## Salida

- La nota DEC con la tabla de puntuación y la sensibilidad, y la matriz al día.
- Al usuario: la recomendación, su margen sobre la segunda opción y qué la haría cambiar.
