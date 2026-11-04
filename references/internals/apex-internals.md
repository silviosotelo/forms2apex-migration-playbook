# APEX 20.2 Internal Tables (wwv_flow_*)

## ID Generation
```sql
SELECT wwv_flow_id.next_val INTO v_id FROM DUAL;
```
Nunca inline en VALUES. Nunca hardcodear IDs de JSON (precision loss con 18+ dígitos).

## Workspace Context
```sql
apex_util.set_security_group_id(<workspace_id>);
```
Siempre antes de cualquier operación.

## UPDATE/DELETE seguro
Usar `WHERE page_id=X AND plug_source_type='Y'` — nunca `WHERE id=<big_number>`.

## wwv_flow_steps (Pages)

| Column | Valor | Notas |
|--------|-------|-------|
| user_interface_id | (resolver dinámicamente) | **SIN ESTO LA PÁGINA ES INVISIBLE** |
| page_component_map | '18' / '02' / '03' | IR / Form-Modal / Blank |
| step_title | 'Título' | Mismo que name |
| alias | 'PAGE-ALIAS' | Kebab-case, SIEMPRE setear |
| page_mode | 'NORMAL' / 'MODAL' | |
| step_template | NULL / (modal dialog tmpl) | NULL normal, template para modal |
| include_apex_css_js_yn | 'Y' | |
| first_item | 'NO_FIRST_ITEM' | |
| reload_on_submit | 'S' | |
| warn_on_unsaved_changes | 'Y' | |
| autocomplete_on_off | 'OFF' | |
| css_file_urls | '#WORKSPACE_IMAGES#template-floating-minimalista.css' | |

## wwv_flow_page_plugs (Regions)

**NOT NULL obligatorios:**
- `translate_title`: 'Y'
- `include_in_reg_disp_sel_yn`: 'Y' o 'N'
- `plug_customized`: 0
- `plug_caching`: 'NOCACHE'
- `security_group_id`: workspace ID

**Region Types (plug_source_type):**
- `NATIVE_STATIC` = Static Content (Filtros, Botones, Title Bar)
- `NATIVE_IR` = Interactive Report
- `NATIVE_FORM` = Form Region (DML)
- `NATIVE_BREADCRUMB` = Breadcrumb (necesita menu_id!)
- **NUNCA** `NATIVE_DISPLAY_STATIC` — causa ORA-01403

**NATIVE_STATIC attributes:**
- attribute_01 = 'N', attribute_02 = 'TEXT', attribute_03 = 'Y'

**NATIVE_FORM DEBE tener:**
- query_type = 'TABLE', query_table = 'TABLE_NAME', is_editable = 'Y'
- attribute_01 a attribute_05 = NULL
- plug_query_options = NULL

**Dialog Footer (para botones en modal):**
- plug_display_point = 'REGION_POSITION_03'

## wwv_flow_step_items (Page Items)

**NOT NULL obligatorios:**
- `data_type`: 'VARCHAR' (NO 'VARCHAR2')
- `is_primary_key`: 'Y' o 'N'
- `is_query_only`: 'N'
- `protection_level`: 'N'

**Para items en NATIVE_FORM:**
- `item_source_plug_id` DEBE apuntar al region ID del NATIVE_FORM
  - Sin esto -> NO_PRIMARY_KEY_ITEM error
- `source`: nombre de columna en la tabla
- `source_data_type`: tipo Oracle (NUMBER, VARCHAR2, DATE)
- `item_field_template`: (resolver Optional-Floating dinámicamente)
- `prompt`: SIEMPRE setear para items visibles

## wwv_flow_worksheets (IR)

- FK a region via `region_id`
- `detail_link`: URL con `#COLUMN#` substitutions
- `detail_link_text`: `<img src="#IMAGE_PREFIX#app_ui/img/icons/apex-edit-pencil.png" class="apex-edit-pencil" alt="">`
- **NUNCA** insertar `UNIQUELY_IDENTIFY_ROWS_BY` — es columna virtual (ORA-54013)

**detail_link format:**
```
f?p=&APP_ID.:<form_page>:&SESSION.::&DEBUG.:RP,<form_page>:P<form_page>_<PK>:#PK_COLUMN#
```

## wwv_flow_worksheet_columns

