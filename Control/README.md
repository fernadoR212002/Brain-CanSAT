# Control

El frente de control a fondo: alcance, requisitos derivados de control (RC-NNN, cada uno con su RQ de origen), modelos de planta, controladores, simulaciones y métricas.

- Requisitos de control: `rc-NNN-titulo-corto.md` (plantilla: [requisito](../Plantillas/requisito.md)).
- Diseños: `diseno-<tema>.md`, con los RC que atienden en `requisitos` (skill `control`).
- Modelos de planta: `modelo-<tema>.md`, con sus comprobaciones en `sim/`.

## Notas

- [alcance.md](alcance.md) — Alcance del frente de control: lo que sabemos, pendientes, preguntas para la guía y métricas de desempeño.
- [modelo-rumbo-espacio-estados.md](modelo-rumbo-espacio-estados.md) — Modelo del lazo de rumbo: hipótesis, ecuaciones físicas, matrices A, B, C, D (cuerpo, cámara sobre servomotor, modelo completo con sensores y estimador), controlabilidad, observabilidad, discretización y cero de muestreo.
