---
type: concepto
status: borrador
id: sensores-giroscopio-magnetometro
tags: [concepto, sensores, giroscopio, magnetometro, rumbo, estabilizacion]
created: 2026-10-25
source: [raw/mision/cansat-mission-guide-2027-r1.1.pdf, raw/pruebas/tst-001-1-giroscopio-giro.png, raw/pruebas/tst-001-2-magnetometro-giro.png, raw/datos/notion-hardware-2026-10-25.md, raw/LINKS.md]
requisitos: []
---

# Giróscopo y magnetómetro: qué miden y por qué los necesitamos

> [!NOTE]
> Nota de aprendizaje, construida paso a paso con el líder de control a partir de la pregunta «¿qué necesito saber de la caja, en cada instante, para que el suelo no rote en el video?». Los experimentos están en [TST-001](../Pruebas/tst-001-exploracion-sensores-celular.md). La parte 4 es la caracterización rigurosa del avance; el modelo en espacio de estados está en [Control](../Control/modelo-rumbo-espacio-estados.md).

**El problema en una frase:** para que el suelo no rote más de ±10° en el video (C8, p. 9) y la vista gire 90° por comando (C11, p. 9; PQ17 y PQ18, p. 14), hay que conocer en todo momento el **rumbo** (heading) de la cámara: hacia dónde mira, en grados desde el norte.

## 1. Cómo funcionan

### Giróscopo (gyroscope)

- **D1.** Mide la **velocidad angular** ω, es decir, qué tan rápido gira algo, en rad/s o en °/s, en tres ejes. 1 rad/s ≈ 57,3 °/s.
- **D2.** No mide el ángulo. Para obtenerlo hay que **integrar** (ir sumando) la velocidad desde un ángulo inicial θ₀ que el giróscopo no conoce:

$$
\theta(t) = \theta_0 + \int_0^t \omega\,d\tau
$$

- **P1.** Un error constante del sensor (sesgo, bias) b crece con el tiempo al integrarlo:

$$
\Delta\theta(t) = b\,t
$$

  Por ejemplo, 0,01 rad/s durante los 120 s del descenso dan 1,2 rad, unos 69° (cálculo ilustrativo).
- **Ventajas:** responde rápido y no le afectan los imanes. **Desventajas:** deriva con el tiempo y no sabe dónde está el norte.
- **En el experimento:** el giróscopo solo «habla» mientras hay giro (TST-001·M1) y en reposo queda en ≈ 0 con un ruido de ≈ ±0,003 rad/s (TST-001·M2).

![Giróscopo durante el giro: solo cambia mientras gira](../raw/pruebas/tst-001-1-giroscopio-giro.png)

### Magnetómetro (magnetometer)

- **D3.** Mide el **campo magnético** B en tres ejes, en µT. La guía lo pide en miligauss: 1 G = 100 µT y 1 mG = 0,1 µT.
- **D4.** El campo de la Tierra apunta hacia el norte magnético y, en el hemisferio norte, también hacia abajo. Con el sensor nivelado y los ejes de la guía (X este, Y sur, Z nadir, p. 25), el rumbo magnético sale de las dos componentes horizontales. El rumbo verdadero se obtiene sumando la declinación D:

$$
\psi_m = \operatorname{atan2}(-B_x,\,-B_y),\qquad \psi = \psi_m + D
$$

  Esta fórmula es una derivación propia; si el sensor está inclinado, primero hay que «enderezar» la medida con la inclinación (siguiente paso: el acelerómetro).
- **Ventajas:** da una referencia **absoluta** (el norte). **Desventajas:** mide **todos** los campos cercanos: el del propio aparato (hierro duro y blando, hard iron y soft iron), motores, servos, la carcasa de acero de la batería y el edificio.
- **En el experimento:** los valores cambian con la orientación y se quedan en el valor nuevo (TST-001·M3). También aparecieron un campo que gira con el celular (TST-001·A1) y lecturas muy distintas según el entorno (TST-001·A2).

![Magnetómetro durante el giro: X e Y cambian y se quedan](../raw/pruebas/tst-001-2-magnetometro-giro.png)

