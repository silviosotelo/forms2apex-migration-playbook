# Oracle Database PL/SQL APIs — Reference for APEX Development

Commonly used Oracle DB packages, functions, and patterns in APEX applications.

---

## DBMS_LOB — Large Object Manipulation

### Key Functions
```plsql
-- Get CLOB/BLOB length
v_len := DBMS_LOB.GETLENGTH(v_clob);

-- Read substring (up to 32767 chars)
v_chunk := DBMS_LOB.SUBSTR(v_clob, p_amount => 4000, p_offset => 1);

-- Create temporary LOB
DBMS_LOB.CREATETEMPORARY(v_clob, TRUE);  -- TRUE = cache

-- Write/append to CLOB
DBMS_LOB.WRITEAPPEND(v_clob, LENGTH(v_text), v_text);

-- Copy between LOBs
DBMS_LOB.COPY(
    dest_lob    => v_dest,
    src_lob     => v_src,
    amount      => DBMS_LOB.GETLENGTH(v_src),
    dest_offset => 1,
    src_offset  => 1
);

-- Compare LOBs (returns 0 if equal)
IF DBMS_LOB.COMPARE(v_lob1, v_lob2) = 0 THEN ...

-- Free temporary LOB
IF DBMS_LOB.ISTEMPORARY(v_clob) = 1 THEN
    DBMS_LOB.FREETEMPORARY(v_clob);
END IF;

-- Trim LOB
DBMS_LOB.TRIM(v_clob, 0);  -- empty it

-- Search within LOB
v_pos := DBMS_LOB.INSTR(v_clob, 'search_text', 1, 1);
```

### Chunk Reading Pattern (for large CLOBs)
```plsql
DECLARE
    v_clob    CLOB := :P10_BIG_DATA;
    v_len     PLS_INTEGER := DBMS_LOB.GETLENGTH(v_clob);
    v_chunk   VARCHAR2(32767);
    v_offset  PLS_INTEGER := 1;
    v_amount  PLS_INTEGER := 8000;
BEGIN
    WHILE v_offset <= v_len LOOP
        v_chunk := DBMS_LOB.SUBSTR(v_clob, v_amount, v_offset);
        -- Process chunk...
        HTP.PRN(v_chunk);
        v_offset := v_offset + v_amount;
    END LOOP;
END;
```

### CLOB Construction Pattern
```plsql
DECLARE
    v_clob CLOB;
BEGIN
    DBMS_LOB.CREATETEMPORARY(v_clob, TRUE);
    FOR r IN (SELECT line_text FROM my_lines ORDER BY line_no) LOOP
        DBMS_LOB.WRITEAPPEND(v_clob, LENGTH(r.line_text), r.line_text);
    END LOOP;
    -- Use v_clob...
    DBMS_LOB.FREETEMPORARY(v_clob);
END;
```

---

## DBMS_SQL — Dynamic SQL

```plsql
DECLARE
    v_cursor  INTEGER := DBMS_SQL.OPEN_CURSOR;
    v_sql     VARCHAR2(4000) := 'SELECT * FROM ' || v_table_name;
    v_col_cnt INTEGER;
    v_desc    DBMS_SQL.DESC_TAB;
    v_rows    INTEGER;
BEGIN
    DBMS_SQL.PARSE(v_cursor, v_sql, DBMS_SQL.NATIVE);
    DBMS_SQL.DESCRIBE_COLUMNS(v_cursor, v_col_cnt, v_desc);

    -- Print column names
    FOR i IN 1..v_col_cnt LOOP
        DBMS_OUTPUT.PUT_LINE(v_desc(i).col_name || ' ' || v_desc(i).col_type);
    END LOOP;

    -- Define columns for fetch
    FOR i IN 1..v_col_cnt LOOP
        DBMS_SQL.DEFINE_COLUMN(v_cursor, i, '', 4000);
    END LOOP;

    v_rows := DBMS_SQL.EXECUTE(v_cursor);

    WHILE DBMS_SQL.FETCH_ROWS(v_cursor) > 0 LOOP
        FOR i IN 1..v_col_cnt LOOP
            DBMS_SQL.COLUMN_VALUE(v_cursor, i, v_value);
        END LOOP;
    END LOOP;

    DBMS_SQL.CLOSE_CURSOR(v_cursor);
EXCEPTION
    WHEN OTHERS THEN
        IF DBMS_SQL.IS_OPEN(v_cursor) THEN
            DBMS_SQL.CLOSE_CURSOR(v_cursor);
        END IF;
        RAISE;
END;
```

