#!/usr/bin/env python3
"""Lint del CanSat Brain: revisión mecánica de la wiki y la memoria.

Uso (desde la raíz del repo):  python3 scripts/lint.py
Termina con código 1 si hay errores; los avisos no bloquean. Las unidades sin declarar y
las contradicciones las revisa la skill lint leyendo las notas.
"""
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

import brain

RAIZ = brain.RAIZ
TIPOS_AVISO = {"NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"}
ARCHIVOS_RAIZ = ["CLAUDE.md", "GUIA.md", "README.md", "index.md", "log.md", "estado.md"]
MAX_LINEAS_CLAUDE = 150

WIKILINK_RE = re.compile(r"\[\[[^\]\n]+\]\]")
ENLACE_RE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)")
REFERENCIA_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)")
AVISO_RE = re.compile(r"^\s*>\s*\[!(\w+)\](.*)$")
DECIMAL_RE = re.compile(r"(?<![\w.,/-])\d+\.\d+(?![\w.])")
NO_DECIMAL_ANTES = re.compile(r"(secci[oó]n|numeral|apartado|[ií]tem|cap[ií]tulo|tabla|figura|"
                              r"anexo|versi[oó]n|§|v)\s*$", re.IGNORECASE)
ENCABEZADO_LOG_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2}) · [a-z]+ · \S")

hallazgos = {"ERROR": [], "AVISO": [], "INFO": []}


def reportar(nivel: str, ruta, linea: int, mensaje: str) -> None:
    lugar = ruta.relative_to(RAIZ).as_posix() if isinstance(ruta, Path) else str(ruta)
    if linea:
        lugar += f":{linea}"
    hallazgos[nivel].append(f"{lugar}  {mensaje}")


def rel(ruta: Path) -> str:
    return ruta.relative_to(RAIZ).as_posix()


def omitir(partes: tuple) -> bool:
    if partes[0] == ".git" or "__pycache__" in partes or ".venv" in partes:
        return True
    if partes[0] == "raw" and len(partes) > 2:  # fuentes inmutables: no se corrigen
        return True
    if partes[0] == "derivados" and partes[-1] != "README.md":
        return True
    return False


def archivos_md() -> list[Path]:
    return [r for r in sorted(RAIZ.rglob("*.md")) if not omitir(r.relative_to(RAIZ).parts)]


def lineas_de_prosa(texto: str):
    """(número, línea) de la prosa: sin frontmatter, bloques de código, bloques $$ ni comentarios
    HTML, y sin código ni matemáticas en línea."""
    lineas = texto.splitlines()
    inicio = 0
    if lineas and lineas[0].strip() == "---":
        inicio = next((i + 1 for i in range(1, len(lineas)) if lineas[i].strip() == "---"), 0)
    valla, en_math, en_comentario = None, False, False
    for n, linea in enumerate(lineas[inicio:], start=inicio + 1):
        s = linea.strip()
        m = re.match(r"^(`{3,}|~{3,})", s)
        if m and (valla is None or s.startswith(valla)):
            valla = m.group(1)[:3] if valla is None else None
            continue
        if valla is not None:
            continue
        if en_math:
            en_math = not s.endswith("$$")
            continue
        if s.startswith("$$"):
            en_math = not (len(s) > 2 and s.endswith("$$"))
            continue
        if en_comentario:
            if "-->" in linea:
                en_comentario = False
                linea = linea.split("-->", 1)[1]
            else:
                continue
        linea = re.sub(r"<!--.*?-->", "", linea)
        if "<!--" in linea:
            linea, en_comentario = linea.split("<!--", 1)[0], True
        linea = re.sub(r"`[^`]*`", "", linea)
        linea = re.sub(r"\$[^$]+\$", "", linea)
        yield n, linea


def revisar_enlaces(ruta: Path, texto: str, entrantes: dict) -> None:
    for n, linea in lineas_de_prosa(texto):
        if WIKILINK_RE.search(linea):
            reportar("ERROR", ruta, n, f"wikilink: {WIKILINK_RE.search(linea).group(0)} (usa un enlace relativo)")
        destinos = ENLACE_RE.findall(linea)
        m = REFERENCIA_RE.match(linea)
        if m:
            destinos.append(m.group(1))
        for destino in destinos:
            if destino.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", destino):
                continue
            camino = unquote(destino.split("#", 1)[0].split("?", 1)[0])
            if not camino:
                continue
            if camino.startswith("/"):
                reportar("AVISO", ruta, n, f"enlace absoluto {destino} (usa una ruta relativa)")
                objetivo = RAIZ / camino.lstrip("/")
            else:
                objetivo = ruta.parent / camino
            objetivo = Path(os.path.normpath(objetivo))
            if not objetivo.exists():
                reportar("ERROR", ruta, n, f"enlace roto: {destino}")
            elif objetivo != ruta:
                entrantes[objetivo].add(ruta)


