# ¿Cómo funciona el filtro de Kalman con las señales de nuestro CanSat? {#filtro-kalman-rumbo}

El filtro de Kalman hace lo mismo que el filtro complementario del modelo: **predice el rumbo con el giróscopo y lo corrige con el magnetómetro**. La diferencia es que en cada muestra recalcula cuánto creerle a cada sensor, a partir del ruido de cada uno.

- Corrección: compara el rumbo del magnetómetro con el rumbo predicho y reparte esa diferencia entre el rumbo y el sesgo del giróscopo.[](source:estimador)
- Predicción: suma 10 milisegundos de giro medido, menos el sesgo estimado, y entrega el rumbo actual.
- Con los supuestos de ruido del brain, en régimen queda casi igual al complementario: 1,50 frente a 1,55 grados de error cuadrático medio.[](source:kalman)
- Lo que gana es el arranque, la sintonía a partir de medidas y una prueba para rechazar lecturas magnéticas malas. No corrige la calibración del magnetómetro.

@answer scope="Rumbo del cuerpo · 100 muestras por segundo · señales simuladas con los supuestos del diseño de la cámara, sin datos crudos medidos"
@meta locale=es
@source estimador title="Estimador actual: filtro complementario (sim/diseno-estabilizacion-camara.py)" path=sim/diseno-estabilizacion-camara.py lines=186:191
@source kalman title="Simulación del filtro de Kalman frente al complementario (sim/filtro-kalman-rumbo.py y sus cuatro tablas en derivados)" path=sim/filtro-kalman-rumbo.py
@source sensores title="Giróscopo y magnetómetro: qué miden y caracterización" path=Conceptos/sensores-giroscopio-magnetometro.md
@source tst003 title="Prueba TST-003: primera lectura del BNO055 sin calibrar" path=Pruebas/tst-003-bno055-sin-calibrar-esp32-matlab.md
@source tst002 title="Prueba TST-002: guía de datos estacionarios de los sensores" path=Pruebas/tst-002-guia-datos-estacionarios-sensores.md
@source diseno title="Diseño del lazo de estabilización de la cámara" path=Control/diseno-estabilizacion-camara.md
@source modelo title="Modelo del lazo de rumbo en espacio de estados, sección 4" path=Control/modelo-rumbo-espacio-estados.md
@source riesgo title="Riesgo RSK-002: calibración del magnetómetro" path=Riesgos/rsk-002-calibracion-magnetometro.md

## ¿Qué señales entran y qué hace el filtro con ellas? {#senales-y-filtro}

@workflow id=ciclo-kalman title="Un ciclo del filtro de Kalman del rumbo, cada 10 milisegundos"
| magnetometro | Magnetómetro LIS3MDL | external |
| nivelar | Rumbo magnético nivelado | backend |
| correccion | Corrección | backend |
| giroscopio | Giróscopo del BNO055 | external |
| prediccion | Predicción | backend |
| controlador | Controlador de la cámara | frontend |
| magnetometro > nivelar | campo magnético |
| nivelar > correccion | rumbo medido |
| correccion > prediccion | rumbo corregido | emphasis |
| giroscopio > prediccion | velocidad de giro |
| prediccion > controlador | rumbo actual |

@steps id=pasos-ciclo
| paso-magnetometro | Magnetómetro LIS3MDL | Mide el campo magnético en tres ejes, en miligauss, desde la punta del brazo. Señala el norte y no se desvía con el tiempo, pero es ruidoso. | ciclo-kalman | magnetometro |
| paso-nivelar | Rumbo magnético nivelado | Endereza el campo con la inclinación que entrega el BNO055 y calcula el rumbo medido hacia el norte. | ciclo-kalman | nivelar |
| paso-correccion | Corrección | Resta el rumbo predicho al rumbo medido, entre menos 180 y más 180 grados. Una parte de esa diferencia corrige el rumbo y otra corrige el sesgo del giróscopo. | ciclo-kalman | correccion |
| paso-giro | Giróscopo del BNO055 | Mide la velocidad de giro alrededor del eje vertical, en grados por segundo, 100 veces por segundo. Es rápido, pero arrastra un sesgo que no conoce. | ciclo-kalman | giroscopio |
| paso-prediccion | Predicción | Suma 0,01 segundos por la velocidad medida menos el sesgo estimado. Es la parte predictiva: lleva el rumbo hasta el instante actual. Ese rumbo predicho es el que compara la siguiente corrección. | ciclo-kalman | prediccion |
| paso-controlador | Controlador de la cámara | Recibe el rumbo actual del cuerpo y mueve el motor para que la cámara mantenga su rumbo. | ciclo-kalman | controlador |

