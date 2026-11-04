# APEX PL/SQL API Reference — 41+ Packages (Comprehensive)

## Package Index

`APEX_ACL` · `APEX_APP_SETTING` · `APEX_APPLICATION` · `APEX_APPLICATION_INSTALL` · `APEX_AUTHENTICATION` · `APEX_AUTHORIZATION` · `APEX_COLLECTION` · `APEX_CREDENTIAL` · `APEX_CSS` · `APEX_DATA_PARSER` · `APEX_DEBUG` · `APEX_ERROR` · `APEX_ESCAPE` · `APEX_EXEC` · `APEX_EXPORT` · `APEX_IG` · `APEX_INSTANCE_ADMIN` · `APEX_IR` · `APEX_ITEM` · `APEX_JAVASCRIPT` · `APEX_JSON` · `APEX_JWT` · `APEX_LANG` · `APEX_LDAP` · `APEX_MAIL` · `APEX_PAGE` · `APEX_PKG_APP_INSTALL` · `APEX_PLUGIN` · `APEX_PLUGIN_UTIL` · `APEX_REGION` · `APEX_REST_SOURCE_SYNC` · `APEX_SESSION` · `APEX_SPATIAL` · `APEX_STRING` · `APEX_STRING_UTIL` · `APEX_THEME` · `APEX_UI_DEFAULT_UPDATE` · `APEX_UTIL` · `APEX_WEB_SERVICE` · `APEX_ZIP`

---

## Core Runtime

### APEX_APPLICATION — Session State and Engine Control

#### Global Variables (read in PL/SQL processes)
| Variable | Type | Description |
|----------|------|-------------|
| `g_user` | VARCHAR2 | Current APEX user (uppercase) |
| `g_flow_id` | NUMBER | Application ID |
| `g_flow_step_id` | NUMBER | Current page ID |
| `g_session` | NUMBER | Session ID (for URL building) |
| `g_request` | VARCHAR2 | REQUEST value (button name or custom) |
| `g_debug` | VARCHAR2 | 'YES' when debug mode active |
| `g_x01..g_x20` | VARCHAR2 | Scalar AJAX parameters from JS |
| `g_f01..g_f50` | wwv_flow_global.vc_arr2 | Array AJAX parameters from JS |
| `g_clob_01` | CLOB | CLOB AJAX parameter (p_clob_01 from JS) |
| `g_print_success_message` | VARCHAR2 | Set page success message programmatically |

```plsql
-- Read AJAX parameters
v_id   := TO_NUMBER(apex_application.g_x01);
v_name := apex_application.g_x02;
v_clob := apex_application.g_clob_01;

-- Read array parameters (from f01..f50 checkbox/tabular)
FOR i IN 1..apex_application.g_f01.COUNT LOOP
    v_val := apex_application.g_f01(i);
END LOOP;

-- Set success message
apex_application.g_print_success_message := 'Record saved successfully.';

-- Stop page rendering (use before BLOB download or custom output)
APEX_APPLICATION.STOP_APEX_ENGINE;
```

---

### APEX_PAGE — Page Control

```plsql
-- Page mode detection
v_mode := APEX_PAGE.GET_PAGE_MODE;  -- 'NORMAL', 'MODAL_DIALOG', 'NON_MODAL_DIALOG'
IF APEX_PAGE.IS_READ_ONLY THEN ...
IF APEX_PAGE.IS_DESKTOP_UI THEN ...

-- Build URL (preferred over f?p string concatenation)
v_url := APEX_PAGE.GET_URL(
    p_application => :APP_ID,
    p_page        => 10,
    p_items       => 'P10_ID,P10_MODE',
    p_values      => v_id || ',EDIT',
    p_clear_cache => '10'
);

-- Purge page cache
APEX_PAGE.PURGE_CACHE(
    p_application_id => :APP_ID,
    p_page_id        => 10
);
```

---

### APEX_SESSION — Non-HTTP Session Management

> Use for scheduled jobs, PL/SQL scripts, and any code running outside the APEX HTTP engine.

```plsql
-- Attach to existing session
APEX_SESSION.ATTACH(
    p_app_id     => 400,
    p_page_id    => 1,
    p_session_id => v_session_id
);
-- Now you can use APEX_UTIL.SET_SESSION_STATE, apex_collections, etc.
APEX_SESSION.DETACH;

-- Create new session (for background jobs)
APEX_SESSION.CREATE_SESSION(
    p_app_id   => 400,
    p_page_id  => 1,
    p_username => 'ADMIN'
);
-- Work with session context...
APEX_SESSION.DETACH;

-- Delete old session
APEX_SESSION.DELETE_SESSION(p_session_id => v_old_session);
```

---

## JSON & Data

### APEX_JSON — JSON Generation and Parsing

#### Generate JSON (AJAX callback - most common pattern)
```plsql
-- Standard AJAX response
APEX_JSON.OPEN_OBJECT;
  APEX_JSON.WRITE('success', TRUE);
  APEX_JSON.WRITE('message', 'Saved');
  APEX_JSON.WRITE('id', v_new_id);
  -- Array of objects
  APEX_JSON.OPEN_ARRAY('items');
    FOR r IN (SELECT id, nombre FROM tabla WHERE activo = 1) LOOP
      APEX_JSON.OPEN_OBJECT;
        APEX_JSON.WRITE('id', r.id);
        APEX_JSON.WRITE('nombre', r.nombre);
      APEX_JSON.CLOSE_OBJECT;
    END LOOP;
  APEX_JSON.CLOSE_ARRAY;
APEX_JSON.CLOSE_OBJECT;
```

