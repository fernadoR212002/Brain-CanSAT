"""Funciones comunes del CanSat Brain: notas de la wiki, frontmatter y matriz de requisitos.

Solo usa la biblioteca estándar, para que funcione sin instalar nada.
"""
from __future__ import annotations

import csv
import io
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

CARPETAS_WIKI = ["Mision", "Control", "Subsistemas", "Decisiones", "Pruebas",
                 "Riesgos", "Conceptos", "Entregas", "Plantillas"]
SUBCARPETAS_RAW = ["mision", "revisiones", "datasheets", "pruebas", "vuelos",
                   "reuniones", "lecturas", "datos"]
CARPETAS_CON_README = CARPETAS_WIKI + ["raw", "derivados", "sim", "scripts", "salida"]
CAMPOS_OBLIGATORIOS = ["type", "status", "id", "tags", "created", "source", "requisitos"]

PATRONES_ID = [r"RQ-\d{3}", r"RC-\d{3}", r"DEC-\d{3}", r"TST-\d{3}", r"RSK-\d{3}",
               r"ICD-\d{3}", r"DS-\d{2}", r"L-\d{2}", r"ACT-\d{4}-\d{2}-\d{2}(?:-[a-z])?",
               r"REV-[A-Z]+"]
ID_RE = re.compile(r"^(?:%s)$" % "|".join(PATRONES_ID))
REQ_RE = re.compile(r"^R[QC]-\d{3}$")

METODOS = {"I", "A", "D", "T"}
VERIFICACION = {"pendiente", "en curso", "verificado", "fallido"}

RUTA_MATRIZ = RAIZ / "salida" / "matriz-requisitos.csv"
COLUMNAS_MATRIZ = ["id", "tipo", "ref_oficial", "titulo", "texto", "control", "origen",
                   "derivados", "metodo", "responsable", "verificacion", "decisiones",
                   "pruebas", "evidencia", "entregas", "riesgos", "nota"]


# --- Frontmatter -------------------------------------------------------------

def _quitar_comentario(texto: str) -> str:
    """Quita un comentario YAML (' # …') que no esté entre comillas."""
    comillas = None
    for i, c in enumerate(texto):
        if c in "\"'":
            if comillas is None:
                comillas = c
            elif comillas == c:
                comillas = None
        elif c == "#" and comillas is None and (i == 0 or texto[i - 1].isspace()):
            return texto[:i]
    return texto


def _sin_comillas(texto: str) -> str:
    texto = texto.strip()
    if len(texto) >= 2 and texto[0] == texto[-1] and texto[0] in "\"'":
        return texto[1:-1]
    return texto


def _valor(texto: str):
    texto = _quitar_comentario(texto).strip()
    if texto.startswith("[") and texto.endswith("]"):
        return [_sin_comillas(p) for p in texto[1:-1].split(",") if p.strip()]
    return _sin_comillas(texto)


def leer_nota(ruta: Path):
    """Devuelve (frontmatter, cuerpo). El frontmatter es None si la nota no lo tiene.

    Lector mínimo de YAML: claves simples, listas en línea [a, b] y listas en bloque (- a).
    """
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    if not lineas or lineas[0].strip() != "---":
        return None, "\n".join(lineas)
    fin = next((i for i in range(1, len(lineas)) if lineas[i].strip() == "---"), None)
    if fin is None:
        return None, "\n".join(lineas)
    datos, clave = {}, None
    for linea in lineas[1:fin]:
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):(?:\s+(.*))?$", linea)
        if m:
            clave = m.group(1)
            datos[clave] = _valor(m.group(2) or "")
            continue
        m = re.match(r"^\s+-\s+(.*)$", linea)
        if m and clave:
            if not isinstance(datos[clave], list):
                datos[clave] = []
            datos[clave].append(_valor(m.group(1)))
    return datos, "\n".join(lineas[fin + 1:])


def como_lista(valor) -> list[str]:
    if valor in (None, ""):
        return []
    if isinstance(valor, list):
        return [str(v).strip() for v in valor if str(v).strip()]
    return [str(valor).strip()]


def es_si(valor) -> bool:
    return str(valor).strip().lower() in {"si", "sí", "true", "yes"}


