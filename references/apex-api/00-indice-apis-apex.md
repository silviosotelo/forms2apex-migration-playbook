# Índice de APIs de APEX y buenas prácticas de código

Referencia de consulta de la skill `forms2apex`. **Versión objetivo fija: APEX 20.2 sobre Oracle 12.1** (según el perfil):
no usar nada de versiones posteriores (ver tabla de versiones más abajo y `version-compatibility.md`). Si una API no está documentada para 20.2,
marcarla `VERIFICATION REQUIRED` y probarla en la base antes de usarla.

Para confirmar la versión de la base conectada:
```sql
SELECT VERSION_NO FROM APEX_RELEASE;
SELECT BANNER FROM V$VERSION WHERE ROWNUM = 1;
```

## Supported Versions

| APEX Version | Min DB Version | URL Scheme | Key Differences |
|---|---|---|---|
| 19.1 - 19.2 | 11.2.0.4+ | Legacy (f?p=) | Base APIs, Form Region (19.1), Faceted Search (19.2) |
| 20.1 - 20.2 | 11.2.0.4+ | Friendly (20.1+) | +Cards (20.2), +Automations, +APEX_DATA_EXPORT, +APEX_EXEC |
| 21.1 - 21.2 | 12.1.0.2+ | Friendly URLs | +Map region, +APEX_MARKDOWN, +apex.date, +PWA basics (21.2) |
| 22.1 - 22.2 | 12.1.0.2+ | Friendly URLs | +APEX_APPROVAL, +Dynamic Content, +Invoke API process |
| 23.1 - 23.2 | 19c+ | Friendly URLs | +Template Components, +Workflow, +APEX_PWA, +Combobox, +QR Code |
| 24.1 - 24.2 | 19c+ | Friendly URLs | +APEX_AI, +Select One/Many, +Vector Search (24.2), +JSON Sources |

## Golden Rules

1. **NEVER** invent APEX API methods not in official documentation for the target version
2. **NEVER** use features from a newer APEX version than what the user has
3. **NEVER** suggest UPDATE/INSERT/DELETE on `apex_collections` view (causes ORA-01732 in ALL versions)
4. **NEVER** use row-by-row processing when bulk operations exist
5. **NEVER** use functions inside SQL queries (performance killer)
6. **NEVER** create GTT when PL/SQL TYPES suffice
7. **ALWAYS** put PL/SQL business logic in compiled database packages
8. **ALWAYS** prefer PL/SQL TYPES over GTT for in-memory operations
9. **ALWAYS** implement proper error handling with logging
10. If uncertain about an API: mark as `VERIFICATION REQUIRED - Consult official APEX {version} docs`
11. If a feature is unsupported in the user's version: state `NOT AVAILABLE in APEX {version} - Available from APEX {min_version}. Alternative: [solution]`

## Architecture Pattern (All Versions)

```
Browser (JavaScript)          Server (PL/SQL)              Database
  apex.item.getValue()   -->   apex.server.process()   -->  Package procedures
  apex.message.show*()   <--   apex_json / htp.p       <--  Tables/Views
  apex.region.refresh()       apex_collection
  apex.theme.openRegion()     apex_escape.html()
```

## PL/SQL APIs by Version

### Available in ALL versions (19.1+)
- APEX_APPLICATION, APEX_COLLECTION, APEX_CUSTOM_AUTH, APEX_CSS
- APEX_DEBUG, APEX_ESCAPE, APEX_ERROR, APEX_EXPORT
- APEX_IG, APEX_IR, APEX_ITEM, APEX_JAVASCRIPT, APEX_JSON
- APEX_LANG, APEX_LDAP, APEX_MAIL, APEX_PAGE
- APEX_PLUGIN, APEX_PLUGIN_UTIL, APEX_REGION
- APEX_SESSION, APEX_STRING, APEX_STRING_UTIL
- APEX_THEME, APEX_UI_DEFAULT_UPDATE, APEX_UTIL
- APEX_ACL, APEX_APP_SETTING, APEX_APPLICATION_INSTALL
- APEX_AUTHENTICATION, APEX_AUTHORIZATION, APEX_CREDENTIAL
- APEX_INSTANCE_ADMIN

### Added in 20.1+
- **APEX_EXEC** — Execute queries against local, remote, REST data sources
- **APEX_DATA_PARSER** — Parse CSV, JSON, XML, XLSX files
- **APEX_DATA_EXPORT** — Export data in various formats
- **APEX_JWT** — JSON Web Token generation/validation
- **APEX_AUTOMATION** — Automated tasks and schedules
- **APEX_REST_SOURCE_SYNC** — Synchronize REST data sources
- **APEX_SPATIAL** — Spatial/map operations