#### WRITE Overloads (19 signatures)
```plsql
APEX_JSON.WRITE(p_name, p_value);  -- VARCHAR2, NUMBER, BOOLEAN, DATE, CLOB, BLOB, TIMESTAMP, xmltype
APEX_JSON.WRITE(p_value);          -- unnamed (inside arrays)
APEX_JSON.WRITE_RAW(p_value);      -- raw JSON string (no escaping)
APEX_JSON.WRITE(p_name, p_value CLOB);  -- CLOB overload (preferred for large text)
```

#### Generate to CLOB (not HTTP output)
```plsql
APEX_JSON.INITIALIZE_CLOB_OUTPUT;
APEX_JSON.OPEN_OBJECT;
  APEX_JSON.WRITE('key', 'value');
  -- CRITICAL: For large CLOBs use WRITE overload, NEVER STRINGIFY
  APEX_JSON.WRITE('big_field', v_clob_value);  -- CLOB overload
APEX_JSON.CLOSE_OBJECT;
v_result := APEX_JSON.GET_CLOB_OUTPUT;
APEX_JSON.FREE_OUTPUT;
```

#### Parse JSON
```plsql
-- Parse into global state
APEX_JSON.PARSE(p_source => v_json_text);

-- Parse into variable (allows multiple simultaneous parses)
APEX_JSON.PARSE(p_values => l_values, p_source => v_json_clob);

-- Read values (dot-path navigation)
v_status   := APEX_JSON.GET_VARCHAR2('status');
v_count    := APEX_JSON.GET_NUMBER('result.count');
v_flag     := APEX_JSON.GET_BOOLEAN('result.active');
v_date     := APEX_JSON.GET_DATE('created_at');
v_clob     := APEX_JSON.GET_CLOB('big_field');
v_arr_len  := APEX_JSON.GET_COUNT('items');           -- array length
v_first_id := APEX_JSON.GET_NUMBER('items[1].id');    -- 1-based index!

-- Read from variable
v_val := APEX_JSON.GET_VARCHAR2(p_values => l_values, p_path => 'status');

-- Check existence
IF APEX_JSON.DOES_EXIST('result.data') THEN ...

-- Get all members of an object
v_members := APEX_JSON.GET_MEMBERS('result');  -- returns apex_t_varchar2
```

> **CRITICAL RULE:** Never use `APEX_JSON.STRINGIFY` for CLOBs. Use `APEX_JSON.WRITE(p_name, p_value CLOB)` overload instead.

---

### APEX_EXEC — Query/DML Context API (20.1+)

```plsql
-- Query context (local)
DECLARE
    l_ctx APEX_EXEC.T_CONTEXT;
BEGIN
    l_ctx := APEX_EXEC.OPEN_QUERY_CONTEXT(
        p_location         => APEX_EXEC.C_LOCATION_LOCAL_DB,
        p_sql_query        => 'SELECT id, name, salary FROM employees WHERE dept_id = :d',
        p_sql_parameters   => APEX_EXEC.T_PARAMETERS(
            1 => APEX_EXEC.T_PARAMETER(name => 'd', value => v_dept_id)
        )
    );

    WHILE APEX_EXEC.NEXT_ROW(l_ctx) LOOP
        v_id     := APEX_EXEC.GET_NUMBER(l_ctx, 'ID');
        v_name   := APEX_EXEC.GET_VARCHAR2(l_ctx, 'NAME');
        v_salary := APEX_EXEC.GET_NUMBER(l_ctx, 'SALARY');
    END LOOP;
    APEX_EXEC.CLOSE(l_ctx);
EXCEPTION WHEN OTHERS THEN
    APEX_EXEC.CLOSE(l_ctx);  -- ALWAYS close in exception handler!
    RAISE;
END;

-- Query context from region
l_ctx := APEX_EXEC.OPEN_QUERY_CONTEXT(
    p_application_id   => :APP_ID,
    p_page_id          => :APP_PAGE_ID,
    p_region_static_id => 'my_ir'
);

-- DML context
DECLARE
    l_ctx APEX_EXEC.T_CONTEXT;
BEGIN
    l_ctx := APEX_EXEC.OPEN_LOCAL_DML_CONTEXT(
        p_table_owner => 'ANAMNESIS',
        p_table_name  => 'CLIENTE'
    );
    APEX_EXEC.ADD_DML_ROW(l_ctx, APEX_EXEC.C_DML_OP_INSERT);
    APEX_EXEC.SET_VALUE(l_ctx, 'NOMBRE', :P10_NOMBRE);
    APEX_EXEC.SET_VALUE(l_ctx, 'CI', :P10_CI);
    APEX_EXEC.EXECUTE_DML(l_ctx);
    APEX_EXEC.CLOSE(l_ctx);
EXCEPTION WHEN OTHERS THEN
    APEX_EXEC.CLOSE(l_ctx);
    RAISE;
END;
```

---

### APEX_DATA_PARSER — File Parsing (20.1+)

