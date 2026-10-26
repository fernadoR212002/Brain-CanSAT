---
type: modelo
status: borrador
id: modelo-rumbo-espacio-estados
tags: [control, modelo, espacio-de-estados, rumbo, camara, servomotor, giroscopio, magnetometro, discretizacion]
created: 2026-10-25
source: [raw/mision/cansat-mission-guide-2027-r1.1.pdf, raw/datos/notion-hardware-2026-10-25.md, raw/LINKS.md]
requisitos: []
---

# Modelo del lazo de rumbo en espacio de estados

> [!NOTE]
> Modelo del avance de control. Cada matriz, función de transferencia, rango y límite de esta nota está comprobado con álgebra simbólica (sympy) en [modelo-rumbo.py](../sim/modelo-rumbo.py), cuya salida se guarda en [modelo-rumbo.txt](../derivados/modelo-rumbo.txt). Los resultados valen para cualquier valor positivo de los parámetros: todavía no se ha medido ninguno. La caracterización de los sensores está en [sensores-giroscopio-magnetometro](../Conceptos/sensores-giroscopio-magnetometro.md) y el ejemplo de seguimiento de un modelo de referencia, en [L-07](../Conceptos/l-07-servomotor-self-tuning.md).

## 1. Qué se modela

El objetivo es que el suelo no rote más de ±10° en el video (C8, p. 9; PQ15, p. 14) y que la vista gire el ángulo que mande la estación terrena (C11, p. 9; PQ17 y PQ18, p. 14). La variable a controlar es el **rumbo de la cámara** (camera heading).

- **D1. Ejes.** Los de la guía (p. 25): +X al este, +Y al sur y +Z al nadir. La cámara apunta al nadir y su referencia es el norte, es decir, −Y. Con +Z hacia abajo, un giro positivo alrededor de +Z va en sentido horario visto desde arriba, el mismo sentido en que crece el rumbo (de norte a este).
- **D2. Ángulos.** $\psi_b$ es el rumbo del cuerpo del PocketQube, $\theta_g$ el ángulo del servo de la cámara medido respecto al cuerpo, $\psi_c$ el rumbo de la cámara y $\psi_{ref}$ el rumbo pedido. Todos en rad.

$$
\psi_c = \psi_b + \theta_g
$$

- **C1. C8 como desigualdad** (interpretación propia): $|\psi_c(t)-\psi_{ref}(t)| < 10°$ durante todo el vuelo. C11 agrega un escalón de $\psi_{ref}$ de 90° en el sentido que indique el juez, a los 30 s de vuelo (p. 6).

## 2. Hipótesis

- **S1.** El cuerpo y la cámara son sólidos rígidos.
- **S2.** Solo se modela el giro alrededor de Z. El balanceo bajo el paracaídas, que inclina el eje Z, se deja para el nivel N3; su efecto sobre el magnetómetro está cuantificado en la caracterización (en Virginia, 4,8° de inclinación sin compensar bastan para agotar los 10°).
- **S3.** La cámara gira alrededor de Z, movida por un servomotor de corriente continua con reductora de relación N (decisión del líder: estabilizar con servomotores). **Pendiente** — la decisión del actuador (futuro DEC): servo de hobby comandado por PWM o motor DC con codificador, y si además se gira el cuerpo.
- **S4.** La inercia de la cámara es mucho menor que la del cuerpo ($J_c \ll J_b$), así que el par de reacción del motor sobre el cuerpo se desprecia.
- **S5.** Fricción viscosa lineal.
- **S6.** Entre el paracaídas y el cuerpo puede haber un destorcedor (swivel, $k_r = 0$) o una rigidez torsional de las cuerdas ($k_r > 0$). **Pendiente** — se analizan los dos casos.
- **S7.** Los sensores van en el cuerpo, como en la base «Hardware» ([copia en raw/datos](../raw/datos/notion-hardware-2026-10-25.md)): el BNO055 en la tarjeta y el LIS3MDL en la punta del brazo.
- **S8.** La dinámica eléctrica del motor es mucho más rápida que la mecánica ($L_a/R_a \ll \tau_c$). Se verifica cuando se midan los parámetros.

