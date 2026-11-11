#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

// Prueba del acelerómetro del BNO055 (datos crudos, sin fusión).
// Trama por el puerto serie, una línea por muestra:
//   t_ms,ax,ay,az        (aceleración en m/s², incluye la gravedad)

// Inicializar el sensor BNO055 (misma dirección que la prueba de orientación)
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x29, &Wire);

const uint32_t PERIODO_MS = 50;  // 20 Hz (cada 50 ms)
uint32_t t_siguiente = 0;

void setup(void) {
  Serial.begin(115200);

  // Modo AMG: acelerómetro, magnetómetro y giróscopo crudos, sin fusión.
  // Así se ve lo que mide el acelerómetro tal cual, sin filtrado interno.
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

  // Leer aceleración en m/s² (con la gravedad incluida)
  imu::Vector<3> acc = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);

  // Enviar datos en formato: t_ms,ax,ay,az
  Serial.print(millis());
  Serial.print(",");
  Serial.print(acc.x(), 3);
  Serial.print(",");
  Serial.print(acc.y(), 3);
  Serial.print(",");
  Serial.println(acc.z(), 3);
}
