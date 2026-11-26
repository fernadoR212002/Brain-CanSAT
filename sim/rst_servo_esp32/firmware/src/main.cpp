// Firmware de E/S para sim/rst_servo_esp32/rst_servo_vivo.m
//
// El ESP32 solo hace entrada y salida; el control lo calcula MATLAB:
//   1. Cada 10 ms (100 Hz) lee el giróscopo y el magnetómetro del BNO055 y manda una línea:
//        t_ms,gz_dps,mx_uT,my_uT,mz_uT,cal_sys,cal_gir,cal_mag,pulso_us
//   2. Recibe de MATLAB el ancho de pulso del servo, una línea por orden:  P1500
//      y lo saca por PIN_SERVO a 50 Hz (LEDC de 16 bits, paso de 0,3 µs).
//
// Conexiones:
//   BNO055  SDA -> GPIO 21,  SCL -> GPIO 22,  VIN -> 3V3,  GND -> GND   (dirección I2C 0x29)
//   SG90    naranja (señal) -> GPIO 18,  rojo (+) -> 5 V de una fuente aparte,
//           café (-) -> GND de la fuente Y GND del ESP32.  El BNO055, a 10 cm o más del SG90.
//
// Si deja de llegar orden, el servo se queda en el último pulso. Al arrancar va al centro (1500 µs).
//
// Calibración: cuando el BNO055 llega a cal_mag = 3, el firmware guarda sus offsets en la memoria
// del ESP32 (NVS) y los vuelve a cargar en cada arranque. Basta calibrar (mover en ochos) una vez.

#include <Arduino.h>
#include <Wire.h>
#include <Preferences.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>

// ---------------------------------------------------------------- configuración
const int      PIN_SERVO    = 18;      // señal del servo
const uint32_t F_SERVO      = 50;      // Hz, trama del servo
const uint8_t  BITS_PWM     = 16;      // resolución del ciclo útil
const int      PULSO_MIN    = 600;     // µs, tope inferior (0,6 ms)
const int      PULSO_MAX    = 2400;    // µs, tope superior (2,4 ms)
const int      PULSO_CENTRO = 1500;    // µs
const uint32_t PERIODO_US   = 10000;   // 100 Hz, el T del RST

// NDOF: el BNO055 calibra solo el magnetómetro (mover el montaje hasta cal_mag = 3).
// Se leen el giróscopo y el magnetómetro; la fusión del BNO055 no se usa.
// Para datos crudos sin calibración interna: OPERATION_MODE_AMG.
const adafruit_bno055_opmode_t MODO_BNO = OPERATION_MODE_NDOF;

Adafruit_BNO055 bno(55, 0x29, &Wire);
Preferences nvs;
bool cal_guardada = false;   // ya se guardó en este arranque

const int CANAL_LEDC = 0;   // solo lo usa el núcleo 2.x
uint32_t t_sig = 0;
int pulso_us = PULSO_CENTRO;
uint8_t cal_sys = 0, cal_gir = 0, cal_acel = 0, cal_mag = 0;
uint32_t n_muestra = 0;
char orden[16];
uint8_t n_orden = 0;

// ---------------------------------------------------------------- PWM del servo
void pwmIniciar() {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcAttach(PIN_SERVO, F_SERVO, BITS_PWM);
#else
  ledcSetup(CANAL_LEDC, F_SERVO, BITS_PWM);
  ledcAttachPin(PIN_SERVO, CANAL_LEDC);
#endif
}

void pwmPulso(int us) {
  us = constrain(us, PULSO_MIN, PULSO_MAX);
  pulso_us = us;
  // ciclo útil = pulso / periodo; periodo = 1e6/F_SERVO µs
  uint32_t cuentas = (uint32_t)((uint64_t)us * (1UL << BITS_PWM) * F_SERVO / 1000000UL);
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(PIN_SERVO, cuentas);
#else
  ledcWrite(CANAL_LEDC, cuentas);
#endif
}

// ---------------------------------------------------------------- órdenes de MATLAB ("P1500\n")
void leerOrdenes() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      orden[n_orden] = '\0';
      if (n_orden > 1 && orden[0] == 'P') pwmPulso(atoi(orden + 1));
      n_orden = 0;
    } else if (n_orden < sizeof(orden) - 1) {
      orden[n_orden++] = c;
    } else {
      n_orden = 0;   // línea demasiado larga: se descarta
    }
  }
}

// ---------------------------------------------------------------- arranque
void setup() {
  Serial.begin(921600);
  pwmIniciar();
  pwmPulso(PULSO_CENTRO);

  if (!bno.begin(MODO_BNO)) {
    while (true) {
      Serial.println("# Error: no se detecta el BNO055 en 0x29. Revisa SDA=21, SCL=22, 3V3 y GND.");
      delay(1000);
    }
  }
  delay(100);
  bno.setExtCrystalUse(true);

  // calibración guardada en un arranque anterior
  nvs.begin("bno055", false);
  adafruit_bno055_offsets_t off;
  if (nvs.getBytesLength("off") == sizeof(off)) {
    nvs.getBytes("off", &off, sizeof(off));
    bno.setSensorOffsets(off);
    Serial.println("# calibración del BNO055 cargada de la memoria del ESP32");
  } else {
    Serial.println("# sin calibración guardada: mueve el montaje en ochos hasta cal. mag 3/3");
  }
  Serial.println("# rst_servo_esp32 listo: t_ms,gz_dps,mx_uT,my_uT,mz_uT,cal_sys,cal_gir,cal_mag,pulso_us");
  t_sig = micros();
}

// ---------------------------------------------------------------- lazo de 100 Hz
void loop() {
  leerOrdenes();
  uint32_t ahora = micros();
  if ((int32_t)(ahora - t_sig) < 0) return;
  t_sig += PERIODO_US;
  if ((int32_t)(ahora - t_sig) > (int32_t)PERIODO_US) t_sig = ahora + PERIODO_US;   // se atrasó: resincroniza

  imu::Vector<3> g = bno.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);     // °/s
  imu::Vector<3> m = bno.getVector(Adafruit_BNO055::VECTOR_MAGNETOMETER);  // µT
  if (n_muestra % 10 == 0) bno.getCalibration(&cal_sys, &cal_gir, &cal_acel, &cal_mag);   // a 10 Hz
  n_muestra++;

  // primera vez en este arranque que el magnetómetro queda calibrado: guardar (≈ 50 ms, una vez)
  if (cal_mag == 3 && !cal_guardada) {
    adafruit_bno055_offsets_t off;
    bno.getSensorOffsets(off);
    nvs.putBytes("off", &off, sizeof(off));
    cal_guardada = true;
    Serial.println("# calibración del magnetómetro guardada en el ESP32");
    t_sig = micros() + PERIODO_US;
    return;
  }

  Serial.printf("%lu,%.4f,%.3f,%.3f,%.3f,%u,%u,%u,%d\n",
                (unsigned long)millis(), g.z(), m.x(), m.y(), m.z(),
                cal_sys, cal_gir, cal_mag, pulso_us);
}
