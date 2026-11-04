#!/usr/bin/env python3
"""
extraer_fmb_rdf.py - Extrae la LOGICA de un .fmb (Oracle Forms 6i) o .rdf (Oracle Reports 6i)
sin Oracle, sin Java y sin Forms2XML. Solo Python 3 (libreria estandar).

Que recupera (el formato binario ROS.6xxxx guarda el texto en claro):
  - Triggers de Forms (nombre, dueno BLOQUE.ITEM, cuerpo PL/SQL)
  - Program units (nombre, texto)
  - Sentencias SQL (record groups, LOVs, queries de reportes)
  - Referencias :BLOQUE.ITEM usadas por el codigo -> mapa de bloques e items que importan
  - Llamadas a otros formularios / reportes (CALL_FORM, OPEN_FORM, NEW_FORM, RUN_PRODUCT...)
  - Parametros del reporte y triggers de formato/validacion (.rdf), en la medida que estan en claro

Que NO recupera (binario, solo lo entrega Forms2XML): propiedades de items (tipo, longitud,
requerido, LOV asociada), canvases, posiciones, estilos, relaciones master-detail, alertas.
Si el extracto dice algo que contradice el XML de Forms2XML, manda el XML.

Uso:
  python extraer_fmb_rdf.py ARCHIVO.fmb [-o CARPETA] [--json] [--md] [--verificar ARCHIVO_fmb.xml]

Sin -o escribe junto al archivo de entrada. --verificar compara contra un XML de Forms2XML
(si existe) y reporta el porcentaje de triggers y program units recuperados: sirve para saber
cuanto confiar en el extracto de ESE archivo.
"""
import argparse
import html
import json
import os
import re
import struct
import sys

NUL = b"\x00"
TAG = re.compile(r"^P\d+_\d+_[A-Z]{3}_\d{4}")  # marca de fecha que antecede a cada trigger
# nombre de trigger: WHEN-BUTTON-PRESSED (BLOQUE.ITEM) | KEY-EXIT (Pantalla) | NOMBRE (DUENO)
TRG_NAME = re.compile(
    r"^[A-Z][A-Z0-9_$#]*(?:-[A-Z0-9_$#]+)+(?: \(.*\))?$|^[A-Z][A-Z0-9_$#]* \([A-Z0-9_$#. ]+\)$"
)
PU_START = re.compile(rb"(?:PROCEDURE|FUNCTION|PACKAGE BODY|PACKAGE|/\*|--)", re.I)
PU_KW = re.compile(r"^\s*(?:(?:/\*.*?\*/|--[^\n]*\n)\s*)*(PROCEDURE|FUNCTION|PACKAGE(?: BODY)?)\s+([A-Za-z_][A-Za-z0-9_$#]*)", re.I | re.S)
REF = re.compile(r":([A-Za-z_][A-Za-z0-9_$#]*)\.([A-Za-z_][A-Za-z0-9_$#]*)")
CALLS = re.compile(r"\b(CALL_FORM|OPEN_FORM|NEW_FORM|RUN_PRODUCT|RUN_REPORT_OBJECT|CALL_QUERY|HOST|DO_KEY|EXECUTE_TRIGGER|SHOW_LOV|LIST_VALUES|SET_LOV_PROPERTY|SET_ITEM_PROPERTY|SET_BLOCK_PROPERTY)\s*\(([^)]*)\)", re.I)
SQL_START = re.compile(r"(?is)(?:^|[^A-Za-z0-9_])((?:select|with)\s+.{15,})")


def decodificar(b):
    try:
        return b.decode("cp1252")
    except UnicodeDecodeError:
        return b.decode("latin-1")


def imprimible(b, tolerancia=0.0):
    if not b:
        return False
    malos = sum(1 for c in b if not (c >= 32 or c in (9, 10, 13)) or c == 127)
    return malos <= len(b) * tolerancia


def cadenas_prefijadas(d):
    """Cadenas con prefijo de longitud de 4 bytes big-endian (formato de las tablas de texto)."""
    out, i, n = [], 0, len(d)
    while i < n - 5:
        if d[i] == 0 and d[i + 1] == 0:
            L = struct.unpack(">I", d[i:i + 4])[0]
            if 1 <= L <= 200000 and i + 4 + L <= n and imprimible(d[i + 4:i + 4 + L]):
                out.append((i, decodificar(d[i + 4:i + 4 + L])))
                i += 4 + L
                continue
        i += 1
    return out