### Added in 21.1+
- **APEX_MARKDOWN** — Convert markdown to HTML
- **APEX_DATA_LOADING** — Data loading utilities

### Added in 22.1+
- **APEX_APPROVAL** — Approval workflow management
- **APEX_DG_DATA_GEN** — Blueprint-based test data generation
- **APEX_SEARCH** — Unified search configuration
- **APEX_SESSION_STATE** — Session state management

### Added in 23.1+
- **APEX_BACKGROUND_PROCESS** — Background PL/SQL execution
- **APEX_BARCODE** — Barcode generation
- **APEX_HUMAN_TASK** — Human task / workflow tasks
- **APEX_PWA** — Progressive Web App management

### Added in 24.1+
- **APEX_AI** — AI/LLM integration (Generative AI)
- **APEX_HTTP** — HTTP client (replaces APEX_WEB_SERVICE patterns)
- **APEX_EXTENSION** — Extension framework
- **APEX_APPLICATION_ADMIN** — Application administration

## JavaScript APIs by Version

### Available in ALL versions (19.1+)
```javascript
// Core - available everywhere
apex.item('P10_NAME').getValue();
apex.item('P10_NAME').setValue('value');
apex.item('P10_NAME').show() / .hide() / .enable() / .disable();
apex.region('static_id').refresh();
apex.server.process('PROCESS_NAME', {x01: 'val'}, {dataType: 'json', success: fn});
apex.message.showPageSuccess('msg');
apex.message.showErrors([{type:'error', location:'page', message:'msg'}]);
apex.message.clearErrors();
apex.message.confirm('Sure?', callback);
apex.theme.openRegion('dialog_id');   // Inline Dialog
apex.theme.closeRegion('dialog_id');
apex.util.escapeHTML(str);
apex.util.showSpinner($container);
apex.navigation.redirect(url);
apex.navigation.dialog(url, options);
apex.page.submit({request: 'SAVE', showWait: true});
```

### Added in 21.1+
```javascript
apex.date.parse('2024-01-15', 'YYYY-MM-DD');   // Date utilities
apex.date.format(dateObj, 'YYYY-MM-DD');
apex.date.add(dateObj, 1, apex.date.UNIT.DAY);
```

### Added in 23.1+
```javascript
apex.pwa.installApp();     // PWA support
apex.pwa.isPWAInstalled();
```

## Server-Side PL/SQL Patterns (All Versions)

### Ajax Callback Process
```plsql
DECLARE
    v_id     NUMBER := TO_NUMBER(apex_application.g_x01);
    v_name   VARCHAR2(200) := apex_application.g_x02;
    v_clob   CLOB := apex_application.g_clob_01;
    v_result VARCHAR2(4000);
BEGIN
    pkg_myapp.process_data(p_id => v_id, p_name => v_name, p_result => v_result);

    apex_json.open_object;
    apex_json.write('status', 'OK');
    apex_json.write('message', v_result);
    apex_json.close_object;
EXCEPTION
    WHEN OTHERS THEN
        apex_json.open_object;
        apex_json.write('status', 'ERROR');
        apex_json.write('message', SQLERRM);
        apex_json.close_object;
END;
```

### APEX Collections (ALL versions — official API only)
```plsql
apex_collection.create_or_truncate_collection('MY_COLL');
apex_collection.add_member(p_collection_name => 'MY_COLL', p_c001 => 'val1', p_n001 => 42);
-- NEVER: UPDATE apex_collections SET ... (causes ORA-01732)
apex_collection.update_member(p_collection_name => 'MY_COLL', p_seq => v_seq, p_c001 => 'new');
SELECT seq_id, c001, n001 FROM apex_collections WHERE collection_name = 'MY_COLL';
```

### Security - Input Escaping (ALL versions)
```plsql
v_safe := apex_escape.html(v_user_input);      -- XSS prevention
v_safe := apex_util.url_encode(v_param);        -- URL encode
-- ALWAYS use bind variables (SQL injection prevention)
```

## Universal Theme Patterns (ALL versions)

### Inline Dialog (NEVER use jQuery UI .dialog())
```javascript
apex.theme.openRegion('dlgMyDialog');
apex.theme.closeRegion('dlgMyDialog');
```

### CSS Classes
- Buttons: `t-Button`, `t-Button--hot`, `t-Button--danger`, `t-Button--success`
- Forms: `t-Form-fieldContainer`, `t-Form-label`, `t-Form-inputContainer`
- Reports: `t-Report-report`, `t-Report-colHead`, `t-Report-cell`
- Dialogs: `t-DialogRegion-body`, `t-DialogRegion-buttons`

