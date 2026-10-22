---
type: entrega
status: plantilla          # en preparación | entregada | evaluada
id: REV-XXX                # REV-PDR, REV-CDR, REV-PFR…, según la guía
tags: [entrega, revision]
created: AAAA-MM-DD
source: []                 # [raw/revisiones/<plantilla oficial>]
requisitos: []             # RQ y RC que esta entrega debe cubrir
fecha_limite: ""           # AAAA-MM-DD HH:MM (America/Bogota), de la guía o el calendario oficial
plantilla_oficial: ""      # raw/revisiones/<archivo>
exportado: []              # [salida/rev-xxx-AAAA-MM-DD.pdf]
---

# REV-XXX · Nombre de la revisión

> [!NOTE]
> Plantilla. Cópiala a `Entregas/rev-xxx.md`. La estructura sale de la plantilla oficial en `raw/revisiones/`; si no está, no se inventa: se pide.

## Datos de la entrega

- Fecha límite: <…> (America/Bogota) · Formato: <PDF, PPTX…> · Límite de páginas o diapositivas: <…>
- Plantilla oficial: `raw/revisiones/<archivo>`
- Criterios de evaluación (texto literal): …

## Estructura

| Sección oficial | Contenido (notas del brain) | Responsable | Estado |
|---|---|---|---|
| … | … | … | pendiente |

## Cobertura de requisitos

| Requisito | Sección | Evidencia | Verificación |
|---|---|---|---|
| RQ-000 | … | TST-000·M1 | pendiente |

Sin cubrir: …

## Lista de chequeo antes de exportar

- [ ] Todas las secciones oficiales están presentes y en el orden de la plantilla.
- [ ] Cada número tiene su unidad SI y su fuente (TST, DS, DEC).
- [ ] No hay avisos de **Pendiente** ni de **Sin fuente en raw/** sin resolver.
- [ ] La matriz está regenerada y los estados de verificación coinciden.

## Comentarios de los jueces

<!-- Se copian literales a raw/revisiones/ y aquí se resumen, con las acciones que generan. -->

| Comentario (fuente) | Acción | Registro |
|---|---|---|
| … | … | RSK-000 · DEC-000 · TST-000 |

## Ejemplo

> [!NOTE]
> **Ejemplo** (no es una entrega real; bórralo al usar la plantilla).
> REV-PDR · Revisión preliminar de diseño. Secciones según la plantilla oficial; cobertura: los RQ marcados como de control, cada uno con su RC, su DEC y su TST planificado.