def extraer_triggers(S):
    res = []
    for k, (o, s) in enumerate(S):
        if not TAG.match(s):
            continue
        j, cuerpo = k + 1, []
        while j < len(S) and j - k < 800:
            t = S[j][1]
            if "\n" not in t and TRG_NAME.match(t.strip()):
                break
            cuerpo.append(t)
            j += 1
        if j < len(S) and j - k < 800:
            nombre = S[j][1].strip()
            m = re.match(r"^(.*?)(?: \((.*)\))?$", nombre)
            texto = "".join(cuerpo)
            texto = re.sub(r"^BEGIN\n", "", texto)
            texto = re.sub(r"\nEND;$", "", texto)
            res.append({"nombre": m.group(1), "dueno": m.group(2) or "", "cuerpo": texto, "offset": o})
    return res


def extraer_program_units(d, S):
    """Texto precedido de un largo de 2 bytes big-endian. Tolera bytes binarios incrustados."""
    cand = []
    for m in PU_START.finditer(d):
        p = m.start()
        if p < 2:
            continue
        L = int.from_bytes(d[p - 2:p], "big")
        if not (15 <= L <= 65000) or p + L > len(d):
            continue
        bruto = d[p:p + L]
        if not imprimible(bruto, 0.10):
            continue
        texto = decodificar(bruto.replace(NUL, b"")).strip()
        if not PU_KW.match(texto) or not re.search(r"(;|\*/)\s*$", texto):
            continue
        cand.append((p, p + L, texto))
    # descartar los contenidos dentro de otro
    cand.sort(key=lambda c: (c[0], -(c[1] - c[0])))
    final, fin = [], -1
    for p, e, t in cand:
        if p >= fin:
            final.append((p, e, t))
            fin = e
    nombres = {}
    for o, s in S:  # nombre: cadena identificador que antecede al texto
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$#]*", s):
            nombres[o] = s
    res = []
    for p, e, t in final:
        m = PU_KW.match(t)
        res.append({"nombre": m.group(2), "tipo": m.group(1).upper(), "texto": t, "offset": p})
    return res


def extraer_sql(d, S):
    vistos, res = set(), []
    # 1) grupos contiguos de cadenas prefijadas (consultas partidas en trozos)
    grupos, actual, fin = [], [], -1
    for o, s in S:
        if actual and o != fin:
            grupos.append(actual)
            actual = []
        actual.append((o, s))
        fin = o + 4 + len(s.encode("cp1252", "replace"))
    if actual:
        grupos.append(actual)
    textos = ["".join(s for _, s in g) for g in grupos]
    # 2) corridas imprimibles sueltas
    for m in re.finditer(rb"[\x20-\x7e\xa0-\xff\r\n\t]{25,}", d):
        textos.append(decodificar(m.group(0)))
    for t in textos:
        m = SQL_START.search(t)
        if not m:
            continue
        sql = m.group(1).strip()
        if len(sql) < 25 or not re.search(r"(?i)\bfrom\b|\bselect\b.*\bfrom\b|\bunion\b|\bdual\b", sql):
            continue
        clave = re.sub(r"\s+", "", sql)[:300]
        if clave in vistos or any(clave in v for v in vistos if len(v) > len(clave)):
            continue
        vistos.add(clave)
        res.append(sql)
    return res


def extraer_plsql_rdf(S):
    """En .rdf el cuerpo PL/SQL viene como cadena prefijada con el nombre justo antes."""
    res, prev = [], ""
    for o, s in S:
        t = s.strip()
        if re.match(r"(?is)^(function|procedure|begin|declare|package)\b", t) and len(t) > 15:
            res.append({"nombre": prev, "texto": t, "offset": o})
        elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$#]*", t):
            prev = t
    return res


def analizar(path):
    d = open(path, "rb").read()
    ext = os.path.splitext(path)[1].lower()
    cab = d[:9].decode("latin-1", "replace")
    S = cadenas_prefijadas(d)
    out = {
        "archivo": os.path.basename(path),
        "tipo": "reporte (.rdf)" if ext == ".rdf" else "formulario (.fmb)",
        "cabecera": cab,
        "bytes": len(d),
    }
    if ext == ".rdf":
        out["plsql"] = extraer_plsql_rdf(S)
        out["triggers"], out["program_units"] = [], []
    else:
        out["triggers"] = extraer_triggers(S)
        out["program_units"] = extraer_program_units(d, S)
        out["plsql"] = []
    out["sql"] = extraer_sql(d, S)
    codigo = "\n".join(
        [t["cuerpo"] for t in out["triggers"]]
        + [p["texto"] for p in out["program_units"]]
        + [p["texto"] for p in out["plsql"]]
    )
    refs = {}
    for b, i in REF.findall(codigo):
        k = (b.upper(), i.upper())
        refs[k] = refs.get(k, 0) + 1
    out["referencias"] = [{"bloque": b, "item": i, "usos": n} for (b, i), n in sorted(refs.items())]
    llamadas = {}
    for fn, arg in CALLS.findall(codigo):
        k = fn.upper() + "(" + re.sub(r"\s+", " ", arg.strip())[:80] + ")"
        llamadas[k] = llamadas.get(k, 0) + 1
    out["llamadas"] = [{"llamada": k, "usos": n} for k, n in sorted(llamadas.items())]
    return out


