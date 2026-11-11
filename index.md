# Índice del CanSat Brain

Catálogo de todo lo que hay en el brain. La skill `subir` agrega las fuentes y cada skill que crea una nota la agrega aquí y en el README de su carpeta.

## Fuentes (`raw/`)

`procesado`: **no** (solo catalogada) · **parcial** (algunas secciones; se dice cuáles) · **sí** (texto extraído y notas escritas).

| ID | Archivo | Tipo | Fecha | Procesado | Derivado | Nota |
|---|---|---|---|---|---|---|
| — | [raw/mision/cansat-mission-guide-2027-r1.1.pdf](raw/mision/cansat-mission-guide-2027-r1.1.pdf) | guía oficial de misión, 56 p. | 2026-08-03 (Rev 1.1) | parcial: lo del lazo de rumbo, ver la ficha | [texto](derivados/cansat-mission-guide-2027-r1.1.txt) | [guia-mision-2027](Mision/guia-mision-2027.md) |
| TST-001 | [raw/pruebas/tst-001-1-giroscopio-giro.png](raw/pruebas/tst-001-1-giroscopio-giro.png) | captura de phyphox: giróscopo durante un giro | Pendiente (hora 1:28) | sí (lectura visual) | — | [TST-001](Pruebas/tst-001-exploracion-sensores-celular.md) |
| TST-001 | [raw/pruebas/tst-001-2-magnetometro-giro.png](raw/pruebas/tst-001-2-magnetometro-giro.png) | captura de phyphox: magnetómetro durante un giro | Pendiente (hora 1:31) | sí (lectura visual) | — | [TST-001](Pruebas/tst-001-exploracion-sensores-celular.md) |
| TST-001 | [raw/pruebas/tst-001-3-giroscopio-quieto.png](raw/pruebas/tst-001-3-giroscopio-quieto.png) | captura de phyphox: giróscopo quieto | Pendiente (hora 1:44) | sí (lectura visual) | — | [TST-001](Pruebas/tst-001-exploracion-sensores-celular.md) |
| TST-001 | [raw/pruebas/tst-001-4-magnetometro-absoluto.png](raw/pruebas/tst-001-4-magnetometro-absoluto.png) | captura de phyphox: magnitud total del campo | Pendiente (hora 1:46) | sí (lectura visual) | — | [TST-001](Pruebas/tst-001-exploracion-sensores-celular.md) |
| TST-003 | [raw/pruebas/tst-003-1-magnetometro-sin-calibrar.png](raw/pruebas/tst-003-1-magnetometro-sin-calibrar.png) | captura de MATLAB: magnetómetro del BNO055 crudo (AMG), girando plano (original `Magnetometro_sin_calibrar.png`) | 2026-11-10, 11:30 p. m. | sí (lectura visual) | — | [TST-003](Pruebas/tst-003-bno055-sin-calibrar-esp32-matlab.md) |
| TST-003 | [raw/pruebas/tst-003-2-acelerometro-sin-calibrar.png](raw/pruebas/tst-003-2-acelerometro-sin-calibrar.png) | captura de MATLAB: acelerómetro del BNO055 crudo (AMG), quieto y en movimiento (original `Acelerometro_sin_calibrar.png`) | 2026-11-10, 11:41 p. m. | sí (lectura visual) | — | [TST-003](Pruebas/tst-003-bno055-sin-calibrar-esp32-matlab.md) |
| TST-003 | [raw/pruebas/tst-003-3-orientacion-ndof-sin-calibrar.png](raw/pruebas/tst-003-3-orientacion-ndof-sin-calibrar.png) | captura de MATLAB: orientación NDOF y estado de calibración (original `Giroscopio_sin_calibrar.png`) | 2026-11-10, 11:48 p. m. | sí (lectura visual) | — | [TST-003](Pruebas/tst-003-bno055-sin-calibrar-esp32-matlab.md) |
| TST-003 | [raw/pruebas/tst-003-firmware-acelerometro.cpp](raw/pruebas/tst-003-firmware-acelerometro.cpp), [-magnetometro.cpp](raw/pruebas/tst-003-firmware-magnetometro.cpp), [-orientacion-ndof.cpp](raw/pruebas/tst-003-firmware-orientacion-ndof.cpp) y [platformio.ini](raw/pruebas/tst-003-platformio.ini) | firmware de PlatformIO del compañero (ESP32 clásico, Adafruit BNO055); los tres `platformio.ini` eran idénticos y se guardó uno | 2026-11-10 | sí | — | [TST-003](Pruebas/tst-003-bno055-sin-calibrar-esp32-matlab.md) |
| TST-003 | [raw/pruebas/tst-003-matlab-acelerometro.m](raw/pruebas/tst-003-matlab-acelerometro.m), [-magnetometro.m](raw/pruebas/tst-003-matlab-magnetometro.m) y [-orientacion.m](raw/pruebas/tst-003-matlab-orientacion.m) | scripts de MATLAB del compañero: lectura serie, gráfica en vivo y CSV | 2026-11-10 | sí | — | [TST-003](Pruebas/tst-003-bno055-sin-calibrar-esp32-matlab.md) |
| TST-003 | [raw/pruebas/tst-003-guia-calibracion-bno055.md](raw/pruebas/tst-003-guia-calibracion-bno055.md) | guía de calibración del BNO055 que acompaña los programas (plan de códigos del siguiente paso) | 2026-11-10 | sí | — | [TST-003](Pruebas/tst-003-bno055-sin-calibrar-esp32-matlab.md) |
| — | [raw/datos/notion-hardware-2026-10-25.md](raw/datos/notion-hardware-2026-10-25.md) | copia de la base «Hardware» de Notion (31 componentes) | 2026-10-25 | sí | — | [sensores-giroscopio-magnetometro](Conceptos/sensores-giroscopio-magnetometro.md) |

