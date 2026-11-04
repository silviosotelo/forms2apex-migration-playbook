# Pantallas de reporte: `.rdf` → PDF de referencia → JasperReports

Aplica cuando el formulario imprime: el `.rdf` original es **la fuente de verdad visual**. Nunca reconstruir el
reporte "a ojo" desde el SQL.

## 1. Sacar el PDF de referencia

```
RWRUN60.EXE report=X.rdf userid=anamnesis/<pass>@devnew \
  destype=file desname=original.pdf desformat=pdf batch=yes <params>
```

**"PDF generado con éxito" NO significa que tenga datos.** El archivo pesa y termina en `%%EOF` igual estando
vacío. **Abrir el PDF y leerlo siempre**: en una tanda real, 16 de 34 PDFs salieron vacíos (sólo título y
"Total: 0") pese a que el script reportaba éxito.

## 2. Si sale vacío o con error: leer el `.fmb` que lo llama

Buscar en el form la `PROCEDURE VISUALIZAR` (o equivalente) con `ADD_PARAMETER` / `RUN_PRODUCT` /
`Rwrun60.exe` armado a mano, y sacar de ahí:

- **El formato de fecha real** que Forms manda (`TO_CHAR(...,'DD-MM-RR')` es el más común, pero **varía por
  reporte**). Confirmar contra el `.fmb` o contra el `TO_DATE(` embebido en el propio `.rdf`.
- **El scope real**: puede que el reporte no liste por fecha sino que reimprima **un** documento puntual.
- **Qué parámetros pasa realmente**: Forms puede omitir parámetros que un extractor heurístico sugiere, o
  mandar valores fijos.

## 3. Errores conocidos y su causa (no reinventar el diagnóstico)

| Síntoma | Causa casi segura |
|---|---|
| `ORA-06502` / `ORA-01821` / `ORA-01858` / `ORA-01847` en `beforepform` | Formato de fecha equivocado, no un bug del reporte |
| Vacío pese a fechas correctas | Parámetro con **default viejo embebido en el `.rdf`** que se aplica en silencio (buscar `P_<nombre>` seguido de un número en el binario) |
| Vacío y el reporte lee de una tabla `_TMP` / staging | La tabla no está poblada en DEVNEW: depende de un proceso de carga previo. Avisar, no poblarla sin OK |
| `REP-1401 'beforepform'` con un parámetro "opcional" | Es obligatorio de hecho: el `IF :P_X IS NOT NULL THEN` que lo protegía está **comentado** |
| `REP-0108: Fichero no encontrado` | Recurso de red (logo, boilerplate) inalcanzable: infraestructura, no parámetros |

Si después de todo esto el reporte sigue sin traer datos o el error no encaja en ningún patrón conocido:
**parar y avisar** con el caso puntual (qué se probó, qué dio). No inventar workarounds ni adivinar parámetros
indefinidamente.

## 4. Coordenadas y formato

`RWCON60.EXE` convierte el `.rdf` a `.rex` para sacar queries, format masks y **coordenadas**
(unidades de **8192 por pulgada** → `pt = valor * 72 / 8192`). Los textos de los labels **no** están en el
`.rex` (van en blobs): salen del PDF.

Portar 1:1: **Courier New** (`pdfFontName="Courier"` / `"Courier-Bold"`), recuadros, headers con fondo, bloque
de firmas, "Página X de Y". Logo institucional: `repo:/Reportes/Recursos/Imagenes/logo_2024.svg`.
Separadores de miles determinísticos desde SQL:
`REPLACE(TO_CHAR(x,'FM999,999,999,990'), ',', '.')`.

## 5. JRXML y publicación

- Crear uno **nuevo** partiendo de un reporte que ya funciona como template; no reusar el de otro reporte vivo.
- La query va por **package**: `{call PKG_REP_<MODULO>.pp_obtener_<datos>($P{P1}, $P{ORACLE_REF_CURSOR})}` con
  `<parameter name="ORACLE_REF_CURSOR" class="java.sql.ResultSet" isForPrompting="false"/>`, o una función
  PIPELINED consultada con SQL directo. Nunca SQL inline armado por el propio reporte.
- No usar `isStretchWithOverflow` (removido en JasperReports 6.x).
- Subir con **delete + upload** (un `update` no invalida el `.jasper` cacheado).
- Probar el PDF contra el server **antes** de integrarlo con APEX.

## 6. Integración con la página

- El endpoint es un **Ajax Callback de la página**, nunca un Application Process: un Application Process **no
  viaja con el export de la página** y rompe el pase.
- JS: `apex.navigation.openInNewWindow(apex.server.url({ p_request: "application_process=<proc>", x01: … }))`.
- El proceso llama a `pkg_jasperreports_server.descarga_reporte` con los arrays de nombres y valores.
- Verificación: en el Network tab, `200 application/pdf`, y **el PDF comparado contra el original** del
  `RWRUN60` para el mismo registro, página por página, no sólo la primera.
