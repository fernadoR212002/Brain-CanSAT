# Log del CanSat Brain

Diario del brain. **Solo crece:** cada entrada se agrega al final con el encabezado `## AAAA-MM-DD · tipo · título` (fecha America/Bogota). Tipos: creacion, subir, requisitos, control, prueba, decision, revision, estado, lint, reunion, ajuste.

## 2026-10-22 · creacion · Montaje inicial del brain

- Capas: `raw/` (`inbox/` y 8 subcarpetas, más `LINKS.md`), `derivados/`, wiki (9 carpetas), `sim/`, `scripts/` y `salida/`, cada una con su README (las subcarpetas de `raw/` no lo llevan; el catálogo es `index.md`).
- Memoria y guías: `CLAUDE.md`, `GUIA.md`, `README.md`, `index.md`, `estado.md` y este log.
- 7 plantillas (requisito, decisión, prueba, riesgo, interfaz, acta, entrega) y `Control/alcance.md`, sin datos de misión.
- 10 skills en `.claude/skills/`: inicio, subir, requisitos, control, prueba, decision, pregunta, revision, estado y lint.
- `.claude/settings.json`: niega `Edit` (cubre `Write`) en las 8 subcarpetas de `raw/`, deja libre `raw/inbox/`, niega las herramientas de escritura de Drive y Notion y registra el hook `SessionStart`. Comprobado en esta sesión: escribir en `raw/mision/` falla (con la herramienta Write y con una redirección de Bash) y en `raw/inbox/` funciona; la regla aplicó sin reiniciar.
- Ingesta: el `git mv` de prueba de `raw/inbox/` a `raw/mision/` lo bloqueó el clasificador del modo automático (no la regla). Queda pendiente que el líder decida si se agrega una regla `allow` solo para `git mv raw/inbox/…`; mientras tanto, `subir` pide aprobación para cada movimiento.
- Hook `SessionStart`: instala `sim/requirements.txt` (numpy 2.5.3, scipy 1.18.1, pandas 3.0.5, matplotlib 3.11.2, control 0.10.2). Instalación limpia en un entorno nuevo: 53 s, sin errores.
- `scripts/matriz-requisitos.py` genera `salida/matriz-requisitos.csv` (solo encabezados) y `scripts/lint.py` pasa sin errores.
- Pendiente: competencia y edición, integrantes y frentes, alcance de control, fechas, propiedad del repo.
- Rama `claude/fervent-gauss-1zksw8` → [PR #1](https://github.com/fernadoR212002/Brain-CanSAT/pull/1) hacia `main` (el repo estaba vacío: `main` se creó con el README como primer commit).

## 2026-10-22 · ajuste · Regla allow para git mv desde raw/inbox/

- El líder de control aprobó agregar a `.claude/settings.json` la regla `allow` `Bash(git mv raw/inbox/* raw/*)`. Resuelve el bloqueo de la ingesta que quedó pendiente en la entrada anterior.
- Comprobado: `git mv raw/inbox/prueba-permiso.md raw/mision/prueba-permiso.md` pasa sin preguntar y editar el archivo ya movido sigue negado. El archivo de prueba se borró sin llegar a ningún commit.
- La regla solo cubre `git mv` con origen en `raw/inbox/` y destino en `raw/`. Un `git mv` con opciones delante (`-f`) o con otro origen no coincide y se pide al usuario.
- Actualizados `CLAUDE.md` (permisos y nube) y la skill `subir` (paso 3: `git add` y `git mv` en comandos separados).

## 2026-10-25 · subir · Guía de misión 2027, capturas de phyphox y copia de la base Hardware de Notion

- La guía oficial pasó de `raw/inbox/` a `raw/mision/cansat-mission-guide-2027-r1.1.pdf`, con su texto en `derivados/`. Quedó procesada en parte (lo del lazo de rumbo); ficha en `Mision/guia-mision-2027.md`.
- Las 4 capturas de phyphox del líder de control pasaron a `raw/pruebas/tst-001-*.png`.
- La base «Hardware» de Notion se leyó en modo solo lectura y se guardó como copia literal en `raw/datos/notion-hardware-2026-10-25.md` (regla 9). Los componentes elegidos que importan aquí son el BNO055, el LIS3MDL y la cámara Cyclops 3 V3.
- Enlaces web L-01 a L-06 agregados a `raw/LINKS.md`. L-03, L-04 y L-05 quedan como no validados.
- Hallazgos: la guía se contradice en las fechas (tabla 1 frente al calendario), y el LIS3MDL podría estar descontinuado (L-05, sin validar).

## 2026-10-25 · prueba · TST-001: exploración del giróscopo y el magnetómetro con un celular

- Prueba exploratoria, sin requisito, con valores leídos a ojo de las capturas: el giróscopo solo cambia mientras hay giro, y el magnetómetro queda en el valor nuevo y muestra distorsión de hierro duro y efecto del entorno.
- Pendiente: exportar los CSV de phyphox para analizarlos con un script (regla 4) y anotar la fecha y el lugar.

## 2026-10-25 · control · Nota de concepto: giróscopo y magnetómetro

- `Conceptos/sensores-giroscopio-magnetometro.md` tiene tres partes: cómo funcionan, Bogotá–Medellín–Virginia y las leyes físicas con los requisitos de la guía.
- `sim/campo-geomagnetico.py` (WMM2025 con `pygeomag`, agregado a `sim/requirements.txt`) da la inclinación: 26,5° en Bogotá, 29,3° en Medellín y 64,7° en Monterey. Allí, cada grado de inclinación mal estimada pesa unas 4 veces más que en Colombia.

## 2026-10-25 · ajuste · Escritura en Notion: bloqueada

- El líder aprobó permitir crear y editar páginas dentro de CANSAT en Notion, sin borrar ni mover nada.
- El clasificador del modo automático bloqueó que Claude editara `.claude/settings.json` (automodificación de permisos). El cambio queda en manos del líder; la regla 9 se ajusta cuando se aplique.

## 2026-10-25 · ajuste · Escritura en Notion habilitada y subpágina de sensores

- Por pedido del líder, `.claude/settings.json` ahora permite crear y editar páginas de Notion y subir archivos (`notion-create-pages`, `notion-update-page`, `notion-create-file-upload`). Siguen negados borrar, mover y duplicar, las bases de datos, las vistas y los comentarios.
- Regla 9 y «Permisos y nube» actualizadas en `CLAUDE.md`: se escribe solo dentro de CANSAT y la fuente de verdad es el brain.
- Subpágina creada bajo CANSAT: «Sensores de rumbo: giróscopo y magnetómetro» (https://app.notion.com/p/404d9b500e34818c9d42dfebb09d3367). Tiene las tres partes de `Conceptos/sensores-giroscopio-magnetometro.md` y enlaces al brain.
- Las 4 capturas de TST-001 no se pudieron subir: la red del entorno bloquea `api.notion.com` (respuesta 403 del proxy). La página tiene un aviso por captura, con su enlace a GitHub, para arrastrarlas a mano.

## 2026-10-25 · control · Avance: caracterización de los sensores, modelo de rumbo en espacio de estados y ejemplo L-07

- Pedido del líder: llevar a la subpágina de Notion «Sensores de rumbo» la caracterización de los sensores, el modelo del sistema en espacio de estados (matrices A, B, C y D) y el ejemplo del seguidor de referencia del brain de Control Adaptativo, con el rigor de un avance.
- La rama `claude/fervent-gauss-1zksw8` se reinició desde `main`, porque el PR #3 ya estaba fusionado.
- [sensores-giroscopio-magnetometro](Conceptos/sensores-giroscopio-magnetometro.md) tiene una parte 4 nueva, la caracterización:
  - la cadena de medición;
  - la ley física con su sensibilidad, para el giróscopo MEMS y para el magnetómetro;
  - los modelos de medición;
  - el error de rumbo que deja cada fuente, sitio por sitio.
  Los números salen de `sim/caracterizacion-sensores.py`.
- [modelo-rumbo-espacio-estados](Control/modelo-rumbo-espacio-estados.md) es una nota nueva:
  - contiene las hipótesis, las ecuaciones físicas y las matrices del cuerpo, de la cámara sobre el servomotor, del modelo reducido, del modelo completo de 6 estados y del estimador;
  - analiza la controlabilidad, la observabilidad, la discretización con ZOH, el cero de muestreo y el error ante un giro constante del cuerpo;
  - todo está comprobado con sympy en `sim/modelo-rumbo.py`, para lo que se agregó `sympy` a `sim/requirements.txt`.
- [L-07](Conceptos/l-07-servomotor-self-tuning.md) es otra nota nueva: el ejemplo del servomotor (RLS + RST) contrastado con el PDF original y reproducido con `sim/l-07-servomotor-self-tuning.py`. Hallazgos:
  1. La fuente tiene dos erratas: la ec. (19) repite la (17), y el primer intervalo dice «0<t<100».
  2. Con las ecuaciones tal como están impresas, sin factor de olvido, el estimador no se readapta; con λ = 0,99, la reproducción coincide con la tabla 1.
  3. Cancelar el cero de muestreo (−0,967, y −0,993 desde t = 20 s) hace zumbar el voltaje; conservarlo elimina el zumbido.
- `raw/LINKS.md` tiene nuevos enlaces:
  - L-07, el PDF del curso, por enlace con commit y SHA-256: es material de terceros y no se copió (regla 7);
  - L-08 y L-09, las hojas de datos oficiales, que no se pudieron abrir;
  - L-10 a L-15, valores de foros y fichas, no validados.
- La red del entorno bloquea `bosch-sensortec.com`, `st.com`, `cdn-shop.adafruit.com` y los espejos que se probaron. **Pendiente:** subir las dos hojas de datos por `raw/inbox/`.
- Notion: a la página se le agregaron el resumen del avance, un índice, las partes 4 a 6, el siguiente paso y los enlaces; las partes 1 a 3 quedaron iguales. Las 2 figuras nuevas quedan como avisos para arrastrarlas a mano, porque la red bloquea `api.notion.com`.

## 2026-11-05 · codigo · Código de prueba del servomotor (MATLAB)

- Pedido del líder: guardar en el brain su código de prueba del servo.
- Nuevo [servo-prueba-futaba.m](sim/servo-prueba-futaba.m): empieza con `clear a s`, lleva el servo a 0 y 180 grados y lo deja en `angulo` (90 grados), con pulso de 0,6 a 2,4 ms. Para moverlo sin correr todo: `angulo = 120; writePosition(s, angulo / recorrido)`.
- Depende de `servo_futaba` (brain de tesis del líder, `code/EXP-005/servo`), que no está en este repo.
- **Pendiente:** confirmar el rango de pulso con la hoja de datos del servo; todavía no hay TST ni datos medidos.


## 2026-11-08 · control · Opciones de control del lazo de la cámara (L0 a L8)

- Pedido del líder: qué controladores sirven para estabilizar la cámara con el BNO055. La respuesta se archivó también en el brain de Control Adaptativo (su PR #1), y aquí se trae con las reglas de este brain.
- Nueva nota [diseno-estabilizacion-camara](Control/diseno-estabilizacion-camara.md), con el script [diseno-estabilizacion-camara.py](sim/diseno-estabilizacion-camara.py), tres CSV en `derivados/` y una figura. Resultados:
  1. Se recomienda L3: RST con integrador que conserva el cero de muestreo, más prealimentación del giróscopo $u_{ff}=-\hat\omega_b/K_c$. Deja un error de control ≤ 0,27° y aguanta sin adaptar los cambios de régimen de L-07.
  2. El error que queda (≈ 2,5–3,1°) es casi todo del estimador de rumbo.
  3. En vuelo no se identifica la planta completa, porque los regresores quedan colineales (cond 1,5–1,8·10¹⁰ frente a 5,7·10⁵ en lazo abierto con SBPA). Sí se identifica $K_c$ (error ≤ 1,7 %).
  4. Cancelar el cero multiplica el RMS de Δu por 21 a 42.
- Nuevo [RSK-001](Riesgos/rsk-001-rango-servo-camara.md): el servo Futaba de 180° gasta la mitad de su recorrido en el giro de 90° de C11. Nivel medio, pendiente de medir el giro real.
- Matiz a la caracterización: bajo el paracaídas el acelerómetro no ve el balanceo (P3 de la nota), así que la inclinación para nivelar el magnetómetro debe salir de la fusión con giróscopos. **Pendiente:** verificarlo con un péndulo.
- **Pendiente:** DEC-001 (los pesos los acuerda el equipo), los RC del lazo de rumbo y los TST de identificación en banco y de caída desde dron.
