---
name: requisitos
description: Extrae o actualiza los requisitos de la competencia (RQ-NNN) con su texto literal, método de verificación y responsable; marca los que tocan a control, deriva los requisitos de control (RC-NNN) y regenera salida/matriz-requisitos.csv. Úsala después de subir la guía de misión o una aclaración oficial, o cuando el usuario diga «requisitos», «actualiza la matriz» o «qué requisitos son de control».
---

# requisitos

## Entrada

- El texto de la guía en `derivados/` (nunca vuelvas a leer el PDF si ya hay derivado) y las aclaraciones oficiales en `raw/mision/`.
- Las notas RQ y RC que ya existan en `Mision/` y `Control/`.

## Proceso

1. **Localizar los requisitos:** frases normativas («deberá», «debe», «no podrá», «shall», «must») e ítems numerados de requisitos. Anota la sección y la página de cada uno.
2. **Asignar el ID:**
   - Si la guía numera con enteros, usa ese número: el requisito 12 es RQ-012.
   - Si la numeración es jerárquica (3.2.1), usa el siguiente RQ libre y pon la numeración oficial en `ref_oficial`.
   - Nunca renumeres. Si una aclaración cambia un requisito, actualiza su texto citando la nueva fuente y anótalo en el Historial. Si lo elimina, ponle `status: reemplazado` y conserva el ID.
3. **Escribir la nota** `Mision/rq-NNN-titulo-corto.md` con [la plantilla](../../../Plantillas/requisito.md):
   - texto **literal** en el bloque de cita, con la fuente y la página;
   - `metodo`: el que diga la guía; si no lo dice, el propuesto, marcado como propuesta en la sección Interpretación;
   - `responsable`: el frente, si se sabe; si no, `Pendiente`;
   - `verificacion: pendiente`.
4. **Marcar control** (`control: si`) cuando el requisito restrinja algo de esto: sensores, actuadores, estimación de estado, guiado, estabilización, secuencia de vuelo o máquina de estados, tiempos o condiciones de despliegue o liberación, o la telemetría de la que depende el control. Ante la duda, `si`, y pregunta al usuario.
5. **Derivar los RC:** por cada RQ de control, uno o más `Control/rc-NNN-titulo-corto.md`:
   - enunciado propio, verificable, con umbral y unidad SI;
   - `requisitos: [RQ-NNN]`, `control: si`, `metodo`, `responsable` (el frente de control);
   - `status: borrador` hasta que el líder de control lo confirme.

   Un umbral que la guía no da no se inventa: va como **Pendiente**.
6. **Regenerar la matriz:** `python3 scripts/matriz-requisitos.py`. Copia a la sección Trazabilidad de cada nota lo que cambió.
7. **Actualizar** `Mision/README.md`, `Control/README.md`, `index.md` (notas e IDs) y `log.md` (`## AAAA-MM-DD · requisitos · …`). Corre `python3 scripts/lint.py`.

## Salida

- Notas RQ y RC nuevas o actualizadas y `salida/matriz-requisitos.csv` regenerada.
- Al usuario: cuántos RQ hay (cuántos de control), cuántos RC se derivaron y la lista de lo ambiguo o lo que debe confirmar (método, responsable, umbrales).