---

## DBMS_METADATA — DDL Extraction

```plsql
-- Get DDL for various object types
SELECT DBMS_METADATA.GET_DDL('TABLE',     'CLIENTE',     'ANAMNESIS') FROM DUAL;
SELECT DBMS_METADATA.GET_DDL('VIEW',      'VW_CLIENTES', 'ANAMNESIS') FROM DUAL;
SELECT DBMS_METADATA.GET_DDL('PACKAGE',   'PKG_CLIENTES','ANAMNESIS') FROM DUAL;
SELECT DBMS_METADATA.GET_DDL('PROCEDURE', 'PR_CALCULAR', 'ANAMNESIS') FROM DUAL;
SELECT DBMS_METADATA.GET_DDL('FUNCTION',  'FN_VALOR',    'ANAMNESIS') FROM DUAL;
SELECT DBMS_METADATA.GET_DDL('TRIGGER',   'TRG_AUDIT',   'ANAMNESIS') FROM DUAL;
SELECT DBMS_METADATA.GET_DDL('INDEX',     'IDX_CLI_CI',  'ANAMNESIS') FROM DUAL;
SELECT DBMS_METADATA.GET_DDL('SEQUENCE',  'SEQ_CLIENTE', 'ANAMNESIS') FROM DUAL;

-- Get dependent DDL (constraints, indexes for a table)
SELECT DBMS_METADATA.GET_DEPENDENT_DDL('INDEX', 'CLIENTE', 'ANAMNESIS') FROM DUAL;
SELECT DBMS_METADATA.GET_DEPENDENT_DDL('CONSTRAINT', 'CLIENTE', 'ANAMNESIS') FROM DUAL;

-- Transform options (remove storage, tablespace, etc.)
BEGIN
    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'STORAGE', FALSE);
    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'TABLESPACE', FALSE);
    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SEGMENT_ATTRIBUTES', FALSE);
    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SQLTERMINATOR', TRUE);
END;
```

---

## DBMS_SESSION / DBMS_APPLICATION_INFO — Session Context

```plsql
-- Tag session for tracing/monitoring
DBMS_APPLICATION_INFO.SET_MODULE(
    module_name => 'APEX_APP_400',
    action_name => 'SAVE_CUSTOMER'
);

DBMS_APPLICATION_INFO.SET_CLIENT_INFO('User: ADMIN, Page: 945');

-- Read back
DBMS_APPLICATION_INFO.READ_MODULE(v_module, v_action);
DBMS_APPLICATION_INFO.READ_CLIENT_INFO(v_client_info);

-- Set context
DBMS_SESSION.SET_CONTEXT('MY_CTX', 'COMPANY_ID', '123');
v_val := SYS_CONTEXT('MY_CTX', 'COMPANY_ID');
```

---

## DBMS_SCHEDULER — Job Scheduling

```plsql
-- Create a one-time job
DBMS_SCHEDULER.CREATE_JOB(
    job_name        => 'JOB_SYNC_DATA',
    job_type        => 'PLSQL_BLOCK',
    job_action      => 'BEGIN pkg_sync.run_sync; END;',
    start_date      => SYSTIMESTAMP,
    enabled         => TRUE,
    auto_drop       => TRUE,
    comments        => 'One-time data sync'
);

-- Create a recurring job
DBMS_SCHEDULER.CREATE_JOB(
    job_name        => 'JOB_NIGHTLY_REPORT',
    job_type        => 'PLSQL_BLOCK',
    job_action      => 'BEGIN pkg_reports.generate_nightly; END;',
    start_date      => SYSTIMESTAMP,
    repeat_interval => 'FREQ=DAILY; BYHOUR=2; BYMINUTE=0; BYSECOND=0',
    enabled         => TRUE,
    auto_drop       => FALSE,
    comments        => 'Nightly report generation'
);

-- Common repeat_interval patterns
-- Every 5 minutes:    'FREQ=MINUTELY; INTERVAL=5'
-- Every hour:         'FREQ=HOURLY; INTERVAL=1'
-- Daily at 3 AM:      'FREQ=DAILY; BYHOUR=3; BYMINUTE=0'
-- Mon-Fri at 8 AM:    'FREQ=DAILY; BYDAY=MON,TUE,WED,THU,FRI; BYHOUR=8'
-- First day of month:  'FREQ=MONTHLY; BYMONTHDAY=1; BYHOUR=0'
-- Every 30 seconds:   'FREQ=SECONDLY; INTERVAL=30'

-- Run immediately
DBMS_SCHEDULER.RUN_JOB('JOB_SYNC_DATA', use_current_session => FALSE);

-- Stop / Drop
DBMS_SCHEDULER.STOP_JOB('JOB_SYNC_DATA');
DBMS_SCHEDULER.DROP_JOB('JOB_SYNC_DATA', force => TRUE);

-- Enable/Disable
DBMS_SCHEDULER.ENABLE('JOB_NIGHTLY_REPORT');
DBMS_SCHEDULER.DISABLE('JOB_NIGHTLY_REPORT');

-- Check job status
SELECT job_name, state, last_start_date, next_run_date, run_count, failure_count
FROM   user_scheduler_jobs;

-- Check job run history
SELECT job_name, status, actual_start_date, run_duration, additional_info
FROM   user_scheduler_job_run_details
WHERE  job_name = 'JOB_NIGHTLY_REPORT'
ORDER  BY actual_start_date DESC;
```

