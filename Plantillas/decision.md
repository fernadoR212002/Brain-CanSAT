---
type: decision
status: plantilla          # propuesta | aceptada | reemplazada | descartada
id: DEC-000
tags: [decision]
created: AAAA-MM-DD
source: []                 # fuentes de los datos de las opciones: DS, L, TST, actas
requisitos: []             # RQ y RC afectados, p. ej. [RQ-000, RC-000]
responsable: ""            # quién decide (si no se sabe: Pendiente)
fecha_decision: ""         # AAAA-MM-DD (America/Bogota), cuando el equipo la acepta
reemplaza: ""              # DEC anterior, si la hay
---

# DEC-000 · Pregunta de la decisión

> [!NOTE]
> Plantilla. Cópiala a `Decisiones/dec-NNN-tema.md`. Claude propone; el equipo decide: la nota queda en `propuesta` hasta que el responsable la acepte.

## Contexto

- **C1.** Requisito que obliga a decidir (cita RQ o RC con su texto).
- **S1.** Supuestos con los que se compara.

## Opciones

| Opción | Descripción | Datos clave (con fuente) |
|---|---|---|
| A | … | DS-00 p. <…> |
| B | … | TST-000·M1 |

## Criterios y pesos

Los pesos los acuerda el equipo y suman 1.

| Criterio | Peso $w_i$ | Ligado a | Cómo se puntúa (1 a 5) |
|---|---|---|---|
| … | 0,40 | RC-000 | … |
| … | 0,60 | RQ-000 | … |

## Puntuación

$$
S_j = \sum_i w_i \, s_{ij}, \qquad \sum_i w_i = 1
$$

| Criterio | Peso | A | B |
|---|---|---|---|
| … | 0,40 | … | … |
| … | 0,60 | … | … |
| **Total $S_j$** | 1,00 | … | … |

Sensibilidad: ¿cambia la ganadora si un peso varía ± 0,10? Anota el resultado.

## Decisión

Opción elegida y por qué, en dos o tres frases.

## Consecuencias

- Requisitos afectados: RQ-000, RC-000 (actualiza su nota y la matriz).
- Riesgos nuevos o que cambian: RSK-000.
- Pruebas necesarias para confirmar: TST-000.

## Ejemplo

> [!NOTE]
> **Ejemplo** (no es una decisión real; bórralo al usar la plantilla).
> DEC-000 · ¿Qué sensor usamos para medir <magnitud>? Opciones: sensor A y sensor B, con datos de sus hojas DS-00. Criterios: resolución (ligada a RC-000), masa (ligada a RQ-000) y consumo. Ganadora: la de mayor $S_j$, con su sensibilidad anotada.