## 3. Ecuaciones físicas

**P1. Cuerpo (ecuación de Euler alrededor de Z).** Par aerodinámico y del paracaídas $\tau_d$, amortiguamiento $b_b$ y rigidez torsional $k_r$:

$$
J_b\,\ddot\psi_b = -\,b_b\,\dot\psi_b - k_r\,\psi_b + \tau_d
$$

**P2. Cámara sobre una base que gira (Newton–Euler).** La inercia responde a la aceleración **absoluta** $\ddot\psi_c = \ddot\psi_b + \ddot\theta_g$. La fricción del rodamiento y la fuerza contraelectromotriz dependen de la velocidad **relativa** $\dot\theta_g$, porque el rodamiento y el estator del motor van montados en el cuerpo:

$$
J_c\,(\ddot\psi_b + \ddot\theta_g) = N\,k_t\,i_a - B_v\,\dot\theta_g
$$

**P3. Armadura (ley de voltajes de Kirchhoff con fuerza contraelectromotriz).** El rotor gira N veces más rápido que la cámara:

$$
L_a\,\frac{di_a}{dt} = u - R_a\,i_a - N\,k_v\,\dot\theta_g
$$

| Símbolo | Qué es | Unidad |
|---|---|---|
| $J_b$, $J_c$ | inercia del cuerpo y de la cámara (con el rotor reflejado) alrededor de Z | kg·m² |
| $b_b$, $B_v$ | amortiguamiento del cuerpo (aire, paracaídas) y del rodamiento de la cámara | N·m·s/rad |
| $k_r$ | rigidez torsional de las cuerdas del paracaídas | N·m/rad |
| $k_t$, $k_v$ | constante de par y de fuerza contraelectromotriz del motor | N·m/A, V·s/rad |
| $R_a$, $L_a$ | resistencia e inductancia de armadura | Ω, H |
| $N$ | relación de la reductora | — |
| $u$ | voltaje de armadura (promedio del PWM): **la entrada de control** | V |
| $\tau_d$ | par de perturbación sobre el cuerpo | N·m |

## 4. Matrices A, B, C, D

Forma general: $\dot x = A x + B u + E d$, $y = C x + D u + v$, con $d$ las perturbaciones y $v$ el ruido de los sensores.

### Cuerpo solo (nivel N0)

Con $x = [\psi_b,\ \omega_b]^T$ y un par de control $\tau_u$ sobre el cuerpo (si la decisión del actuador incluye girar todo el PocketQube):

$$
A_b=\begin{bmatrix}0&1\\-\dfrac{k_r}{J_b}&-\dfrac{b_b}{J_b}\end{bmatrix},\quad
B_b=E_b=\begin{bmatrix}0\\ \dfrac{1}{J_b}\end{bmatrix},\quad
C_{mag}=\begin{bmatrix}1&0\end{bmatrix},\quad
C_{gir}=\begin{bmatrix}0&1\end{bmatrix},\quad D=0
$$

$$
\frac{\Psi_b(s)}{T_u(s)} = \frac{1}{J_b s^2 + b_b s + k_r}
$$

- **Controlabilidad:** $\operatorname{rango}[B_b\ \ A_bB_b] = 2$. Si hay par sobre el cuerpo, su rumbo se puede llevar a cualquier valor.
- **Observabilidad:** con destorcedor ($k_r=0$), el giróscopo solo da rango 1: **el rumbo no es observable** y solo se conoce su derivada. Con el magnetómetro el rango es 2. Con $k_r>0$ el giróscopo daría rango 2, pero a través de $k_r$ y $J_b$, que no se conocen.
- Sin fricción ni rigidez es el doble integrador $1/(J_b s^2)$. Su discretización con ZOH tiene un cero en $z=-1$, el mismo del ejemplo RST del curso.

### Cámara sobre el servomotor (3 estados)

Con $x = [\theta_g,\ \omega_g,\ i_a]^T$ y la aceleración del cuerpo $w = \ddot\psi_b$ como entrada exógena:

$$
A_c=\begin{bmatrix}0&1&0\\0&-\dfrac{B_v}{J_c}&\dfrac{N k_t}{J_c}\\0&-\dfrac{N k_v}{L_a}&-\dfrac{R_a}{L_a}\end{bmatrix},\quad
B_c=\begin{bmatrix}0\\0\\ \dfrac{1}{L_a}\end{bmatrix},\quad
E_c=\begin{bmatrix}0\\-1\\0\end{bmatrix},\quad
C_c=\begin{bmatrix}1&0&0\end{bmatrix},\quad D_c=0
$$

$$
\frac{\Theta_g(s)}{U(s)}=\frac{N k_t}{s\left[(J_c s+B_v)(L_a s+R_a)+N^2 k_t k_v\right]},\qquad
\frac{\Theta_g(s)}{W(s)}=\frac{-J_c\,(L_a s+R_a)}{s\left[(J_c s+B_v)(L_a s+R_a)+N^2 k_t k_v\right]}
$$

- Controlabilidad: rango 3 de 3. Observabilidad con codificador ($\theta_g$ medido): rango 3 de 3.
- **P4. Transmisión pasiva del giro del cuerpo** (motor sin voltaje, $u=0$):

$$
\frac{\Psi_c(s)}{\Psi_b(s)}=\frac{B_v(L_a s+R_a)+N^2 k_t k_v}{(J_c s+B_v)(L_a s+R_a)+N^2 k_t k_v}
$$

  Vale 1 en $s=0$ y tiende a 0 en alta frecuencia. La inercia de la cámara filtra sola los giros rápidos del cuerpo, pero un giro lento o constante se transmite completo: **el control tiene que trabajar sobre todo en baja frecuencia**.

### Modelo reducido ($L_a \to 0$)

Con S8, la función de transferencia tiende a

$$
\frac{\Theta_g(s)}{U(s)}=\frac{K_c}{s(\tau_c s+1)},\qquad
K_c=\frac{N k_t}{B_v R_a+N^2 k_t k_v},\qquad
\tau_c=\frac{J_c R_a}{B_v R_a+N^2 k_t k_v}
$$

y con $x=[\theta_g,\ \omega_g]^T$:

$$
A_r=\begin{bmatrix}0&1\\0&-\dfrac{1}{\tau_c}\end{bmatrix},\quad
B_r=\begin{bmatrix}0\\ \dfrac{K_c}{\tau_c}\end{bmatrix},\quad
E_r=\begin{bmatrix}0\\-1\end{bmatrix},\quad
C_r=\begin{bmatrix}1&0\end{bmatrix},\quad D_r=0
$$

Con $N=1$, $K_c$ y $\tau_c$ son exactamente las ecuaciones (7) y (8) del ejemplo del curso, y $A_r$, $B_r$ son su diagrama de Simulink (figura 3 de [L-07](../Conceptos/l-07-servomotor-self-tuning.md)). **La planta de nuestra cámara tiene la misma estructura que la del ejemplo**, más la perturbación del cuerpo.

### Modelo completo con sensores (6 estados)

$x=[\psi_b,\ \omega_b,\ \theta_g,\ \omega_g,\ i_a,\ b_g]^T$, donde $b_g$ es el sesgo del giróscopo ($\dot b_g = w_b$, caminata aleatoria). Perturbaciones $d=[\tau_d,\ w_b]^T$; medidas $y=[y_g,\ y_\psi,\ y_\theta]^T$: giróscopo Z, rumbo del magnetómetro (ya calibrado y compensado en inclinación) y codificador del servo.

$$
A=\begin{bmatrix}
0&1&0&0&0&0\\
-\dfrac{k_r}{J_b}&-\dfrac{b_b}{J_b}&0&0&0&0\\
0&0&0&1&0&0\\
\dfrac{k_r}{J_b}&\dfrac{b_b}{J_b}&0&-\dfrac{B_v}{J_c}&\dfrac{N k_t}{J_c}&0\\
0&0&0&-\dfrac{N k_v}{L_a}&-\dfrac{R_a}{L_a}&0\\
0&0&0&0&0&0
\end{bmatrix},\qquad
B=\begin{bmatrix}0\\0\\0\\0\\ \dfrac{1}{L_a}\\0\end{bmatrix},\qquad
E=\begin{bmatrix}0&0\\ \dfrac{1}{J_b}&0\\0&0\\-\dfrac{1}{J_b}&0\\0&0\\0&1\end{bmatrix}
$$