## ¿Qué dice cada señal y en qué falla? {#senales}

| Señal | Qué mide | En qué es buena | Qué la engaña | Con qué se simuló |
| --- | --- | --- | --- | --- |
| Velocidad de giro del giróscopo | Qué tan rápido gira el cuerpo, en grados por segundo | Responde sin retardo y no le afectan los imanes | Su sesgo. Con 1 grado por segundo sin corregir, el rumbo pasa los 10 grados a los 10 segundos {bad:Deriva} | Sesgo de 0,5 grados por segundo, ruido de 0,1 grados por segundo por muestra y pasos de 1/16 de grado por segundo |
| Campo magnético del magnetómetro | Hacia dónde está el norte, en miligauss | No se desvía con el tiempo {good:Referencia fija} | Ruido, motores, batería y metales. Sin calibrar, el círculo del campo salió corrido unos 10 microteslas | Ruido de 0,9 grados por muestra, más 1,5 grados de residuo de calibración y 2 grados de inclinación que oscilan a 0,4 hercios |
| Inclinación del BNO055 | Cuánto se ladea el cuerpo | Permite nivelar el campo magnético antes de calcular el rumbo | Bajo el paracaídas, el acelerómetro no ve el balanceo | Entra como el error de inclinación de la fila anterior |

Las dos lecturas llegan con una muestra de retraso: describen lo que pasó hace 10 milisegundos. Las cifras vienen de la caracterización de los sensores[](source:sensores), de la primera prueba del BNO055[](source:tst003) y de los supuestos del diseño de la cámara[](source:diseno).

## ¿Qué calcula en cada muestra de 10 milisegundos? {#cada-muestra}

El filtro guarda el rumbo, el sesgo del giróscopo y cuánto duda de cada uno. Esa duda se llama covarianza del error de estimación.

```text title="Un ciclo del filtro, en palabras"
1. Corrección, con el magnetómetro (la lectura describe hace 10 milisegundos):
   diferencia      = envolver(rumbo_magnético − rumbo_predicho)        entre −180° y +180°
   peso_del_rumbo  = duda_del_rumbo ÷ (duda_del_rumbo + ruido_del_magnetómetro)
   peso_del_sesgo  = duda_compartida ÷ (duda_del_rumbo + ruido_del_magnetómetro)
   rumbo           = rumbo_predicho + peso_del_rumbo × diferencia
   sesgo           = sesgo + peso_del_sesgo × diferencia
   después de corregir, la duda baja

2. Predicción, con el giróscopo (avanza hasta el instante actual):
   rumbo_predicho  = rumbo + 0,01 s × (velocidad_medida − sesgo)
   la duda sube con el ruido del giróscopo y con la deriva del sesgo
```

- Si el filtro duda mucho de su predicción, el peso se acerca a 1 y le cree al magnetómetro.
- Si el magnetómetro es muy ruidoso, el peso se acerca a 0 y le cree al giróscopo.
- La duda compartida dice cuánto del error de rumbo se debe al sesgo. Por eso una sola lectura del magnetómetro corrige las dos cosas.
- El filtro complementario actual hace las mismas dos cuentas, pero con pesos fijos.[](source:estimador)

@callout level=note title="«Predictivo» aquí no es control predictivo"
En el filtro de Kalman, predecir es avanzar el rumbo con el giróscopo hasta el instante actual.
Eso compensa la muestra de retraso de los sensores.
No es el control predictivo por modelo, que elige el voltaje del motor mirando hacia el futuro.

## ¿Por qué su peso cambia solo? {#peso-variable}

Al encenderse, el filtro no conoce el sesgo, porque el PocketQube viaja apagado en el contenedor. Por eso arranca con mucha duda y le cree mucho al magnetómetro. A medida que aprende, la duda baja y el peso también.

@chart type=line data=ganancia-rumbo.csv x=Tiempo y="Filtro de Kalman,Filtro complementario actual" unit="%" title="Porcentaje de la diferencia con el magnetómetro que corrige cada muestra (eje horizontal: tiempo en segundos, desde 0,25)"

@facts
| Peso final del filtro de Kalman | 0,48 % por muestra, frente a 0,70 % del complementario |
| Complementario equivalente | 0,33 radianes por segundo con amortiguamiento de 0,73; el actual usa 0,5 y 0,7 |
| Comprobación | Codex lo calculó con la ecuación de Riccati y Claude lo repitió por iteración directa: coinciden. Codex revisó después el orden de cálculo que corrigió Claude |