- `db_column_name`: DEBE coincidir EXACTO con alias SQL (case-sensitive)
- `column_type`: 'NUMBER', 'STRING' (para TO_CHAR), 'DATE'
- `display_as`: 'TEXT'
- `display_text_as`: 'ESCAPE_SC' o 'WITHOUT_MODIFICATION' (para HTML)
- `lov_display_null`: 'YES'/'NO' (NO 'Y'/'N')
- **Cantidad de columnas DEBE coincidir EXACTO con el SELECT** — mismatch = ORA-01403
- **NUNCA** crear columna 'LINK' — usar native detail_link

## wwv_flow_worksheet_rpts (Default Reports)
- `application_user = 'APXWS_DEFAULT'`, `is_default = 'Y'`
- `report_columns`: colon-separated

## wwv_flow_step_processing (Processes)

| Tipo | process_point | attribute_01 | region_id |
|------|--------------|--------------|-----------|
| NATIVE_FORM_INIT | BEFORE_HEADER | NULL | form region |
| NATIVE_FORM_DML | AFTER_SUBMIT | 'REGION_SOURCE' | form region |
| NATIVE_CLOSE_WINDOW | AFTER_SUBMIT | 'REQUEST' | NULL |

## wwv_flow_page_da_events (Dynamic Actions)
- `bind_type = 'bind'` (NOT NULL obligatorio)
- `triggering_element_type`: 'BUTTON', 'JQUERY_SELECTOR', 'ITEM', 'REGION'

## wwv_flow_page_da_actions
- `event_result = 'TRUE'` (NOT NULL obligatorio)

## Template IDs
Resolver dinámicamente con:
```sql
SELECT template_id, template_name FROM apex_application_templates
WHERE application_id = :app_id AND template_type = 'Region';
```

## IR Programático — Checklist
Crear IR requiere los 4 componentes o da ORA-01403:
1. Region (wwv_flow_page_plugs, plug_source_type = 'NATIVE_IR')
2. Worksheet (wwv_flow_worksheets, FK region_id)
3. Worksheet columns (wwv_flow_worksheet_columns, FK worksheet_id) — cantidad = columnas SQL
4. Default report (wwv_flow_worksheet_rpts, application_user = 'APXWS_DEFAULT')

## Errores Comunes

| Error | Causa | Fix |
|-------|-------|-----|
| ORA-01403 WWV_FLOW_PLUGIN | plug_source_type inválido | Usar NATIVE_STATIC, no NATIVE_DISPLAY_STATIC |
| ORA-01403 IR page | Worksheet columns != SQL columns | Cantidad y nombres deben coincidir |
| NO_PRIMARY_KEY_ITEM | item_source_plug_id NULL | Setear al ID del region NATIVE_FORM |
| Buttons no aparecen | security_group_id falta | Llamar apex_util.set_security_group_id |
| Items sin estilo | item_field_template incorrecto | Usar Optional-Floating |
| Página "unknown" | user_interface_id falta | Setear al Desktop UI ID |
| DA INSERT falla | bind_type o event_result NULL | bind_type='bind', event_result='TRUE' |
| ORA-54013 | INSERT en columna virtual | No insertar UNIQUELY_IDENTIFY_ROWS_BY |

## APEX Data Dictionary Views — Verified Column Names

These are the CORRECT column names for APEX data dictionary views. Using wrong names causes ORA-00904.

### APEX_APPLICATION_PAGES
```
APPLICATION_ID, PAGE_ID, PAGE_NAME, PAGE_ALIAS, PAGE_TITLE, PAGE_MODE,
PAGE_TEMPLATE,                    -- NOT "TEMPLATE"
PAGE_GROUP,
PAGE_FUNCTION,
JAVASCRIPT_FILE_URLS,             -- external JS file references
JAVASCRIPT_CODE,                  -- inline JS in Function and Global Variable Declaration
JAVASCRIPT_CODE_ONLOAD,           -- JS Execute when Page Loads
CSS_FILE_URLS,                    -- external CSS file references
INLINE_CSS,                       -- page-level inline CSS
DIALOG_TITLE, DIALOG_HEIGHT, DIALOG_WIDTH,  -- for modal/non-modal dialogs
AUTHORIZATION_SCHEME,
PAGE_REQUIRES_AUTHENTICATION,
CREATED_BY, CREATED_ON, LAST_UPDATED_BY, LAST_UPDATED_ON
```