Enlaces externos ([raw/LINKS.md](raw/LINKS.md)): L-01 modelo WMM2025 (NOAA) · L-02 pygeomag · L-03 sitio de lanzamiento 2027 (no validada) · L-04 giróscopos MEMS (no validada) · L-05 LIS3MDL de ST (no validada) · L-06 phyphox · L-07 ejemplo del servomotor auto-sintonizable (curso de Control Adaptativo; procesado: sí, en [l-07](Conceptos/l-07-servomotor-self-tuning.md)) · L-08 y L-09 hojas de datos oficiales del BNO055 y del LIS3MDL (no abiertas: dominio bloqueado) · L-10 a L-15 valores de foros y fichas para el BNO055 y el LIS3MDL (no validadas).

## Wiki

| Carpeta | Notas |
|---|---|
| [Mision/](Mision/README.md) | [guia-mision-2027.md](Mision/guia-mision-2027.md): ficha de la guía oficial (procesada en parte) |
| [Control/](Control/README.md) | [alcance.md](Control/alcance.md): alcance del frente de control (con pendientes) · [diseno-estabilizacion-camara.md](Control/diseno-estabilizacion-camara.md): opciones de control del lazo de la cámara (L0 a L8), simulación, identificabilidad, qué cambia con TST-003 y réplica en Simulink · [modelo-rumbo-espacio-estados.md](Control/modelo-rumbo-espacio-estados.md): modelo del lazo de rumbo con sus matrices A, B, C, D |
| [Subsistemas/](Subsistemas/README.md) | _(sin notas)_ |
| [Decisiones/](Decisiones/README.md) | _(sin notas)_ |
| [Pruebas/](Pruebas/README.md) | [tst-001-exploracion-sensores-celular.md](Pruebas/tst-001-exploracion-sensores-celular.md): TST-001, giróscopo y magnetómetro con un celular · [tst-002-guia-datos-estacionarios-sensores.md](Pruebas/tst-002-guia-datos-estacionarios-sensores.md): TST-002, guía de laboratorio de datos estacionarios de los sensores reales (planificada) · [tst-003-bno055-sin-calibrar-esp32-matlab.md](Pruebas/tst-003-bno055-sin-calibrar-esp32-matlab.md): TST-003, primera lectura del BNO055 real sin calibrar (exploratoria) |
| [Riesgos/](Riesgos/README.md) | [rsk-001-rango-servo-camara.md](Riesgos/rsk-001-rango-servo-camara.md): RSK-001, recorrido del servo de la cámara · [rsk-002-calibracion-magnetometro.md](Riesgos/rsk-002-calibracion-magnetometro.md): RSK-002, calibración del magnetómetro en vuelo (alto) |
| [Conceptos/](Conceptos/README.md) | [sensores-giroscopio-magnetometro.md](Conceptos/sensores-giroscopio-magnetometro.md): qué miden, Bogotá–Medellín–Virginia, leyes físicas, requisitos y caracterización · [l-07-servomotor-self-tuning.md](Conceptos/l-07-servomotor-self-tuning.md): L-07, seguidor de un modelo de referencia (RLS + RST) |
| [Entregas/](Entregas/README.md) | _(sin notas)_ |
| [Plantillas/](Plantillas/README.md) | [requisito](Plantillas/requisito.md) · [decision](Plantillas/decision.md) · [prueba](Plantillas/prueba.md) · [riesgo](Plantillas/riesgo.md) · [interfaz](Plantillas/interfaz.md) · [acta](Plantillas/acta.md) · [entrega](Plantillas/entrega.md) |

## IDs asignados

Último número usado por tipo (el siguiente es este más uno; nunca se reutilizan).

| RQ | RC | DEC | TST | RSK | ICD | DS | L | ACT | REV |
|---|---|---|---|---|---|---|---|---|---|
| — | — | — | TST-003 | RSK-002 | — | — | L-15 | — | — |

## Derivados (`derivados/`)

