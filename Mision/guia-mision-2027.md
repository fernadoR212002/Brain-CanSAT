---
type: guia
status: borrador
id: guia-mision-2027
tags: [mision, guia, fuente]
created: 2026-10-25
source: [raw/mision/cansat-mission-guide-2027-r1.1.pdf, derivados/cansat-mission-guide-2027-r1.1.txt]
requisitos: []
---

# Guía de misión de la CanSat Competition 2027 (PocketQube)

Ficha de la fuente oficial. El título en la portada es «Cansat Competition Guide 2027 · PocketQube · Rev 1.1 · Aug 3, 2026» (p. 1).

| Campo | Valor |
|---|---|
| Archivo | [cansat-mission-guide-2027-r1.1.pdf](../raw/mision/cansat-mission-guide-2027-r1.1.pdf) · 56 páginas · SHA-256 `9d573570…dfc6ec72fe` |
| Texto extraído | [cansat-mission-guide-2027-r1.1.txt](../derivados/cansat-mission-guide-2027-r1.1.txt) (`pdftotext -layout`) |
| Procesado | **parcial**: solo lo que toca a la estabilización de video (ver abajo) |

## Qué se leyó

Las páginas son las del PDF.

- Portada, índice e historial de revisiones (pp. 1–4).
- Visión general de la misión (pp. 5–6).
- Requisitos operativos C1 a C13 (pp. 8–9).
- Requisitos del PocketQube PQ1 a PQ36 (pp. 13–15).
- Requisitos mecánicos, eléctricos, de comunicaciones, de estación terrena y de software de vuelo (pp. 16–21).
- Telemetría, definición de ejes, comandos y modo simulación (pp. 22–28).
- Prueba de caída (pp. 29–30).
- Contenido del PDR, el CDR y el PFR (pp. 35–36).
- Tabla 1 de entregas (p. 37) y apéndices G y H: figura de ejes y calendario (pp. 53–56).

> [!WARNING]
> **Pendiente** — Sin procesar todavía: los requisitos del contenedor (pp. 9–12), los demás requisitos del concurso, la operación del día de lanzamiento y la puntuación. Los requisitos RQ se crearán con la skill `requisitos`.

## Datos clave para el lazo de rumbo

- **C1.** La cámara graba hacia el nadir y la orientación del video debe mantenerse para que el suelo no rote: «The PocketQube shall maintain the video orientation so the video of the ground is not rotating (Requirement C8 & PQ15).» (p. 6)
- **C2.** El comando de giro: «After 30 seconds of flight, a command shall be transmitted to rotate the camera view 90 degree along the nadir axis in the direction specified by the ground station judge» (p. 6).
- **C3.** Ejes: «When perfectly aligned (zero pointing error on all axes), the positive Yaw axis (+Z) points towards the earth (nadir direction), the positive Pitch axis (+Y) points south, and the positive Roll axis (+X) points east.» y «The camera pointing requirement is due north, which is the negative Pitch -Y direction.» (p. 25)
- **C4.** El PocketQube va apagado dentro del contenedor (PQ21, p. 14), se suelta al 90 % de la altura máxima (C3, p. 8) y baja a 3–5 m/s (C13, p. 9).

## Fechas: la guía se contradice

| Entrega | Tabla 1 (p. 37) | Calendario, apéndice H (p. 56) |
|---|---|---|
| PDR | 30-ene-2027, 23:59:59 UTC | 28-ene-2027, 23:59:59 UTC |
| CDR | 27-mar-2027, 23:59:59 UTC | 1-abr-2027, 23:59:59 UTC |
| Documento de pruebas ambientales | 22-may-2027 | 21-may-2027 |
| PFR | 7-jun-2027, 9:30 hora local | 13-jun-2027 |
| Lanzamiento | — | 12-jun-2027 |

> [!IMPORTANT]
> Interpretación propia: se planea con la fecha más temprana y se pregunta a la organización cuál vale.
