# Guia Completa: Migracion Oracle Forms 6i a Oracle APEX

Todos los patrones, reglas, errores comunes y conocimiento acumulado para migrar Oracle Forms a APEX usando Claude Code + oracle-apex MCP + oracle-forms-migration skill.

---

## 1. INSTALACION

```bash
# 1. MCP Server (conexion a Oracle DB + APEX)
git clone https://github.com/silviosotelo/oracle-apex-mcp-server.git
cd oracle-apex-mcp-server
npm run install:claude

# 2. Skill de migracion (Forms -> APEX)
git clone https://github.com/silviosotelo/oracle-forms-migration.git
cd oracle-forms-migration
bash scripts/install.sh    # Linux/Mac/Git Bash
# scripts\install.bat      # Windows CMD

# 3. Reiniciar Claude Code
```

---

## 2. ARQUITECTURA OBLIGATORIA

### Dos paginas por entidad (SIEMPRE)
- **Pagina IR** (Interactive Report): lista con filtros, busqueda, export
- **Pagina Form** (Modal): CRUD (Create/Read/Update/Delete)
- **NUNCA** usar Form como pagina principal sin IR detras

### Un paquete PL/SQL por entidad (SIEMPRE)
- Nombre: `PKG_<ENTITY>` (ej: `PKG_ORDEN_PAGO`)
- **NUNCA** separar en `_LECTURA` / `_ESCRITURA` — todo junto
- Contiene: queries (get_lista, get_detalle), DML (guardar, eliminar), validaciones (validar), logica de negocio (procesar, anular, procesar_lote)
- **BULK operations**: FORALL, BULK COLLECT — NUNCA row-by-row FOR LOOP con DML adentro
- **Sin COMMIT interno** — APEX controla la transaccion
- **RETURNING INTO** para inserts (obtener ID generado)
- **SQL%ROWCOUNT** despues de cada DML para verificar filas afectadas

---

## 3. NAMING CONVENTIONS

| Elemento | Patron | Ejemplo |
|----------|--------|---------|
| Page Items | P<page>_<COLUMN_NAME> | P937_ID_ORDEN_PAGO |
| LOVs | LV_<ENTITY> | LV_EMPRESA |
| Paquetes | PKG_<ENTITY> | PKG_ORDEN_PAGO |
| Page Alias | kebab-case | ORD-PAGO, TALON-CHEQUE-FORM |
| Auth Scheme | MN_<module>_DEF_<prog_id> | MN_ORD_PAGO_DEF_827 |

---

## 4. ESTILO VISUAL

- **Regions con borde**: Template "Blank with Attributes", CSS class `region-con-bordes borde-primario`
- **Template de items**: Optional-Floating (NUNCA Required-Floating)
- **CSS en toda pagina**: `#WORKSPACE_IMAGES#template-floating-minimalista.css`
- **Montos**: `TO_CHAR(col, 'FM999G999G999G990D00')`
- **Estados con color**: HTML spans en columnas IR con display_text_as = 'WITHOUT_MODIFICATION'

---

## 5. BOTONES ESTANDAR (Modal Form)

| Boton | Tipo | Comportamiento |
|-------|------|----------------|
| CANCEL | DEFINED_BY_DA | DA -> NATIVE_DIALOG_CANCEL, en Dialog Footer, icon warning+arrow-left |
| DELETE | REDIRECT_URL | JS confirm -> delete process -> redirect a IR, en Dialog Footer |
| SAVE | SUBMIT | Condicion PK NOT NULL (database_action UPDATE) |
| CREATE | SUBMIT | Condicion PK IS NULL (database_action INSERT), icon success+plus |

---

## 6. FORMS -> APEX MAPPING

### Bloques -> Regiones
| Forms Block | APEX Region |
|-------------|-------------|
| Data block (table/view) | IR (listado) + Form (CRUD) |
| Master-detail blocks | Master-Detail pattern, FK relationship |
| Control block (no base table) | Static Content, hidden items, parametros |
| Non-database block (UI) | Static Content con items source NULL |

### Items -> Page Items
| Forms Item | APEX Item |
|------------|-----------|
| Text (VARCHAR2) | Text Field |
| Number | Number Field (con format mask) |
| Date | Date Picker |
| Checkbox | Checkbox |
| Radio | Radio Group |
| List | Select List + Shared LOV |
| Display (computed) | Display Only + PL/SQL function |
| Hidden | Hidden item |