Si el modelo del ruido es correcto, ese arranque rápido aprende el sesgo antes. A los 2 segundos, al filtro de Kalman le quedan 0,16 grados por segundo de error de sesgo y al complementario, 0,53.[](source:kalman)

@chart type=line data=sesgo-ruido-blanco.csv x=Tiempo y="Filtro de Kalman,Filtro complementario actual,Sesgo verdadero" unit="grados por segundo" title="Sesgo estimado al arrancar, con el error del magnetómetro como ruido blanco (eje horizontal: tiempo en segundos)"

@callout level=warning title="El filtro vale lo que valga su modelo del ruido"
Con el residuo de calibración y la inclinación que oscila, el filtro de Kalman se sobrerreacciona al arrancar.
A los 2 segundos su error de sesgo es de 1,82 grados por segundo, frente a 0,42 del complementario.
Ese error no es ruido blanco, y el filtro lo toma por giro verdadero.

@chart type=line data=sesgo-error-nominal.csv x=Tiempo y="Filtro de Kalman,Filtro complementario actual,Sesgo verdadero" unit="grados por segundo" title="Sesgo estimado al arrancar, con el residuo de calibración y la inclinación (eje horizontal: tiempo en segundos)"

## ¿Qué gana y qué no frente al filtro complementario actual? {#comparacion}

| Criterio | Filtro complementario actual | Filtro de Kalman |
| --- | --- | --- |
| Error de rumbo en régimen, giro continuo, desde 5 segundos | 1,55 grados de error cuadrático medio | 1,50 grados {caution:Casi igual} |
| Error de rumbo en régimen, oscilación sin giro neto | 1,60 grados | 1,55 grados |
| Error de sesgo a los 2 segundos, ruido blanco | 0,53 grados por segundo | 0,16 grados por segundo {good:Aprende antes} |
| Error de sesgo a los 2 segundos, error magnético nominal | 0,42 grados por segundo | 1,82 grados por segundo {bad:Se sobrerreacciona} |
| Magnetómetro corrido 20 grados durante 3 segundos | 24,66 grados de error máximo | 20,91 grados; 1,87 con compuerta {good:Rechaza la lectura} |
| Error de calibración del magnetómetro | No lo corrige | No lo corrige {bad:Sigue igual} |
| Cómo se ajusta | Dos números elegidos a mano | Sale del ruido medido de cada sensor |
| Cálculo en el ESP32 | Dos líneas por muestra | Unas decenas de operaciones más, con matrices de 2 por 2 |

La compuerta rechaza la corrección cuando la diferencia supera 3 veces la que el filtro espera. Un complementario también puede tener compuerta, pero con un umbral fijo elegido a mano. El de Kalman sale de su propia duda.[](source:kalman)

@chart type=line data=perturbacion.csv x=Tiempo y="Filtro complementario actual,Filtro de Kalman,Filtro de Kalman con compuerta" unit="grados" title="Error de rumbo cuando un motor corre el magnetómetro 20 grados entre 20 y 23 segundos (eje horizontal: tiempo en segundos)"

@callout level=warning title="El error de calibración no se puede filtrar"
Un desfase fijo del magnetómetro se ve igual que un rumbo distinto: ningún filtro lo distingue con estos dos sensores.
En régimen, el filtro de Kalman cree que su error es de 0,06 grados, pero el real es de 1,5 grados de error cuadrático medio.
Esa diferencia es el residuo de calibración e inclinación, que no es ruido. Por eso la calibración sigue siendo la ruta crítica.[](source:riesgo)

## ¿Qué hay que medir para usarlo? {#siguientes-pasos}

- [ ] Registrar el giróscopo quieto a 100 muestras por segundo y medir su ruido por muestra; hoy se suponen 0,1 grados por segundo.[](source:tst002)
- [ ] Registrar varios minutos quieto y medir cuánto se mueve el sesgo, para fijar su deriva; hoy se suponen 0,01 grados por segundo por raíz de segundo.
- [ ] Medir el ruido del rumbo magnético con el brazo desplegado; hoy se suponen 0,9 grados por muestra.
- [ ] Calibrar el magnetómetro en tres dimensiones con el servo, la batería y el brazo en su sitio, y guardar las constantes en el firmware.
- [ ] Decidir cómo tratar el error de inclinación que oscila: más duda del magnetómetro al arrancar, o un estado más en el filtro.
- [ ] Programar el filtro en el ESP32 y compararlo con el complementario y con la fusión interna del BNO055, con el codificador del motor como referencia.
