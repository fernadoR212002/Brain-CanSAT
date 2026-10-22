---
type: riesgo
status: plantilla          # abierto | mitigado | cerrado | materializado
id: RSK-000
tags: [riesgo]
created: AAAA-MM-DD
source: []
requisitos: []             # RQ y RC que el riesgo amenaza
probabilidad: 0            # 1 a 5
impacto: 0                 # 1 a 5
nivel: ""                  # bajo | medio | alto
responsable: ""
---

# RSK-000 · Riesgo en una línea

> [!NOTE]
> Plantilla. Cópiala a `Riesgos/rsk-NNN-tema.md`. La escala de 5 × 5 es una convención inicial; si la guía o el equipo usan otra, cámbiala aquí y en todas las notas de riesgo.

## Enunciado

Si <causa>, entonces <consecuencia> sobre <requisito o fase de la misión>.

## Evaluación

| Probabilidad (1 a 5) | Impacto (1 a 5) | Nivel = P × I |
|---|---|---|
| … | … | … |

Nivel: bajo de 1 a 6, medio de 8 a 12 y alto de 15 a 25.

## Mitigación

| Acción | Responsable | Ligada a | Estado |
|---|---|---|---|
| … | … | DEC-000 · TST-000 | pendiente |

## Señal de alerta y contingencia

- Señal que indica que el riesgo se está materializando: …
- Plan si ocurre: …

## Historial

- AAAA-MM-DD: identificado en <fuente o acta>.

## Ejemplo

> [!NOTE]
> **Ejemplo** (no es un riesgo real; bórralo al usar la plantilla).
> RSK-000 · Si el sensor de <magnitud> se satura durante <fase>, entonces el controlador pierde la realimentación y no se cumple RC-000. Mitigación: verificar el rango con TST-000 antes del CDR.