### Triggers -> Processes, Validations, DAs
| Trigger | APEX |
|---------|------|
| WHEN-NEW-FORM-INSTANCE | Before Header process |
| WHEN-NEW-BLOCK-INSTANCE | Region load / DA on page load |
| PRE-QUERY | Ajustes al source query de la region |
| POST-QUERY | Columnas computadas en SQL |
| PRE/POST-INSERT/UPDATE/DELETE | PL/SQL empaquetado desde page process |
| WHEN-VALIDATE-ITEM | Validation o DA Change + AJAX |
| WHEN-VALIDATE-RECORD | Validation a nivel record |
| KEY-COMMIT | Boton SAVE + submit process |
| KEY-EXIT | Boton CANCEL + branch |
| WHEN-BUTTON-PRESSED | DA Click + PL/SQL/AJAX |
| ON-ERROR | apex.message.showErrors() + apex_debug.error() |
| ON-MESSAGE | apex.message.showPageSuccess() |
| :BLOCK.ITEM | :P<page>_ITEM |
| MESSAGE() | apex_application.g_print_success_message |
| RAISE FORM_TRIGGER_FAILURE | apex_error.add_error() |

### Program Units -> Packages
- TODO va a paquetes de base de datos
- APEX solo llama procedimientos/funciones empaquetadas
- Refactorizar utilidades cross-cutting en paquetes dedicados

### Seguridad
| Forms | APEX |
|-------|------|
| Menu-based security | Authorization Schemes en pages/regions |
| Role/RESP-based | Auth Schemes + pkg_security.has_permission |
| Parameter-based | Session state + Application Items |

---

## 7. APEX INTERNAL TABLES (wwv_flow_*) — REFERENCIA CRITICA

### ID Generation
```sql
SELECT wwv_flow_id.next_val INTO v_id FROM DUAL;
```
Nunca inline en VALUES. Nunca hardcodear IDs de JSON (precision loss con 18+ digitos).

### Workspace Context
```sql
apex_util.set_security_group_id(<workspace_id>);
```
**Siempre** antes de cualquier operacion con wwv_flow_*.

### UPDATE/DELETE seguro
Usar `WHERE page_id=X AND plug_source_type='Y'` — nunca `WHERE id=<big_number>` (precision loss).

---

### wwv_flow_steps (Pages)

| Column | Valor | Notas |
|--------|-------|-------|
| user_interface_id | (resolver dinamicamente) | **SIN ESTO LA PAGINA ES INVISIBLE** |
| page_component_map | '18' / '02' / '03' | IR / Form-Modal / Blank |
| step_title | 'Titulo' | Mismo que name |
| alias | 'PAGE-ALIAS' | Kebab-case, SIEMPRE setear |
| page_mode | 'NORMAL' / 'MODAL' | |
| step_template | NULL / (modal dialog tmpl) | NULL normal, template para modal |
| include_apex_css_js_yn | 'Y' | |
| first_item | 'NO_FIRST_ITEM' | |
| reload_on_submit | 'S' | |
| warn_on_unsaved_changes | 'Y' | |
| autocomplete_on_off | 'OFF' | |
| css_file_urls | '#WORKSPACE_IMAGES#template-floating-minimalista.css' | |

**Resolver user_interface_id:**
```sql
SELECT id FROM wwv_flow_user_interfaces WHERE flow_id = <app_id>;
```

**Modal pages:** `page_mode = 'MODAL'`, `step_template` = dialog template ID
**Normal pages:** `page_mode = 'NORMAL'`, `step_template` = NULL

---

### wwv_flow_page_plugs (Regions)

**NOT NULL obligatorios:**
- `translate_title`: 'Y'
- `include_in_reg_disp_sel_yn`: 'Y' o 'N'
- `plug_customized`: 0 (numero, no string)
- `plug_caching`: 'NOCACHE' (NO 'NOT_CACHED')
- `security_group_id`: workspace ID

**Region Types (plug_source_type):**
- `NATIVE_STATIC` = Static Content (Filtros, Botones, Title Bar)
- `NATIVE_IR` = Interactive Report
- `NATIVE_FORM` = Form Region (DML)
- `NATIVE_BREADCRUMB` = Breadcrumb (necesita menu_id!)
- **NUNCA** `NATIVE_DISPLAY_STATIC` — NO EXISTE, causa ORA-01403

**NATIVE_STATIC attributes:**
- attribute_01 = 'N', attribute_02 = 'TEXT', attribute_03 = 'Y'

