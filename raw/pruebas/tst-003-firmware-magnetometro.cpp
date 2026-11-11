#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

// Prueba del magnetómetro del BNO055 (datos crudos, sin fusión).
// Trama por el puerto serie, una línea por muestra:
//   t_ms,mx,my,mz        (campo magnético en µT, sin calibrar)

// Inicializar el sensor BNO055 (misma dirección que la prueba de orientación)
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x29, &Wire);

const uint32_t PERIODO_MS = 50;  // 20 Hz (cada 50 ms)
uint32_t t_siguiente = 0;

void setup(void) {
  Serial.begin(115200);

  // Modo AMG: sensores crudos, sin fusión. El campo sale sin la calibración
  // automática del BNO055, así que se ve el hierro duro y el entorno tal cual.
  if (!bno.begin(OPERATION_MODE_AMG)) {
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

  // Leer campo magnético en µT
  imu::Vector<3> mag = bno.getVector(Adafruit_BNO055::VECTOR_MAGNETOMETER);

  // Enviar datos en formato: t_ms,mx,my,mz
  Serial.print(millis());
  Serial.print(",");
  Serial.print(mag.x(), 2);
  Serial.print(",");
  Serial.print(mag.y(), 2);
  Serial.print(",");
  Serial.println(mag.z(), 2);
}