# --- Notas -------------------------------------------------------------------

def notas_wiki(incluir_plantillas: bool = False):
    """Rutas de las notas de la wiki (sin los README)."""
    for carpeta in CARPETAS_WIKI:
        if carpeta == "Plantillas" and not incluir_plantillas:
            continue
        for ruta in sorted((RAIZ / carpeta).rglob("*.md")):
            if ruta.name != "README.md":
                yield ruta


def titulo(cuerpo: str, id_nota: str) -> str:
    """Título del encabezado H1 sin el prefijo «ID ·»."""
    for linea in cuerpo.splitlines():
        if linea.startswith("# "):
            return re.sub(r"^%s\s*[·:\-–—]\s*" % re.escape(id_nota), "", linea[2:].strip())
    return ""


def texto_requisito(cuerpo: str) -> str:
    """Primer bloque de cita bajo «## Texto» que no sea un aviso, sin la etiqueta **C1.**."""
    partes, dentro, aviso = [], False, False
    for linea in cuerpo.splitlines():
        if linea.startswith("## "):
            if dentro:
                break
            dentro = linea[3:].strip().lower() == "texto"
            continue
        if not dentro:
            continue
        if not linea.lstrip().startswith(">"):
            if partes:
                break
            aviso = False
            continue
        t = linea.lstrip()[1:].strip()
        if not partes and t.startswith("[!"):
            aviso = True
        if aviso:
            continue
        t = re.sub(r"^\*\*[PCDSM]\d+\.\*\*\s*", "", t)
        if t:
            partes.append(t)
    return " ".join(partes)


# --- Matriz de requisitos ----------------------------------------------------

def construir_matriz() -> list[dict]:
    """Filas de la matriz RQ → RC → DEC → TST → evidencia → REV, desde el frontmatter."""
    notas = []
    for ruta in notas_wiki():
        fm, cuerpo = leer_nota(ruta)
        if fm and fm.get("id"):
            notas.append((ruta, fm, cuerpo))

    def que_citan(prefijo: str, rid: str) -> list[str]:
        return sorted({str(fm["id"]) for _, fm, _ in notas
                       if str(fm["id"]).startswith(prefijo) and rid in como_lista(fm.get("requisitos"))})

    filas = []
    requisitos = [n for n in notas if REQ_RE.match(str(n[1]["id"]))]
    for ruta, fm, cuerpo in sorted(requisitos, key=lambda n: str(n[1]["id"])):
        rid = str(fm["id"])
        es_rc = rid.startswith("RC-")
        pruebas = que_citan("TST-", rid)
        evidencia = sorted({e for _, f, _ in notas if str(f["id"]) in pruebas
                            for e in como_lista(f.get("evidencia"))})
        filas.append({
            "id": rid,
            "tipo": "RC" if es_rc else "RQ",
            "ref_oficial": str(fm.get("ref_oficial", "")),
            "titulo": titulo(cuerpo, rid),
            "texto": texto_requisito(cuerpo),
            "control": "si" if es_rc or es_si(fm.get("control")) else "no",
            "origen": "; ".join(r for r in como_lista(fm.get("requisitos")) if r.startswith("RQ-")) if es_rc else "",
            "derivados": "" if es_rc else "; ".join(que_citan("RC-", rid)),
            "metodo": str(fm.get("metodo", "")),
            "responsable": str(fm.get("responsable", "")),
            "verificacion": str(fm.get("verificacion", "")),
            "decisiones": "; ".join(que_citan("DEC-", rid)),
            "pruebas": "; ".join(pruebas),
            "evidencia": "; ".join(evidencia),
            "entregas": "; ".join(que_citan("REV-", rid)),
            "riesgos": "; ".join(que_citan("RSK-", rid)),
            "nota": ruta.relative_to(RAIZ).as_posix(),
        })
    return filas


def matriz_csv(filas: list[dict]) -> str:
    salida = io.StringIO()
    escritor = csv.DictWriter(salida, fieldnames=COLUMNAS_MATRIZ, lineterminator="\n")
    escritor.writeheader()
    escritor.writerows(filas)
    return salida.getvalue()