**NATIVE_FORM DEBE tener:**
- query_type = 'TABLE', query_table = 'TABLE_NAME', is_editable = 'Y'
- attribute_01 a attribute_05 = NULL (NO el nombre de tabla!)
- plug_query_options = NULL (NO 'DERIVED_REPORT_COLUMNS')

**Dialog Footer (para botones en modal):**
- plug_display_point = 'REGION_POSITION_03'

**Title Bar sin breadcrumb:**
- Usar NATIVE_STATIC con template Title Bar
- Position: REGION_POSITION_01, sequence 1

---

### wwv_flow_step_items (Page Items)

**NOT NULL obligatorios:**
- `data_type`: 'VARCHAR' (NO 'VARCHAR2')
- `is_primary_key`: 'Y' o 'N'
- `is_query_only`: 'N'
- `protection_level`: 'N'

**Para items en NATIVE_FORM:**
- `item_source_plug_id` **DEBE** apuntar al region ID del NATIVE_FORM
  - Sin esto -> `NO_PRIMARY_KEY_ITEM` error
- `source`: nombre de columna en la tabla (ej: 'ID_ORDEN')
- `source_data_type`: tipo Oracle ('NUMBER', 'VARCHAR2', 'DATE')
- `item_field_template`: resolver Optional-Floating dinamicamente
- `prompt`: **SIEMPRE** setear para items visibles (sin esto, items aparecen sin label)

**Resolver template Optional-Floating:**
```sql
SELECT template_id FROM apex_application_templates
WHERE application_id = <app_id> AND template_type = 'Field' AND template_name LIKE '%Optional%Float%';
```

---

### wwv_flow_worksheets (IR)

- FK a region via `region_id`
- `detail_link`: URL con `#COLUMN#` substitutions
- `detail_link_text`: `<img src="#IMAGE_PREFIX#app_ui/img/icons/apex-edit-pencil.png" class="apex-edit-pencil" alt="">`
- **NUNCA** insertar `UNIQUELY_IDENTIFY_ROWS_BY` — es columna virtual (ORA-54013)
- **Cada columna en detail_link #...# debe existir en el SQL query**

**detail_link format:**
```
f?p=&APP_ID.:<form_page>:&SESSION.::&DEBUG.:RP,<form_page>:P<form_page>_<PK>:#PK_COLUMN#
```

---

### wwv_flow_worksheet_columns

- `db_column_name`: DEBE coincidir EXACTO con alias SQL (case-sensitive)
- `column_type`: 'NUMBER' para numerico, 'STRING' para text/TO_CHAR, 'DATE' para fechas
- `display_as`: 'TEXT' (no 'WITHOUT_MODIFICATION')
- `display_text_as`: 'ESCAPE_SC' (default) o 'WITHOUT_MODIFICATION' (para HTML como estados)
- `lov_display_null`: 'YES'/'NO' (NO 'Y'/'N')
- **Cantidad de columnas DEBE coincidir EXACTO con el SELECT** — mismatch = ORA-01403
- **NUNCA** crear columna 'LINK' — usar native detail_link en worksheet

---

### wwv_flow_worksheet_rpts (Default Reports)
- `application_user = 'APXWS_DEFAULT'`
- `is_default = 'Y'`
- `report_columns`: colon-separated (ej: 'COL1:COL2:COL3')
- Solo referenciar columnas que existen en worksheet_columns

---

### wwv_flow_step_processing (Processes)

| Tipo | process_point | attribute_01 | region_id |
|------|--------------|--------------|-----------|
| NATIVE_FORM_INIT | BEFORE_HEADER | NULL | form region ID |
| NATIVE_FORM_DML | AFTER_SUBMIT | 'REGION_SOURCE' | form region ID |
| NATIVE_CLOSE_WINDOW | AFTER_SUBMIT | 'REQUEST' | NULL |

---

### wwv_flow_page_da_events (Dynamic Actions)

- `bind_type = 'bind'` (**NOT NULL** obligatorio, no 'live')
- `event_result = 'TRUE'` (**NOT NULL** obligatorio, no 'true' minuscula)
- `triggering_element_type`: 'BUTTON', 'JQUERY_SELECTOR', 'ITEM', 'REGION'
- `triggering_element`: CSS selector o nombre del item/boton

### wwv_flow_page_da_actions