---

## DBMS_CRYPTO — Hashing and Encryption

```plsql
-- Hash constants
-- DBMS_CRYPTO.HASH_SH1   = SHA-1 (160-bit)
-- DBMS_CRYPTO.HASH_SH256 = SHA-256 (256-bit)
-- DBMS_CRYPTO.HASH_SH512 = SHA-512 (512-bit)
-- DBMS_CRYPTO.HASH_MD5   = MD5 (128-bit, deprecated for security)

-- Hash a string
v_hash_raw := DBMS_CRYPTO.HASH(
    src => UTL_RAW.CAST_TO_RAW('text to hash'),
    typ => DBMS_CRYPTO.HASH_SH256
);
v_hash_hex := RAWTOHEX(v_hash_raw);
-- or lowercase: v_hash_hex := LOWER(RAWTOHEX(v_hash_raw));

-- Hash a CLOB
v_hash_raw := DBMS_CRYPTO.HASH(
    src => v_clob,
    typ => DBMS_CRYPTO.HASH_SH256
);

-- AES-256 Encryption
DECLARE
    v_key     RAW(32) := UTL_RAW.CAST_TO_RAW('12345678901234567890123456789012');  -- 32 bytes
    v_iv      RAW(16) := UTL_RAW.CAST_TO_RAW('1234567890123456');  -- 16 bytes
    v_enc_typ PLS_INTEGER := DBMS_CRYPTO.ENCRYPT_AES256
                           + DBMS_CRYPTO.CHAIN_CBC
                           + DBMS_CRYPTO.PAD_PKCS5;
    v_encrypted RAW(2000);
    v_decrypted RAW(2000);
BEGIN
    v_encrypted := DBMS_CRYPTO.ENCRYPT(
        src => UTL_RAW.CAST_TO_RAW('secret data'),
        typ => v_enc_typ,
        key => v_key,
        iv  => v_iv
    );

    v_decrypted := DBMS_CRYPTO.DECRYPT(
        src => v_encrypted,
        typ => v_enc_typ,
        key => v_key,
        iv  => v_iv
    );

    DBMS_OUTPUT.PUT_LINE(UTL_RAW.CAST_TO_VARCHAR2(v_decrypted));
END;

-- HMAC (Hash-based Message Authentication Code)
v_hmac := DBMS_CRYPTO.MAC(
    src => UTL_RAW.CAST_TO_RAW('message'),
    typ => DBMS_CRYPTO.HMAC_SH256,
    key => UTL_RAW.CAST_TO_RAW('secret_key')
);
```

---

## UTL_RAW — Raw Data Conversion

```plsql
-- String ↔ RAW
v_raw := UTL_RAW.CAST_TO_RAW('Hello World');
v_str := UTL_RAW.CAST_TO_VARCHAR2(v_raw);

-- Concatenate RAW values
v_combined := UTL_RAW.CONCAT(v_raw1, v_raw2, v_raw3);

-- Compare RAW values
IF UTL_RAW.COMPARE(v_raw1, v_raw2) = 0 THEN -- equal

-- Substring of RAW
v_sub := UTL_RAW.SUBSTR(v_raw, 1, 10);

-- Length of RAW
v_len := UTL_RAW.LENGTH(v_raw);

-- XOR (useful for crypto)
v_xor := UTL_RAW.BIT_XOR(v_raw1, v_raw2);
```

