# Guía de calibración del BNO055

Esta guía prepara el siguiente paso: escribir los códigos que calibran el giróscopo, el acelerómetro y el magnetómetro del BNO055 con la ESP32 y MATLAB.

Usa los tres proyectos que ya funcionan:

| Proyecto | Modo del BNO055 | Trama | Script de MATLAB |
|---|---|---|---|
| `Prueba_MATLAB` | NDOF (fusión) | `t_ms,yaw,roll,pitch,cal_sys,cal_gir,cal_acel,cal_mag` | `Codigos/Orientacion.m` |
| `Prueba_Acelerometro` | AMG (crudo) | `t_ms,ax,ay,az` (m/s²) | `Codigos/Acelerometro.m` |
| `Prueba_Magnetometro` | AMG (crudo) | `t_ms,mx,my,mz` (µT) | `Codigos/Magnetometro.m` |

> [!WARNING]
> Los valores de registros, modos y rangos de esta guía son los que usa la librería de Adafruit y el conocimiento general del chip. La hoja de datos oficial del BNO055 (L-08 en el brain) todavía no está en `raw/`: confírmalos con ella antes de cerrar la calibración.

## 1. Por qué hay que calibrar

Cada sensor tiene errores propios que se corrigen con un modelo simple:

| Sensor | Error principal | Modelo de corrección | Qué se ve sin calibrar |
|---|---|---|---|
| Giróscopo | sesgo (bias) $b_g$ | $\omega = \omega_{med} - b_g$ | con el sensor quieto no da 0 °/s; el ángulo integrado deriva |
| Acelerómetro | sesgo $b_a$ y factor de escala $s$ por eje | $a = (a_{med} - b_a)\,/\,s$ | quieto, $\lvert a\rvert$ no da 9,81 m/s² en todas las poses |
| Magnetómetro | hierro duro $b_m$ (desfase) y hierro blando $A$ (deformación) | $m = A\,(m_{med} - b_m)$ | al girar plano, el círculo $m_x$–$m_y$ está corrido o es una elipse; el rumbo sale mal |

- **Hierro duro (hard iron):** imanes y piezas magnetizadas que se mueven con el sensor (servo, batería, tornillos). Suman un vector fijo.
- **Hierro blando (soft iron):** metal que deforma el campo según la orientación. Convierte la esfera de datos en un elipsoide.

## 2. La calibración interna del BNO055 (modo NDOF)

En los modos de fusión (como NDOF, el de `Prueba_MATLAB`) el BNO055 se calibra solo mientras lo mueves. El estado de cada parte sale en la trama: **0 = sin calibrar, 3 = calibrado**.

### Cómo llevar cada uno a 3

Mira la gráfica de abajo de `Orientacion.m` mientras haces esto:

1. **Giróscopo:** deja el sensor **quieto** sobre la mesa unos segundos. Suele llegar a 3 enseguida.
2. **Magnetómetro:** mueve el sensor en el aire **dibujando un ocho**, girándolo en todas las direcciones, unos 20–30 s. Hazlo lejos de metal, del computador, de motores y de imanes.
3. **Acelerómetro:** el más lento. Pon el sensor en **6 poses quietas**, unos 3–5 s cada una: cada eje (X, Y, Z) apuntando hacia arriba y luego hacia abajo, como las caras de un dado. Muévelo despacio entre poses. Ayuda pasar también por algunas poses inclinadas a 45°.
4. **Sistema:** llega a 3 cuando los otros están calibrados, sobre todo el magnetómetro.

### Lo importante: la calibración se pierde al apagar