def revisar_avisos(ruta: Path, texto: str) -> None:
    for n, linea in lineas_de_prosa(texto):
        m = AVISO_RE.match(linea)
        if not m:
            continue
        if m.group(1) not in TIPOS_AVISO:
            reportar("AVISO", ruta, n, f"aviso [!{m.group(1)}] no existe en GitHub (usa {', '.join(sorted(TIPOS_AVISO))})")
        elif m.group(2).strip():
            reportar("AVISO", ruta, n, "el marcador del aviso debe ir solo en su línea; el texto, en la línea siguiente")


def revisar_decimales(ruta: Path, texto: str) -> None:
    for n, linea in lineas_de_prosa(texto):
        linea = re.sub(r"\]\([^)]*\)", "]", linea)   # destinos de enlaces
        linea = re.sub(r"«[^»]*»", "", linea)          # texto oficial citado: no se altera
        for m in DECIMAL_RE.finditer(linea):
            if not NO_DECIMAL_ANTES.search(linea[:m.start()]):
                reportar("AVISO", ruta, n, f"posible punto decimal «{m.group(0)}» (en las notas va coma decimal)")


def revisar_nota(ruta: Path, fm, cuerpo: str, ids: dict) -> None:
    carpeta = ruta.relative_to(RAIZ).parts[0]
    if fm is None:
        reportar("ERROR", ruta, 0, "nota sin frontmatter YAML")
        return
    faltan = [c for c in brain.CAMPOS_OBLIGATORIOS if c not in fm]
    if faltan:
        reportar("ERROR", ruta, 0, f"frontmatter sin: {', '.join(faltan)}")
    if not re.match(r"^[a-z0-9][a-z0-9-]*\.md$", ruta.name):
        reportar("AVISO", ruta, 0, "nombre de archivo: minúsculas, números y guiones")
    if carpeta == "Plantillas":
        return

    id_nota = str(fm.get("id", ""))
    if id_nota:
        ids[id_nota].append(ruta)
    if brain.ID_RE.match(id_nota):
        if not (ruta.stem == id_nota.lower() or ruta.stem.startswith(id_nota.lower() + "-")):
            reportar("AVISO", ruta, 0, f"el nombre del archivo debe empezar por el ID ({id_nota.lower()}-…)")
        if re.search(r"-0+$", id_nota):
            reportar("AVISO", ruta, 0, f"{id_nota}: el número 000 está reservado para plantillas")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(fm.get("created", ""))):
        reportar("AVISO", ruta, 0, "created debe ser AAAA-MM-DD")

    for campo in ("source", "evidencia"):
        for valor in brain.como_lista(fm.get(campo)):
            camino = valor.split()[0]
            if "/" in camino and not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", camino) and not (RAIZ / camino).exists():
                reportar("AVISO", ruta, 0, f"{campo}: la ruta {camino} no existe")

    if brain.REQ_RE.match(id_nota):
        if str(fm.get("metodo", "")) not in brain.METODOS:
            reportar("AVISO", ruta, 0, f"{id_nota} sin método de verificación (I, A, D o T)")
        if str(fm.get("responsable", "")).strip().lower() in ("", "pendiente"):
            reportar("AVISO", ruta, 0, f"{id_nota} sin responsable")
        if str(fm.get("verificacion", "")) not in brain.VERIFICACION:
            reportar("AVISO", ruta, 0, f"{id_nota}: verificacion debe ser {', '.join(sorted(brain.VERIFICACION))}")
        if id_nota.startswith("RC-") and not any(r.startswith("RQ-") for r in brain.como_lista(fm.get("requisitos"))):
            reportar("AVISO", ruta, 0, f"{id_nota} sin RQ de origen en requisitos")
    if id_nota.startswith("TST-") and not brain.como_lista(fm.get("requisitos")):
        reportar("AVISO", ruta, 0, f"{id_nota}: prueba sin requisito")