### APEX_APPLICATION_PAGE_REGIONS
```
APPLICATION_ID, PAGE_ID, REGION_ID, REGION_NAME,
TEMPLATE,                         -- ** NOT REGION_TEMPLATE **
DISPLAY_POSITION,
DISPLAY_SEQUENCE,
SOURCE_TYPE,                      -- NATIVE_IR, NATIVE_FORM, NATIVE_STATIC, etc.
REGION_SOURCE,                    -- SQL query or PL/SQL block
QUERY_TYPE, TABLE_NAME, INCLUDE_ROWID_COLUMN,
REGION_CSS_CLASSES,               -- custom CSS classes
STATIC_ID,                        -- static HTML ID
AJAX_ITEMS_TO_SUBMIT,             -- items sent on AJAX refresh
INIT_JAVASCRIPT_CODE,             -- JS executed on region init
COMPONENT_COMMENT,                -- ** NOT REGION_COMMENT **
PARENT_REGION_ID,
CONDITION_TYPE, CONDITION_EXPRESSION1, CONDITION_EXPRESSION2,
AUTHORIZATION_SCHEME,
CREATED_BY, CREATED_ON, LAST_UPDATED_BY, LAST_UPDATED_ON
```

### APEX_APPLICATION_PAGE_ITEMS
```
APPLICATION_ID, PAGE_ID, ITEM_ID, ITEM_NAME, ITEM_SOURCE_TYPE,
REGION,                           -- ** NOT REGION_NAME ** (text label of parent region)
DISPLAY_AS,                       -- NATIVE_TEXT_FIELD, NATIVE_SELECT_LIST, etc.
LABEL,                            -- item prompt text
ITEM_LABEL_TEMPLATE,              -- template name (Optional-Floating, etc.)
ITEM_SOURCE,                      -- source column or expression
ITEM_SOURCE_TYPE,                 -- Database Column, Static Value, etc.
ITEM_DATA_TYPE,
LOV_NAMED_LOV,                    -- shared LOV name
LOV_DEFINITION,                   -- inline LOV query
IS_REQUIRED,                      -- Yes/No
DISPLAY_SEQUENCE,
COMPONENT_COMMENT,                -- ** NOT ITEM_COMMENT **
CONDITION_TYPE, CONDITION_EXPRESSION1, CONDITION_EXPRESSION2,
READ_ONLY_TYPE, READ_ONLY_EXPRESSION1,
ITEM_DEFAULT, ITEM_DEFAULT_TYPE,
AUTHORIZATION_SCHEME,
CREATED_BY, CREATED_ON, LAST_UPDATED_BY, LAST_UPDATED_ON
```

### APEX_APPLICATION_PAGE_BUTTONS
```
APPLICATION_ID, PAGE_ID, BUTTON_ID, BUTTON_NAME,
LABEL,                            -- display text
REGION,
BUTTON_POSITION,
BUTTON_IS_HOT,                    -- Yes/No (hot = primary style)
BUTTON_ACTION,                    -- SUBMIT, REDIRECT, DEFINED_BY_DA
DATABASE_ACTION,                  -- SQL_INSERT, SQL_UPDATE, SQL_DELETE
BUTTON_TEMPLATE,
DISPLAY_SEQUENCE,
COMPONENT_COMMENT,
CONDITION_TYPE, CONDITION_EXPRESSION1, CONDITION_EXPRESSION2,
AUTHORIZATION_SCHEME,
CREATED_BY, CREATED_ON, LAST_UPDATED_BY, LAST_UPDATED_ON
```

### APEX_APPLICATION_PAGE_DA (Dynamic Actions)
```
APPLICATION_ID, PAGE_ID, DYNAMIC_ACTION_ID, DYNAMIC_ACTION_NAME,
WHEN_EVENT_NAME,                  -- change, click, ready, apexafterclosedialog, etc.
WHEN_ELEMENT_TYPE,                -- Item, Button, Region, jQuery Selector, DOM Object
WHEN_ELEMENT,                     -- #P1_ITEM, .class, etc.
WHEN_CONDITION_TYPE, WHEN_CONDITION_ELEMENT, WHEN_CONDITION_EXPRESSION,
CONDITION_TYPE, CONDITION_EXPRESSION1,
AUTHORIZATION_SCHEME,
COMPONENT_COMMENT,
CREATED_BY, CREATED_ON, LAST_UPDATED_BY, LAST_UPDATED_ON
```