- El BNO055 **no guarda** la calibración: al quitarle la energía vuelve a 0.
- La solución es leer los **offsets** cuando todo está en 3 y guardarlos en la ESP32. En cada arranque se le vuelven a escribir al sensor.
- Son 22 bytes, en los registros `0x55` a `0x6A`: desfases del acelerómetro, del magnetómetro y del giróscopo, más el radio del acelerómetro y el del magnetómetro.
- Con la librería de Adafruit:
  - `bno.isFullyCalibrated()`: indica si los cuatro estados están en 3.
  - `bno.getSensorOffsets(adafruit_bno055_offsets_t &offsets)`: los lee.
  - `bno.setSensorOffsets(const adafruit_bno055_offsets_t &offsets)`: los escribe. Solo se pueden escribir en modo de configuración; la librería cambia de modo por ti.
- En la ESP32 se guardan en la memoria no volátil con `Preferences` (no hace falta una EEPROM externa).
- Aun con los offsets cargados, el magnetómetro pide un poco de movimiento al arrancar para volver a 3. Es normal.

> [!IMPORTANT]
> En el PocketQube el sensor arranca apagado y se suelta en vuelo (PQ21 en la guía de misión): **no habrá tiempo de dibujar ochos**. Para la competencia hay que cargar offsets guardados desde el arranque, calibrados con el montaje final.

## 3. Calibración propia con los datos crudos (modo AMG)

Los proyectos `Prueba_Acelerometro` y `Prueba_Magnetometro` usan el modo AMG: sin fusión y sin calibración automática. Con sus CSV se calcula la calibración en MATLAB y se aplica en la ESP32. Así se sabe exactamente qué se corrige, y el mismo método sirve después para el LIS3MDL del brazo.

### 3.1 Giróscopo: sesgo

- **Ensayo:** sensor quieto sobre una mesa firme, al menos 60 s (mejor 5 min), sin tocarlo.
- **Cálculo:** $b_g = \overline{\omega_{med}}$ (la media de cada eje). La desviación estándar es el ruido.
- **Falta:** un proyecto `Prueba_Giroscopo` (modo AMG, trama `t_ms,gx,gy,gz` en °/s) y su `Giroscopo.m`. Es el primer código del siguiente paso.

### 3.2 Acelerómetro: método de las 6 poses

- **Ensayo:** con `Prueba_Acelerometro`, pon el sensor en las 6 poses del dado (+X, −X, +Y, −Y, +Z, −Z hacia arriba), 10 s quieto en cada una. Usa una caja o un bloque con caras a escuadra para que las poses sean exactas.
- **Cálculo por eje:** con $a_+$ la lectura media con el eje hacia arriba y $a_-$ hacia abajo, y $g = 9{,}81$ m/s²:

$$
b_a = \frac{a_+ + a_-}{2}, \qquad s = \frac{a_+ - a_-}{2\,g}
$$

- **Mejor (opcional):** ajustar una elipsoide a todas las poses imponiendo $\lvert a\rvert = g$. Corrige también la desalineación entre ejes.
- **Validación:** después de corregir, $\lvert a\rvert$ debe dar 9,81 m/s² en las 6 poses y en poses inclinadas.

### 3.3 Magnetómetro: ajuste de elipsoide

- **Ensayo:** con `Prueba_Magnetometro`, gira el sensor **despacio en todas las direcciones** durante 60–90 s, para que los puntos cubran la esfera completa (no solo el círculo horizontal). Hazlo en el sitio y con el montaje que se vaya a usar.
- **Cálculo:**
  - **Rápido (solo hierro duro):** $b_m = (\max + \min)/2$ por eje. `Magnetometro.m` ya lo imprime.
  - **Completo (duro + blando):** ajuste de elipsoide por mínimos cuadrados, $m = A\,(m_{med} - b_m)$, con $A$ una matriz de 3×3.
    - Si tienes el *Sensor Fusion and Tracking Toolbox* o el *Navigation Toolbox*, `[A, b, campo] = magcal(datos)` lo hace directo.
    - Si no, se programa el ajuste con álgebra lineal básica (sin toolbox).