### Por qué necesitamos los dos

| | Giróscopo | Magnetómetro |
|---|---|---|
| Qué mide | velocidad de giro | dirección del campo magnético |
| Unidad | rad/s o °/s | µT o mG |
| ¿Sabe dónde está el norte? | no | sí |
| Rapidez | alta, sin retardo | menor; hay que filtrar el ruido |
| Lo que lo engaña | su sesgo, que se acumula al integrar | imanes, motores, batería, metales |
| Papel en el lazo | movimientos rápidos (lazo interno) | referencia absoluta (lazo externo) |

- **S1.** El PocketQube va apagado dentro del contenedor y se enciende al soltarse, en el aire (PQ21, p. 14). Al encenderse, el giróscopo no sabe hacia dónde está el norte; solo el magnetómetro puede decirlo. A corto plazo, en cambio, el giróscopo es más confiable.
- **Siguiente paso:** combinar los dos (fusión de sensores).

### Sensores elegidos por el equipo

Según la base «Hardware» de Notion (copia en [notion-hardware-2026-10-25.md](../raw/datos/notion-hardware-2026-10-25.md)):

- **BNO055** (IMU, seleccionado): «9 ejes con fusión interna a 100 Hz», y advierte: «su magnetómetro interno sufrirá con un actuador cercano».
- **LIS3MDL** (magnetómetro del brazo, seleccionado): «0.146 mG por LSB en ±4 G: cumple PQ30», y «En la punta del boom queda lejos del ruido magnético de servos y batería».
- **Turbowing Cyclops 3 V3** (cámara, seleccionada): «El video no pasa por el MCU, así que la estabilización (C8) y el giro de 90° (C11) deben ser mecánicos.»

