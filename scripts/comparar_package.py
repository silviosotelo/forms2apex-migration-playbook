#!/usr/bin/env python3
"""
comparar_package.py - Verifica que el .sql de un package en disco == lo que esta compilado en la base.

Por que: los parches hechos solo en la base (o el cliente que descarta los comentarios '--') hacen que
el archivo entregado difiera de lo que corre. Comparar texto crudo da falsos positivos (espacios,
mayusculas, comentarios); este script tokeniza ambos lados y compara los tokens.

Uso:
  python comparar_package.py ARCHIVO.sql COMPILADO.txt
    ARCHIVO.sql   spec y/o body tal como se entrega (puede traer 'CREATE OR REPLACE', '/' y comentarios)
    COMPILADO.txt texto de la base, una linea por fila:  SELECT text FROM all_source
                  WHERE owner=:o AND name=:n AND type=:t ORDER BY line   (guardar el resultado en un archivo)

Se ignoran: comentarios (-- y /* */), espacios, saltos de linea, el prefijo CREATE [OR REPLACE] [EDITIONABLE],
la barra '/' final y el punto y coma final; las mayusculas fuera de literales.
Sale con codigo 0 si son iguales y 1 si difieren (mostrando el primer token distinto con contexto).
"""
import re
import sys

TOKEN = re.compile(r"""
    (?P<q>[qQ]'(?P<d>[\[\{\(<!~#|]).*?(?P=d)')   # q'[ ... ]' (aprox.: cierra con el mismo delimitador)
  | (?P<s>'(?:[^']|'')*')                         # literal 'texto'
  | (?P<i>"[^"]*")                                # identificador entre comillas
  | (?P<w>[A-Za-z_][A-Za-z0-9_$#]*)               # palabra
  | (?P<n>\d+(?:\.\d+)?)                          # numero
  | (?P<o>\S)                                     # cualquier otro signo
""", re.X | re.S)
CIERRE = {"[": "]", "{": "}", "(": ")", "<": ">"}


def sin_comentarios(t):
    out, i, n = [], 0, len(t)
    while i < n:
        c = t[i]
        if c == "'":
            j = i + 1
            while j < n:
                if t[j] == "'" and j + 1 < n and t[j + 1] == "'":
                    j += 2
                elif t[j] == "'":
                    break
                else:
                    j += 1
            out.append(t[i:j + 1]); i = j + 1
        elif t.startswith("--", i):
            j = t.find("\n", i)
            i = n if j < 0 else j
        elif t.startswith("/*", i):
            j = t.find("*/", i + 2)
            i = n if j < 0 else j + 2
        else:
            out.append(c); i += 1
    return "".join(out)


def tokens(t):
    t = sin_comentarios(t.replace("\r\n", "\n"))
    t = re.sub(r"(?im)^\s*create\s+(or\s+replace\s+)?(editionable\s+|noneditionable\s+)?", "", t, count=1)
    toks = []
    for m in TOKEN.finditer(t):
        if m.group("w"):
            toks.append(m.group("w").lower())
        elif m.group("n") or m.group("o") or m.group("i"):
            toks.append(m.group(0))
        else:
            toks.append(m.group(0))  # literales: se comparan tal cual
    while toks and toks[-1] in ("/", ";"):
        toks.pop()
    # el archivo puede traer varias unidades separadas por '/': se descarta el separador
    return [x for x in toks if x != "/"]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    a = tokens(open(sys.argv[1], encoding="utf-8", errors="replace").read())
    b = tokens(open(sys.argv[2], encoding="utf-8", errors="replace").read())
    print(f"tokens: archivo={len(a)} compilado={len(b)}")
    if a == b:
        print("IGUALES")
        return
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            print(f"Primer token distinto en la posicion {i}:")
            print("  archivo  :", " ".join(a[max(0, i - 8):i + 8]))
            print("  compilado:", " ".join(b[max(0, i - 8):i + 8]))
            break
    else:
        print("Un lado es prefijo del otro: sobran tokens al final del", "archivo" if len(a) > len(b) else "compilado")
    sys.exit(1)


if __name__ == "__main__":
    main()