---

## UTL_ENCODE — Base64 Encoding

```plsql
-- Base64 Encode
v_base64 := UTL_ENCODE.BASE64_ENCODE(UTL_RAW.CAST_TO_RAW('Hello World'));
-- Returns RAW, convert to string:
v_str := UTL_RAW.CAST_TO_VARCHAR2(UTL_ENCODE.BASE64_ENCODE(UTL_RAW.CAST_TO_RAW('Hello')));

-- Base64 Decode
v_raw := UTL_ENCODE.BASE64_DECODE(UTL_RAW.CAST_TO_RAW('SGVsbG8='));
v_str := UTL_RAW.CAST_TO_VARCHAR2(v_raw);

-- BLOB to Base64 CLOB (complete pattern)
FUNCTION blob_to_base64(p_blob BLOB) RETURN CLOB IS
    v_clob    CLOB;
    v_step    PLS_INTEGER := 12000;  -- must be multiple of 3
    v_offset  PLS_INTEGER := 1;
    v_len     PLS_INTEGER := DBMS_LOB.GETLENGTH(p_blob);
BEGIN
    DBMS_LOB.CREATETEMPORARY(v_clob, TRUE);
    WHILE v_offset <= v_len LOOP
        DBMS_LOB.WRITEAPPEND(
            v_clob,
            LENGTH(UTL_RAW.CAST_TO_VARCHAR2(
                UTL_ENCODE.BASE64_ENCODE(DBMS_LOB.SUBSTR(p_blob, v_step, v_offset))
            )),
            UTL_RAW.CAST_TO_VARCHAR2(
                UTL_ENCODE.BASE64_ENCODE(DBMS_LOB.SUBSTR(p_blob, v_step, v_offset))
            )
        );
        v_offset := v_offset + v_step;
    END LOOP;
    RETURN v_clob;
END;

-- URL-safe Base64 (replace +/ with -_)
v_urlsafe := REPLACE(REPLACE(v_base64_str, '+', '-'), '/', '_');
```

---

## UTL_URL — URL Encoding

```plsql
-- URL encode (UTF-8)
v_encoded := UTL_URL.ESCAPE(
    url            => v_param_value,
    escape_reserved_chars => TRUE,
    url_charset    => 'UTF-8'
);

-- URL decode
v_decoded := UTL_URL.UNESCAPE(
    url         => v_encoded_value,
    url_charset => 'UTF-8'
);
```

---

## UTL_HTTP — HTTP Client

> **Prefer `APEX_WEB_SERVICE.MAKE_REST_REQUEST` in APEX contexts.** Use UTL_HTTP only when you need streaming, chunked transfer, or run outside APEX.

```plsql
DECLARE
    v_req  UTL_HTTP.REQ;
    v_resp UTL_HTTP.RESP;
    v_body VARCHAR2(32767);
BEGIN
    -- Set wallet for HTTPS
    UTL_HTTP.SET_WALLET('file:/path/to/wallet', 'wallet_password');

    v_req := UTL_HTTP.BEGIN_REQUEST('https://api.example.com/data', 'POST');
    UTL_HTTP.SET_HEADER(v_req, 'Content-Type', 'application/json');
    UTL_HTTP.SET_HEADER(v_req, 'Authorization', 'Bearer ' || v_token);
    UTL_HTTP.SET_HEADER(v_req, 'Content-Length', LENGTH(v_json_body));
    UTL_HTTP.WRITE_TEXT(v_req, v_json_body);

    v_resp := UTL_HTTP.GET_RESPONSE(v_req);

    -- Read response
    BEGIN
        LOOP
            UTL_HTTP.READ_TEXT(v_resp, v_body, 32767);
        END LOOP;
    EXCEPTION
        WHEN UTL_HTTP.END_OF_BODY THEN NULL;
    END;

    UTL_HTTP.END_RESPONSE(v_resp);
EXCEPTION
    WHEN OTHERS THEN
        IF v_resp.status_code IS NOT NULL THEN
            UTL_HTTP.END_RESPONSE(v_resp);
        END IF;
        RAISE;
END;
```

---

## JSON_OBJECT_T / JSON_ARRAY_T — Native JSON (12c+)