def a_markdown(r):
    L = [f"# Extracto de {r['archivo']}", "",
         f"- Tipo: {r['tipo']}  | cabecera `{r['cabecera']}`  | {r['bytes']:,} bytes",
         f"- Triggers: {len(r['triggers'])} | Program units: {len(r['program_units'])} | "
         f"PL/SQL de reporte: {len(r['plsql'])} | SQL: {len(r['sql'])}",
         "",
         "> Extracto de texto sin Oracle. No incluye propiedades de items, canvases ni posiciones "
         "(eso solo lo da Forms2XML). Si hay XML, el XML manda.", ""]
    if r["triggers"]:
        L += ["## Triggers", ""]
        for t in r["triggers"]:
            L += [f"### {t['nombre']}" + (f"  ({t['dueno']})" if t["dueno"] else ""), "```plsql", t["cuerpo"].strip(), "```", ""]
    if r["program_units"]:
        L += ["## Program units", ""]
        for p in r["program_units"]:
            L += [f"### {p['tipo']} {p['nombre']}", "```plsql", p["texto"], "```", ""]
    if r["plsql"]:
        L += ["## PL/SQL del reporte", ""]
        for p in r["plsql"]:
            L += [f"### {p['nombre'] or '(sin nombre)'}", "```plsql", p["texto"], "```", ""]
    if r["sql"]:
        L += ["## SQL (record groups, LOVs, queries)", ""]
        for i, q in enumerate(r["sql"], 1):
            L += [f"### SQL {i}", "```sql", q, "```", ""]
    if r["referencias"]:
        L += ["## Referencias :BLOQUE.ITEM usadas por el codigo", "", "| Bloque | Item | Usos |", "|---|---|---|"]
        L += [f"| {x['bloque']} | {x['item']} | {x['usos']} |" for x in r["referencias"]]
        L.append("")
    if r["llamadas"]:
        L += ["## Llamadas a otros modulos / built-ins relevantes", "", "| Llamada | Usos |", "|---|---|"]
        L += [f"| `{x['llamada']}` | {x['usos']} |" for x in r["llamadas"]]
        L.append("")
    return "\n".join(L)


def verificar(r, xml_path):
    import xml.etree.ElementTree as ET
    root = ET.parse(xml_path).getroot()
    norm = lambda t: re.sub(r"\s+", "", t or "")
    xt = [html.unescape(e.attrib.get("TriggerText", "")) for e in root.iter() if e.tag.endswith("Trigger")]
    xp = [html.unescape(e.attrib.get("ProgramUnitText", "") or "") for e in root.iter() if e.tag.endswith("ProgramUnit")]
    bt = [norm(t["cuerpo"]) for t in r["triggers"]]
    bp = [norm(p["texto"]) for p in r["program_units"]]
    et = sum(1 for t in xt if norm(t) and any(norm(t) in b for b in bt))
    ep = sum(1 for t in xp if norm(t) and norm(t) in bp)
    print(f"Verificacion contra {os.path.basename(xml_path)}:")
    print(f"  triggers      : {et}/{len(xt)} recuperados")
    print(f"  program units : {ep}/{len(xp)} recuperados "
          f"(los que faltan suelen ser librerias estandar de Forms o con binario incrustado)")


def main():
    ap = argparse.ArgumentParser(description="Extrae triggers, program units y SQL de .fmb/.rdf sin Oracle.")
    ap.add_argument("archivo")
    ap.add_argument("-o", "--salida", help="carpeta de salida (por defecto, junto al archivo)")
    ap.add_argument("--json", action="store_true", help="escribir solo JSON")
    ap.add_argument("--md", action="store_true", help="escribir solo Markdown")
    ap.add_argument("--verificar", metavar="XML", help="comparar contra un XML de Forms2XML")
    a = ap.parse_args()
    if not os.path.isfile(a.archivo):
        sys.exit("No existe: " + a.archivo)
    r = analizar(a.archivo)
    carpeta = a.salida or os.path.dirname(os.path.abspath(a.archivo))
    os.makedirs(carpeta, exist_ok=True)
    base = os.path.join(carpeta, os.path.splitext(os.path.basename(a.archivo))[0] + "_extracto")
    if not a.json:
        open(base + ".md", "w", encoding="utf-8").write(a_markdown(r))
        print("Escrito", base + ".md")
    if not a.md:
        json.dump(r, open(base + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("Escrito", base + ".json")
    print(f"triggers={len(r['triggers'])} program_units={len(r['program_units'])} plsql_rdf={len(r['plsql'])} sql={len(r['sql'])} "
          f"referencias={len(r['referencias'])}")
    if a.verificar:
        verificar(r, a.verificar)


if __name__ == "__main__":
    main()