## APEX Dictionary Views — Version Differences

### Column differences across versions:
| View | Column | Available From | Alternative for older versions |
|---|---|---|---|
| APEX_APPLICATIONS | CREATED_ON | 21.1+ | Use LAST_UPDATED_ON |
| APEX_APPLICATIONS | PAGES | All | Direct column (not subquery) |
| APEX_APPLICATION_PAGES | INLINE_CSS | All (20.1+) | Was CSS_INLINE pre-20.1 |
| APEX_APPLICATION_PAGE_REGIONS | TEMPLATE | All (20.1+) | Was REGION_TEMPLATE pre-20.1 |
| APEX_APPLICATION_PAGE_REGIONS | STATIC_ID | All | Always available |
| WWV_FLOW_PAGE_PLUGS | REGION_NAME | Internal | Maps to STATIC_ID in views |

### Safe queries (work in ALL versions):
```sql
SELECT application_id, application_name, pages, workspace FROM apex_applications;
SELECT page_id, page_name, page_mode FROM apex_application_pages WHERE application_id = :app;
SELECT region_id, region_name, static_id, source_type, template
FROM apex_application_page_regions WHERE application_id = :app AND page_id = :page;
```

## Region Types by Version

| Region Type | Available From |
|---|---|
| Static Content, Classic Report, Interactive Report | All |
| Interactive Grid, Form | 5.1+ |
| Faceted Search | 20.1+ |
| Cards, Content Row | 21.1+ |
| Map | 21.2+ |
| Smart Filters (enhanced) | 22.1+ |
| Workflow, Approvals | 23.1+ |
| AI Assistant | 24.1+ |

## Oracle DB Feature Availability

| Feature | Min DB Version |
|---|---|
| FETCH FIRST N ROWS | 12c (12.1)+ |
| Identity columns | 12c (12.1)+ |
| JSON support (basic) | 12c (12.1)+ |
| PL/SQL in WITH clause | 12c (12.1)+ |
| LISTAGG DISTINCT | 19c+ |
| JSON_TABLE, JSON_OBJECT | 12c R2 (12.2)+ |
| Polymorphic table functions | 18c+ |
| SQL macros | 21c+ |
| JSON Relational Duality | 23ai+ |
| Boolean in SQL | 23ai+ |
| IF [NOT] EXISTS DDL | 23ai+ |

## Programmatic Page Generation (wwv_flow_api — All Versions)

```plsql
BEGIN
    apex_util.set_security_group_id(<workspace_id>);
    -- INTERNAL / UNSUPPORTED API - VERIFICATION REQUIRED
    wwv_flow_api.create_page_plug(
        p_id => <id>, p_flow_id => <app_id>, p_page_id => <page_id>,
        p_plug_name => 'Region Name', p_region_name => 'static_id',
        p_plug_template => <template_id>, p_plug_display_sequence => 10,
        p_plug_source => '<content>', p_plug_source_type => 'NATIVE_STATIC',
        p_plug_display_point => 'BODY'
    );
    COMMIT;
END;
```

Always resolve template IDs dynamically:
```sql
SELECT template_id, template_name FROM apex_application_templates
WHERE application_id = :app_id AND template_type = 'Region';
```

## Production Development Patterns

### Page Architecture (MANDATORY)
- **NEVER** create a direct Form page as entry point
- **ALWAYS** use: IR (list with filters) → Form (edit page)
- IR page: bordered Filter region + IR region + floating action buttons
- Form page: opened from IR via native IR Link Column or "New" button
- Modal dialogs only for lookups/selection

### IR Link Column
- Use native IR "Link Column" attribute (Target Page + Set Items) for edit links
- Never add custom HTML edit columns — redundant and harder to maintain

### Programmatic IR Creation
Creating an IR region programmatically requires 4 internal components:
1. Region (`wwv_flow_page_plugs`, `plug_source_type = 'NATIVE_IR'`)
2. Worksheet (`wwv_flow_worksheets`, FK to region)
3. Worksheet columns (`wwv_flow_worksheet_columns`, FK to worksheet)
4. Default report (`wwv_flow_worksheet_rpts`, `application_user = 'APXWS_DEFAULT'`)
Missing any causes ORA-01403 at render time.

### LOV Standards
- Format: `ID || ' - ' || Descripcion || ' (' || OtroDato || ')'`
- Don't create Display Only items for LOV data — use Popup LOV additional return columns
- With DISTINCT: ORDER BY must reference SELECT list columns, use `ORDER BY 1`