- `action`: 'NATIVE_JAVASCRIPT_CODE', 'NATIVE_SUBMIT_PAGE', 'NATIVE_REFRESH', 'NATIVE_HIDE', 'NATIVE_SHOW', 'NATIVE_SET_VALUE', 'NATIVE_EXECUTE_PLSQL_CODE', 'NATIVE_DIALOG_CANCEL'
- `attribute_01`: JavaScript code o PL/SQL code segun action type
- `event_id`: FK a wwv_flow_page_da_events.id
- `execute_on_page_init`: 'Y' o 'N'

---

### wwv_flow_step_buttons (Buttons)

- `button_position`: 'REGION_TEMPLATE_CLOSE' (Cancel), 'REGION_TEMPLATE_DELETE' (Delete), 'REGION_TEMPLATE_NEXT' (Save/Create)
- `button_action`: 'SUBMIT', 'REDIRECT_URL', 'DEFINED_BY_DA'
- `icon_css_classes`: 'fa-arrow-left' (Cancel), 'fa-trash-o' (Delete), 'fa-save' (Save), 'fa-plus' (Create)

---

## 8. IR PROGRAMATICO — CHECKLIST

Crear un Interactive Report funcional requiere los **4 componentes** o da ORA-01403:

1. **Region** (`wwv_flow_page_plugs`) con `plug_source_type = 'NATIVE_IR'` y el SQL query en `plug_source`
2. **Worksheet** (`wwv_flow_worksheets`) con FK `region_id`
3. **Worksheet Columns** (`wwv_flow_worksheet_columns`) con FK `worksheet_id` — cantidad = columnas del SELECT, `column_identifier` = A, B, C...
4. **Default Report** (`wwv_flow_worksheet_rpts`) con `application_user = 'APXWS_DEFAULT'` y `is_default = 'Y'`

**Falta cualquiera = pagina IR rota/vacia.**

---

## 9. VIRTUAL COLUMN PARA FORMS

Cuando el Form Region usa query (no tabla), agregar columna virtual para PK:
```sql
SELECT id, col1, col2, ..., id AS UNIQUELY_IDENTIFY_ROWS_BY FROM my_table
```
Esto le dice a APEX cual columna es la PK para operaciones DML.

---

## 10. AUTORIZACION

```sql
dev_permiso_apx(p_nIdPrograma => :APP_PAGE_ID, p_vPermisoDml => 'S')
```
- `p_vPermisoDml`: 'S' = select/ver, 'I' = insert, 'U' = update, 'D' = delete
- Se aplica como Authorization Scheme en paginas, regiones, botones, o items

---

## 11. FORMS XML — CLAVES PARA PARSING

Despues de convertir .fmb con frmf2xml:

- `<Block>` -> APEX Region (buscar `QueryDataSourceName` para tabla/view)
- `<Item>` -> APEX Page Item (buscar `ItemType`, `DataType`, `MaximumLength`)
- `<Trigger>` -> APEX Process, Validation, o Dynamic Action (buscar `TriggerType`)
- `<LOV>` -> APEX List of Values (buscar `ListType`, `RecordGroup`)
- `<ProgramUnit>` -> Candidato para procedimiento/funcion en paquete PL/SQL

**DataType codes:** 1=CHAR, 2=NUMBER, 12=DATE, 23=INT, 96=CHAR(fixed), 112=CLOB
**ItemType codes:** 0=hidden, 1=TEXT, 2=text, 3=LIST(SELECT), 4=checkbox, 6=RADIO, 7=CHECK_BOX, 8=DISPLAY_ONLY, 9=display, 12=LONG_TEXT/list, 14=BUTTON

- `DMLDataTargetName` = tabla base para DML
- `QueryDataSourceName` = fuente de query (puede diferir del DML target)
- `TriggerText` = codigo PL/SQL fuente
- `ProgramUnitText` = PL/SQL completo

---

## 12. SCHEMAS LEGACY — PATRONES COMUNES

Los schemas de Oracle Forms 6i usan nombres abreviados:
- `ORD_PAGO` en vez de `ORDEN_PAGO`
- `PREST_SRV` en vez de `PRESTADOR_SERVICIO`
- `COBR`, `PROM`, `MND`, `EMP`, `TRANS`, `PROV`

**SIEMPRE verificar nombres reales:**
```sql
SELECT table_name FROM all_tables WHERE owner='<SCHEMA>' AND table_name LIKE '%keyword%';
```
- `CONTRATO_CLIENTE` es generalmente la tabla central de joins
- `FACTURA_PREPAGA`: los nombres de columnas varian entre schemas (NRO_FACTURA vs NUMERO_FACTURA)

