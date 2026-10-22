---
name: estado
description: Reescribe estado.md y el bloque de estado del README con la próxima revisión y los días que faltan, los requisitos de control verificados (X de Y), los riesgos altos abiertos y los 3 próximos pasos. Úsala con «estado», al cerrar cada sesión y después de subir fuentes, verificar requisitos o registrar riesgos.
---

# estado

## Entrada

El estado actual del brain: matriz, notas de `Entregas/`, `Riesgos/` y `Mision/`, `raw/inbox/` y `log.md`.

## Proceso

1. **Fecha real:** `TZ=America/Bogota date '+%Y-%m-%d'`.
2. **Próxima revisión:** la `fecha_limite` futura más cercana en `Entregas/` o en `Mision/calendario.md`. Días que faltan: `python3 -c "from datetime import date; print((date(AAAA,MM,DD) - date.today()).days)"` (con `TZ=America/Bogota`). Sin fecha: **Pendiente**.
3. **Requisitos de control:** `python3 scripts/matriz-requisitos.py`, que imprime «Requisitos de control verificados: X de Y» (los de `control = si` con `verificacion = verificado`).
4. **Riesgos altos:** notas de `Riesgos/` con `nivel: alto` y `status: abierto`. Lista sus ID y títulos.
5. **Inbox:** número de archivos en `raw/inbox/` (sin `.gitkeep`). **Último lint:** la última entrada `lint` del log.
6. **Tres próximos pasos:** en este orden, lo que bloquea la próxima revisión, los requisitos de control sin verificar y los pendientes del log. Son concretos y con la skill que los resuelve.
7. **Escribir:**
   - `estado.md` completo (una página como máximo, con la misma estructura);
   - en `README.md`, solo lo que está entre `<!-- estado:inicio … -->` y `<!-- estado:fin -->`;
   - los avisos **Pendiente** que sigan sin resolver se conservan;
   - `log.md`: `## AAAA-MM-DD · estado · …` en una línea.

## Salida

`estado.md` y el bloque del README al día, y al usuario un resumen de 4 líneas: revisión y días, control X de Y, riesgos altos y el próximo paso.
