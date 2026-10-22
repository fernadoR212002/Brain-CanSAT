---
name: inicio
description: Abre una sesión de trabajo en el CanSat Brain. Trae lo nuevo de main, lee las reglas, el estado y el log, toma la fecha real, revisa raw/inbox/ y saluda con lo nuevo, la próxima revisión y los días que faltan. Úsala al empezar cada sesión o cuando el usuario diga «inicio», «empecemos», «qué hay de nuevo» o «buenos días».
---

# inicio

## Entrada

Nada. Opcional: el tema del día.

## Proceso

1. **Traer lo nuevo:** `git pull --no-rebase origin main`. Así llegan los archivos que se subieron a `raw/inbox/` desde GitHub. Si hay un conflicto, detente y avisa; no lo resuelvas a ciegas.
2. **Leer:** `CLAUDE.md`, `estado.md` y las últimas 5 entradas del log. Para ubicarlas, `grep -n '^## [0-9]' log.md | tail -5`; luego lee desde la primera de esas líneas hasta el final.
3. **Fecha real:** `TZ=America/Bogota date '+%Y-%m-%d %H:%M %Z'`. Nunca la supongas.
4. **Inbox:** `ls -la raw/inbox/`, sin contar `.gitkeep`. Anota nombre y tamaño de cada archivo.
5. **Próxima revisión:** búscala en `estado.md`, en `Mision/calendario.md` y en el `fecha_limite` de las notas de `Entregas/`. Si hay fecha, calcula los días que faltan:
   `python3 -c "from datetime import date; print((date(AAAA,MM,DD) - date.today()).days)"` (con `TZ=America/Bogota`). Si no hay fecha, es **Pendiente**.
6. **Lint vencido:** si la última entrada `lint` del log tiene más de 14 días, sugiere correr `lint`.

## Salida

Un saludo de 8 líneas como máximo, sin escribir en el repo:

- fecha y hora (America/Bogota);
- lo nuevo: archivos en el inbox, commits nuevos de `main` y lo último del log;
- próxima revisión y días que faltan, o «Pendiente»;
- la siguiente palabra sugerida (por ejemplo, «subir» si hay archivos en el inbox).