---

## 13. ERRORES COMUNES Y SOLUCIONES

| Error | Causa | Solucion |
|-------|-------|----------|
| ORA-01403 WWV_FLOW_PLUGIN | plug_source_type invalido | Usar NATIVE_STATIC, NO NATIVE_DISPLAY_STATIC |
| ORA-01403 IR page | Worksheet columns != SQL columns | Cantidad y nombres deben coincidir exacto |
| NO_PRIMARY_KEY_ITEM | item_source_plug_id NULL | Setear al ID del region NATIVE_FORM |
| Buttons no aparecen | security_group_id falta | Llamar apex_util.set_security_group_id antes |
| Items sin estilo/label | item_field_template o prompt falta | Usar Optional-Floating y setear prompt siempre |
| Pagina "unknown" sin Run | user_interface_id falta | Resolver con query a wwv_flow_user_interfaces |
| DA INSERT falla | bind_type o event_result NULL | bind_type='bind', event_result='TRUE' |
| ORA-54013 | INSERT en columna virtual | No insertar UNIQUELY_IDENTIFY_ROWS_BY |
| Precision loss en IDs | JavaScript Number overflow | Usar TO_CHAR(id) en queries, WHERE compuestos |
| frmf2xml falla | Espacios en path del .fmb | Copiar .fmb a /tmp/forms/ o C:\temp\forms\ |

---

## 14. APEX DICTIONARY VIEWS — DIFERENCIAS POR VERSION

Estas columnas causan ORA-00904 si usas la version equivocada:
- `APEX_APPLICATIONS.CREATED_ON` — solo APEX 21.1+, usar `LAST_UPDATED_ON`
- `APEX_APPLICATION_PAGES.PAGE_CSS_CLASSES` — solo APEX 20.2+
- `APEX_APPLICATION_PAGE_REGIONS.TEMPLATE` — era `REGION_TEMPLATE` antes de APEX 20.1
- `APEX_APPLICATION_PAGE_DA`: usar `DYNAMIC_ACTION_NAME` (no DA_NAME), `WHEN_EVENT_NAME` (no EVENT_NAME)
- `APEX_APPLICATION_PAGE_VAL`: usar `VALIDATION_FAILURE_TEXT` (no ERROR_MESSAGE)
- `APEX_APPLICATION_LOVS`: usar `LIST_OF_VALUES_NAME` (no LOV_NAME)
- CLOB columns: usar `oracledb.fetchAsString = [oracledb.CLOB]` o `DBMS_LOB.SUBSTR()` en queries

---

## 15. JASPERREPORTS SERVER + APEX INTEGRATION

### Arquitectura
```
APEX Page (Button click)
  -> AJAX Callback (apex.server.process)
    -> PL/SQL (pkg_jasperreports.descarga_reporte)
      -> JasperReports Server REST API
        -> PDF/Excel/HTML
          -> Download al browser
```

### REST API
```
# Login
POST /jasperserver/rest_v2/login
Content-Type: application/x-www-form-urlencoded
j_username=<user>&j_password=<pass>
-> Retorna JSESSIONID cookie

# Ejecutar Reporte
GET /jasperserver/rest_v2/reports/<report_uri>.<format>?<params>
Cookie: JSESSIONID=<session>
Formatos: pdf, xlsx, html, csv, docx
```