$$
C=\begin{bmatrix}0&1&0&0&0&1\\1&0&0&0&0&0\\0&0&1&0&0&0\end{bmatrix},\qquad D=\begin{bmatrix}0\\0\\0\end{bmatrix},\qquad
z=\psi_c=\begin{bmatrix}1&0&1&0&0&0\end{bmatrix}x
$$

La cuarta fila de A sale de despejar $\ddot\theta_g$ en P2 y reemplazar $\ddot\psi_b$ con P1. D es cero porque ningún sensor responde al voltaje en el mismo instante.

| Sensores disponibles | Rango de observabilidad | Qué queda sin observar |
|---|---|---|
| giróscopo + magnetómetro + codificador | 6 de 6 | nada |
| giróscopo + magnetómetro | 3 de 6 | el estado de la cámara ($\theta_g$, $\omega_g$, $i_a$) |
| giróscopo + codificador, con destorcedor | 5 de 6 | el rumbo del cuerpo $\psi_b$ |

- **Controlabilidad desde u: rango 3 de 6.** El servo no gobierna el cuerpo ni el sesgo; para la cámara, el giro del cuerpo es una **perturbación que hay que medir o estimar y restar**.
- **Consecuencia 1.** Con un servo de hobby sin acceso a su potenciómetro, $\theta_g$ no se observa desde el cuerpo: la cámara queda en lazo abierto respecto a $\theta_g$ y todo depende del lazo interno del servo.
- **Consecuencia 2.** Sin magnetómetro, el rumbo del cuerpo no se observa (con destorcedor). Es la prueba formal de lo que se vio en [TST-001](../Pruebas/tst-001-exploracion-sensores-celular.md).

### Estimador de rumbo (fusión de sensores)

Si el giróscopo se trata como entrada y no como medida, con $x_e=[\psi_b,\ b_g]^T$, $u_e=y_g$ y la medida $y_\psi$:

$$
\dot x_e=\begin{bmatrix}0&-1\\0&0\end{bmatrix}x_e+\begin{bmatrix}1\\0\end{bmatrix}y_g,\qquad
y_\psi=\begin{bmatrix}1&0\end{bmatrix}x_e,\qquad D_e=0
$$

- El rango de observabilidad es 2: con el magnetómetro se estiman a la vez el rumbo **y el sesgo del giróscopo**.
- Un observador con ganancias $l_1$ y $l_2$ resulta ser un **filtro complementario** (complementary filter): el magnetómetro entra por un pasabajos y el giróscopo por un pasaaltos, y los dos filtros suman 1.

$$
\hat\Psi=\frac{l_1 s+l_2}{s^2+l_1 s+l_2}\,Y_\psi+\frac{s}{s^2+l_1 s+l_2}\,Y_g
$$

- Con un sesgo constante $b$, el error final es 0 si el sesgo es un estado. Sin ese estado (filtro de primer orden) el error final es $b/l_1$.

## 5. Discretización con ZOH

El lazo corre a 100 Hz (T = 0,01 s, el mismo periodo del ejemplo del curso), según la base «Hardware» («lazos de control a 100 Hz» y «fusión interna a 100 Hz»). Para el modelo reducido, con $p=e^{-T/\tau_c}$:

$$
\Phi=e^{A_rT}=\begin{bmatrix}1&\tau_c(1-p)\\0&p\end{bmatrix},\qquad
\Gamma=\int_0^T e^{A_r\sigma}B_r\,d\sigma=K_c\begin{bmatrix}T-\tau_c(1-p)\\1-p\end{bmatrix}
$$