```plsql
-- Discover columns from file
v_profile := APEX_DATA_PARSER.DISCOVER(
    p_content   => v_blob,
    p_file_name => 'data.csv'
);

-- Get file profile for XLSX
v_profile := APEX_DATA_PARSER.GET_FILE_PROFILE(
    p_content   => v_blob,
    p_file_name => 'data.xlsx'
);

-- List XLSX worksheets
v_sheets := APEX_DATA_PARSER.GET_XLSX_WORKSHEETS(p_content => v_blob);
FOR i IN 1..v_sheets.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE(v_sheets(i).sheet_name);
END LOOP;

-- Parse rows (works for CSV, JSON, XML, XLSX)
FOR r IN (
    SELECT line_number, col001, col002, col003
    FROM   TABLE(APEX_DATA_PARSER.PARSE(
               p_content      => v_blob,
               p_file_name    => 'data.xlsx',
               p_file_profile => v_profile,
               p_max_rows     => 10000
           ))
) LOOP
    INSERT INTO staging_table VALUES (r.col001, r.col002, r.col003);
END LOOP;
```

---

### APEX_COLLECTION — Session-Level Temporary Storage

```plsql
-- Create
APEX_COLLECTION.CREATE_COLLECTION('CART');
APEX_COLLECTION.CREATE_OR_TRUNCATE_COLLECTION('CART');
APEX_COLLECTION.CREATE_COLLECTION_FROM_QUERY(
    p_collection_name => 'ITEMS',
    p_query => 'SELECT id, name, price FROM products WHERE active = 1'
);

-- Add member (50 varchar2, 5 number, 5 date, 1 clob, 1 blob, 1 xmltype columns)
v_seq := APEX_COLLECTION.ADD_MEMBER(
    p_collection_name => 'CART',
    p_c001    => v_product_id,
    p_c002    => v_product_name,
    p_n001    => v_quantity,
    p_d001    => SYSDATE,
    p_clob001 => v_large_text,
    p_blob001 => v_binary_data
);

-- NEVER use UPDATE on apex_collections view! (ORA-01732)
APEX_COLLECTION.UPDATE_MEMBER(
    p_collection_name => 'CART',
    p_seq             => v_seq,
    p_c001            => v_new_value,
    p_n001            => v_new_qty
);

-- Update single attribute
APEX_COLLECTION.UPDATE_MEMBER_ATTRIBUTE(
    p_collection_name => 'CART',
    p_seq             => v_seq,
    p_attr_number     => 1,  -- c001
    p_attr_value      => 'new_value'
);

-- Delete
APEX_COLLECTION.DELETE_MEMBER(p_collection_name => 'CART', p_seq => v_seq);
APEX_COLLECTION.DELETE_COLLECTION('CART');
APEX_COLLECTION.TRUNCATE_COLLECTION('CART');

-- Bulk add
APEX_COLLECTION.ADD_MEMBERS(
    p_collection_name => 'BULK',
    p_c001 => apex_t_varchar2('A','B','C')
);

-- Query
SELECT seq_id, c001, c002, n001, d001, clob001
FROM   apex_collections
WHERE  collection_name = 'CART'
ORDER  BY seq_id;

-- Utilities
v_count := APEX_COLLECTION.COLLECTION_MEMBER_COUNT('CART');
IF APEX_COLLECTION.COLLECTION_EXISTS('CART') THEN ...
```

---

### APEX_STRING — String & Collection Utilities

```plsql
-- Format with placeholders (%s, %0, %1, %LABEL%)
v_msg := APEX_STRING.FORMAT('Processing %s of %s records', v_done, v_total);
v_msg := APEX_STRING.FORMAT('Hello %0, welcome to %1', 'Juan', 'APEX');

-- Split/join
v_arr := APEX_STRING.SPLIT('A:B:C', ':');              -- returns apex_t_varchar2
v_str := APEX_STRING.JOIN(v_arr, ',');                  -- 'A,B,C'
v_nums := APEX_STRING.SPLIT_NUMBERS('1:2:3', ':');     -- returns apex_t_number

-- Push to array
APEX_STRING.PUSH(v_arr, 'new_item');

-- Grep (regex filter)
v_matches := APEX_STRING.GREP(v_arr, '^A');  -- items starting with A

-- Plist (key=value pairs)
v_val    := APEX_STRING.PLIST_GET(v_config, 'key');
v_config := APEX_STRING.PLIST_PUT(v_config, 'key', 'value');

-- Process large CLOB in chunks
APEX_STRING.NEXT_CHUNK(
    p_str    => v_clob,
    p_chunk  => v_chunk,
    p_offset => v_offset,
    p_amount => 8000
);

-- Legacy (still works)
v_arr := APEX_STRING.STRING_TO_TABLE('A:B:C', ':');
v_str := APEX_STRING.TABLE_TO_STRING(v_arr, ',');
```

---

## Security

### APEX_ESCAPE — Output Escaping

```plsql
-- HTML escape (XSS prevention) — mandatory for user input
v_safe := APEX_ESCAPE.HTML(v_user_input);

-- HTML attribute escape
v_attr := APEX_ESCAPE.HTML_ATTRIBUTE(v_value);

-- JavaScript literal (for PL/SQL-generated JS strings)
v_js := APEX_ESCAPE.JS_LITERAL(v_text);

-- JSON string escape
v_json := APEX_ESCAPE.JSON(v_text);

-- LDAP escaping
v_dn := APEX_ESCAPE.LDAP_DN(v_dn);
v_filter := APEX_ESCAPE.LDAP_SEARCH_FILTER(v_filter);

-- Regex escape
v_pat := APEX_ESCAPE.REGEXP(v_pattern);

-- Truncate with HTML escape
v_trunc := APEX_ESCAPE.HTML_TRUNC(v_long_text, 200);

-- Explicit no-escape (documents intent — trusted source)
v_trusted := APEX_ESCAPE.NOOP(v_html_from_db);
```

