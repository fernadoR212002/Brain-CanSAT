---
type: requisito            # requisito (RQ, de la competencia) | requisito-control (RC, derivado)
status: plantilla          # borrador | vigente | reemplazado
id: RQ-000                 # RQ-NNN o RC-NNN; el 000 está reservado para plantillas
tags: [requisito]
created: AAAA-MM-DD
source: []                 # RQ: [raw/mision/<archivo>]; RC: [] si no hay fuente nueva
requisitos: []             # RC: el o los RQ de origen, p. ej. [RQ-000]; RQ: []
ref_oficial: ""            # numeración de la guía si no cabe en NNN (p. ej. "3.2.1")
control: no                # si | no: ¿toca al frente de control?
metodo: ""                 # I inspección | A análisis | D demostración | T prueba
responsable: ""            # persona o frente; si no se sabe: Pendiente
verificacion: pendiente    # pendiente | en curso | verificado | fallido
---

# RQ-000 · Título corto del requisito

> [!NOTE]
> Plantilla. Cópiala a `Mision/rq-NNN-titulo-corto.md` (RQ) o a `Control/rc-NNN-titulo-corto.md` (RC). Cambia el `id`, el título y el `status`, y borra los comentarios `#` del frontmatter y esta nota.

## Texto

<!-- RQ: copia literal de la guía en el bloque de cita; no se corrige ni la ortografía. RC: enunciado propio, verificable, con umbral y unidad SI. -->

> **C1.** «Texto literal del requisito, tal cual aparece en la guía.»

Fuente: `raw/mision/<archivo>.pdf`, sección <…>, p. <…> (texto extraído en `derivados/<archivo>.txt`).

## Interpretación (propia)

> [!IMPORTANT]
> Esta sección es interpretación del equipo, no texto oficial.

- **D1.** Qué significa cada término del requisito para nosotros.
- **S1.** Supuesto que hacemos para poder verificarlo (y por qué).

## Verificación

| Método | Criterio de éxito | Prueba o análisis | Estado |
|---|---|---|---|
| T | <magnitud> ≤ <valor> <unidad SI> durante <condición> | TST-000 | pendiente |

## Trazabilidad

<!-- La calcula scripts/matriz-requisitos.py desde el frontmatter de RC, DEC, TST y REV. La skill requisitos la copia aquí; si no coincide, manda el frontmatter. -->

- Origen (solo RC): RQ-000
- Requisitos de control derivados (solo RQ): RC-000
- Decisiones: DEC-000
- Pruebas: TST-000
- Evidencia: `raw/pruebas/<archivo>`
- Entrega: REV-PDR

## Historial

- AAAA-MM-DD: creado desde `raw/mision/<archivo>` (skill requisitos).

## Ejemplo

> [!NOTE]
> **Ejemplo** (no es un requisito real; bórralo al usar la plantilla).
> RC-000 · «El sistema de control deberá mantener <magnitud> dentro de ± <valor> <unidad> durante <fase de la misión>». Origen: RQ-000. Método: T. Responsable: frente de control. Verificación: pendiente.
