#!/usr/bin/env python3
"""
export_apex.py - Herramientas locales para parchar una pagina APEX por re-import (APEX 20.2).

Cuando no hay API para tocar un DA, un proceso o el JS de una pagina, el camino es:
  export vivo (apex_export) -> reemplazo de un fragmento UNICO -> ejecutar el export por bloques.
Este script hace lo determinista de ese flujo, sin tocar la base:

  contar    EXPORT.sql                      cuenta los create_* (procesos, DA, items, botones...)
  dividir   EXPORT.sql -o CARPETA           parte el export en bloques (un bloque = lo que va entre lineas "/")
  parchear  EXPORT.sql CAMBIOS.json -o OUT  aplica reemplazos exigiendo que cada fragmento sea unico

Por que existe:
  - Un reemplazo que no es unico (o que no encuentra nada) cambia la pagina en silencio: se exige el conteo.
  - Un bloque del export puede superar 32.767 caracteres; si se lo copia con dbms_lob.substr se trunca
    en silencio y se pierde la cola (procesos y DA enteros). 'dividir' avisa de los bloques grandes.
  - Antes de ejecutar hay que comparar los conteos con los esperados: 'contar' antes y despues.

CAMBIOS.json: [ {"buscar": "texto exacto", "reemplazar": "texto nuevo", "esperado": 1}, ... ]
  "esperado" (por defecto 1) es la cantidad de veces que "buscar" DEBE aparecer. Para insertar un
  componente nuevo, usar como "buscar" una linea ancla unica y repetirla dentro de "reemplazar".
"""
import argparse
import json
import os
import re
import sys

LIMITE_BLOQUE = 32767
CLASES = [
    "create_page", "create_page_plug", "create_page_button", "create_page_branch", "create_page_item",
    "create_page_computation", "create_page_validation", "create_page_process",
    "create_page_da_event", "create_page_da_action", "create_worksheet", "create_worksheet_column",
    "create_worksheet_rpt", "create_worksheet_condition", "create_report_region", "create_report_columns",
]


def leer(p):
    return open(p, encoding="utf-8", newline="").read()


def contar_en(texto):
    res = {}
    for c in CLASES:
        n = len(re.findall(r"wwv_flow_api\." + re.escape(c) + r"\s*\(", texto))
        if n:
            res[c] = n
    return res


def bloques(texto):
    """Un export es una secuencia de bloques PL/SQL separados por una linea con solo '/'."""
    partes, actual = [], []
    for linea in texto.splitlines(keepends=True):
        if linea.strip() == "/":
            partes.append("".join(actual))
            actual = []
        else:
            actual.append(linea)
    resto = "".join(actual)
    if resto.strip():
        partes.append(resto)
    return partes


def cmd_contar(a):
    res = contar_en(leer(a.export))
    for k, v in res.items():
        print(f"{k:28s} {v}")
    print(f"{'TOTAL create_*':28s} {sum(res.values())}")


def cmd_dividir(a):
    texto = leer(a.export)
    os.makedirs(a.salida, exist_ok=True)
    grandes = 0
    for i, b in enumerate(bloques(texto), 1):
        if not b.strip():
            continue
        p = os.path.join(a.salida, f"bloque_{i:03d}.sql")
        open(p, "w", encoding="utf-8", newline="").write(b)
        aviso = ""
        if len(b) > LIMITE_BLOQUE:
            grandes += 1
            aviso = f"   <-- {len(b)} caracteres > {LIMITE_BLOQUE}: NO copiar con dbms_lob.substr (trunca); usar createtemporary + copy"
        print(f"{os.path.basename(p)}  {len(b):>8} caracteres{aviso}")
    print(f"{len(bloques(texto))} bloques; {grandes} superan el limite de VARCHAR2 de PL/SQL")


def cmd_parchear(a):
    texto = leer(a.export)
    antes = contar_en(texto)
    cambios = json.load(open(a.cambios, encoding="utf-8"))
    for n, c in enumerate(cambios, 1):
        esperado = c.get("esperado", 1)
        real = texto.count(c["buscar"])
        if real != esperado:
            sys.exit(f"Cambio #{n}: el fragmento aparece {real} veces y se esperaban {esperado}. No se aplico nada.\n"
                     f"Fragmento: {c['buscar'][:120]!r}")
        texto = texto.replace(c["buscar"], c["reemplazar"])
    despues = contar_en(texto)
    open(a.salida, "w", encoding="utf-8", newline="").write(texto)
    print(f"Escrito {a.salida} ({len(cambios)} cambios)")
    claves = sorted(set(antes) | set(despues))
    print(f"{'componente':28s} {'antes':>6} {'despues':>8}")
    for k in claves:
        marca = "" if antes.get(k, 0) == despues.get(k, 0) else "   <-- cambio"
        print(f"{k:28s} {antes.get(k, 0):>6} {despues.get(k, 0):>8}{marca}")
    print("Revisar que la diferencia sea exactamente la esperada ANTES de ejecutar el export.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("contar"); c.add_argument("export"); c.set_defaults(f=cmd_contar)
    d = sp.add_parser("dividir"); d.add_argument("export"); d.add_argument("-o", "--salida", required=True); d.set_defaults(f=cmd_dividir)
    p = sp.add_parser("parchear"); p.add_argument("export"); p.add_argument("cambios"); p.add_argument("-o", "--salida", required=True); p.set_defaults(f=cmd_parchear)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