---

### APEX_ERROR — Error Management

```plsql
-- Signature 1: Field-level error (most common)
APEX_ERROR.ADD_ERROR(
    p_message          => 'Value cannot be negative',
    p_display_location => APEX_ERROR.C_INLINE_WITH_FIELD_AND_NOTIF,
    p_page_item_name   => 'P10_AMOUNT'
);

-- Signature 2: ORA exception error
APEX_ERROR.ADD_ERROR(
    p_message          => 'Error saving record',
    p_ora_sqlcode      => SQLCODE,
    p_ora_sqlerrm      => SQLERRM,
    p_display_location => APEX_ERROR.C_INLINE_IN_NOTIFICATION
);

-- Signature 3: Constraint violation
APEX_ERROR.ADD_ERROR(
    p_message          => 'Duplicate record',
    p_constraint_name  => 'UQ_CLIENTE_CI'
);

-- Signature 4: IG column-level error
APEX_ERROR.ADD_ERROR(
    p_message          => 'Invalid value',
    p_display_location => APEX_ERROR.C_INLINE_WITH_FIELD_AND_NOTIF,
    p_region_id        => v_region_id,
    p_column_alias     => 'SALARY',
    p_row_num          => v_row_num
);

-- Signature 5: t_error record (custom error handling function)
-- Used in Error Handling Function attribute of application

-- Check if errors occurred
IF APEX_ERROR.HAVE_ERRORS_OCCURRED THEN
    RETURN;
END IF;
```

**Display location constants:**
| Constant | Description |
|----------|-------------|
| `C_INLINE_WITH_FIELD` | Inline only (next to item) |
| `C_INLINE_WITH_FIELD_AND_NOTIF` | Inline + notification area (default) |
| `C_INLINE_IN_NOTIFICATION` | Notification area only |
| `C_ON_ERROR_PAGE` | Separate error page |

---

### APEX_AUTHENTICATION — Login/Logout

```plsql
APEX_AUTHENTICATION.LOGIN(p_username => :P9999_USERNAME, p_password => :P9999_PASSWORD);
APEX_AUTHENTICATION.LOGOUT(p_session_id => v('APP_SESSION'), p_app_id => :APP_ID);
APEX_AUTHENTICATION.POST_LOGIN;
IF APEX_AUTHENTICATION.IS_AUTHENTICATED THEN ...
IF APEX_AUTHENTICATION.IS_PUBLIC_USER THEN ...
v_url := APEX_AUTHENTICATION.GET_CALLBACK_URL;
```

---

### APEX_AUTHORIZATION — Authorization Schemes

```plsql
IF APEX_AUTHORIZATION.IS_AUTHORIZED(p_authorization_name => 'ADMIN_ONLY') THEN ...
APEX_AUTHORIZATION.RESET_CACHE;  -- re-evaluate all schemes
APEX_AUTHORIZATION.ENABLE_DYNAMIC_GROUPS(p_application_id => :APP_ID);
```

---

### APEX_ACL — Role-Based Access Control

```plsql
APEX_ACL.ADD_USER_ROLE(p_user_name => 'JOHN', p_role_name => 'ADMIN');
APEX_ACL.REMOVE_USER_ROLE(p_user_name => 'JOHN', p_role_name => 'ADMIN');
APEX_ACL.REPLACE_USER_ROLES(p_user_name => 'JOHN', p_role_names => 'ADMIN:VIEWER');
APEX_ACL.REMOVE_ALL_USER_ROLES(p_user_name => 'JOHN');
IF APEX_ACL.HAS_USER_ROLE(p_user_name => 'JOHN', p_role_name => 'ADMIN') THEN ...
IF APEX_ACL.HAS_USER_ANY_ROLES(p_user_name => 'JOHN') THEN ...
```

---

### APEX_CREDENTIAL — REST Credential Management

```plsql
APEX_CREDENTIAL.SET_SESSION_CREDENTIALS(
    p_credential_static_id => 'MY_API',
    p_username => 'user',
    p_password => 'pass'
);
APEX_CREDENTIAL.SET_PERSISTENT_CREDENTIALS(
    p_credential_static_id => 'MY_API',
    p_username => 'user',
    p_password => 'pass'
);
APEX_CREDENTIAL.SET_PERSISTENT_TOKEN(
    p_credential_static_id => 'MY_API',
    p_token      => v_token,
    p_token_type => 'Bearer',
    p_expires    => SYSDATE + 1/24
);
APEX_CREDENTIAL.CLEAR_TOKENS(p_credential_static_id => 'MY_API');
```

---

## UI Generation

### APEX_ITEM — HTML Form Elements from PL/SQL

> Used in Classic Reports to create editable columns.