### PL/SQL Package
```sql
CREATE OR REPLACE PACKAGE pkg_jasperreports AS
  PROCEDURE descarga_reporte(
    p_report_uri  VARCHAR2,
    p_format      VARCHAR2 DEFAULT 'pdf',
    p_parameters  VARCHAR2 DEFAULT NULL,
    p_filename    VARCHAR2 DEFAULT 'reporte'
  );
END;
/

CREATE OR REPLACE PACKAGE BODY pkg_jasperreports AS

  gc_server_url  CONSTANT VARCHAR2(200) := '<configurar_url_jasper>';
  gc_username    CONSTANT VARCHAR2(50)  := '<configurar_user>';
  gc_password    CONSTANT VARCHAR2(50)  := '<configurar_pass>';

  FUNCTION get_mime_type(p_format VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    RETURN CASE LOWER(p_format)
      WHEN 'pdf'  THEN 'application/pdf'
      WHEN 'xlsx' THEN 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      WHEN 'html' THEN 'text/html'
      WHEN 'csv'  THEN 'text/csv'
      WHEN 'docx' THEN 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ELSE 'application/octet-stream'
    END;
  END;

  FUNCTION login RETURN VARCHAR2 IS
    v_response CLOB;
    v_cookie   VARCHAR2(500);
  BEGIN
    apex_web_service.g_request_headers.DELETE;
    apex_web_service.g_request_headers(1).name := 'Content-Type';
    apex_web_service.g_request_headers(1).value := 'application/x-www-form-urlencoded';

    v_response := apex_web_service.make_rest_request(
      p_url         => gc_server_url || '/rest_v2/login',
      p_http_method => 'POST',
      p_body        => 'j_username=' || gc_username || '&j_password=' || gc_password
    );

    FOR i IN 1..apex_web_service.g_headers.COUNT LOOP
      IF LOWER(apex_web_service.g_headers(i).name) = 'set-cookie'
         AND INSTR(apex_web_service.g_headers(i).value, 'JSESSIONID') > 0 THEN
        v_cookie := REGEXP_SUBSTR(apex_web_service.g_headers(i).value, 'JSESSIONID=[^;]+');
        EXIT;
      END IF;
    END LOOP;
    RETURN v_cookie;
  END;

  PROCEDURE descarga_reporte(
    p_report_uri  VARCHAR2,
    p_format      VARCHAR2 DEFAULT 'pdf',
    p_parameters  VARCHAR2 DEFAULT NULL,
    p_filename    VARCHAR2 DEFAULT 'reporte'
  ) IS
    v_cookie VARCHAR2(500);
    v_url    VARCHAR2(4000);
    v_blob   BLOB;
  BEGIN
    v_cookie := login();
    IF v_cookie IS NULL THEN
      raise_application_error(-20001, 'No se pudo autenticar en JasperReports Server');
    END IF;

    v_url := gc_server_url || '/rest_v2/reports' || p_report_uri || '.' || LOWER(p_format);
    IF p_parameters IS NOT NULL THEN
      v_url := v_url || '?' || p_parameters;
    END IF;

    apex_web_service.g_request_headers.DELETE;
    apex_web_service.g_request_headers(1).name := 'Cookie';
    apex_web_service.g_request_headers(1).value := v_cookie;

    v_blob := apex_web_service.make_rest_request_b(p_url => v_url, p_http_method => 'GET');

    IF apex_web_service.g_status_code != 200 THEN
      raise_application_error(-20002, 'Error HTTP ' || apex_web_service.g_status_code);
    END IF;

    OWA_UTIL.MIME_HEADER(get_mime_type(p_format), FALSE);
    HTP.P('Content-Disposition: attachment; filename="' || p_filename || '.' || LOWER(p_format) || '"');
    HTP.P('Content-Length: ' || DBMS_LOB.GETLENGTH(v_blob));
    OWA_UTIL.HTTP_HEADER_CLOSE;
    WPG_DOCLOAD.DOWNLOAD_FILE(v_blob);
    apex_application.stop_apex_engine;
  END;
END;
/
```

### APEX AJAX Callback Process
```sql
-- Process: DESCARGAR_REPORTE, Type: NATIVE_PLSQL, Point: AJAX_CALLBACK
BEGIN
  pkg_jasperreports.descarga_reporte(
    p_report_uri => apex_application.g_x01,
    p_format     => NVL(apex_application.g_x02, 'pdf'),
    p_parameters => apex_application.g_x03,
    p_filename   => NVL(apex_application.g_x04, 'reporte')
  );
END;
```

### JavaScript (Boton de descarga)
```javascript
function descargarReporte(reportUri, formato, params, filename) {
  var form = document.createElement('form');
  form.method = 'POST';
  form.action = 'f?p=' + $v('pFlowId') + ':' + $v('pFlowStepId') + ':' + $v('pInstance');
  form.target = '_blank';

  function addField(name, value) {
    var input = document.createElement('input');
    input.type = 'hidden'; input.name = name; input.value = value;
    form.appendChild(input);
  }

  addField('x01', reportUri);
  addField('x02', formato || 'pdf');
  addField('x03', params || '');
  addField('x04', filename || 'reporte');
  addField('p_instance', $v('pInstance'));
  addField('p_flow_id', $v('pFlowId'));
  addField('p_flow_step_id', $v('pFlowStepId'));
  addField('p_request', 'APPLICATION_PROCESS=DESCARGAR_REPORTE');

  document.body.appendChild(form);
  form.submit();
  document.body.removeChild(form);
}
```

