#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

// Prueba de orientación del BNO055 (modo de fusión NDOF, por defecto).
// Trama por el puerto serie, una línea por muestra:
//   t_ms,yaw,roll,pitch,cal_sys,cal_gir,cal_acel,cal_mag
// Ángulos en grados. Cada estado de calibración va de 0 (sin calibrar) a 3 (calibrado).

// Inicializar el sensor BNO055
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x29, &Wire);

const uint32_t PERIODO_MS = 50;  // 20 Hz (cada 50 ms)
uint32_t t_siguiente = 0;

void setup(void) {
  Serial.begin(115200);

  // Intentar conectar con el sensor (modo NDOF: fusión de los 9 ejes)
  if (!bno.begin()) {
    Serial.println("Error: No se detectó el BNO055. Revisa las conexiones I2C.");
    while (1); // Detener ejecución si falla
  }
  delay(1000);
  bno.setExtCrystalUse(true); // Usar cristal externo para mayor precisión

  t_siguiente = millis();
}

void loop(void) {
  // Muestreo a periodo fijo (no se acumula el retraso del envío)
  if ((int32_t)(millis() - t_siguiente) < 0) return;
  t_siguiente += PERIODO_MS;

  // Leer evento de orientación (Ángulos de Euler)
  sensors_event_t event;
  bno.getEvent(&event);

  // Estado de calibración del BNO055 (0 a 3 cada uno)
  uint8_t cal_sys, cal_gir, cal_acel, cal_mag;
  bno.getCalibration(&cal_sys, &cal_gir, &cal_acel, &cal_mag);

  // Enviar datos en formato: t_ms,Yaw,Roll,Pitch,cal_sys,cal_gir,cal_acel,cal_mag
  Serial.print(millis());
  Serial.print(",");
  Serial.print(event.orientation.x, 2);
  Serial.print(",");
  Serial.print(event.orientation.y, 2);
  Serial.print(",");
  Serial.print(event.orientation.z, 2);
  Serial.print(",");
  Serial.print(cal_sys);
  Serial.print(",");
  Serial.print(cal_gir);
  Serial.print(",");
  Serial.print(cal_acel);
  Serial.print(",");
  Serial.println(cal_mag);
}