- [cansat-mission-guide-2027-r1.1.txt](derivados/cansat-mission-guide-2027-r1.1.txt): texto de la guía (`pdftotext -layout`).
- [campo-geomagnetico.csv](derivados/campo-geomagnetico.csv): campo WMM2025 en Bogotá, Medellín y Monterey (lo escribe `sim/campo-geomagnetico.py`).
- [caracterizacion-sensores.csv](derivados/caracterizacion-sensores.csv): error de rumbo por fuente y por sitio (`sim/caracterizacion-sensores.py`).
- [modelo-rumbo.txt](derivados/modelo-rumbo.txt), [modelo-rumbo-cero-de-muestreo.csv](derivados/modelo-rumbo-cero-de-muestreo.csv) y [modelo-rumbo-giro-maximo.csv](derivados/modelo-rumbo-giro-maximo.csv): comprobación simbólica del modelo de rumbo (`sim/modelo-rumbo.py`).
- [diseno-estabilizacion-camara-metricas.csv](derivados/diseno-estabilizacion-camara-metricas.csv), [-robustez.csv](derivados/diseno-estabilizacion-camara-robustez.csv) y [-identificabilidad.csv](derivados/diseno-estabilizacion-camara-identificabilidad.csv): comparación de leyes de control de la cámara (`sim/diseno-estabilizacion-camara.py`).
- [simulink-lazo-camara-l3-metricas.csv](derivados/simulink-lazo-camara-l3-metricas.csv): métricas de L3 en Simulink, S1 y S2 (`sim/simulink_lazo_camara_l3.m`).
- [l-07-modelos-discretos.csv](derivados/l-07-modelos-discretos.csv), [l-07-reproduccion-str.csv](derivados/l-07-reproduccion-str.csv) y [l-07-cero-de-muestreo.csv](derivados/l-07-cero-de-muestreo.csv): reproducción del ejemplo L-07 (`sim/l-07-servomotor-self-tuning.py`).

## Simulación y herramientas

- [sim/requirements.txt](sim/requirements.txt): entorno de simulación. Scripts de `sim/`: [campo-geomagnetico.py](sim/campo-geomagnetico.py) · [caracterizacion-sensores.py](sim/caracterizacion-sensores.py) · [modelo-rumbo.py](sim/modelo-rumbo.py) · [l-07-servomotor-self-tuning.py](sim/l-07-servomotor-self-tuning.py) · [diseno-estabilizacion-camara.py](sim/diseno-estabilizacion-camara.py) · [servo-prueba-futaba.m](sim/servo-prueba-futaba.m) (MATLAB, prueba de banco del servo) · [simulink_lazo_camara_l3.m](sim/simulink_lazo_camara_l3.m) (MATLAB, construye y corre el modelo de Simulink [lazo_camara_l3.slx](sim/lazo_camara_l3.slx) de L3, con colores por función).
- [scripts/matriz-requisitos.py](scripts/matriz-requisitos.py) · [scripts/lint.py](scripts/lint.py) · [scripts/brain.py](scripts/brain.py).

## Salidas (`salida/`)

- [matriz-requisitos.csv](salida/matriz-requisitos.csv): matriz de trazabilidad (vacía, con encabezados).
- [tst-002-guia-laboratorio-sensores.pdf](salida/tst-002-guia-laboratorio-sensores.pdf): TST-002 exportada a PDF para compartir con eléctrica (la fuente de verdad es la nota).
- [figuras/diseno-estabilizacion-camara.png](salida/figuras/diseno-estabilizacion-camara.png): error de la cámara en S2 y zumbido del cero cancelado.
- [figuras/simulink-lazo-camara-l3.png](salida/figuras/simulink-lazo-camara-l3.png): error de la cámara con L3 en Simulink (S1 y S2); [figuras/simulink-lazo-camara-l3-modelo.png](salida/figuras/simulink-lazo-camara-l3-modelo.png): el diagrama de Simulink con los colores por función.
- [presentacion-control-camara/](salida/presentacion-control-camara/index.html): presentación para el equipo (7 diapositivas con three.js) del control de la cámara y del trabajo con el BNO055, con las capturas originales y el diagrama archify del lazo por colores. Artifact privado: https://claude.ai/artifact/7NkQKFxgatcrG7yPeDGqz4.
- [figuras/l-07-reproduccion-str.png](salida/figuras/l-07-reproduccion-str.png) y [figuras/l-07-cero-de-muestreo.png](salida/figuras/l-07-cero-de-muestreo.png): figuras del ejemplo L-07.

## Memoria, guías y configuración

- [README.md](README.md) · [GUIA.md](GUIA.md) · [CLAUDE.md](CLAUDE.md) · [estado.md](estado.md) · [log.md](log.md)
- `.claude/settings.json` (permisos y hook) · `.claude/hooks/session-start.sh` · `.claude/skills/` (10 skills)