```plsql
-- Text input (idx maps to apex_application.g_f01..g_f50)
HTP.P(APEX_ITEM.TEXT(p_idx => 1, p_value => col1, p_size => 30, p_maxlength => 100));

-- Hidden
HTP.P(APEX_ITEM.HIDDEN(p_idx => 10, p_value => col_id));

-- Select list from named LOV
HTP.P(APEX_ITEM.SELECT_LIST_FROM_LOV(
    p_idx       => 2,
    p_value     => col2,
    p_lov       => 'LV_ESTADO',
    p_show_null => 'YES',
    p_null_text => '- Select -'
));

-- Select list from query
HTP.P(APEX_ITEM.SELECT_LIST_FROM_QUERY(
    p_idx   => 2,
    p_value => col2,
    p_query => 'SELECT display_val d, return_val r FROM my_lov ORDER BY 1'
));

-- Checkbox
HTP.P(APEX_ITEM.CHECKBOX2(
    p_idx            => 3,
    p_value          => col3,
    p_checked_values => col3
));

-- Date popup
HTP.P(APEX_ITEM.DATE_POPUP2(
    p_idx         => 4,
    p_value       => TO_CHAR(col_fecha, 'DD/MM/YYYY'),
    p_date_format => 'DD/MM/YYYY'
));

-- Textarea
HTP.P(APEX_ITEM.TEXTAREA(
    p_idx   => 5,
    p_value => col_obs,
    p_rows  => 3,
    p_cols  => 50
));
```

---

### APEX_JAVASCRIPT — Inject JS

```plsql
APEX_JAVASCRIPT.ADD_INLINE_CODE(p_code => 'console.log("loaded");');
APEX_JAVASCRIPT.ADD_ONLOAD_CODE(
    p_code => 'apex.region("my_region").refresh();',
    p_key  => 'MY_REFRESH'  -- prevents duplicates
);
APEX_JAVASCRIPT.ADD_LIBRARY(
    p_name      => 'my-plugin',
    p_directory => '#PLUGIN_PREFIX#js/',
    p_version   => '1.0'
);
```

---

### APEX_CSS — Inject CSS

```plsql
APEX_CSS.ADD(p_css => '.my-class { color: red; }', p_key => 'MY_KEY');
APEX_CSS.ADD_FILE(p_name => 'my-style', p_directory => '#APP_IMAGES#', p_version => '1.0');
```

---

### APEX_REGION — Programmatic Region Control

```plsql
APEX_REGION.CLEAR(p_region_id => v_region_id);
APEX_REGION.RESET(p_region_id => v_region_id);
APEX_REGION.PURGE_CACHE(
    p_application_id => :APP_ID,
    p_page_id        => :APP_PAGE_ID,
    p_region_id      => v_region_id
);
IF APEX_REGION.IS_READ_ONLY(p_region_id => v_region_id) THEN ...

-- Export data from region
v_blob := APEX_REGION.EXPORT_DATA(
    p_region_id    => v_region_id,
    p_export_format => 'CSV'  -- CSV, PDF, XLSX, HTML, JSON, XML
);

-- Open query context from region (20.1+)
l_ctx := APEX_REGION.OPEN_QUERY_CONTEXT(
    p_page_id          => :APP_PAGE_ID,
    p_region_static_id => 'my_report'
);
```

---

### APEX_THEME — Theme Control

```plsql
APEX_THEME.SET_SESSION_STYLE(p_theme_style_id => 12);
APEX_THEME.SET_USER_STYLE(p_theme_style_id => 12, p_application_id => :APP_ID);
APEX_THEME.SET_SESSION_STYLE_CSS(p_css => ':root { --ut-focus-base-color: #4B8DF8; }');
APEX_THEME.CLEAR_USER_STYLE(p_application_id => :APP_ID, p_user_name => :APP_USER);
v_style_id := APEX_THEME.GET_USER_STYLE(p_application_id => :APP_ID);
```

---

## Reports & Communication

### APEX_MAIL — Email

```plsql
-- Send email
v_mail_id := APEX_MAIL.SEND(
    p_to        => 'user@example.com',
    p_from      => 'noreply@santaclara.com',
    p_subj      => 'System Notification',
    p_body      => 'Plain text body',
    p_body_html => '<h1>HTML body</h1>'
);

-- Add attachment
APEX_MAIL.ADD_ATTACHMENT(
    p_mail_id   => v_mail_id,
    p_attachment => v_blob_content,
    p_filename  => 'report.pdf',
    p_mime_type => 'application/pdf'
);

-- Flush queue (actually sends)
APEX_MAIL.PUSH_QUEUE;

-- Email template (from Shared Components)
APEX_MAIL.PREPARE_TEMPLATE(
    p_static_id      => 'WELCOME',
    p_placeholders   => '{"NAME":"' || v_name || '","URL":"' || v_url || '"}',
    p_application_id => :APP_ID,
    p_subject        => v_subj,
    p_html           => v_html,
    p_text           => v_text
);
```

---

### APEX_WEB_SERVICE — REST/SOAP Client