$$
G(z)=\frac{b_1 z+b_0}{(z-1)(z-p)},\qquad b_1=K_c\big(T-\tau_c(1-p)\big),\qquad b_0=K_c\big(\tau_c(1-p)-Tp\big)
$$

**P5. Cero de muestreo.** Con $h=T/\tau_c$:

$$
z_0=-\frac{b_0}{b_1}=\frac{h-e^{h}+1}{h\,e^{h}-e^{h}+1}\;\xrightarrow[h\to 0]{}\;-1,\qquad z_0\approx -1+\frac{h}{3}
$$

La planta continua no tiene ceros, pero la discreta sí, y muestreando rápido el cero queda pegado a −1. Si un controlador lo cancela, su modo $(z_0)^k$ cambia de signo en cada muestra y tarda unas $3\tau_c$ en caer a $1/e$ ([tabla](../derivados/modelo-rumbo-cero-de-muestreo.csv)):

| $\tau_c$ | $z_0$ con T = 0,01 s | el modo cancelado cae a 1/e en |
|---|---|---|
| 0,05 s | −0,936 | 0,15 s |
| 0,1 s | −0,967 | 0,3 s |
| 0,2 s | −0,984 | 0,6 s |
| 0,5 s | −0,993 | 1,5 s |
| 1 s | −0,997 | 3 s |

**Implicación de diseño** (interpretación propia, verificada en [L-07](../Conceptos/l-07-servomotor-self-tuning.md)): con nuestro periodo de muestreo **el cero no se cancela**. Va en $B^-$ y el modelo de referencia lo incluye, como en el ejemplo del doble integrador del curso.

## 6. Giro constante del cuerpo

Para la cámara, el rumbo del cuerpo es una perturbación que se suma a la salida: $\Psi_c=\frac{BT}{AR+BS}\Psi_{ref}+\frac{AR}{AR+BS}\Psi_b$. Si el cuerpo gira a velocidad constante Ω (una rampa), con el RST del ejemplo, que cancela el cero y no tiene integrador, el error final es

$$
e_{ss}=\frac{(1-p)\,T\,\Omega}{A_m(1)}\;\approx\;\frac{\Omega}{\tau_c\,\omega_n^2}
$$

($\omega_n$: frecuencia natural del modelo de referencia). Con acción integral ($R(1)=0$) el error final es cero. El giro del cuerpo que basta para agotar los 10° sin acción integral ([tabla](../derivados/modelo-rumbo-giro-maximo.csv), con ξ = 0,7):

| $\tau_c$ | $\omega_n$ = 5 rad/s | 10 rad/s | 20 rad/s | 65 rad/s (el del ejemplo) |
|---|---|---|---|---|
| 0,1 s | 25,4 °/s | 98,0 °/s | 365,4 °/s | 2815,2 °/s |
| 0,5 s | 121,9 °/s | 470,9 °/s | 1756,0 °/s | 13 529,3 °/s |

Como la batería limita el voltaje, nuestro modelo de referencia será más lento que el del ejemplo. **Con un modelo lento, un giro moderado del cuerpo ya rompe C8**: hace falta acción integral o compensar con el giróscopo (prealimentación). **Pendiente** — la velocidad de giro del PocketQube bajo el paracaídas no se conoce; hay que medirla.

## 7. Pendientes

> [!WARNING]
> **Pendiente**
> 1. Identificar $J_c$, $B_v$, $k_t$, $k_v$, $R_a$, $L_a$, $N$ (o directamente $K_c$ y $\tau_c$) con una prueba del servo, y $J_b$, $b_b$, $k_r$ con una caída desde dron.
> 2. La decisión del actuador: tipo de servo y si también se gira el cuerpo. Y dónde va el IMU: en el cuerpo (como hoy) o en la cámara.
> 3. N3: balanceo bajo el paracaídas, que acopla la inclinación con el rumbo.
> 4. Requisitos de control (RC) del lazo de rumbo, cuando se carguen los RQ.

## Cómo se reproduce

```bash
python3 sim/modelo-rumbo.py   # escribe derivados/modelo-rumbo.txt y las dos tablas CSV
```
