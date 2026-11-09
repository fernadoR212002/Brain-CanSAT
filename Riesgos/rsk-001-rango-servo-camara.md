---
type: riesgo
status: abierto
id: RSK-001
tags: [riesgo, control, camara, servomotor, actuador]
created: 2026-11-08
source: [raw/mision/cansat-mission-guide-2027-r1.1.pdf]
requisitos: []
probabilidad: 3
impacto: 4
nivel: medio
responsable: "Pendiente"
---

# RSK-001 · El recorrido del servo de la cámara no alcanza para el giro de 90° y el giro del cuerpo

> [!WARNING]
> **Pendiente** — Sin RC todavía: el riesgo amenaza C8 y C11 (p. 9) y PQ15 y PQ17 (p. 14). La probabilidad es una propuesta de Claude que debe validar el equipo.

## Enunciado

Si la cámara se mueve con un servo de recorrido limitado (como el Futaba de 180° de [servo-prueba-futaba.m](../sim/servo-prueba-futaba.m)) y el PocketQube oscila más de ≈ ±45° o gira de forma continua bajo el paracaídas, entonces el servo llega a su tope y el video rota con el cuerpo. Eso incumple C8 (±10°) en la etapa 5 del vuelo, sobre todo después del giro de 90° de C11.

- **P1.** El recorrido necesario es al menos el giro comandado más la excursión pico a pico del cuerpo:

$$
\text{recorrido} \ \ge\ 90° + (\psi_{b,\max}-\psi_{b,\min})
$$

  El giro de C11 gasta la mitad de un servo de 180°.
- **M1.** Simulado en [diseno-estabilizacion-camara](../Control/diseno-estabilizacion-camara.md) (escenario S1, con el cuerpo entre −80° y 67°):
  - servo de ±90°: rompe C8 el 21,4 % del tiempo, casi todo después del giro;
  - servo de ±180°: máximo de 10,71°;
  - con giro continuo (S2): ninguno de los dos cumple.

## Evaluación

| Probabilidad (1 a 5) | Impacto (1 a 5) | Nivel = P × I |
|---|---|---|
| 3: no se ha medido el giro del PocketQube; con destorcedor o con paneles que hagan de hélice, sube a 5 | 4: C8 y C11 se pierden en el tramo con video | 12 · medio |

Nivel: bajo de 1 a 6, medio de 8 a 12 y alto de 15 a 25.

## Mitigación

| Acción | Responsable | Ligada a | Estado |
|---|---|---|---|
| Medir el giro y el balanceo del PocketQube con una caída desde dron | Pendiente | TST por crear | pendiente |
| Decidir entre destorcedor y rotación continua, y el actuador (servo de 270° o 360°, o motor DC con codificador y anillo colector) | Pendiente | DEC-001 (pendiente de pesos) | pendiente |
| Si se queda el servo: elegir un modelo digital de tramas rápidas (≥ 100 Hz), porque a 50 Hz la latencia sola deja ≈ 10,7° | Pendiente | DEC-001 | pendiente |

## Señal de alerta y contingencia

- **Señal:** en la caída desde dron, una excursión pico a pico del cuerpo mayor de 90° o un giro neto sostenido.
- **Contingencia:** cambiar a rotación continua (L3 de [diseno-estabilizacion-camara](../Control/diseno-estabilizacion-camara.md)). Si no da el tiempo, centrar el servo en el rumbo después del giro de C11 y aceptar la pérdida en las excursiones grandes.
