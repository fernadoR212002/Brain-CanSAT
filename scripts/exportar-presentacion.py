#!/usr/bin/env python3
"""Exporta la presentación a un solo archivo HTML para enviarlo por WhatsApp, correo o Drive.

Toma salida/presentacion-control-camara/ (la fuente del Artifact) y escribe
salida/presentacion-control-camara.html con las imágenes y el diagrama de archify adentro.
La escena 3D (three.js) y las tipografías se siguen cargando de internet.

Uso: python3 scripts/exportar-presentacion.py
"""
import base64
import html
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "salida" / "presentacion-control-camara"
DESTINO = RAIZ / "salida" / "presentacion-control-camara.html"


def reemplazar(texto, viejo, nuevo):
    """Reemplaza un fragmento que debe aparecer exactamente una vez."""
    n = texto.count(viejo)
    if n != 1:
        sys.exit(f"Se esperaba una aparición de {viejo[:60]!r} y hay {n}.")
    return texto.replace(viejo, nuevo)


def main():
    pagina = (CARPETA / "index.html").read_text(encoding="utf-8")

    # 1. Las imágenes van adentro, como data URI.
    def a_data(m):
        datos = (CARPETA / m.group(1)).read_bytes()
        return 'src="data:image/png;base64,' + base64.b64encode(datos).decode("ascii") + '"'

    pagina, n_img = re.subn(r'src="(img/[^"]+\.png)"', a_data, pagina)

    # 2. La lupa amplía la misma imagen incrustada (sin duplicarla).
    pagina, n_lupa = re.subn(r' data-lupa="img/[^"]+"', ' data-lupa=""', pagina)
    pagina = reemplazar(pagina, "img.src = b.dataset.lupa;",
                        "img.src = b.dataset.lupa || (fuente ? fuente.src : '');")

    # 3. El diagrama de archify va adentro (srcdoc), con un botón de pantalla completa en vez del enlace.
    diagrama = (CARPETA / "lazo-camara-colores.html").read_text(encoding="utf-8")
    pagina = reemplazar(pagina, '<iframe src="lazo-camara-colores.html"',
                        '<iframe srcdoc="' + html.escape(diagrama, quote=True) + '"')
    pagina = reemplazar(
        pagina,
        '<a href="lazo-camara-colores.html" target="_blank" rel="noopener">Abrir el diagrama en otra pestaña</a>',
        '<button class="enlace" type="button" data-pantalla>Ver el diagrama en pantalla completa</button>')
    pagina = reemplazar(
        pagina, "</style>",
        ".enlace { background: none; border: 0; padding: 0; font: inherit; color: inherit;"
        " text-decoration: underline; text-underline-offset: 3px; cursor: pointer; }\n"
        ":root { padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }\n"
        "[hidden] { display: none !important; }\n</style>")
    pagina = reemplazar(
        pagina, "  /* ---------- escena 3D */",
        "  document.querySelectorAll('[data-pantalla]').forEach(b => b.addEventListener('click', () => {\n"
        "    const f = document.querySelector('.embed iframe');\n"
        "    f.closest('.embed').classList.add('activo');\n"
        "    const pedir = f.requestFullscreen || f.webkitRequestFullscreen;\n"
        "    if (pedir) { try { const r = pedir.call(f); if (r && r.catch) r.catch(() => {}); } catch (e) { /* sin pantalla completa */ } }\n"
        "  }));\n\n"
        "  /* ---------- escena 3D */")

    # 4. Documento completo: el Artifact agrega el encabezado al publicar; aquí va explícito.
    corte = pagina.index("</style>") + len("</style>")
    documento = ("<!doctype html>\n<html lang=\"es\">\n<head>\n<meta charset=\"utf-8\">\n"
                 "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
                 + pagina[:corte] + "\n</head>\n<body>\n" + pagina[corte:].lstrip("\n")
                 + "\n</body>\n</html>\n")
    DESTINO.write_text(documento, encoding="utf-8")
    print(f"{DESTINO.relative_to(RAIZ)}: {DESTINO.stat().st_size / 1e6:.1f} MB; "
          f"{n_img} imágenes y el diagrama incrustados ({n_lupa} figuras con lupa).")


if __name__ == "__main__":
    main()
