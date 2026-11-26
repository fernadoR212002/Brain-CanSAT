# Antares · Control de la cámara

El [video MP4](../antares-control-15s.mp4) incluye la animación y su sonido original. Para ver la [versión HTML](index.html) desde el disco, conserva juntos los archivos de esta carpeta. La pieza de 15 s conecta la adquisición de datos del hardware con el diseño y la simulación del lazo de rumbo de la cámara.

La [dirección visual](DESIGN.md) fija la paleta y describe cómo construir cada escena.

## Fuentes

- Luis Parra conectó el BNO055 a un ESP32 y registró señales en MATLAB. La prueba documenta el montaje y las capturas del sensor. [TST-003](../../Pruebas/tst-003-bno055-sin-calibrar-esp32-matlab.md)
- Angel Fernando Revelo Narvaez dirigió el trabajo de control. El diseño L3 incorpora realimentación y prealimentación del giróscopo para compensar el giro del cuerpo. [Diseño de estabilización](../../Control/diseno-estabilizacion-camara.md)
- Los errores máximos de rumbo de 3,01° en S1 y 2,60° en S2 corresponden a los escenarios del modelo de Simulink, excluidos el arranque y la maniobra de 90°. [Métricas de simulación](../../derivados/simulink-lazo-camara-l3-metricas.csv)

## Reproducir la exportación

Desde la raíz del repositorio, ejecuta el siguiente comando con acceso a HyperFrames. La salida verificada tiene 900 fotogramas en 1920 × 1080, video H.264 y audio AAC.

```bash
npx hyperframes@0.9.70 render salida/antares-control-15s --fps 60 --quality high --output salida/antares-control-15s.mp4
```