### APEX_APPLICATION_PAGE_DA_ACTS (DA Actions)
```
APPLICATION_ID, PAGE_ID, ACTION_ID, DYNAMIC_ACTION_ID,
ACTION_SEQUENCE,
ACTION_CODE,                      -- NATIVE_EXECUTE_PLSQL_CODE, NATIVE_JAVASCRIPT_CODE, NATIVE_REFRESH, etc.
ATTRIBUTE_01,                     -- PL/SQL code (for PLSQL action), JS code (for JS action)
ATTRIBUTE_02,                     -- Items to Submit (for PLSQL action)
ATTRIBUTE_03,                     -- Items to Return (for PLSQL action)
EXECUTE_ON_PAGE_INIT,             -- ** NOT FIRE_ON_INITIALIZATION ** — Yes/No
EVENT_RESULT,                     -- TRUE or FALSE (true/false action)
AFFECTED_ELEMENTS_TYPE,
AFFECTED_ELEMENTS,
STOP_EXECUTION_ON_ERROR,
WAIT_FOR_RESULT,
CREATED_BY, CREATED_ON, LAST_UPDATED_BY, LAST_UPDATED_ON
```

### APEX_APPLICATION_PAGE_PROC (Page Processes)
```
APPLICATION_ID, PAGE_ID, PROCESS_ID, PROCESS_NAME,
EXECUTION_SEQUENCE,               -- ** NOT PROCESS_SEQUENCE **
PROCESS_POINT,                    -- BEFORE_HEADER, AFTER_SUBMIT, ON_DEMAND, etc.
PROCESS_TYPE,                     -- NATIVE_PLSQL, NATIVE_FORM_INIT, NATIVE_FORM_DML, etc.
PROCESS_SOURCE,                   -- PL/SQL code block
PROCESS_ERROR_MESSAGE,            -- ** NOT ERROR_MESSAGE **
REGION,
CONDITION_TYPE, CONDITION_EXPRESSION1, CONDITION_EXPRESSION2,
AUTHORIZATION_SCHEME,
COMPONENT_COMMENT,
CREATED_BY, CREATED_ON, LAST_UPDATED_BY, LAST_UPDATED_ON
```

### APEX_APPLICATION_LOVS (Shared LOVs)
```
APPLICATION_ID, LOV_ID,
LIST_OF_VALUES_NAME,              -- the LOV name
LOV_TYPE,                         -- Static, Dynamic
LOV_QUERY,                        -- SQL query for dynamic LOVs
CREATED_BY, CREATED_ON, LAST_UPDATED_BY, LAST_UPDATED_ON
```

### APEX_APPLICATION_STATIC_FILES / APEX_WORKSPACE_STATIC_FILES
```
-- Application static files:
APPLICATION_ID, FILE_NAME, MIME_TYPE, FILE_CONTENT (BLOB),
FILE_CHARACTER_SET, CREATED_BY, CREATED_ON, LAST_UPDATED_BY, LAST_UPDATED_ON

-- Workspace static files:
WORKSPACE, FILE_NAME, MIME_TYPE, FILE_CONTENT (BLOB),
FILE_CHARACTER_SET, CREATED_BY, CREATED_ON, LAST_UPDATED_BY, LAST_UPDATED_ON
```

## ORA-00904 Common Errors — Wrong vs Correct Column Names

| Wrong Column Name | Correct Column Name | View |
|---|---|---|
| REGION_TEMPLATE | TEMPLATE | APEX_APPLICATION_PAGE_REGIONS |
| REGION_COMMENT | COMPONENT_COMMENT | APEX_APPLICATION_PAGE_REGIONS |
| ITEM_COMMENT | COMPONENT_COMMENT | APEX_APPLICATION_PAGE_ITEMS |
| PROCESS_SEQUENCE | EXECUTION_SEQUENCE | APEX_APPLICATION_PAGE_PROC |
| ERROR_MESSAGE | PROCESS_ERROR_MESSAGE | APEX_APPLICATION_PAGE_PROC |
| BRANCH_SEQUENCE | PROCESS_SEQUENCE | APEX_APPLICATION_PAGE_BRANCHES |
| FIRE_ON_INITIALIZATION | EXECUTE_ON_PAGE_INIT | APEX_APPLICATION_PAGE_DA_ACTS |
| REGION_NAME (in items) | REGION | APEX_APPLICATION_PAGE_ITEMS |
| TEMPLATE (in pages) | PAGE_TEMPLATE | APEX_APPLICATION_PAGES |
| BUTTON_LABEL | LABEL | APEX_APPLICATION_PAGE_BUTTONS |