### Oracle Reports -> JRXML Mapping

| Oracle Reports | JasperReports JRXML |
|----------------|---------------------|
| Data Model Query | `<queryString>` |
| User Parameter | `<parameter>` |
| Formula Column | `<variable>` con expression |
| Summary Column | `<variable calculation="Sum/Count/Avg">` |
| Group | `<group>` con header/footer bands |
| Header Section | `<title>` y `<pageHeader>` |
| Body Section | `<detail>` band |
| Trailer Section | `<summary>` y `<pageFooter>` |
| Boilerplate Text | `<staticText>` |
| Field | `<textField>` con `<textFieldExpression>` |
| Format Mask | attribute `pattern` en textField |
| Conditional Format | `<printWhenExpression>` |

---

## 16. TEMPLATE PL/SQL PACKAGE

```sql
-- Template: PKG_<ENTITY>
-- Un solo paquete por entidad. Queries, DML, validaciones y logica juntos.
-- BULK operations obligatorias. Sin COMMIT interno.

CREATE OR REPLACE PACKAGE PKG_<ENTITY> AS

  -- === QUERIES ===
  FUNCTION get_lista(
    p_fecha_desde  DATE     DEFAULT NULL,
    p_fecha_hasta  DATE     DEFAULT NULL,
    p_filtro1      NUMBER   DEFAULT NULL,
    p_filtro2      VARCHAR2 DEFAULT NULL,
    p_estado       VARCHAR2 DEFAULT NULL
  ) RETURN SYS_REFCURSOR;

  FUNCTION get_detalle(p_id NUMBER) RETURN SYS_REFCURSOR;

  -- === DML ===
  PROCEDURE guardar(
    p_id       IN OUT NUMBER,  -- NULL = insert, NOT NULL = update
    p_campo1   VARCHAR2,
    p_campo2   NUMBER,
    p_campo3   DATE,
    p_usuario  VARCHAR2
  );

  PROCEDURE eliminar(p_id NUMBER);

  -- === VALIDACIONES ===
  PROCEDURE validar(p_id NUMBER, p_campo1 VARCHAR2, p_campo2 NUMBER);

  -- === LOGICA DE NEGOCIO ===
  PROCEDURE procesar(p_id NUMBER, p_usuario VARCHAR2);
  PROCEDURE anular(p_id NUMBER, p_usuario VARCHAR2);

  -- === BULK ===
  PROCEDURE procesar_lote(p_ids IN sys.odcinumberlist, p_usuario VARCHAR2);

END PKG_<ENTITY>;
/

CREATE OR REPLACE PACKAGE BODY PKG_<ENTITY> AS

  FUNCTION get_lista(
    p_fecha_desde  DATE     DEFAULT NULL,
    p_fecha_hasta  DATE     DEFAULT NULL,
    p_filtro1      NUMBER   DEFAULT NULL,
    p_filtro2      VARCHAR2 DEFAULT NULL,
    p_estado       VARCHAR2 DEFAULT NULL
  ) RETURN SYS_REFCURSOR IS
    v_cursor SYS_REFCURSOR;
  BEGIN
    OPEN v_cursor FOR
      SELECT t.id, t.campo1, t.campo2,
             TO_CHAR(t.fecha, 'DD/MM/YYYY') AS fecha_fmt,
             TO_CHAR(t.importe, 'FM999G999G999G990D00') AS importe_fmt,
             CASE t.estado
               WHEN 'A' THEN '<span style="color:green;font-weight:bold">Activo</span>'
               WHEN 'I' THEN '<span style="color:red">Inactivo</span>'
             END AS estado_html
      FROM <table> t
      WHERE (p_fecha_desde IS NULL OR t.fecha >= p_fecha_desde)
        AND (p_fecha_hasta IS NULL OR t.fecha <= p_fecha_hasta)
        AND (p_filtro1 IS NULL OR t.id_filtro1 = p_filtro1)
        AND (p_filtro2 IS NULL OR t.filtro2 LIKE '%' || p_filtro2 || '%')
        AND (p_estado IS NULL OR t.estado = p_estado)
      ORDER BY t.fecha DESC, t.id DESC;
    RETURN v_cursor;
  END;

  FUNCTION get_detalle(p_id NUMBER) RETURN SYS_REFCURSOR IS
    v_cursor SYS_REFCURSOR;
  BEGIN
    OPEN v_cursor FOR SELECT * FROM <table> WHERE id = p_id;
    RETURN v_cursor;
  END;

  PROCEDURE guardar(
    p_id       IN OUT NUMBER,
    p_campo1   VARCHAR2,
    p_campo2   NUMBER,
    p_campo3   DATE,
    p_usuario  VARCHAR2
  ) IS
  BEGIN
    validar(p_id, p_campo1, p_campo2);

    IF p_id IS NULL THEN
      INSERT INTO <table> (campo1, campo2, campo3, usuario_alta, fecha_alta)
      VALUES (p_campo1, p_campo2, p_campo3, p_usuario, SYSDATE)
      RETURNING id INTO p_id;
    ELSE
      UPDATE <table>
      SET campo1 = p_campo1, campo2 = p_campo2, campo3 = p_campo3,
          usuario_modif = p_usuario, fecha_modif = SYSDATE
      WHERE id = p_id;

      IF SQL%ROWCOUNT = 0 THEN
        raise_application_error(-20001, 'Registro no encontrado: ' || p_id);
      END IF;
    END IF;
  END;

  PROCEDURE eliminar(p_id NUMBER) IS
  BEGIN
    DELETE FROM <table> WHERE id = p_id;
    IF SQL%ROWCOUNT = 0 THEN
      raise_application_error(-20002, 'Registro no encontrado: ' || p_id);
    END IF;
  END;

  PROCEDURE validar(p_id NUMBER, p_campo1 VARCHAR2, p_campo2 NUMBER) IS
    v_count NUMBER;
  BEGIN
    IF p_campo1 IS NULL THEN
      raise_application_error(-20010, 'Campo1 es obligatorio');
    END IF;
    IF p_campo2 < 0 THEN
      raise_application_error(-20011, 'Campo2 no puede ser negativo');
    END IF;
    SELECT COUNT(*) INTO v_count FROM <table>
    WHERE campo1 = p_campo1 AND (p_id IS NULL OR id != p_id);
    IF v_count > 0 THEN
      raise_application_error(-20012, 'Ya existe un registro con ese Campo1');
    END IF;
  END;

  PROCEDURE procesar(p_id NUMBER, p_usuario VARCHAR2) IS
  BEGIN
    UPDATE <table>
    SET estado = 'P', fecha_proceso = SYSDATE, usuario_proceso = p_usuario
    WHERE id = p_id AND estado = 'A';
    IF SQL%ROWCOUNT = 0 THEN
      raise_application_error(-20020, 'No se puede procesar: estado invalido');
    END IF;
  END;

  PROCEDURE anular(p_id NUMBER, p_usuario VARCHAR2) IS
  BEGIN
    UPDATE <table>
    SET estado = 'X', fecha_anulacion = SYSDATE, usuario_anulacion = p_usuario
    WHERE id = p_id AND estado IN ('A', 'P');
    IF SQL%ROWCOUNT = 0 THEN
      raise_application_error(-20021, 'No se puede anular: estado invalido');
    END IF;
  END;

  PROCEDURE procesar_lote(p_ids IN sys.odcinumberlist, p_usuario VARCHAR2) IS
  BEGIN
    FORALL i IN 1..p_ids.COUNT
      UPDATE <table>
      SET estado = 'P', fecha_proceso = SYSDATE, usuario_proceso = p_usuario
      WHERE id = p_ids(i) AND estado = 'A';
    IF SQL%ROWCOUNT = 0 THEN
      raise_application_error(-20030, 'No se procesaron registros');
    END IF;
  END;

END PKG_<ENTITY>;
/
```

---

## 17. COMO USAR

### Tu amigo debe:

1. Instalar MCP + Skill (seccion 1)
2. Copiar este archivo como `CLAUDE.md` en la raiz del proyecto donde trabaja
3. Reiniciar Claude Code
4. Invocar `/oracle-forms-migration` y pedirle que migre un form

### Ejemplo de uso:
```
/oracle-forms-migration

Migra el formulario FORMA_827.fmb que esta en C:\Forms\

Analiza el XML de FORMA_6201.xml y decime que bloques y triggers tiene

Crea la pagina APEX para la tabla ORDEN_PAGO con IR + Form modal

Converti el reporte REP_ORDEN_PAGO.rdf a JasperReports
```

Claude va a seguir automaticamente todos los patrones de este documento.