### Table Name Discovery
- Never assume table names from FK column names (e.g. `cobr_id_cobrador` ≠ table `cobrador`)
- Always verify: `SELECT table_name FROM all_tables WHERE owner = :schema AND table_name LIKE '%keyword%'`

### Large APEX ID Precision
- JavaScript loses precision with 18+ digit APEX IDs
- Use `TO_CHAR(id)` in queries, `SELECT id INTO v_id` in PL/SQL
- Never hardcode IDs from JSON output — re-query with exact conditions

## Reference Files

| File | Description |
|------|-------------|
| [references/apex-data-dictionary.md](apex-data-dictionary.md) | **APEX Data Dictionary Views** — Verified column names for all APEX_APPLICATION_* views. Prevents ORA-00904 errors. Common wrong/correct column name mapping. |
| [references/apex-plsql-api.md](apex-plsql-api.md) | **APEX PL/SQL API** — All 41 packages with key methods, parameters, and code examples. Organized by category. |
| [references/apex-js-api.md](apex-js-api.md) | **APEX JavaScript API** — All namespaces (apex.server, apex.item, apex.region, apex.page, apex.message, apex.navigation, apex.da, apex.util, apex.lang, apex.locale, apex.theme, apex.storage, apex.actions, apex.event, apex.env). |
| [references/oracle-db-api.md](oracle-db-api.md) | **Oracle DB PL/SQL APIs** — DBMS_LOB, DBMS_SQL, DBMS_METADATA, DBMS_SCHEDULER, DBMS_CRYPTO, UTL_RAW/ENCODE/URL/HTTP, JSON_OBJECT_T, REGEXP, analytics, dictionary views. Combined PL/SQL+JS patterns. |
| [references/interactive-grid.md](interactive-grid.md) | **Interactive Grid JS API** — Detailed IG widget methods, model API, record manipulation. |
| [references/interactive-report.md](interactive-report.md) | **Interactive Report** — IR-specific patterns. |
| [references/version-compatibility.md](version-compatibility.md) | **Version Compatibility** — Feature availability across APEX versions. |

## Official Documentation Links

| Version | PL/SQL API | JS API |
|---|---|---|
| 24.2 | [aeapi](https://docs.oracle.com/en/database/oracle/apex/24.2/aeapi/) | [aexjs](https://docs.oracle.com/en/database/oracle/apex/24.2/aexjs/) |
| 24.1 | [aeapi](https://docs.oracle.com/en/database/oracle/apex/24.1/aeapi/) | [aexjs](https://docs.oracle.com/en/database/oracle/apex/24.1/aexjs/) |
| 23.2 | [aeapi](https://docs.oracle.com/en/database/oracle/apex/23.2/aeapi/) | [aexjs](https://docs.oracle.com/en/database/oracle/apex/23.2/aexjs/) |
| 23.1 | [aeapi](https://docs.oracle.com/en/database/oracle/apex/23.1/aeapi/) | [aexjs](https://docs.oracle.com/en/database/oracle/apex/23.1/aexjs/) |
| 22.2 | [aeapi](https://docs.oracle.com/en/database/oracle/apex/22.2/aeapi/) | [aexjs](https://docs.oracle.com/en/database/oracle/apex/22.2/aexjs/) |
| 22.1 | [aeapi](https://docs.oracle.com/en/database/oracle/apex/22.1/aeapi/) | [aexjs](https://docs.oracle.com/en/database/oracle/apex/22.1/aexjs/) |
| 21.2 | [aeapi](https://docs.oracle.com/en/database/oracle/application-express/21.2/aeapi/) | [aexjs](https://docs.oracle.com/en/database/oracle/application-express/21.2/aexjs/) |
| 21.1 | [aeapi](https://docs.oracle.com/en/database/oracle/application-express/21.1/aeapi/) | [aexjs](https://docs.oracle.com/en/database/oracle/application-express/21.1/aexjs/) |
| 20.2 | [aeapi](https://docs.oracle.com/en/database/oracle/application-express/20.2/aeapi/) | [aexjs](https://docs.oracle.com/en/database/oracle/application-express/20.2/aexjs/) |
| 20.1 | [aeapi](https://docs.oracle.com/en/database/oracle/application-express/20.1/aeapi/) | [aexjs](https://docs.oracle.com/en/database/oracle/application-express/20.1/aexjs/) |
| 19.2 | [aeapi](https://docs.oracle.com/en/database/oracle/application-express/19.2/aeapi/) | [aexjs](https://docs.oracle.com/en/database/oracle/application-express/19.2/aexjs/) |
