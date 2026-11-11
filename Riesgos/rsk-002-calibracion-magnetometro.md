---
type: riesgo
status: abierto
id: RSK-002
tags: [riesgo, control, rumbo, magnetometro, calibracion, bno055, lis3mdl]
created: 2026-11-11
source: [raw/pruebas/tst-003-1-magnetometro-sin-calibrar.png, raw/pruebas/tst-003-3-orientacion-ndof-sin-calibrar.png, raw/pruebas/tst-003-guia-calibracion-bno055.md, raw/mision/cansat-mission-guide-2027-r1.1.pdf]
requisitos: []
probabilidad: 4
impacto: 4
nivel: alto
responsable: "Pendiente"
---

# RSK-002 · El rumbo magnético queda mal calibrado en vuelo y se pierde C8

> [!WARNING]
> **Pendiente** — Todavía no hay RC: el riesgo amenaza C8 (p. 9) y los valores calibrados de MAG_X, MAG_Y y MAG_Z de la telemetría (p. 26). La probabilidad y el impacto son una propuesta de Claude que debe validar el equipo.

## Enunciado

El riesgo se materializa si el magnetómetro vuela con cualquiera de estas tres condiciones:
- sin constantes de calibración;
- con constantes medidas en otro montaje (sin el servo, la batería o el brazo en su sitio);
- confiando en la calibración automática del modo NDOF.

En cualquiera de ellas, el rumbo estimado tiene un error del orden de 20°, y la cámara rota más de los ±10° de C8 aunque el control sea perfecto.

- **P1.** El control no corrige este error. En la simulación, L3 deja ≤ 0,27° de error de control, y todo lo demás viene del estimador ([diseno-estabilizacion-camara](../Control/diseno-estabilizacion-camara.md), M1). El lazo sigue fielmente un rumbo estimado que está mal.
- **M1.** En [TST-003](../Pruebas/tst-003-bno055-sin-calibrar-esp32-matlab.md) (lectura visual, sin CSV):
  - el círculo $m_x$–$m_y$ del BNO055 crudo está corrido ≈ 10 µT frente a un radio de ≈ 28 µT; por P1 de TST-003, eso es del orden de 20° de error de rumbo;
  - $\lvert B\rvert$ ≈ 52 µT, cuando el campo total del sitio es de ≈ 30 µT.
- **M2.** En el mismo ensayo:
  - la calibración interna de NDOF necesitó mover el sensor para llegar a 3 en el magnetómetro;
  - el acelerómetro no llegó a 3 en toda la corrida;
  - el yaw saltó entre 0° y 360° mientras no estaba calibrado.

## Evaluación

| Probabilidad (1 a 5) | Impacto (1 a 5) | Nivel = P × I |
|---|---|---|
| 4: no existe todavía un procedimiento de calibración para el montaje de vuelo; PQ21 impide calibrar con movimiento antes de soltar; y desplegar el brazo y mover el servo cambian el hierro duro cerca del sensor | 4: C8 se pierde en todo el tramo con video, no solo en los giros | 16 · alto |

Nivel: bajo de 1 a 6, medio de 8 a 12 y alto de 15 a 25.

## Mitigación

| Acción | Responsable | Ligada a | Estado |
|---|---|---|---|
| Recibir los CSV de TST-003 y medir el desfase real con un script | Pendiente | TST-003 | pendiente |
| Calibrar hierro duro y blando con un ajuste de elipsoide (`magcal` o mínimos cuadrados) y validar $\lvert B\rvert$ contra el WMM2025 | Pendiente | guía del compañero, sección 3.3 · TST-002 E3 | pendiente |
| Calibrar con el montaje final (servo, batería, brazo desplegado) y guardar las constantes en el firmware, no en la memoria volátil del BNO055 | Pendiente | TST por crear | pendiente |
| Medir el campo del servo según la distancia, para ubicar el magnetómetro | Pendiente | TST-002 E4 | pendiente |
| Simular el residuo de calibración (desfase horizontal y en Z, con inclinación) para fijar cuántos grados de los 10° de C8 se le dan | Pendiente | [diseno-estabilizacion-camara](../Control/diseno-estabilizacion-camara.md), sección 9 | pendiente |
| Lógica del estimador: no usar el rumbo magnético hasta tener constantes cargadas; mientras tanto, propagar solo con el giróscopo | Pendiente | firmware de vuelo | pendiente |

## Señal de alerta y contingencia

- **Señales:**
  - $\lvert B\rvert$ calibrado que cambia con la orientación o difiere del WMM2025 del sitio;
  - un rumbo que salta al desplegar el brazo o al mover el servo.
- **Contingencias:**
  - recalibrar con el brazo desplegado;
  - alejar el magnetómetro del servo (brazo de 220 mm de PQ10);
  - si la calibración de vuelo no alcanza, decidir con el equipo si el rumbo absoluto se toma relativo al inicio de la etapa con video (giro integrado) y aceptar la deriva del giróscopo durante el descenso.

## Historial

- 2026-11-11: identificado con las capturas de TST-003.