```plsql
-- Build JSON object
DECLARE
    v_obj  JSON_OBJECT_T := JSON_OBJECT_T();
    v_arr  JSON_ARRAY_T  := JSON_ARRAY_T();
    v_clob CLOB;
BEGIN
    v_obj.put('name', 'Juan');
    v_obj.put('age', 30);
    v_obj.put('active', TRUE);
    v_obj.put_null('middle_name');

    v_arr.append('item1');
    v_arr.append('item2');
    v_obj.put('tags', v_arr);

    v_clob := v_obj.to_clob;
    -- {"name":"Juan","age":30,"active":true,"middle_name":null,"tags":["item1","item2"]}
END;

-- Parse JSON
DECLARE
    v_obj  JSON_OBJECT_T;
    v_arr  JSON_ARRAY_T;
BEGIN
    v_obj := JSON_OBJECT_T.parse('{"name":"Juan","items":[1,2,3]}');
    v_name := v_obj.get_string('name');
    v_arr  := v_obj.get_array('items');

    FOR i IN 0..v_arr.get_size - 1 LOOP  -- 0-based!
        DBMS_OUTPUT.PUT_LINE(v_arr.get_number(i));
    END LOOP;

    -- Check key existence
    IF v_obj.has('name') THEN ...
    IF v_obj.get('maybe_null').is_null THEN ...
END;

-- JSON_TABLE (12c R2+, SQL-level parsing)
SELECT jt.*
FROM   my_table t,
       JSON_TABLE(t.json_col, '$'
           COLUMNS (
               name    VARCHAR2(100) PATH '$.name',
               age     NUMBER        PATH '$.age',
               NESTED PATH '$.items[*]'
                   COLUMNS (
                       item_id   NUMBER        PATH '$.id',
                       item_name VARCHAR2(200) PATH '$.name'
                   )
           )
       ) jt;

-- JSON_OBJECT / JSON_ARRAY in SQL (12c R2+)
SELECT JSON_OBJECT(
    'id'   VALUE id,
    'name' VALUE name,
    'items' VALUE JSON_ARRAYAGG(
        JSON_OBJECT('item_id' VALUE item_id, 'desc' VALUE description)
    )
) AS json_data
FROM  my_table
GROUP BY id, name;

-- IS JSON check
SELECT * FROM my_table WHERE json_col IS JSON;
```

---

## REGEXP Functions

```plsql
-- REGEXP_LIKE — Boolean match (use in WHERE)
SELECT * FROM cliente
WHERE  REGEXP_LIKE(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- REGEXP_REPLACE — Replace with regex
v_clean := REGEXP_REPLACE(v_phone, '[^0-9]', '');  -- digits only
v_spaced := REGEXP_REPLACE(v_text, '([A-Z])', ' \1');  -- space before caps

-- REGEXP_SUBSTR — Extract match
v_domain := REGEXP_SUBSTR(v_email, '@(.+)$', 1, 1, NULL, 1);  -- group 1
v_first_word := REGEXP_SUBSTR(v_text, '\w+');  -- first word
v_nth_part := REGEXP_SUBSTR('A,B,C,D', '[^,]+', 1, 3);  -- 'C' (3rd occurrence)

-- REGEXP_COUNT — Count matches
v_cnt := REGEXP_COUNT(v_text, '\d+');  -- count numbers

-- REGEXP_INSTR — Position of match
v_pos := REGEXP_INSTR(v_text, '\d{3}-\d{4}');  -- position of phone pattern
```

---

## Analytic / Window Functions