```plsql
-- Set request headers
APEX_WEB_SERVICE.G_REQUEST_HEADERS.DELETE;
APEX_WEB_SERVICE.G_REQUEST_HEADERS(1).NAME  := 'Content-Type';
APEX_WEB_SERVICE.G_REQUEST_HEADERS(1).VALUE := 'application/json';
APEX_WEB_SERVICE.G_REQUEST_HEADERS(2).NAME  := 'Accept';
APEX_WEB_SERVICE.G_REQUEST_HEADERS(2).VALUE := 'application/json';

-- REST request
v_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
    p_url                  => 'https://api.example.com/v1/data',
    p_http_method          => 'POST',
    p_body                 => v_json_body,
    p_credential_static_id => 'API_CREDS'
);

-- ALWAYS check status
IF APEX_WEB_SERVICE.G_STATUS_CODE != 200 THEN
    RAISE_APPLICATION_ERROR(-20001, 'API error: ' || APEX_WEB_SERVICE.G_STATUS_CODE);
END IF;

-- Parse response
APEX_JSON.PARSE(p_source => v_response);
v_value := APEX_JSON.GET_VARCHAR2('result.value');

-- Binary response
v_blob := APEX_WEB_SERVICE.MAKE_REST_REQUEST_B(
    p_url         => 'https://api.example.com/file/123',
    p_http_method => 'GET'
);

-- OAuth
APEX_WEB_SERVICE.OAUTH_AUTHENTICATE(
    p_token_url     => 'https://auth.example.com/token',
    p_client_id     => v_client_id,
    p_client_secret => v_client_secret
);
v_token := APEX_WEB_SERVICE.OAUTH_GET_LAST_TOKEN;

-- SOAP
v_xml := APEX_WEB_SERVICE.MAKE_REQUEST(
    p_url      => 'https://soap.example.com/service',
    p_action   => 'GetData',
    p_version  => '1.1',
    p_envelope => v_soap_envelope
);
v_result := APEX_WEB_SERVICE.PARSE_XML(v_xml, '//GetDataResult/text()', 'xmlns:s="..."');
```

---

### APEX_ZIP — ZIP Archives

```plsql
-- Create ZIP
DECLARE
    v_zip BLOB := EMPTY_BLOB();
BEGIN
    DBMS_LOB.CREATETEMPORARY(v_zip, TRUE);
    APEX_ZIP.ADD_FILE(v_zip, 'readme.txt', v_readme_blob);
    APEX_ZIP.ADD_FILE(v_zip, 'data.csv',   v_csv_blob);
    APEX_ZIP.FINISH(v_zip);
END;

-- Read ZIP
v_files := APEX_ZIP.GET_FILES(p_zipped_blob => v_zip);
FOR i IN 1..v_files.COUNT LOOP
    v_content := APEX_ZIP.GET_FILE_CONTENT(v_zip, v_files(i));
END LOOP;
```

---

### APEX_EXPORT — Application Export

```plsql
-- Export application as CLOB collection
v_files := APEX_EXPORT.GET_APPLICATION(
    p_application_id       => 400,
    p_split                => FALSE,
    p_with_date            => TRUE,
    p_with_ir_public_reports => TRUE
);

FOR i IN 1..v_files.COUNT LOOP
    -- v_files(i).name = file name
    -- v_files(i).contents = CLOB content
    DBMS_OUTPUT.PUT_LINE(v_files(i).name);
END LOOP;
```

---

## Interactive Components

### APEX_IG — Interactive Grid

```plsql
APEX_IG.ADD_FILTER(
    p_page_id          => 10,
    p_region_static_id => 'employees_ig',
    p_filter_type      => 'COLUMN',
    p_column_name      => 'DEPT_ID',
    p_filter_value     => '10'
);
APEX_IG.CLEAR_REPORT(p_page_id => 10, p_region_static_id => 'employees_ig', p_report_id => v_report_id);
APEX_IG.RESET_REPORT(p_page_id => 10, p_region_static_id => 'employees_ig', p_report_id => v_report_id);
v_last := APEX_IG.GET_LAST_VIEWED_REPORT_ID('employees_ig');
```

---

### APEX_IR — Interactive Report

```plsql
APEX_IR.ADD_FILTER(
    p_page_id          => 20,
    p_region_static_id => 'orders_ir',
    p_report_column    => 'STATUS',
    p_operator_abbr    => 'EQ',
    p_filter_value     => 'ACTIVE',
    p_app_user         => :APP_USER
);
APEX_IR.CLEAR_REPORT(p_page_id => 20, p_region_static_id => 'orders_ir', p_app_user => :APP_USER);
APEX_IR.RESET_REPORT(p_page_id => 20, p_region_static_id => 'orders_ir', p_app_user => :APP_USER);
v_report_id := APEX_IR.GET_LAST_VIEWED_REPORT_ID(20, 'orders_ir');
```

---

## Utilities

### APEX_UTIL — General Utilities (the broadest package)

#### Session State
```plsql
apex_util.set_session_state('P10_NOMBRE', v_value);
v_val := apex_util.get_session_state('P10_NOMBRE');

-- Preferences (persisted across sessions)
apex_util.set_preference('MY_PREF', v_value, :APP_USER);
v_val := apex_util.get_preference('MY_PREF', :APP_USER);
apex_util.remove_preference('MY_PREF', :APP_USER);
```

#### User Management
```plsql
apex_util.create_user(
    p_user_name       => 'NEW_USER',
    p_email_address   => 'user@example.com',
    p_web_password    => 'temp_pass',
    p_developer_privs => ''
);
apex_util.edit_user(p_user_id => v_uid, p_user_name => 'NEW_USER', p_email_address => 'new@email.com');
apex_util.change_current_user_pw(p_new_password => v_new_pwd);
v_valid := apex_util.is_login_password_valid('USER', 'PASS');
v_uid   := apex_util.get_user_id('USERNAME');
v_email := apex_util.get_email;
v_groups := apex_util.get_groups_user_belongs_to('USERNAME');
apex_util.set_group_grant_privs(p_group_name => 'MY_GROUP', p_privs => 'USER');
```

