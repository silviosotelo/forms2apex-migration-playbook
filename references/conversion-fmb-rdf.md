# Conversión de `.fmb` / `.rdf` a XML

Solo la **conversión**. El proceso de migración, las reglas de arquitectura y el estilo están en `SKILL.md` y `patrones-ui-form.md`.

## Herramientas

| Origen | Herramienta que funciona | Notas |
|---|---|---|
| `.fmb` | `frmf2xml.bat` de **Oracle Forms 12c**, desde **PowerShell** con `ORACLE_HOME` seteado | El conversor con `.jar` de `frmf2xml` falla por falta de `frmjapi.dll` nativa |
| `.rdf` | `RWCON60.EXE` (`C:\orant\bin\`) para el `.rex`; `RWRUN60.EXE` para el PDF de referencia | Ver `reportes-rdf.md` |

Los conversores bundled `.jar` (`frmf2xml`, `rdf2xml`, ~13 MB) **no están en esta skill**: viven en
https://github.com/silviosotelo/oracle-forms-migration (`tools/`). Se usan solo si el entorno tiene Java y el módulo no depende de `frmjapi.dll`.

**Copiar siempre el archivo a una carpeta sin espacios** antes de convertir (los conversores fallan con espacios en la ruta). Los fuentes originales
son de solo lectura.

## Pasos

1. **Convertir**: copiar el `.fmb` a `C:\tmp\forms\` y generar `<FORMA>_fmb.xml` en `Migraciones/<nro> - <nombre>/`.
2. **Analizar el XML**: bloques (de datos vs. de control), items (tipo, datatype, LOV asociada, `Formula`/`CalculateMode`), triggers de módulo, bloque e item,
   program units, record groups y LOVs.
3. **Descubrir las tablas reales** con `all_tables` (nunca deducirlas del nombre de la columna: los esquemas legacy usan abreviaturas).
4. **Package**: usar `plantillas/package-template.sql` como esqueleto.
5. **Reportes**: seguir `reportes-rdf.md` y `internals/jasperreports.md`.

## Referencias

- `internals/apex-internals.md` — tablas `wwv_flow_*`, template IDs, vistas del diccionario, errores ORA-00904.
- `internals/forms-mapping.md` — mapeo detallado Forms → APEX.
- `internals/jasperreports.md` — JasperReports Server + APEX.
- `apex-api/apex-plsql-api.md`, `apex-api/apex-js-api.md`, `apex-api/oracle-db-api.md` — APIs.