- **Validación:**
  - después de corregir, la nube de puntos debe ser una **esfera centrada en el origen**;
  - $\lvert B\rvert$ debe ser casi constante, con poca desviación, en cualquier orientación;
  - $\lvert B\rvert$ debe parecerse al campo del modelo WMM2025 (calculado en el brain, `derivados/campo-geomagnetico.csv`):

| Sitio | Campo total | Horizontal | Vertical | Inclinación | Declinación |
|---|---|---|---|---|---|
| Bogotá | 29,9 µT | 26,8 µT | 13,3 µT | 26,5° | −8,8° |
| Medellín | 30,8 µT | 26,9 µT | 15,1 µT | 29,3° | −8,0° |
| Monterey, Virginia (lanzamiento) | 50,2 µT | 21,4 µT | 45,4 µT | 64,7° | −9,2° |

> [!NOTE]
> Dentro de un edificio el campo puede diferir unos µT del modelo por el hierro de la estructura. Si la magnitud calibrada difiere mucho, prueba otra mesa o sal al aire libre.

> [!CAUTION]
> La calibración del magnetómetro **solo vale para el montaje con que se hizo**. Si se mueve el servo, la batería o los cables, o se despliega el brazo, hay que repetirla. La definitiva se hace con el sensor en su posición final del PocketQube.

## 4. Cómo se aplica la calibración en la ESP32

- **Calibración interna (NDOF):** guardar los 22 bytes de offsets en `Preferences` y cargarlos con `setSensorOffsets()` en cada `setup()`.
- **Calibración propia (AMG):** copiar los números de MATLAB ($b_g$, $b_a$, $s$, $b_m$, $A$) como constantes en el firmware y corregir cada lectura antes de enviarla o usarla:

```cpp
// Ejemplo de la forma que tendrá (valores de ejemplo, no medidos)
const float B_MAG[3]    = {0.0f, 0.0f, 0.0f};   // µT, hierro duro
const float A_MAG[3][3] = {{1,0,0},{0,1,0},{0,0,1}}; // hierro blando
// m_cal = A_MAG * (m_med - B_MAG)
```

## 5. Consejos para todos los ensayos

- Deja el sensor encendido 2–3 minutos antes de medir, para que se estabilice la temperatura.
- Mesa firme, lejos del computador, de celulares, de motores y de piezas de acero.
- Anota en una bitácora: fecha y hora, lugar, montaje (qué había cerca) y el nombre del CSV que guardó MATLAB.
- Guarda todos los CSV: en el brain van por `raw/inbox/` como evidencia (es el ensayo E3 de TST-002).

## 6. Plan de códigos para el siguiente paso

| # | Código | Qué hace |
|---|---|---|
| 1 | `Prueba_Giroscopo` (PlatformIO) + `Giroscopo.m` | lee el giróscopo crudo (modo AMG) y guarda el CSV, igual que los otros dos |
| 2 | `Calibracion_BNO055` (PlatformIO) | modo NDOF: muestra el estado de calibración; al llegar a 3, imprime los 22 offsets y los guarda en `Preferences`; en el arranque los restaura |
| 3 | `Calibracion_Giroscopo.m` | lee el CSV quieto y calcula el sesgo y el ruido de cada eje |
| 4 | `Calibracion_Acelerometro.m` | guía las 6 poses en vivo (te dice cuándo girar), o lee el CSV, y calcula $b_a$ y $s$ |
| 5 | `Calibracion_Magnetometro.m` | lee el CSV, ajusta la elipsoide (con `magcal` o sin toolbox), grafica antes y después y compara $\lvert B\rvert$ con el WMM |
| 6 | `Prueba_Calibrada` (PlatformIO) | aplica las constantes de 3 a 5 a los datos crudos y envía los valores corregidos, para validar |

Para empezar el siguiente paso, ten a mano:

1. un CSV de `Acelerometro.m` con las 6 poses;
2. un CSV de `Magnetometro.m` girando en todas las direcciones;
3. si tienes los toolboxes de MATLAB *Sensor Fusion and Tracking* o *Navigation* (para usar `magcal`).