#### Security and Workspace
```plsql
apex_util.set_security_group_id(p_security_group_id => v_ws_id);
v_ws_id := apex_util.find_security_group_id('MY_WORKSPACE');
apex_util.set_workspace('MY_WORKSPACE');
apex_util.set_parsing_schema_for_request('ANAMNESIS');
```

#### URL and Navigation
```plsql
v_encoded := apex_util.url_encode(v_param);
v_url     := apex_util.prepare_url('f?p=400:10:&APP_SESSION.');
apex_util.redirect_url(v_url);
v_host    := apex_util.host_url('SCRIPT');  -- base URL with /ords/
```

#### Hash and Security
```plsql
v_hash := apex_util.get_hash(p_concat_value => v_id || v_user);
v_hash := apex_util.get_hash(apex_t_varchar2(v_val1, v_val2, v_val3));
```

#### Cache Control
```plsql
apex_util.clear_page_cache(p_page_id => 10);
apex_util.clear_app_cache(p_app_id => 400);
apex_util.clear_user_cache;
```

#### Application Control
```plsql
apex_util.set_application_status(
    p_application_id     => 400,
    p_application_status => 'RESTRICTED_ACCESS',
    p_restricted_user_list => 'ADMIN'
);
```

---

### APEX_STRING_UTIL — Text Utilities

```plsql
v_diff     := APEX_STRING_UTIL.DIFF(v_old_clob, v_new_clob);
v_emails   := APEX_STRING_UTIL.FIND_EMAIL_ADDRESSES(v_text);
v_slug     := APEX_STRING_UTIL.GET_SLUG('Hello World');  -- 'hello-world'
v_size     := APEX_STRING_UTIL.TO_DISPLAY_FILESIZE(1048576);  -- '1 MB'
v_domain   := APEX_STRING_UTIL.GET_DOMAIN('https://example.com/path');
v_ext      := APEX_STRING_UTIL.GET_FILE_EXTENSION('report.xlsx');
```

---

### APEX_LANG — Internationalization

```plsql
v_translated := APEX_LANG.MESSAGE(
    p_name           => 'MSG_GREETING',
    p0               => v_username,
    p_application_id => :APP_ID
);
v_msg := APEX_LANG.LANG('Hello World');
APEX_LANG.CREATE_MESSAGE(
    p_application_id => :APP_ID,
    p_name           => 'MSG_NEW',
    p_language       => 'es',
    p_message_text   => 'Nuevo mensaje'
);
```

---

### APEX_SPATIAL — Geospatial (20.1+)

```plsql
v_point  := APEX_SPATIAL.POINT(p_longitude => -57.5, p_latitude => -25.3);
v_circle := APEX_SPATIAL.CIRCLE_POLYGON(-57.5, -25.3, 1000, 0.5, 8307);
v_rect   := APEX_SPATIAL.RECTANGLE(-57.6, -25.4, -57.4, -25.2, 8307);
```

---

## Admin & Install

### APEX_APPLICATION_INSTALL

```plsql
APEX_APPLICATION_INSTALL.SET_SCHEMA('NEW_SCHEMA');
APEX_APPLICATION_INSTALL.SET_WORKSPACE('MY_WORKSPACE');
APEX_APPLICATION_INSTALL.SET_APPLICATION_ID(p_application_id => 400);
APEX_APPLICATION_INSTALL.GENERATE_OFFSET;
APEX_APPLICATION_INSTALL.INSTALL(p_source => v_export_clob);
APEX_APPLICATION_INSTALL.REMOVE_APPLICATION(p_application_id => 999);
```

---

### APEX_INSTANCE_ADMIN

```plsql
APEX_INSTANCE_ADMIN.ADD_WORKSPACE(p_workspace => 'MY_WS', p_schema => 'MY_SCHEMA');
APEX_INSTANCE_ADMIN.SET_PARAMETER('MAX_SESSION_LENGTH_SEC', '28800');
v_val := APEX_INSTANCE_ADMIN.GET_PARAMETER('MAX_SESSION_LENGTH_SEC');
APEX_INSTANCE_ADMIN.REMOVE_APPLICATION(p_application_id => 999);
```

---

### APEX_APP_SETTING

```plsql
APEX_APP_SETTING.SET_VALUE(p_name => 'MAX_ITEMS', p_value => '100');
v_val := APEX_APP_SETTING.GET_VALUE(p_name => 'MAX_ITEMS');
```

---

### APEX_UI_DEFAULT_UPDATE

```plsql
APEX_UI_DEFAULT_UPDATE.SYNCH_TABLE(p_table_name => 'CLIENTE');
APEX_UI_DEFAULT_UPDATE.UPD_COLUMN(
    p_table_name       => 'CLIENTE',
    p_column_name      => 'FECHA_NACIMIENTO',
    p_label            => 'Date of Birth',
    p_format_mask      => 'DD/MM/YYYY',
    p_display_seq_form => 3,
    p_display_in_form  => 'YES'
);
```

---

## Debugging

### APEX_DEBUG

