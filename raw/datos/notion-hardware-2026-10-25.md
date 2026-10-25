# Copia de la base «🔧 Hardware» de Notion

- **Fuente:** base de datos «🔧 Hardware» de la página Plan de desarrollo / School / CANSAT, en Notion: https://app.notion.com/p/7b8ef90e7b744d1cb708c075ca58fab7
- **Leída por:** Claude, con el conector de Notion en modo solo lectura, el 2026-10-25T18:59Z (UTC), a pedido del líder de control.
- **Contenido:** copia literal de las 31 filas (texto tal cual, con punto decimal como en el original). Solo se ordenaron por función y estado.

| Componente | Función | Estado | Masa (g) | Precio (USD) | Notas |
|---|---|---|---|---|---|
| ESP32-S3 DevKit N16R8 (antena IPEX) | Microcontrolador | Seleccionado | 10 | 32 | Doble núcleo a 240 MHz, 512 KB de SRAM y 8 MB de PSRAM; ESP-NOW (X1) con antena externa. Sobra para lazos de control a 100 Hz y redes pequeñas. Se necesitan 2 (contenedor y PocketQube) + 1 para la estación terrena. Verificar el regulador de la placa si se alimenta directo de la 18650. |
| Teensy 4.1 | Microcontrolador | Alternativa | 15 | 32 | Cortex-M7 a 600 MHz con SD integrada, pero sin ESP-NOW: incumple X1. |
| ESP32-WROOM-32U | Microcontrolador | Alternativa | 15 | 10 | ESP-NOW y conector U.FL a menor costo; menos memoria y sin las instrucciones vectoriales para redes neuronales del S3. |
| BNO055 (Bosch) | IMU | Seleccionado | 3 | 25 | 9 ejes con fusión interna a 100 Hz: resuelve la orientación de GS4 y alimenta el lazo de la cámara. Ojo: la aceleración sale escalada a 0.01 m/s² (1 m/s² = 100 LSB), no los 0.001 m/s² de PQ29; su magnetómetro interno sufrirá con un actuador cercano, y su I2C da problemas con ESP32-S3 (usar ESP-IDF ≥ 5.3.2 o modo UART). |
| BMI270 | IMU | Alternativa | 1.5 | 10 | 6 ejes, 0.85 mA y aceleración de 16 bits (cumple los 0.001 m/s² de PQ29), sin magnetómetro ni fusión interna. Buen complemento si se exige PQ29. |
| MPU-6050 | IMU | Alternativa | 2 | 5 | 6 ejes, sin magnetómetro; diseño antiguo con muchos clones en el mercado. |
| LIS3MDL (STMicroelectronics) | Magnetómetro (boom) | Seleccionado | 1 | 6 | 0.146 mG por LSB en ±4 G: cumple PQ30. En la punta del boom queda lejos del ruido magnético de servos y batería: mejor referencia de rumbo una vez desplegado. Con 220 mm de cable, preferir SPI o I2C a baja velocidad. |
| QMC5883L | Magnetómetro (boom) | Alternativa | 1 | 3 | El más barato (~0.24 mG), solo I2C. |
| MMC5983MA | Magnetómetro (boom) | Alternativa | 1 | 12 | 18 bits (~0.06 mG), la mejor resolución, con más consumo (~1 mA). |
| Turbowing Cyclops 3 V3 | Cámara | Seleccionado | 4.5 | 25 | 720p a 30 fps con DVR propio en microSD: cumple PQ14. El video no pasa por el MCU, así que la estabilización (C8) y el giro de 90° (C11) deben ser mecánicos. La grabación se activa con un botón: habría que emularlo con un GPIO para PQ16 y C7. Algunas fichas del V3 dan operación hasta 50 °C (la prueba térmica es a 60 °C). |
| ESP32-CAM | Cámara | Alternativa | 10 | 8 | El video pasa por un ESP32, lo que permitiría rotarlo por software, pero su capacidad de grabar video fluido es limitada. |
| EYESEC X6D | Cámara | Alternativa | 60.5 | 20 | 1080p, pero 60.5 g y app cerrada: demasiado pesada. |
| BMP390 | Barómetro y temperatura | Seleccionado | 2 | 10 | Precisión relativa de ±3 Pa (≈ ±0.25 m), ruido de 0.02 Pa y hasta 200 Hz: cumple CTR18–20 y PQ24–25. Base del filtro de altitud y de la detección de apogeo y del 90 %. Se necesitan 2. Su temperatura es interna, no la del aire exterior. |
| DPS310 | Barómetro y temperatura | Alternativa | 2 | 8 | Resolución ~0.2 Pa; también cumple 1 Pa y es el más barato. |
| BMP581 | Barómetro y temperatura | Alternativa | 2 | 15 | Resolución ~0.015 Pa, pero precisión relativa de ±6 Pa frente a ±3 Pa del BMP390: la elección del BMP390 es correcta. |
| SAM-M10Q (u-blox) | GNSS | Seleccionado | 10 | 35 | 4 constelaciones y antena integrada, ~12 mA: cumple PQ34. Ojo: el PocketQube va apagado hasta la liberación, así que arranca en frío (≈ 24 s o más sin posición) dentro de un descenso de 2–3 min. La antena debe mirar al cielo. |
| NEO-M9N (u-blox) | GNSS | Alternativa | 15 | 45 | Necesita antena activa externa: más masa y ~36 mA. |
| NEO-6M (u-blox) | GNSS | Alternativa | 20 | 10 | Solo GPS y el mayor consumo (~45 mA). |
| Celda Li-ion 18650 "4000 mAh" | Batería | Seleccionado | 45 | 12 | Química permitida (E2). Ojo: las 18650 reales llegan a ≈ 3500–3600 mAh, así que una de "4000 mAh" a USD 8–12 casi seguro está sobreetiquetada. Mejor una celda verificable como la Vapcell M35. Se necesitan 2. |
| Vapcell M35 18650 | Batería | Alternativa | 48 | 5.27 | Celda de marca con capacidad creíble (3500 mAh, 12.95 Wh). Recomendada en lugar de la de "4000 mAh". |
| SureFire SR123A (CR123A) | Batería | Alternativa | 22 | 5.48 | Primaria (no recargable), 4.65 Wh y 22 g: opción liviana para el contenedor. |
| DS3231 | RTC | Seleccionado | 4 | 4 | Oscilador compensado (±2 ppm) con pila de respaldo: mantiene la hora de misión tras reinicios (F2–F3). En el módulo ZS-042, retirar el circuito de carga si se usa una CR2032. Se necesitan 2. |
| DS1307 | RTC | Alternativa | 4 | 2 | Deriva con la temperatura y pide 4.5–5.5 V. |
| PCF8523 | RTC | Alternativa | 2.5 | 5 | Precisión media; opera desde 1 V. |
| Buzzer piezo activo de alto dB | Beacon sonoro | Seleccionado | 2 | 1 | Cambiar el cableado: la guía pide que el beacon suene al energizar y no dependa del software (CTR26, PQ35–36), así que va al riel de alimentación, no a un GPIO. Se necesitan 2. |
| VIFLY Finder 2 | Beacon sonoro | Alternativa | 5 | 12 | ~105 dB, pero trae batería LiPo integrada: prohibida (E1). |
| Buzzer electromagnético | Beacon sonoro | Alternativa | 3.5 | 1.5 | ~80 dB y más corriente que el piezo. |
| INA219 | Voltaje y corriente | Seleccionado | — | 4.43 | Con shunt de 0.1 Ω: 0.1 mA y 4 mV por LSB, cumple CTR21–22 y PQ26–27. Se necesitan 2; los voltajes de los paneles solares (PQ31) piden otro canal. |
| INA260 | Voltaje y corriente | Alternativa | — | 5.52 | Shunt interno; resolución fija de 1.25 mA: no llega al 1 mA que pide CTR22. |
| PAC1934 | Voltaje y corriente | Alternativa | — | 5 | 4 canales en un chip: podría medir la batería y los dos paneles solares (PQ26, PQ31). |
| INA226 | Voltaje y corriente | Alternativa | — | 6 | 16 bits y shunt configurable: mejor resolución que el INA219. |
