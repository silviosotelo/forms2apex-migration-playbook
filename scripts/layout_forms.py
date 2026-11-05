#!/usr/bin/env python3
"""layout_forms.py - arma el LAYOUT real de un formulario a partir del XML de Forms2XML.

Uso:  python layout_forms.py MODULO_fmb.xml [-o salida.md]

Por cada canvas (y pestaña) agrupa los items en FILAS segun su YPosition y los ordena por XPosition,
y sugiere un colspan sobre la grilla de 12 de APEX segun el ancho relativo. Asi la ficha APEX copia
la disposicion del original en lugar de apilar los items uno debajo del otro.

Las unidades del XML (X/Y/Width/Height) son las del modulo; solo importan las proporciones.
Sin XML no hay layout: ver references/conversion-fmb-rdf.md (seccion Layout).
"""
import argparse, re, sys
import xml.etree.ElementTree as ET


def loc(tag):
    return tag.rsplit('}', 1)[-1]


def num(v, d=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def cargar(path):
    root = ET.parse(path).getroot()
    canvases, items = {}, []
    for el in root.iter():
        t = loc(el.tag)
        if t == 'Canvas':
            canvases[el.get('Name')] = el.attrib
        elif t == 'Item':
            items.append(el)
    return canvases, items


def filas(its):
    """Agrupa por Y: un item entra en la fila si su Y cae dentro de media altura de la fila."""
    its = sorted(its, key=lambda i: (i['y'], i['x']))
    out = []
    for i in its:
        for f in out:
            if abs(i['y'] - f['y']) <= max(f['h'], i['h'], 1) * 0.6:
                f['items'].append(i)
                f['h'] = max(f['h'], i['h'])
                break
        else:
            out.append({'y': i['y'], 'h': i['h'], 'items': [i]})
    for f in out:
        f['items'].sort(key=lambda i: i['x'])
    return out


def colspans(row, ancho):
    """Reparte 12 columnas en proporcion al ancho de cada item (minimo 2)."""
    its = row['items']
    tot = sum(i['w'] for i in its) or 1
    cols = [max(2, round(12 * i['w'] / tot)) for i in its]
    while sum(cols) > 12 and max(cols) > 2:
        cols[cols.index(max(cols))] -= 1
    while sum(cols) < 12:
        cols[cols.index(max(cols))] += 1
    for i, c in zip(its, cols):
        i['col'] = c


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('xml')
    ap.add_argument('-o', '--out')
    a = ap.parse_args()
    canvases, items = cargar(a.xml)

    por = {}
    for el in items:
        at = el.attrib
        cv = at.get('CanvasName')
        if not cv:           # items sin canvas (no visibles): se listan aparte
            cv = '(sin canvas)'
        por.setdefault((cv, at.get('TabPageName', '')), []).append({
            'name': at.get('Name'), 'prompt': at.get('Prompt', ''), 'tipo': at.get('ItemType', ''),
            'x': num(at.get('XPosition')), 'y': num(at.get('YPosition')),
            'w': num(at.get('Width')), 'h': num(at.get('Height'), 1),
            'req': at.get('Required') == 'true', 'vis': at.get('Visible') != 'false',
            'mask': at.get('FormatMask', ''), 'lov': at.get('LovName', ''),
            'bloque': (el.get('BlockName') or '')})

    L = ['# Layout del formulario (desde Forms2XML)', '',
         'Filas por posicion Y; dentro de cada fila, de izquierda a derecha. `col` = colspan sugerido sobre 12.',
         'Es una sugerencia: respetar el ORDEN y el agrupamiento del original, ajustar los anchos mirando la pantalla.', '']
    for (cv, tab), its in sorted(por.items()):
        c = canvases.get(cv, {})
        ancho = num(c.get('Width')) or max((i['x'] + i['w'] for i in its), default=1)
        L.append(f"## Canvas `{cv}`" + (f" - pestana `{tab}`" if tab else '') +
                 (f"  (tipo {c.get('CanvasType')}, {c.get('Width')} x {c.get('Height')})" if c else ''))
        if cv == '(sin canvas)':
            L.append('Items sin canvas (no se muestran): ' + ', '.join(i['name'] for i in its))
            L.append('')
            continue
        for n, f in enumerate(filas(its), 1):
            colspans(f, ancho)
            L.append(f"- Fila {n} (y={int(f['y'])})")
            for i in f['items']:
                extra = ' obligatorio' if i['req'] else ''
                extra += f" mascara {i['mask']}" if i['mask'] else ''
                extra += f" LOV {i['lov']}" if i['lov'] else ''
                L.append(f"  - col {i['col']:>2} | `{i['name']}` \"{i['prompt']}\" ({i['tipo']}, x={int(i['x'])}, w={int(i['w'])}){extra}")
        L.append('')
    txt = '\n'.join(L)
    if a.out:
        open(a.out, 'w', encoding='utf-8').write(txt)
        print('escrito', a.out)
    else:
        sys.stdout.buffer.write(txt.encode('utf-8', 'replace'))


if __name__ == '__main__':
    main()
