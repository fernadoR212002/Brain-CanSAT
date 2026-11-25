---
name: revision
description: Arma el entregable de una revisión de la competencia (PDR, CDR, PFR u otra que fije la guía) con la plantilla oficial de raw/revisiones/, comprueba la cobertura de requisitos y lo exporta a salida/ en PDF o PPTX. Úsala con «revision PDR», «revision CDR», «revision PFR» o cuando se acerque la fecha de una entrega.
argument-hint: PDR | CDR | PFR
---

# revision

## Entrada

- `$ARGUMENTS`: la revisión (PDR, CDR, PFR…).
- La plantilla oficial y los criterios de evaluación en `raw/revisiones/`, la fecha límite (guía o calendario) y las notas del brain.

## Proceso

1. **Plantilla oficial:** búscala en `raw/revisiones/` (e `index.md`). Si no está, **detente**: pide que la suban y no inventes la estructura.
2. **Nota** `Entregas/rev-xxx.md` con [la plantilla](../../../Plantillas/entrega.md):
   - la estructura es la de las secciones oficiales, en su orden y con sus títulos literales;
   - `fecha_limite` en America/Bogota;
   - un responsable por sección, si se sabe.
3. **Cobertura:** `python3 scripts/matriz-requisitos.py` y lee `salida/matriz-requisitos.csv`. Por cada RQ que la revisión deba cubrir (según la guía) y cada RC de control, indica la sección, la evidencia (TST·M, DEC, DS) y el estado. Lista lo que falta: sin método, sin prueba, sin evidencia, `pendiente`.
4. **Contenido:** llena cada sección desde las notas, citando IDs. Los números se copian de las notas con su unidad y su fuente. Lo que no exista se marca **Pendiente** y entra en la lista de faltantes; no se rellena.
5. **Exportar** a `salida/rev-xxx-AAAA-MM-DD.<pdf|pptx>` en el formato que pida la guía:
   - Markdown a PDF o DOCX con `pandoc`;
   - si la plantilla oficial es PPTX o DOCX, llénala con python-pptx o python-docx (o la skill de pptx o docx si está disponible);
   - PDF final con `libreoffice --headless --convert-to pdf`.

   Revisa el resultado visualmente (página por página como imagen) antes de darlo por listo.
6. **Después de la revisión:** los comentarios de los jueces entran literales por `raw/inbox/` → `raw/revisiones/`. Cada uno genera una acción: RSK, DEC, TST o un cambio de RC, registrada en la nota de la entrega.
7. **Actualizar** `Entregas/README.md`, `index.md`, `log.md` (`## AAAA-MM-DD · revision · …`) y la skill `estado`. Corre el lint.

## Salida

- `Entregas/rev-xxx.md` con la estructura oficial y la cobertura, y el archivo exportado en `salida/`.
- Al usuario: la cobertura (X de Y requisitos con evidencia), la lista de faltantes por responsable y los días que quedan hasta la fecha límite.