> [!WARNING]
> **Sin fuente en raw/** — Según la página del producto de ST ([L-05](../raw/LINKS.md), vista solo en un resumen del buscador), el LIS3MDL figura como NRND (no recomendado para diseños nuevos) u obsoleto, con el LIS2MDL como reemplazo. **Pendiente:** confirmar su disponibilidad antes del PDR.

## 2. Bogotá, Medellín y Virginia

Valores del modelo magnético mundial WMM2025 ([L-01](../raw/LINKS.md)), calculados con [campo-geomagnetico.py](../sim/campo-geomagnetico.py) y guardados en [campo-geomagnetico.csv](../derivados/campo-geomagnetico.csv). Las coordenadas son el centro de cada ciudad (supuesto).

| Sitio | Fecha | Campo total | Horizontal | Vertical | Inclinación I | Declinación D | tan I | Error de rumbo por 1° de inclinación | Perturbación que causa 1° de rumbo |
|---|---|---|---|---|---|---|---|---|---|
| Bogotá | 2026-10-25 | 29,9 µT | 26,8 µT | 13,3 µT | 26,5° | −8,8° | 0,50 | 0,50° | 4,7 mG |
| Medellín | 2026-10-25 | 30,8 µT | 26,9 µT | 15,1 µT | 29,3° | −8,0° | 0,56 | 0,56° | 4,7 mG |
| Monterey, Virginia | 2027-06-12 | 50,2 µT | 21,4 µT | 45,4 µT | 64,7° | −9,2° | 2,12 | 2,12° | 3,7 mG |

> [!WARNING]
> **Sin fuente en raw/** — El sitio de lanzamiento (Monterey, Virginia) viene de un anuncio de West Virginia Space Grant ([L-03](../raw/LINKS.md)) que no se pudo abrir; la guía no lo dice. Hay que confirmarlo con la organización.

Qué cambia entre los sitios:

1. **En Colombia el campo es casi horizontal; en Virginia, casi vertical.** La inclinación es de unos 27–29° en Colombia frente a 65° en Virginia.
2. **En Virginia, la «señal del norte» es más débil.** La componente horizontal baja de ≈ 27 µT a ≈ 21 µT, así que la misma perturbación magnética produce más error de rumbo: basta 3,7 mG para 1°, frente a 4,7 mG en Colombia.
3. **Un error de inclinación pesa unas 4 veces más en Virginia.** El error de rumbo crece con tan I: 0,50 en Bogotá frente a 2,12 en Virginia. Una prueba que sale bien en Bogotá o en Medellín **no garantiza** lo mismo en Virginia; hay que simular o corregir ese factor.
4. **La declinación se parece** (entre −8° y −9°), pero en vuelo se usa la de Virginia: −9,2°.
5. **El giróscopo casi no cambia entre sitios.** La rotación de la Tierra (7,3 × 10⁻⁵ rad/s, ≈ 0,004 °/s) queda muy por debajo del ruido observado (≈ ±0,17 °/s, TST-001·M2). Lo que sí lo afecta es la temperatura (la prueba térmica es a 60 °C, M10).

## 3. Las leyes físicas y lo que pide la guía

### Giróscopo MEMS: efecto Coriolis

- **P2.** Dentro del chip, una masa diminuta vibra con velocidad $\vec v$. Si el chip gira con velocidad angular $\vec\Omega$, aparece la fuerza de Coriolis, perpendicular a la vibración y proporcional al giro. El chip la detecta como un cambio de capacitancia ([L-04](../raw/LINKS.md)):

$$
\vec F_C = -2\,m\,\vec\Omega \times \vec v
$$

  Es la misma fuerza que desvía una pelota lanzada sobre un carrusel.
- **P3.** Lo que entrega es Ω, una velocidad. El ángulo exige integrar (D2), y por eso aparece la deriva (P1).

### Magnetómetro: el campo de la Tierra y cómo se mide

- **P4.** En cada lugar, el campo de la Tierra se describe con su intensidad total F, la inclinación I y la declinación D (modelo WMM, [L-01](../raw/LINKS.md)):

$$
H = F\cos I,\qquad Z = F\sin I,\qquad \tan I = \frac{Z}{H}
$$

- **P5.** Principios de medición más comunes. Cuál usa cada chip es **Pendiente** de confirmar en su hoja de datos.
  - **Efecto Hall:** la fuerza de Lorentz desvía las cargas que circulan por una lámina de espesor t y aparece un voltaje transversal:

$$
\vec F = q\,\vec v \times \vec B,\qquad V_H = \frac{I\,B}{n\,q\,t}
$$

  - **Magnetorresistencia anisótropa:** la resistencia de ciertos materiales cambia con el ángulo θ entre la corriente y la magnetización, $R(\theta) = R_0 + \Delta R\,\cos^2\theta$.
  - **Fluxgate:** un núcleo se satura de forma alternada y el campo externo descompensa esa saturación; se mide por inducción (ley de Faraday, $\varepsilon = -\,d\Phi_B/dt$).
- **P6.** Un imán cercano se comporta como un dipolo y su campo cae con la distancia al cubo:

$$
B \propto \frac{1}{r^3}
$$

  Llevar el magnetómetro de 3 cm a 22 cm reduce esa interferencia unas 400 veces. Por eso la guía lo pone en la punta de un brazo.
- **P7.** Si la inclinación estimada tiene un error δ sobre el eje norte–sur, la componente vertical del campo «se filtra» en el rumbo:

$$
\Delta\psi \approx \arctan\big(\tan I\,\sin\delta\big)
$$

### Lo que pide la guía (texto oficial)

| ID | Texto oficial | Página | Qué implica |
|---|---|---|---|
| PQ28 | «The PocketQube shall measure the rotation rate in the X,Y,Z axis in degrees/sec to 0.1 degree/sec resolution.» | p. 15 | giróscopo de 3 ejes, reportado en °/s con resolución de 0,1 °/s |
| PQ30 | «The PocketQube shall measure earth’s magnetic field in the X,Y,Z axis in milli Gauss to 1 milli Gauss resolution.» | p. 15 | magnetómetro de 3 ejes, en mG con resolución de 1 mG |
| Telemetría | «Calibrated magnetometer values in milliGauss at 1 mGauss (Requirement PQ30)» | p. 26 | los valores deben ir **calibrados** |
| PQ9 | «The PocketQube shall include a boom with a magnetometer mounted on the end.» | p. 13 | magnetómetro en la punta del brazo |
| PQ10 | «The boom shall extend 220 mm from the nadir edge of the PocketQube when commanded by the ground station.» | pp. 13–14 | 220 mm de distancia: menos interferencia (P6) |
| Ejes | «The following satellite industry standard definition of the Roll, Pitch, and Yaw axes shall be used for telemetry data and must be considered when mounting and aligning inertial measurement units.» | p. 25 | los ejes del IMU y del magnetómetro se montan alineados con X (este), Y (sur) y Z (nadir) |
| PQ21 | «The PocketQube shall be powered off while in the container.» | p. 14 | no se puede calibrar el sesgo en tierra justo antes del vuelo (S1) |
| C8 | «The PocketQube shall record video in the nadir direction with less than +/- 10 degrees rotation in the video.» | p. 9 | error de rumbo de la imagen < 10° |
| C11 | «The PocketQube shall rotate the video along the nadir axis at the specified angle on command.» | p. 9 | giro controlado por comando |
| PQ15 | «The video of the ground shall be stabilized so the ground does not rotate during the flight.» | p. 14 | estabilizar todo el vuelo |
| PQ17 | «The video camera orientation shall be controlled by an uplink command.» | p. 14 | orientación de la cámara controlada desde tierra |
| PQ18 | «The camera orientation command shall control the angle change in degrees.» | p. 14 | el comando lleva el ángulo en grados |

Además, la estación terrena debe graficar la orientación del PocketQube en tres ejes a partir de los sensores (GS4, p. 18).

## 4. Caracterización de los sensores (avance)

> [!NOTE]
> Para cada sensor: ley física, sensibilidad, modelo de medición y cuánto error de rumbo deja cada fuente. Los números salen de [caracterizacion-sensores.py](../sim/caracterizacion-sensores.py) ([CSV](../derivados/caracterizacion-sensores.csv)). Cada valor dice de dónde viene: **en raw/**, **no validado** (fuente en `raw/LINKS.md` sin abrir el original) o **Pendiente**. Cómo entran los sensores al modelo (matrices C y observabilidad): [modelo del lazo de rumbo](../Control/modelo-rumbo-espacio-estados.md).

> [!WARNING]
> **Sin fuente en raw/** — las hojas de datos oficiales del BNO055 ([L-08](../raw/LINKS.md)) y del LIS3MDL ([L-09](../raw/LINKS.md)) no se pudieron abrir: la red del entorno bloquea esos dominios. Los valores de los fabricantes que aparecen aquí salen de foros y fichas comerciales (L-10 a L-15) y hay que confirmarlos. **Pendiente:** subir los dos PDF a `raw/inbox/` (quedarán como DS-01 y DS-02).

### La cadena de medición

Magnitud física → transductor (masa vibrante, lámina Hall…) → señal eléctrica → conversor analógico-digital (ADC) → cuentas (LSB) → unidades de ingeniería.

- **D5. Sensibilidad** S: cuánto cambia la salida por unidad de entrada, $S=\partial y/\partial x$. En un sensor digital se da en LSB por unidad física.
- **D6. Resolución** q: el cambio más pequeño que se distingue. En un sensor digital, $q = 1\,\mathrm{LSB} = 1/S$. Redondear a q agrega un ruido de cuantización de $q/\sqrt{12}$ rms.
- **D7. Rango** (full scale): la mayor entrada que se mide sin saturar.
- **D8. Sesgo** (bias u offset): la salida cuando la entrada es cero. Importan su estabilidad en el tiempo (bias instability) y su deriva con la temperatura.
- **D9. Ruido:** su densidad espectral (en unidades por √Hz) o su valor rms en un ancho de banda dado.
- **D10. Factor de escala y desalineación** (scale factor, misalignment): el error relativo de S y el acople entre ejes por montaje.
- **D11. Ancho de banda y frecuencia de salida** (output data rate, ODR): qué tan rápido sigue el sensor a la magnitud y cada cuánto entrega un dato.

### Giróscopo MEMS: de Coriolis a grados por segundo

- **P8. Ley física con su sensibilidad** (complemento de literatura, [L-04](../raw/LINKS.md)). Una masa $m$ se excita en el eje x: $x(t)=X_0\sin(\omega_d t)$. Si el chip gira a Ω alrededor de z, la fuerza de Coriolis (P2) empuja la masa en el eje y, el eje de detección, que es un oscilador con frecuencia propia $\omega_s=\sqrt{k/m}$ y factor de calidad $Q=m\omega_s/c$:

$$
m\,\ddot y + c\,\dot y + k\,y = -2\,m\,\Omega\,\dot x = -2\,m\,\Omega\,X_0\,\omega_d\cos(\omega_d t)
$$

$$
Y_0=\frac{2\,\Omega\,X_0\,\omega_d}{\sqrt{(\omega_s^2-\omega_d^2)^2+(\omega_d\,\omega_s/Q)^2}}
\qquad\Longrightarrow\qquad
S_{mec}=\frac{Y_0}{\Omega}=\frac{2\,X_0\,\omega_d}{\sqrt{(\omega_s^2-\omega_d^2)^2+(\omega_d\,\omega_s/Q)^2}}
$$

  La amplitud de detección es **proporcional a Ω**: esa es la ley de transducción. La sensibilidad crece con la amplitud de excitación $X_0$ y es máxima cuando las dos frecuencias coinciden ($\omega_d=\omega_s$, $S_{mec}=2X_0Q/\omega_s$). El desplazamiento se lee como cambio de capacitancia entre placas separadas $g_0$, $\Delta C\approx\varepsilon_0 A\,y/g_0^2$, y luego el ADC lo convierte en cuentas.
- **Sensibilidad digital del BNO055:** 16 LSB por °/s, es decir, q = 0,0625 °/s (**no validado**, [L-10](../raw/LINKS.md); el mismo hilo reporta un error de escala en el firmware). Cumple la resolución de 0,1 °/s de PQ28.
- **Modelo de medición** (eje Z):

$$
y_g=(1+s_g)\,\omega_z+m_{zx}\,\omega_x+m_{zy}\,\omega_y+b_g(t,T)+n_g
$$

  con $s_g$ el error de factor de escala, $m_{zx}$ y $m_{zy}$ la desalineación, $b_g$ el sesgo (depende del tiempo y de la temperatura T) y $n_g$ ruido blanco de densidad N.
- **P9. Del error de velocidad al error de rumbo.** Al integrar, el sesgo crece con el tiempo, el factor de escala con el ángulo girado y el ruido como una caminata aleatoria (angle random walk):

$$
\delta\psi(t)=b_g\,t+s_g\,\Delta\psi+\int_0^t n_g\,d\tau,\qquad \sigma_\psi(t)\approx N\sqrt{t}
$$

| Parámetro del giróscopo (BNO055) | Valor | Estado |
|---|---|---|
| Sensibilidad digital | 16 LSB por °/s (0,0625 °/s por LSB) | no validado (L-10) |
| Ruido de cuantización | 0,018 °/s rms | calculado con el valor anterior |
| Densidad de ruido N | 0,014 °/s/√Hz | no validado y de otra pieza, el BMI055 (L-14) |
| Desfase en reposo | ±1 °/s típico | no validado y de otra pieza, el BMI088 (L-15) |
| Rango, ancho de banda, deriva térmica | — | **Pendiente** (L-08) |

Qué significa para el rumbo ([CSV](../derivados/caracterizacion-sensores.csv)):

| Fuente de error del giróscopo | 30 s (comando de giro) | 120 s | 180 s |
|---|---|---|---|
| Sesgo de 1 °/s sin corregir | 30° | 120° | 180° |
| Sesgo residual de 0,1 °/s (supuesto, tras calibrar) | 3° | 12° | 18° |
| Sesgo residual de 0,01 °/s (supuesto) | 0,3° | 1,2° | 1,8° |
| Caminata aleatoria con N = 0,014 °/s/√Hz | 0,08° | 0,15° | 0,19° |

- Con 1 °/s de sesgo, el rumbo integrado pasa los 10° de C8 a los **10 s**; con 0,1 °/s, a los 100 s. El descenso dura 2–3 min según la base «Hardware».
- Un error de escala del 1 % (supuesto) en el giro de 90° de C11 deja 0,9°.
- La caminata aleatoria es despreciable frente al sesgo. Según la convención de densidad puede haber un factor √2, que no cambia la conclusión.

### Magnetómetro: del campo terrestre a miligauss

- **P10. Efecto Hall con su sensibilidad.** En una lámina de espesor t con densidad de portadores n y corriente I (P5): $V_H = IB/(nqt)$, así que $S_H=\partial V_H/\partial B=I/(nqt)$ en V/T. Más corriente, una lámina más delgada o menos portadores (un semiconductor en vez de un metal) dan más sensibilidad.
- **P11. Magnetorresistencia anisótropa con su sensibilidad.** $R(\theta)=R_0+\Delta R\cos^2\theta$; cerca del punto de trabajo, $dR/d\theta=-\Delta R\sin 2\theta$. Por eso se polariza a 45°, donde la pendiente es máxima, y se mide con un puente de Wheatstone; la sensibilidad se expresa en mV/V por unidad de campo.
- Qué principio usa cada chip: **Pendiente** (L-08, L-09).
- **Sensibilidad digital del LIS3MDL:** 6842 LSB por gauss en ±4 G, es decir, q = 0,146 mG (en raw/datos, la base «Hardware»; también en [L-12](../raw/LINKS.md), no validado). Cumple PQ30 (1 mG).
- **Modelo de medición en 3D:**

$$
\mathbf y_m=W\,R_{nb}^T\,\mathbf m_n+\mathbf h+\mathbf n_m
$$

  $\mathbf m_n$ es el campo de la Tierra (WMM), $R_{nb}$ la actitud del PocketQube, $W$ (3×3) junta el hierro blando, el factor de escala y la desalineación, $\mathbf h$ el hierro duro y el desfase, y $\mathbf n_m$ el ruido.
- **D12. Calibración.** Hallar $W$ y $\mathbf h$ para que el vector corregido $\hat{\mathbf m}_b=W^{-1}(\mathbf y_m-\mathbf h)$ tenga la misma magnitud F en cualquier orientación. Sin calibrar, las medidas caen sobre un elipsoide desplazado; calibradas, sobre una esfera de radio F (ajuste de elipsoide). **Criterio de verificación:** $|\hat{\mathbf m}_b|\approx F$, que vale 299 mG en Bogotá, 308 mG en Medellín y 502 mG en Monterey. La telemetría debe ir calibrada (p. 26).
- **P12. Rumbo nivelado en los ejes de la guía.** Con el sensor horizontal, $\mathbf m_b=[-H\sin\psi_m,\ -H\cos\psi_m,\ Z]^T$, de donde sale D4: $\psi_m=\operatorname{atan2}(-m_x,\,-m_y)$. Con inclinación, primero se lleva el vector a la horizontal con el alabeo y el cabeceo que da el acelerómetro.
- **P13. Del ruido del campo al ruido del rumbo.** Con $u=H\sin\psi$ y $v=H\cos\psi$, $\delta\psi=(\cos\psi\,\delta u-\sin\psi\,\delta v)/H$. Si los dos ejes horizontales tienen el mismo ruido $\sigma_B$, independiente:

$$
\sigma_\psi=\frac{\sigma_B}{H}\ \text{(rad)},\qquad \sigma_{\psi,q}=\frac{q}{\sqrt{12}\,H},\qquad \Delta\psi_{hierro}=\arctan\frac{\delta h_\perp}{H},\qquad \Delta\psi_{incl}=\arctan(\tan I\,\sin\delta)
$$

  El error **no depende del rumbo**, pero sí del sitio, a través de H y de I.

| Parámetro | LIS3MDL (en el brazo) | Magnetómetro interno del BNO055 |
|---|---|---|
| Resolución | 0,146 mG (en raw/datos) | ≈ 3 mG, es decir, ≈ 0,3 µT (no validado, [L-11](../raw/LINKS.md)) |
| ¿Cumple PQ30 (1 mG)? | sí | **no**, si se confirma su resolución |
| Ruido | 3,2 mG rms en X e Y; 4,1 mG en Z (no validado, [L-13](../raw/LINKS.md); depende del modo) | **Pendiente** |
| Rango | ±4 G en la configuración de la base «Hardware» | ±1300 µT en X e Y; ±2500 µT en Z (no validado, L-11) |
| Frecuencia de salida, deriva térmica, principio | **Pendiente** (L-09) | **Pendiente** (L-08) |

### Cuánto error de rumbo deja cada fuente, sitio por sitio

| Fuente de error | Bogotá | Medellín | Monterey (Virginia) |
|---|---|---|---|
| Campo horizontal H | 268 mG | 269 mG | 214 mG |
| Campo total esperado tras calibrar | 299 mG | 308 mG | 502 mG |
| Ruido del LIS3MDL, por muestra (3,2 mG, no validado) | 0,69° rms | 0,68° rms | 0,86° rms |
| Cuantización del LIS3MDL | 0,009° rms | 0,009° rms | 0,011° rms |
| Cuantización de la telemetría a 1 mG (PQ30) | 0,06° rms | 0,06° rms | 0,08° rms |
| Perturbación perpendicular a H que da 1°, 5° y 10° | 4,7 / 23,4 / 47,2 mG | 4,7 / 23,5 / 47,4 mG | 3,7 / 18,7 / 37,8 mG |
| Inclinación sin compensar de 1°, 2°, 5° y 10° | 0,50 / 1,00 / 2,48 / 4,94° | 0,56 / 1,12 / 2,80 / 5,56° | 2,12 / 4,23 / 10,46 / 20,19° |
| **Inclinación sin compensar que agota los 10°** | 20,75° | 18,32° | **4,78°** |
| Rotación de la Tierra integrada en 180 s | 0,06° | 0,08° | 0,47° |

El brazo de 220 mm (PQ10) reduce unas 394 veces la interferencia de un imán que, sin brazo, estaría a 30 mm (supuesto ilustrativo), por la ley $1/r^3$ (P6).

### Conclusiones de la caracterización

1. **El giróscopo solo no alcanza.** Con 1 °/s de sesgo rompe C8 en 10 s, y con 0,1 °/s en 100 s. Se necesita la referencia absoluta del magnetómetro, y el [modelo](../Control/modelo-rumbo-espacio-estados.md) lo confirma: sin magnetómetro el rumbo no es observable.
2. **PQ30 lo cumple el LIS3MDL, no el BNO055.** Si se confirma la resolución de ≈ 3 mG del magnetómetro interno del BNO055, MAG_X, MAG_Y y MAG_Z deben salir del LIS3MDL.
3. **La inclinación es la fuente dominante en Virginia.** Allí bastan 4,8° de inclinación sin compensar para agotar los 10°; en Bogotá harían falta 20,8°. **Compensar la inclinación con el acelerómetro es obligatorio**, y una prueba en Colombia subestima este error unas 4 veces.
4. **Calibrar con el brazo desplegado.** En Monterey, 38 mG de perturbación residual perpendicular a H agotan los 10°. La verificación es $|\hat{\mathbf m}_b|\approx$ 502 mG allá y ≈ 299 mG en Bogotá.
5. **El ruido del magnetómetro (≈ 0,86° rms por muestra, no validado) se filtra con la fusión;** no se usa la lectura cruda.
6. **Despreciables frente a C8:** la cuantización (≤ 0,08°), la caminata aleatoria del giróscopo (≤ 0,19° en 180 s) y la rotación de la Tierra (≤ 0,47° en 180 s).

## Preguntas para el siguiente paso

1. Cuando el PocketQube se balancea bajo el paracaídas, ¿cómo sabe hacia dónde es «abajo»? Pista: el acelerómetro.
2. ¿Cómo se combinan un sensor rápido que deriva y uno lento que no deriva? Pista: el filtro complementario.
