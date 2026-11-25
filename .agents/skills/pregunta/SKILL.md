---
name: pregunta
description: Responde preguntas sobre la misión, los requisitos, los componentes, las pruebas o el control usando solo las notas y fuentes del brain, y cita RQ, DS (con página), TST y DEC. Úsala cuando el usuario pregunte algo del proyecto, por ejemplo «pregunta: …», «¿qué dice la guía sobre…?», «¿por qué elegimos…?» o «¿cuánto midió…?».
---

# pregunta

## Entrada

Una pregunta del usuario.

## Proceso

1. **Buscar en el brain:** primero `index.md`. Luego `grep -rn -i "<términos>" Mision Control Subsistemas Decisiones Pruebas Riesgos Conceptos Entregas derivados`, en español y en inglés. Lee las notas que aparezcan y, si hace falta el texto exacto, el derivado en `derivados/`.
2. **Responder con citas:** cada afirmación lleva su fuente, con un enlace relativo cuando apunte a una nota:
   - requisito: `RQ-012` (y `RQ-012·C1` para el texto literal);
   - hoja de datos: `DS-03 p. 12`;
   - medición: `TST-004·M2`;
   - decisión: `DEC-002`;
   - lectura: `L-01 p. 33`.
3. **Separar** lo oficial (texto literal de la guía, entre comillas) de la interpretación del equipo.
4. **Si no está en el brain:** dilo así, «No está en el brain», con `> [!WARNING]` + `> **Sin fuente en raw/** — …`, y sugiere qué subir para responderla. Puedes dar conocimiento general, pero marcado como tal y nunca como dato del proyecto.
5. **No escribir en el repo**, salvo que el usuario pida guardar la respuesta. En ese caso va como nota en `Conceptos/` (con su línea en el README, `index.md` y `log.md`).

## Salida

Una respuesta breve y directa, con citas en cada afirmación y, al final, «Fuentes:» con los enlaces a las notas usadas.
