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

## 2026-11-10 · prueba · TST-002, guía de laboratorio de datos estacionarios de los sensores

- Pedido del líder: un documento para el compañero de ingeniería eléctrica que diga qué datos de los sensores se necesitan y cómo tomarlos, sin vuelo, porque por ahora solo hay datos estacionarios.
- Nueva nota [TST-002](Pruebas/tst-002-guia-datos-estacionarios-sensores.md) (planificada), que incluye:
  - una tabla de qué dato se necesita, para qué y qué valor supuesto reemplaza en `sim/`;
  - siete criterios: PQ28, PQ30 y PQ29 como requisitos; ruido de rumbo, sesgo, campo del servo y campo calibrado como supuestos de diseño;
  - el montaje con el ESP32-S3, el BNO055, el LIS3MDL y el servo;
  - la configuración del firmware y el formato CSV;
  - los ensayos E0 a E4: verificación, quieto corto con apagados, quieto largo, poses estáticas e interferencia del servo a 30, 60, 110 y 220 mm;
  - la bitácora.
- Contexto de la conversación: el líder pide estimar la planta en línea (perturbaciones y modelo cambiante), con acción de control de 0 a 5 V, servo por PWM y ESP32. Los umbrales del estimador en línea dependen del ruido que mide esta prueba.
- Exportada a PDF para compartir: `salida/tst-002-guia-laboratorio-sensores.pdf`.
- **Pendiente:** responsable, sitio de la prueba, modelo del servo (`Servos.pdf` sigue en `raw/inbox/` sin procesar) y las hojas de datos L-08 y L-09 para confirmar modos y registros.


## 2026-11-11 · subir · TST-003, primera lectura del BNO055 real sin calibrar

- El líder subió dos carpetas de su compañero: los proyectos de PlatformIO con los scripts de MATLAB y una guía de calibración, y tres capturas de las gráficas «sin calibrar».
- Fuentes nuevas en `raw/pruebas/` con el prefijo `tst-003-`:
  - 3 capturas;
  - 3 programas del ESP32 y un `platformio.ini` (los tres eran idénticos);
  - 3 scripts de MATLAB;
  - la guía de calibración.
- Quedaron fuera de git, en `raw/inbox/`:
  - las carpetas `.pio`, unos 96 MB de compilados que se pueden regenerar;
  - las carpetas `.vscode`, con rutas de Windows que incluyen el nombre del compañero (regla 7);
  - los README de plantilla de PlatformIO.
  **Pendiente:** que el líder autorice borrarlos del inbox.
- Nueva nota [TST-003](Pruebas/tst-003-bno055-sin-calibrar-esp32-matlab.md): exploratoria, no concluyente y con lectura visual, porque no llegaron los CSV que guarda MATLAB. Lo que mostró:
  1. el BNO055 funciona por I²C (`0x29`) con un ESP32 clásico, a 20 Hz;
  2. el círculo $m_x$–$m_y$ está corrido ≈ 10 µT frente a un radio de ≈ 28 µT, del orden de 20° de rumbo sin calibrar;
  3. $\lvert B\rvert$ ≈ 52 µT frente a ≈ 30 µT del sitio, con la diferencia en $m_z$;
  4. el acelerómetro se aleja de $g$ al moverlo;
  5. la calibración interna de NDOF necesitó movimiento, y la del acelerómetro nunca llegó a 3.
- No es la ejecución de TST-002: cambian la tarjeta, la frecuencia, las unidades, los sensores y falta el giróscopo crudo.
- Control: nueva sección 9 en [diseno-estabilizacion-camara](Control/diseno-estabilizacion-camara.md).
  - La ley L3 no cambia.
  - El estimador y la calibración del magnetómetro pasan a ser la ruta crítica de C8.
  - El lazo debe correr a 100 Hz.
  - NDOF solo sirve de respaldo con `cal_mag = 3`.
- Nuevo [RSK-002](Riesgos/rsk-002-calibracion-magnetometro.md) (alto): el rumbo magnético queda mal calibrado en vuelo.

## 2026-11-11 · control · Réplica en Simulink del lazo L3 con colores por función

- Pedido del líder: cómo correr la simulación en Simulink, con cada bloque coloreado según su función. No había ningún modelo de Simulink, así que se construyó uno por código.
- Nuevo [simulink_lazo_camara_l3.m](sim/simulink_lazo_camara_l3.m), que genera [lazo_camara_l3.slx](sim/lazo_camara_l3.slx). Los colores:
  - verde: referencia;
  - rojo: perturbación;
  - azul: RST;
  - cian: prealimentación;
  - naranja: actuador;
  - magenta: planta;
  - amarillo: sensores;
  - violeta: estimador;
  - gris: medición.
- El diseño RST coincide con el de Python, y las métricas se parecen aunque el ruido sale de otro generador:

  | Escenario | Simulink: máx \|e\| | Simulink: error de control | Python: máx \|e\| | Python: error de control |
  |---|---|---|---|---|
  | S1 | 3,01° | 0,28° | 3,06° | 0,27° |
  | S2 | 2,60° | 0,19° | 2,55° | 0,21° |

  Las métricas están en [simulink-lazo-camara-l3-metricas.csv](derivados/simulink-lazo-camara-l3-metricas.csv).

## 2026-11-11 · salida · Presentación del control de la cámara para el equipo

- Pedido del líder: diapositivas tipo landing page con three.js, máximo 7, que contextualicen el control, explicado con la regla de colores del modelo de Simulink, y el trabajo de Luis Edmundo Parra con el sensor. Sin tecnicismos y con las imágenes originales; el filtro del sensor queda como trabajo futuro y, al final, la necesidad de probar con el recovery.
- Nueva [presentacion-control-camara](salida/presentacion-control-camara/index.html), publicada como Artifact privado (https://claude.ai/artifact/7NkQKFxgatcrG7yPeDGqz4):
  1. portada con los dos autores;
  2. el reto: C8, PQ15 y C11 literales (guía, p. 9 y 14) y dos visores ilustrativos;
  3. el hardware: BNO055 y ESP32, con las 3 capturas de [TST-003](Pruebas/tst-003-bno055-sin-calibrar-esp32-matlab.md);
  4. el control: los 9 colores (cálidos = mundo físico, fríos = software en el ESP32), una vuelta del lazo, el diagrama archify incrustado y la captura del modelo;
  5. los resultados en Simulink: 3,01° y 2,60° frente a ±10°, con la figura y los osciloscopios;
  6. el sensor real: el círculo del magnetómetro, interactivo, y lo que cambia (sección 9 del [diseño](Control/diseno-estabilizacion-camara.md));
  7. lo que sigue: filtro en banco, calibración 3D, registro a 100 Hz, medir el motor y la prueba de caída desde dron con el recovery.
- Los números salen de [simulink-lazo-camara-l3-metricas.csv](derivados/simulink-lazo-camara-l3-metricas.csv), de TST-003 y de la sección 9 del diseño. Las animaciones son ilustraciones y la página lo dice.
- En el mismo commit van el [lazo_camara_l3.slx](sim/lazo_camara_l3.slx) y las dos figuras de `salida/figuras/` que el líder regeneró al correr el script en MATLAB, y la carpeta de archify del diagrama, sin las capturas de la revisión visual.