```plsql
APEX_DEBUG.ENTER('pkg_my.procedure_name', 'p_id', p_id);
APEX_DEBUG.MESSAGE('Processing %s records for user %s', v_count, apex_application.g_user);
APEX_DEBUG.INFO('Checkpoint reached');
APEX_DEBUG.WARN('Unexpected state: %s', v_state);
APEX_DEBUG.ERROR('Fatal error in %s: %s', $$plsql_unit, SQLERRM);
APEX_DEBUG.EXIT('pkg_my.procedure_name');

-- Level constants
-- APEX_DEBUG.C_LOG_LEVEL_ERROR       = 1
-- APEX_DEBUG.C_LOG_LEVEL_WARN        = 2
-- APEX_DEBUG.C_LOG_LEVEL_INFO        = 4
-- APEX_DEBUG.C_LOG_LEVEL_APP_TRACE   = 6
-- APEX_DEBUG.C_LOG_LEVEL_ENGINE_TRACE = 9
```

---

## Tokens

### APEX_JWT — JSON Web Tokens (20.1+)

```plsql
v_token := APEX_JWT.ENCODE(
    p_iss         => 'my-app',
    p_sub         => :APP_USER,
    p_exp         => SYSDATE + 1/24,
    p_private_key => v_key,
    p_algorithm   => 'HS256'
);

l_token := APEX_JWT.DECODE(
    p_jwt       => v_token_string,
    p_algorithm => 'HS256',
    p_key       => v_key
);
APEX_JWT.VALIDATE(l_token, p_iss => 'my-app', p_leeway => 60);
```

---

## Plugins

### APEX_PLUGIN

```plsql
v_ajax_id := APEX_PLUGIN.GET_AJAX_IDENTIFIER;
v_name    := APEX_PLUGIN.GET_INPUT_NAME_FOR_PAGE_ITEM(p_is_multi_value => FALSE);
```

---

### APEX_PLUGIN_UTIL

```plsql
APEX_PLUGIN_UTIL.EXECUTE_PLSQL_CODE(p_plsql_code => v_code);
APEX_PLUGIN_UTIL.PRINT_JSON_HTTP_HEADER;
APEX_PLUGIN_UTIL.PRINT_LOV_AS_JSON(
    p_lov_query => 'SELECT display, value FROM my_lov ORDER BY display',
    p_null_text => '- Select -'
);
v_result := APEX_PLUGIN_UTIL.GET_PLSQL_FUNCTION_RESULT(
    p_plsql_function_body => 'RETURN my_pkg.get_value(:P10_ID);'
);
v_safe := APEX_PLUGIN_UTIL.REPLACE_SUBSTITUTIONS(p_template => 'Hello #APP_USER#!');
```

---

## Other Packages

### APEX_LDAP

```plsql
IF APEX_LDAP.AUTHENTICATE(
    p_username    => :P9999_USERNAME,
    p_password    => :P9999_PASSWORD,
    p_ldap_host   => 'ldap.example.com',
    p_ldap_port   => 389,
    p_search_base => 'dc=example,dc=com'
) THEN ...
```

---

### APEX_REST_SOURCE_SYNC (20.1+)

```plsql
APEX_REST_SOURCE_SYNC.SYNCHRONIZE_DATA(p_static_id => 'MY_REST_SOURCE');
APEX_REST_SOURCE_SYNC.SYNCHRONIZE_TABLE_DEFINITION(p_static_id => 'MY_REST_SOURCE');
v_ts := APEX_REST_SOURCE_SYNC.GET_LAST_SYNC_TIMESTAMP(p_static_id => 'MY_REST_SOURCE');
```

---

## Standard AJAX Callback Pattern

### PL/SQL (On-Demand Process)
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

### JavaScript
```javascript
apex.server.process('PROCESS_NAME', {
    x01: apex.item('P10_ID').getValue(),
    x02: apex.item('P10_NAME').getValue(),
    pageItems: '#P10_EXTRA'
}, {
    dataType: 'json',
    success: function(data) {
        if (data.status === 'OK') {
            apex.message.showPageSuccess(data.message);
        } else {
            apex.message.showErrors([{type:'error', location:'page', message: data.message}]);
        }
    },
    error: function(jqXHR, textStatus) {
        apex.message.showErrors([{type:'error', location:'page', message:'Server error: ' + textStatus}]);
    }
});
```

---

## Critical Rules

1. **APEX_JSON CLOBs:** NEVER `APEX_JSON.STRINGIFY(clob)` — use `APEX_JSON.WRITE(p_name, p_value CLOB)` overload
2. **APEX_EXEC:** ALWAYS call `APEX_EXEC.CLOSE(l_ctx)` in the EXCEPTION handler to free cursors
3. **APEX_SESSION:** Use `ATTACH/DETACH` for scripts outside HTTP context (jobs, SQL scripts)
4. **APEX_ERROR.ADD_ERROR:** For Interactive Grid errors use Signature 4 with `p_region_id`
5. **APEX_APPLICATION.STOP_APEX_ENGINE:** Call before writing BLOB response to stop normal rendering
6. **APEX_WEB_SERVICE:** Always check `G_STATUS_CODE` after every REST call
7. **APEX_UTIL.SET_SESSION_STATE:** Sets page items; `g_x01..g_x20` reads incoming AJAX parameters
8. **APEX_COLLECTION:** NEVER use UPDATE/INSERT/DELETE on `apex_collections` view (ORA-01732)

---

## ORDS REST Administration API

**Base URL:** `{instance}/ords/apex_instance_admin_user/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/stats/latest/instance` | GET | Instance statistics |
| `/stats/latest/workspace/{name}` | GET | Workspace statistics |
| `/stats/latest/application/{id}` | GET | Application statistics |
| `/info/latest/instance/{days}` | GET | Aggregated summary (N days) |
| `/info/latest/` | GET | API version |