```plsql
-- ROW_NUMBER — sequential numbering
SELECT ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rn,
       employee_name, salary
FROM   employees;

-- RANK / DENSE_RANK
SELECT RANK()       OVER (ORDER BY score DESC) AS rank_with_gaps,
       DENSE_RANK() OVER (ORDER BY score DESC) AS rank_no_gaps
FROM   scores;

-- LAG / LEAD — previous/next row values
SELECT fecha,
       monto,
       LAG(monto, 1, 0) OVER (ORDER BY fecha) AS monto_anterior,
       LEAD(monto, 1, 0) OVER (ORDER BY fecha) AS monto_siguiente
FROM   movimientos;

-- LISTAGG — aggregate strings
SELECT dept_id,
       LISTAGG(employee_name, ', ') WITHIN GROUP (ORDER BY employee_name) AS members
FROM   employees
GROUP  BY dept_id;

-- LISTAGG DISTINCT (19c+)
SELECT dept_id,
       LISTAGG(DISTINCT job_title, ', ') WITHIN GROUP (ORDER BY job_title) AS titles
FROM   employees
GROUP  BY dept_id;

-- PIVOT
SELECT *
FROM   (SELECT dept_id, job_title, salary FROM employees)
PIVOT  (SUM(salary) FOR job_title IN ('MANAGER' AS mgr, 'CLERK' AS clk, 'ANALYST' AS anl));

-- UNPIVOT
SELECT *
FROM   quarterly_sales
UNPIVOT (amount FOR quarter IN (q1_sales AS 'Q1', q2_sales AS 'Q2', q3_sales AS 'Q3', q4_sales AS 'Q4'));

-- Running totals
SELECT fecha, monto,
       SUM(monto) OVER (ORDER BY fecha ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM   movimientos;

-- Top-N per group
SELECT * FROM (
    SELECT e.*, ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rn
    FROM   employees e
) WHERE rn <= 3;

-- FETCH FIRST (12c+)
SELECT * FROM employees ORDER BY salary DESC FETCH FIRST 10 ROWS ONLY;
SELECT * FROM employees ORDER BY salary DESC OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;
```

---

## DBMS_STATS — Optimizer Statistics

```plsql
-- Gather stats for a single table
DBMS_STATS.GATHER_TABLE_STATS(
    ownname => 'ANAMNESIS',
    tabname => 'CLIENTE',
    cascade => TRUE,  -- include indexes
    estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE
);

-- Gather stats for entire schema
DBMS_STATS.GATHER_SCHEMA_STATS(
    ownname          => 'ANAMNESIS',
    estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE,
    options          => 'GATHER AUTO'  -- only stale/missing stats
);

-- Check staleness
SELECT table_name, num_rows, last_analyzed, stale_stats
FROM   all_tab_statistics
WHERE  owner = 'ANAMNESIS'
AND    stale_stats = 'YES';
```

---

## Dictionary Views — Quick Reference

```sql
-- All columns of a table
SELECT column_name, data_type, data_length, nullable, data_default
FROM   all_tab_columns
WHERE  owner = 'ANAMNESIS' AND table_name = 'CLIENTE'
ORDER  BY column_id;

-- All objects of a schema
SELECT object_name, object_type, status, last_ddl_time
FROM   user_objects
WHERE  object_type IN ('TABLE','VIEW','PACKAGE','PROCEDURE','FUNCTION','TRIGGER','SEQUENCE')
ORDER  BY object_type, object_name;

-- Dependencies (what uses what)
SELECT name, type, referenced_name, referenced_type
FROM   user_dependencies
WHERE  referenced_name = 'PKG_CLIENTES'
ORDER  BY name;

-- Indexes on a table
SELECT i.index_name, i.uniqueness, i.status,
       LISTAGG(c.column_name, ', ') WITHIN GROUP (ORDER BY c.column_position) AS columns
FROM   user_indexes i
JOIN   user_ind_columns c ON c.index_name = i.index_name
WHERE  i.table_name = 'CLIENTE'
GROUP  BY i.index_name, i.uniqueness, i.status;

-- Constraints
SELECT constraint_name, constraint_type, search_condition, r_constraint_name, status
FROM   user_constraints
WHERE  table_name = 'CLIENTE';

-- FK details
SELECT a.constraint_name, a.column_name, c.table_name AS ref_table, b.column_name AS ref_column
FROM   user_cons_columns a
JOIN   user_constraints c2 ON c2.constraint_name = a.constraint_name
JOIN   user_constraints c ON c.constraint_name = c2.r_constraint_name
JOIN   user_cons_columns b ON b.constraint_name = c.constraint_name
WHERE  a.table_name = 'CLIENTE'
AND    c2.constraint_type = 'R';

-- PL/SQL source code
SELECT line, text
FROM   user_source
WHERE  name = 'PKG_CLIENTES' AND type = 'PACKAGE BODY'
ORDER  BY line;

-- Invalid objects
SELECT object_name, object_type
FROM   user_objects
WHERE  status = 'INVALID'
ORDER  BY object_type, object_name;

-- Table row counts (from stats, not exact)
SELECT table_name, num_rows, last_analyzed
FROM   user_tables
ORDER  BY num_rows DESC NULLS LAST;

-- Table/index sizes
SELECT segment_name, segment_type,
       ROUND(bytes / 1024 / 1024, 2) AS size_mb
FROM   user_segments
WHERE  segment_type IN ('TABLE', 'INDEX', 'LOB')
ORDER  BY bytes DESC;
```

