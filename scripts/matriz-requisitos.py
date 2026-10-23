#!/usr/bin/env python3
"""Regenera salida/matriz-requisitos.csv desde el frontmatter de las notas de la wiki.

Uso (desde la raíz del repo):
    python3 scripts/matriz-requisitos.py           escribe la matriz e imprime el resumen
    python3 scripts/matriz-requisitos.py --check   solo comprueba que esté al día (código 1 si no)
"""
import sys

import brain


def main(argv: list[str]) -> int:
    filas = brain.construir_matriz()
    contenido = brain.matriz_csv(filas)
    ruta = brain.RUTA_MATRIZ
    relativa = ruta.relative_to(brain.RAIZ).as_posix()

    if "--check" in argv:
        actual = ruta.read_text(encoding="utf-8") if ruta.exists() else None
        if actual != contenido:
            print(f"{relativa} está desactualizada: corre python3 scripts/matriz-requisitos.py")
            return 1
        print(f"{relativa} está al día.")
        return 0

    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido, encoding="utf-8")

    rq = [f for f in filas if f["tipo"] == "RQ"]
    rc = [f for f in filas if f["tipo"] == "RC"]
    rq_control = [f for f in rq if f["control"] == "si"]
    control = rq_control + rc

    def verificados(lista):
        return sum(f["verificacion"] == "verificado" for f in lista)

    print(f"Matriz: {len(filas)} requisitos ({len(rq)} RQ, {len(rc)} RC) → {relativa}")
    print(f"Requisitos de control verificados: {verificados(control)} de {len(control)} "
          f"(RQ de control: {verificados(rq_control)} de {len(rq_control)}; "
          f"RC: {verificados(rc)} de {len(rc)})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