def main() -> int:
    for nombre in ARCHIVOS_RAIZ:
        if not (RAIZ / nombre).exists():
            reportar("ERROR", nombre, 0, "falta el archivo")
    if (RAIZ / "CLAUDE.md").exists():
        n = len((RAIZ / "CLAUDE.md").read_text(encoding="utf-8").splitlines())
        if n > MAX_LINEAS_CLAUDE:
            reportar("AVISO", "CLAUDE.md", 0, f"{n} líneas (máximo {MAX_LINEAS_CLAUDE})")
    for carpeta in brain.CARPETAS_CON_README:
        if not (RAIZ / carpeta / "README.md").exists():
            reportar("ERROR", f"{carpeta}/", 0, "carpeta sin README.md")
    for sub in brain.SUBCARPETAS_RAW + ["inbox"]:
        if (RAIZ / "raw" / sub / "README.md").exists():
            reportar("AVISO", f"raw/{sub}/README.md", 0, "las subcarpetas de raw/ no llevan README (el catálogo es index.md)")

    entrantes = defaultdict(set)
    ids = defaultdict(list)
    notas = set(brain.notas_wiki(incluir_plantillas=True))
    for ruta in archivos_md():
        texto = ruta.read_text(encoding="utf-8")
        revisar_enlaces(ruta, texto, entrantes)
        revisar_avisos(ruta, texto)
        if ruta in notas:
            fm, cuerpo = brain.leer_nota(ruta)
            revisar_nota(ruta, fm, cuerpo, ids)
            revisar_decimales(ruta, texto)

    for id_nota, rutas in sorted(ids.items()):
        if len(rutas) > 1:
            reportar("ERROR", rutas[0], 0, f"ID duplicado {id_nota}: {', '.join(rel(r) for r in rutas)}")

    for ruta in sorted(notas):
        leeme = ruta.parent / "README.md"
        if not entrantes.get(ruta):
            reportar("AVISO", ruta, 0, "nota huérfana: ningún archivo enlaza a ella")
        elif leeme not in entrantes[ruta]:
            reportar("AVISO", ruta, 0, "no está en el README de su carpeta")

    indice = (RAIZ / "index.md").read_text(encoding="utf-8") if (RAIZ / "index.md").exists() else ""
    for sub in brain.SUBCARPETAS_RAW:
        for fuente in sorted((RAIZ / "raw" / sub).rglob("*")):
            if fuente.is_file() and fuente.name != ".gitkeep" and rel(fuente) not in indice:
                reportar("AVISO", fuente, 0, "fuente sin catalogar en index.md")
    en_inbox = [f for f in (RAIZ / "raw" / "inbox").glob("*") if f.name != ".gitkeep"]
    if en_inbox:
        reportar("INFO", "raw/inbox/", 0, f"{len(en_inbox)} archivo(s) por procesar con la skill subir")

    if (RAIZ / "log.md").exists():
        fechas = []
        for n, linea in enumerate((RAIZ / "log.md").read_text(encoding="utf-8").splitlines(), start=1):
            if linea.startswith("## "):
                m = ENCABEZADO_LOG_RE.match(linea)
                if not m:
                    reportar("AVISO", "log.md", n, "encabezado del log: ## AAAA-MM-DD · tipo · título")
                else:
                    fechas.append((m.group(1), n))
        for (anterior, _), (fecha, n) in zip(fechas, fechas[1:]):
            if fecha < anterior:
                reportar("AVISO", "log.md", n, "entrada con fecha anterior a la previa: el log solo crece al final")

    filas = brain.construir_matriz()
    actual = brain.RUTA_MATRIZ.read_text(encoding="utf-8") if brain.RUTA_MATRIZ.exists() else None
    if actual != brain.matriz_csv(filas):
        reportar("AVISO", rel(brain.RUTA_MATRIZ), 0, "matriz desactualizada: corre python3 scripts/matriz-requisitos.py")
    sin_verificar = [f["id"] for f in filas if f["verificacion"] != "verificado"]
    if sin_verificar:
        reportar("INFO", "requisitos", 0, f"{len(sin_verificar)} sin verificar: {', '.join(sin_verificar)}")
    for f in filas:
        if f["verificacion"] == "verificado" and not f["evidencia"]:
            reportar("AVISO", f["nota"], 0, f"{f['id']} verificado sin evidencia en raw/ (ninguna TST con evidencia)")

    for nivel in ("ERROR", "AVISO", "INFO"):
        if hallazgos[nivel]:
            print(f"\n{nivel} ({len(hallazgos[nivel])})")
            for h in hallazgos[nivel]:
                print(f"  {h}")
    print(f"\nLint: {len(hallazgos['ERROR'])} errores, {len(hallazgos['AVISO'])} avisos, "
          f"{len(hallazgos['INFO'])} notas informativas ({len(archivos_md())} archivos Markdown revisados).")
    return 1 if hallazgos["ERROR"] else 0


if __name__ == "__main__":
    sys.exit(main())