---

## Combined Patterns: PL/SQL + JS AJAX Callback

### BLOB Download via AJAX
```plsql
-- PL/SQL Process (On Demand): DOWNLOAD_FILE
DECLARE
    v_blob      BLOB;
    v_filename  VARCHAR2(200);
    v_mime      VARCHAR2(100);
BEGIN
    SELECT file_content, file_name, mime_type
    INTO   v_blob, v_filename, v_mime
    FROM   my_files
    WHERE  id = TO_NUMBER(apex_application.g_x01);

    OWA_UTIL.MIME_HEADER(v_mime, FALSE);
    HTP.P('Content-Disposition: attachment; filename="' || v_filename || '"');
    HTP.P('Content-Length: ' || DBMS_LOB.GETLENGTH(v_blob));
    OWA_UTIL.HTTP_HEADER_CLOSE;
    WPG_DOCLOAD.DOWNLOAD_FILE(v_blob);
    APEX_APPLICATION.STOP_APEX_ENGINE;
END;
```

```javascript
// JS: trigger download
window.location.href = apex.server.url({
    x01: fileId,
    p_request: 'APPLICATION_PROCESS=DOWNLOAD_FILE'
});
```

### BLOB Chunk Reading from JS (Large Files)
```plsql
-- PL/SQL Process: GET_FILE_CHUNK
DECLARE
    v_blob    BLOB;
    v_offset  NUMBER := NVL(TO_NUMBER(apex_application.g_x02), 1);
    v_amount  NUMBER := 24000;  -- ~32K base64
    v_chunk   RAW(32767);
    v_len     NUMBER;
BEGIN
    SELECT file_content INTO v_blob
    FROM   my_files
    WHERE  id = TO_NUMBER(apex_application.g_x01);

    v_len := DBMS_LOB.GETLENGTH(v_blob);
    v_amount := LEAST(v_amount, v_len - v_offset + 1);

    IF v_offset <= v_len THEN
        DBMS_LOB.READ(v_blob, v_amount, v_offset, v_chunk);
    END IF;

    apex_json.open_object;
    apex_json.write('total_size', v_len);
    apex_json.write('offset', v_offset);
    apex_json.write('chunk_size', v_amount);
    apex_json.write('data', UTL_RAW.CAST_TO_VARCHAR2(UTL_ENCODE.BASE64_ENCODE(v_chunk)));
    apex_json.write('done', v_offset + v_amount > v_len);
    apex_json.close_object;
END;
```

```javascript
// JS: Read file in chunks
function readFileChunks(fileId, offset, chunks) {
    offset = offset || 1;
    chunks = chunks || [];
    apex.server.process('GET_FILE_CHUNK', {
        x01: fileId,
        x02: String(offset)
    }, {
        dataType: 'json',
        success: function(data) {
            chunks.push(data.data);
            if (!data.done) {
                readFileChunks(fileId, data.offset + data.chunk_size, chunks);
            } else {
                var fullBase64 = chunks.join('');
                // Process complete file...
                console.log('File loaded:', data.total_size, 'bytes');
            }
        }
    });
}
```

### Session-Context Job Pattern (APEX_SESSION + DBMS_SCHEDULER)
```plsql
-- Create a job that runs with APEX session context
DECLARE
    v_job_name VARCHAR2(100) := 'JOB_PROCESS_' || TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS');
BEGIN
    DBMS_SCHEDULER.CREATE_JOB(
        job_name   => v_job_name,
        job_type   => 'PLSQL_BLOCK',
        job_action => '
            BEGIN
                APEX_SESSION.CREATE_SESSION(p_app_id => 400, p_page_id => 1, p_username => ''ADMIN'');
                pkg_batch.heavy_process(p_param => ' || v_param || ');
                APEX_SESSION.DETACH;
            EXCEPTION
                WHEN OTHERS THEN
                    APEX_SESSION.DETACH;
                    RAISE;
            END;',
        start_date => SYSTIMESTAMP,
        enabled    => TRUE,
        auto_drop  => TRUE
    );
END;
```
