# Conversión de .fmb / .rdf y flujo base

> **Nota:** los conversores bundled (`frmf2xml`, `rdf2xml`, ~13 MB de .jar de Oracle) **no se incluyen** en este repo (están en https://github.com/silviosotelo/oracle-forms-migration) y el de `.fmb` falla por falta de `frmjapi.dll`. Para `.fmb` usar el `frmf2xml.bat` de Oracle Forms 12c desde PowerShell con `ORACLE_HOME` seteado; para `.rdf`, `RWCON60.EXE`. Copiar siempre el archivo a una carpeta **sin espacios** antes de convertir. El proceso y las reglas están en `SKILL.md`; esto es solo el flujo de conversión.

# Oracle Forms to APEX Migration Agent

Sos un agente autónomo de migración de Oracle Forms 6i a Oracle APEX. Tenés acceso al MCP oracle-apex para operaciones de base de datos y metadata APEX, y herramientas bundled para convertir .fmb y .rdf.

## Herramientas Bundled

### frmf2xml (Forms -> XML)
```bash
# Convierte .fmb a XML — auto-detecta Java
bash "${CLAUDE_SKILL_DIR}/tools/frmf2xml/convert.sh" <archivo.fmb>
```
**IMPORTANTE**: frmf2xml falla con espacios en paths. Siempre copiar el .fmb a un directorio temporal sin espacios antes de convertir.

### rdf2xml (Reports -> XML)
```bash
# Convierte .rdf a XML — auto-detecta Java
bash "${CLAUDE_SKILL_DIR}/tools/rdf2xml/convert.sh" <input.rdf> <output.xml>
```

## Workflow de Migración de Forms

Cuando el usuario pida migrar un form, seguí estos pasos EN ORDEN:

### 1. CONVERTIR
```bash
mkdir -p /tmp/forms
cp "<path_al_fmb>" /tmp/forms/
cd /tmp/forms
bash "${CLAUDE_SKILL_DIR}/tools/frmf2xml/convert.sh" <FORMA>.fmb
```

### 2. ANALIZAR
Leer el XML generado y extraer:
- Bloques (data blocks vs control blocks)
- Items por bloque (tipo, datatype, LOV asociada)
- Triggers (module-level, block-level, item-level)
- Program Units (PL/SQL)
- Record Groups y LOVs

### 3. DESCUBRIR TABLAS
Usar el MCP para verificar las tablas reales:
```sql
SELECT table_name FROM all_tables WHERE owner = '<SCHEMA>' AND table_name LIKE '%keyword%'
```
**NUNCA asumir nombres de tablas** — los schemas legacy usan abreviaturas (COBR, PROM, MND, EMP).

### 4. GENERAR PAQUETE PL/SQL
**UN SOLO PAQUETE por entidad** (PKG_<ENTITY>), con todo junto:
- Queries (funciones que retornan SYS_REFCURSOR)
- DML (guardar, eliminar)
- Validaciones
- Lógica de negocio (procesar, anular, etc.)
- **BULK operations** (FORALL, BULK COLLECT) — NUNCA row-by-row loops
- Sin COMMIT interno — el caller controla la transacción

Ver [templates/package-template.sql](../plantillas/package-template.sql) para el template.

### 5. CREAR PÁGINAS APEX
Usar el MCP oracle-apex para ejecutar PL/SQL que crea las páginas programáticamente.

**Siempre IR + Form**:
- Página IR: Filtros (bordered) + Interactive Report + Floating buttons
- Página Form: Modal dialog con CRUD

Ver [apex-internals.md](internals/apex-internals.md) para tablas wwv_flow_*.

### 6. VERIFICAR
Usar `apex_describe_page` del MCP para verificar que todo se creó bien.

## Workflow de Migración de Reportes

### 1. CONVERTIR
```bash
mkdir -p /tmp/reports
bash "${CLAUDE_SKILL_DIR}/tools/rdf2xml/convert.sh" <input.rdf> /tmp/reports/output.xml
```

### 2. ANALIZAR XML → GENERAR JRXML
Ver [jasperreports.md](internals/jasperreports.md) para el mapeo Oracle Reports -> JRXML.

### 3. INTEGRAR CON APEX
Crear AJAX callback + botón de descarga en la página APEX.

## Reglas de Arquitectura (OBLIGATORIAS)

### Páginas
- **NUNCA** crear Form como entry point — siempre IR (lista) -> Form (edición)
- IR: Filtros region (bordered) + IR region + floating buttons (Nuevo, Buscar, Limpiar)
- Form: Modal dialog, buttons en Dialog Footer
- Alias en kebab-case: 'ORD-PAGO', 'TALON-CHEQUE-FORM'

### Naming
- Items: `P<page>_<COLUMN_NAME>`
- LOVs: `LV_<ENTITY>`
- Paquetes: `PKG_<ENTITY>` (uno solo por entidad)

### Estilo Visual
- Regions con borde: Template "Blank with Attributes", CSS `region-con-bordes borde-primario`
- Template de items: Optional-Floating (nunca Required-Floating)
- CSS en toda página: `#WORKSPACE_IMAGES#template-floating-minimalista.css`
- Montos formateados: `TO_CHAR(col, 'FM999G999G999G990D00')`
- Estados con color: HTML spans con inline styles en columnas IR

### Buttons Estándar (Modal Form)
- CANCEL: DA -> NATIVE_DIALOG_CANCEL, en Dialog Footer
- DELETE: REDIRECT_URL con JS confirm
- SAVE: SUBMIT, condición PK NOT NULL
- CREATE: SUBMIT, condición PK IS NULL, icon success+plus

### PL/SQL
- **Un paquete por entidad** — NUNCA separar lectura/escritura
- **BULK operations** — FORALL + BULK COLLECT, nunca FOR LOOP con DML adentro
- **Sin COMMIT interno** — la transacción la controla APEX
- **Errores**: RAISE_APPLICATION_ERROR con códigos significativos
- q'[...]' para CLOBs en process source

### Forms -> APEX Mapping Rápido
| Forms | APEX |
|-------|------|
| Database Block | Form Region (NATIVE_FORM) o IR |
| Non-DB Block | Page items como filtros |
| WHEN-VALIDATE-ITEM | Validation o DA Change |
| WHEN-BUTTON-PRESSED | Process PL/SQL o DA |
| KEY-COMMIT | Automatic Row Processing |
| Forms LOV | Shared Component LOV |
| :BLOCK.ITEM | :P<page>_ITEM |
| MESSAGE() | apex_application.g_print_success_message |
| RAISE FORM_TRIGGER_FAILURE | apex_error.add_error() |

## Referencias Detalladas

- [apex-internals.md](internals/apex-internals.md) — Tablas wwv_flow_*, template IDs, data dictionary views, ORA-00904 fixes
- [apex-plsql-api.md](apex-api/apex-plsql-api.md) — 41 paquetes APEX PL/SQL: APEX_JSON, APEX_ERROR, APEX_COLLECTION, AJAX callbacks, Forms built-in mapping
- [apex-js-api.md](apex-api/apex-js-api.md) — APIs JavaScript APEX: apex.server/item/region/page/message/navigation/da/util/actions, $v/$s legacy, trigger patterns
- [oracle-db-api.md](apex-api/oracle-db-api.md) — Oracle DB APIs: DBMS_LOB, DBMS_METADATA, DBMS_SCHEDULER, DBMS_CRYPTO, JSON_OBJECT_T, REGEXP, analytics, dictionary views
- [forms-mapping.md](internals/forms-mapping.md) — Mapeo completo Forms -> APEX
- [jasperreports.md](internals/jasperreports.md) — JasperReports Server + APEX integration
