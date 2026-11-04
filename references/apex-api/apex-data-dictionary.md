# APEX Data Dictionary Views — Verified Column Reference

> **RULE:** Never assume column names. Always verify with `all_tab_columns`. The error **ORA-00904** is ALWAYS caused by an incorrect column name.

---

## How to Verify Columns

```sql
-- Get the correct APEX schema prefix for your version
SELECT column_name, data_type, data_length
FROM   all_tab_columns
WHERE  owner = (SELECT 'APEX_' || version_no FROM apex_release)
AND    table_name = 'APEX_APPLICATION_PAGE_REGIONS'
ORDER  BY column_id;
```

```sql
-- List all APEX dictionary views
SELECT view_name
FROM   all_views
WHERE  owner = (SELECT 'APEX_' || version_no FROM apex_release)
AND    view_name LIKE 'APEX_APPLICATION%'
ORDER  BY view_name;
```

---

## APEX_APPLICATION_PAGES (89 columns)

### Identity
| Column | Type | Notes |
|--------|------|-------|
| `APPLICATION_ID` | NUMBER | FK to APEX_APPLICATIONS |
| `APPLICATION_NAME` | VARCHAR2 | App display name |
| `PAGE_ID` | NUMBER | Unique page number within app |
| `PAGE_NAME` | VARCHAR2 | Page title/name |
| `PAGE_ALIAS` | VARCHAR2 | Friendly URL alias |
| `PAGE_GROUP` | VARCHAR2 | Logical grouping |
| `PAGE_FUNCTION` | VARCHAR2 | Page purpose tag |
| `PAGE_MODE` | VARCHAR2 | NORMAL, MODAL_DIALOG, NON_MODAL_DIALOG |

### Template / CSS / JS
| Column | Type | Notes |
|--------|------|-------|
| `PAGE_TEMPLATE` | VARCHAR2 | Page template name |
| `INLINE_CSS` | CLOB | CSS in "Inline CSS" section (NOT css_inline) |
| `CSS_FILE_URLS` | VARCHAR2 | External CSS file references |
| `JAVASCRIPT_CODE` | CLOB | "Function and Global Variable Declaration" |
| `JAVASCRIPT_CODE_ONLOAD` | CLOB | "Execute when Page Loads" |
| `JAVASCRIPT_FILE_URLS` | VARCHAR2 | External JS file references |

### Structure
| Column | Type | Notes |
|--------|------|-------|
| `PAGE_TITLE` | VARCHAR2 | Browser title |
| `STEP_TITLE` | VARCHAR2 | Internal step title |
| `HEADER_TEXT` | CLOB | Header text region |
| `FOOTER_TEXT` | CLOB | Footer text region |
| `BODY_HEADER` | CLOB | Body header text |

### Dialog Properties (PAGE_MODE = MODAL_DIALOG)
| Column | Type | Notes |
|--------|------|-------|
| `DIALOG_TITLE` | VARCHAR2 | Modal dialog title |
| `DIALOG_HEIGHT` | VARCHAR2 | Dialog height |
| `DIALOG_WIDTH` | VARCHAR2 | Dialog width |
| `DIALOG_CSS_CLASSES` | VARCHAR2 | Extra CSS classes for dialog |
| `DIALOG_CHAINED` | VARCHAR2 | Yes/No — chain dialogs |

### Authorization / Security
| Column | Type | Notes |
|--------|------|-------|
| `AUTHORIZATION_SCHEME` | VARCHAR2 | Auth scheme name |
| `BUILD_OPTION` | VARCHAR2 | Build option status |
| `READ_ONLY_WHEN_TYPE` | VARCHAR2 | Read-only condition type |
| `READ_ONLY_WHEN` | VARCHAR2 | Read-only condition expression |

### Counters / Metadata
| Column | Type | Notes |
|--------|------|-------|
| `REGIONS` | NUMBER | Count of regions on page |
| `ITEMS` | NUMBER | Count of items on page |
| `BUTTONS` | NUMBER | Count of buttons on page |
| `PROCESSES` | NUMBER | Count of processes on page |
| `COMPUTATIONS` | NUMBER | Count of computations |
| `VALIDATIONS` | NUMBER | Count of validations |
| `BRANCHES` | NUMBER | Count of branches |
| `DYNAMIC_ACTIONS` | NUMBER | Count of dynamic actions |
| `LAST_UPDATED_BY` | VARCHAR2 | Developer who last modified |
| `LAST_UPDATED_ON` | DATE | Last modification timestamp |
| `COMPONENT_COMMENT` | VARCHAR2 | Page comment |

---

## APEX_APPLICATION_PAGE_REGIONS (174 columns)

> **CRITICAL:** The template column is `TEMPLATE`, NOT `REGION_TEMPLATE`.

### Identity
| Column | Type | Notes |
|--------|------|-------|
| `APPLICATION_ID` | NUMBER | FK |
| `PAGE_ID` | NUMBER | FK |
| `REGION_ID` | NUMBER | Unique internal ID |
| `REGION_NAME` | VARCHAR2 | Display name |
| `STATIC_ID` | VARCHAR2 | Static ID for JS/CSS targeting |
| `DISPLAY_SEQUENCE` | NUMBER | Render order |
| `DISPLAY_POSITION` | VARCHAR2 | Slot: BODY, DIALOG_FOOTER, etc. |
| `PARENT_REGION_NAME` | VARCHAR2 | Parent region (sub-regions) |

### Source
| Column | Type | Notes |
|--------|------|-------|
| `SOURCE_TYPE` | VARCHAR2 | NATIVE_STATIC, NATIVE_SQL_REPORT, NATIVE_IR, NATIVE_IG, NATIVE_JQM_LIST_VIEW, etc. |
| `SOURCE_TYPE_PLUGIN_NAME` | VARCHAR2 | Plugin internal name |
| `QUERY_TYPE` | VARCHAR2 | SQL Query, Table, Function, etc. |
| `SQL_QUERY` | CLOB | SQL source |
| `PLSQL_CODE` | CLOB | PL/SQL source for regions |
| `AJAX_ENABLED` | VARCHAR2 | Yes/No |
| `AJAX_ITEMS_TO_SUBMIT` | VARCHAR2 | Items submitted on refresh |

### Template / Appearance
| Column | Type | Notes |
|--------|------|-------|
| `TEMPLATE` | VARCHAR2 | **Region template name** (NOT region_template!) |
| `ICON_CSS_CLASSES` | VARCHAR2 | Icon classes |
| `CUSTOM_CSS` | VARCHAR2 | Custom CSS classes |
| `CUSTOM_CSS_CLASSES` | VARCHAR2 | Template option classes |
| `REGION_CSS_CLASSES` | VARCHAR2 | Additional CSS classes on outer div |

### Conditions
| Column | Type | Notes |
|--------|------|-------|
| `CONDITION_TYPE` | VARCHAR2 | Condition type code |
| `CONDITION_EXPRESSION1` | VARCHAR2 | Condition expr 1 |
| `CONDITION_EXPRESSION2` | VARCHAR2 | Condition expr 2 |
| `AUTHORIZATION_SCHEME` | VARCHAR2 | Auth scheme |
| `BUILD_OPTION` | VARCHAR2 | Build option |

### Metadata
| Column | Type | Notes |
|--------|------|-------|
| `COMPONENT_COMMENT` | VARCHAR2 | **Region comment** (NOT region_comment) |
| `LAST_UPDATED_BY` | VARCHAR2 | Developer |
| `LAST_UPDATED_ON` | DATE | Timestamp |
| `WORKSPACE` | VARCHAR2 | Workspace name |

---

## APEX_APPLICATION_PAGE_ITEMS (139 columns)

> **CRITICAL:** The region reference column is `REGION`, NOT `REGION_NAME`.

### Identity
| Column | Type | Notes |
|--------|------|-------|
| `APPLICATION_ID` | NUMBER | FK |
| `PAGE_ID` | NUMBER | FK |
| `ITEM_NAME` | VARCHAR2 | e.g., P10_NOMBRE |
| `ITEM_ID` | NUMBER | Internal ID |
| `DISPLAY_AS` | VARCHAR2 | Item type (Text Field, Select List, etc.) |
| `DISPLAY_AS_CODE` | VARCHAR2 | Internal type code (NATIVE_TEXT_FIELD, etc.) |
| `DISPLAY_SEQUENCE` | NUMBER | Order within region |
| `REGION` | VARCHAR2 | **Region name** (NOT region_name!) |
| `REGION_ID` | NUMBER | FK to region |

### Label / Appearance
| Column | Type | Notes |
|--------|------|-------|
| `LABEL` | VARCHAR2 | Display label |
| `FIELD_TEMPLATE` | VARCHAR2 | Label template name |
| `PRE_ELEMENT_TEXT` | VARCHAR2 | Text before item |
| `POST_ELEMENT_TEXT` | VARCHAR2 | Text after item |
| `FORMAT_MASK` | VARCHAR2 | Display/parse format |
| `CSS_CLASSES` | VARCHAR2 | Extra CSS classes |
| `ICON_CSS_CLASSES` | VARCHAR2 | Icon for item |
| `PLACEHOLDER` | VARCHAR2 | Placeholder text |

### Source / Default
| Column | Type | Notes |
|--------|------|-------|
| `ITEM_SOURCE_TYPE` | VARCHAR2 | Source type |
| `ITEM_SOURCE` | VARCHAR2 | Source expression |
| `ITEM_DEFAULT` | VARCHAR2 | Default value |
| `ITEM_DEFAULT_TYPE` | VARCHAR2 | Default type |
| `IS_PERSISTENT` | VARCHAR2 | Y/N — persists in session |

### LOV
| Column | Type | Notes |
|--------|------|-------|
| `LOV_NAMED_LOV` | VARCHAR2 | Shared LOV name |
| `LOV_DEFINITION` | CLOB | Inline LOV query |
| `LOV_DISPLAY_NULL` | VARCHAR2 | Show null option |
| `LOV_NULL_TEXT` | VARCHAR2 | Null display text |
| `LOV_NULL_VALUE` | VARCHAR2 | Null return value |
| `LOV_CASCADE_PARENT_ITEMS` | VARCHAR2 | Cascading parent items |

### Validation
| Column | Type | Notes |
|--------|------|-------|
| `IS_REQUIRED` | VARCHAR2 | Y/N |
| `MAX_LENGTH` | NUMBER | Maximum length |

### Conditions
| Column | Type | Notes |
|--------|------|-------|
| `CONDITION_TYPE` | VARCHAR2 | Condition type |
| `CONDITION_EXPRESSION1` | VARCHAR2 | Condition expr 1 |
| `CONDITION_EXPRESSION2` | VARCHAR2 | Condition expr 2 |
| `AUTHORIZATION_SCHEME` | VARCHAR2 | Auth scheme |
| `READ_ONLY_WHEN_TYPE` | VARCHAR2 | Read-only condition type |
| `READ_ONLY_WHEN` | VARCHAR2 | Read-only condition |

### Metadata
| Column | Type | Notes |
|--------|------|-------|
| `COMPONENT_COMMENT` | VARCHAR2 | **Item comment** (NOT item_comment) |
| `LAST_UPDATED_BY` | VARCHAR2 | Developer |
| `LAST_UPDATED_ON` | DATE | Timestamp |

---

## APEX_APPLICATION_PAGE_BUTTONS (53 columns)

### Identity
| Column | Type | Notes |
|--------|------|-------|
| `APPLICATION_ID` | NUMBER | FK |
| `PAGE_ID` | NUMBER | FK |
| `BUTTON_ID` | NUMBER | Internal ID |
| `BUTTON_NAME` | VARCHAR2 | Internal name (e.g., BTN_SAVE) |
| `LABEL` | VARCHAR2 | Display label |
| `BUTTON_SEQUENCE` | NUMBER | Display order |
| `REGION` | VARCHAR2 | Parent region name |
| `BUTTON_POSITION` | VARCHAR2 | Position slot |
| `BUTTON_ALIGNMENT` | VARCHAR2 | Left/Center/Right |

### Action
| Column | Type | Notes |
|--------|------|-------|
| `BUTTON_ACTION` | VARCHAR2 | SUBMIT, REDIRECT_URL, DEFINED_BY_DA, etc. |
| `BUTTON_REDIRECT_URL` | VARCHAR2 | URL for redirect action |
| `BUTTON_EXECUTE_VALIDATIONS` | VARCHAR2 | Yes/No |
| `DATABASE_ACTION` | VARCHAR2 | SQL_ACTION for form buttons |

### Appearance
| Column | Type | Notes |
|--------|------|-------|
| `BUTTON_TEMPLATE` | VARCHAR2 | Template name |
| `BUTTON_CSS_CLASSES` | VARCHAR2 | Extra CSS classes |
| `ICON_CSS_CLASSES` | VARCHAR2 | Icon classes |
| `BUTTON_IS_HOT` | VARCHAR2 | Yes/No — hot (primary) button |

### Conditions
| Column | Type | Notes |
|--------|------|-------|
| `CONDITION_TYPE` | VARCHAR2 | Condition type |
| `CONDITION_EXPRESSION1` | VARCHAR2 | Condition expr 1 |
| `CONDITION_EXPRESSION2` | VARCHAR2 | Condition expr 2 |
| `AUTHORIZATION_SCHEME` | VARCHAR2 | Auth scheme |

### Metadata
| Column | Type | Notes |
|--------|------|-------|
| `COMPONENT_COMMENT` | VARCHAR2 | **Button comment** (NOT button_comment or button_condition) |
| `LAST_UPDATED_BY` | VARCHAR2 | Developer |
| `LAST_UPDATED_ON` | DATE | Timestamp |

---

## APEX_APPLICATION_PAGE_DA (38 columns)

> **CRITICAL:** `FIRE_ON_INITIALIZATION` does **NOT** exist in this view. It exists only as `EXECUTE_ON_PAGE_INIT` in `APEX_APPLICATION_PAGE_DA_ACTS`.

### Identity
| Column | Type | Notes |
|--------|------|-------|
| `APPLICATION_ID` | NUMBER | FK |
| `PAGE_ID` | NUMBER | FK |
| `DYNAMIC_ACTION_ID` | NUMBER | Internal ID |
| `DYNAMIC_ACTION_NAME` | VARCHAR2 | DA name |
| `DISPLAY_SEQUENCE` | NUMBER | DA order |

### Event
| Column | Type | Notes |
|--------|------|-------|
| `DYNAMIC_ACTION_EVENT` | VARCHAR2 | Event name: Change, Click, Page Load, etc. |
| `DYNAMIC_ACTION_EVENT_SCOPE` | VARCHAR2 | Static, Dynamic, Once |
| `TRIGGERING_ELEMENT_TYPE` | VARCHAR2 | Item, Region, jQuery Selector, etc. |
| `TRIGGERING_ELEMENT` | VARCHAR2 | The element reference |
| `TRIGGERING_REGION_ID` | NUMBER | FK to region |
| `BIND_TYPE` | VARCHAR2 | bind/live/one |

### Condition
| Column | Type | Notes |
|--------|------|-------|
| `WHEN_ELEMENT_TYPE` | VARCHAR2 | Condition on item type |
| `WHEN_ELEMENT` | VARCHAR2 | Condition item |
| `WHEN_CONDITION` | VARCHAR2 | Condition expression |
| `CONDITION_TYPE` | VARCHAR2 | Server condition type |
| `CONDITION_EXPRESSION1` | VARCHAR2 | Server condition expr 1 |
| `CONDITION_EXPRESSION2` | VARCHAR2 | Server condition expr 2 |
| `AUTHORIZATION_SCHEME` | VARCHAR2 | Auth scheme |
| `BUILD_OPTION` | VARCHAR2 | Build option |

### Metadata
| Column | Type | Notes |
|--------|------|-------|
| `COMPONENT_COMMENT` | VARCHAR2 | DA comment |
| `LAST_UPDATED_BY` | VARCHAR2 | Developer |
| `LAST_UPDATED_ON` | DATE | Timestamp |

---

## APEX_APPLICATION_PAGE_DA_ACTS (44 columns)

> **CRITICAL:** `EXECUTE_ON_PAGE_INIT` is here (not `FIRE_ON_INITIALIZATION`).

### Identity
| Column | Type | Notes |
|--------|------|-------|
| `APPLICATION_ID` | NUMBER | FK |
| `PAGE_ID` | NUMBER | FK |
| `DYNAMIC_ACTION_ID` | NUMBER | FK to parent DA |
| `ACTION_ID` | NUMBER | Internal action ID |
| `ACTION_NAME` | VARCHAR2 | Action display name |
| `ACTION_SEQUENCE` | NUMBER | Action order |
| `ACTION_CODE` | VARCHAR2 | Internal action type code |

### Execution
| Column | Type | Notes |
|--------|------|-------|
| `EXECUTE_ON_PAGE_INIT` | VARCHAR2 | **Yes/No — fire on page init** (NOT fire_on_initialization) |
| `WAIT_FOR_RESULT` | VARCHAR2 | Yes/No — wait for async result |
| `EVENT_RESULT` | VARCHAR2 | True/False — fires on true or false branch |

### Affected Elements
| Column | Type | Notes |
|--------|------|-------|
| `AFFECTED_ELEMENTS_TYPE` | VARCHAR2 | Item, Region, jQuery Selector, etc. |
| `AFFECTED_ELEMENTS` | VARCHAR2 | Element reference |
| `AFFECTED_REGION_ID` | NUMBER | FK to region |

### Attributes (meaning depends on ACTION_CODE)
| Column | Type | Notes |
|--------|------|-------|
| `ATTRIBUTE_01` | VARCHAR2 | See table below |
| `ATTRIBUTE_02` | VARCHAR2 | |
| `ATTRIBUTE_03` | VARCHAR2 | |
| `ATTRIBUTE_04` | VARCHAR2 | |
| `ATTRIBUTE_05` | VARCHAR2 | |
| `ATTRIBUTE_06` | VARCHAR2 | |
| `ATTRIBUTE_07` | VARCHAR2 | |
| `ATTRIBUTE_08` | VARCHAR2 | |
| `ATTRIBUTE_09` | VARCHAR2 | |
| `ATTRIBUTE_10` | VARCHAR2 | |
| `ATTRIBUTE_11` | VARCHAR2 | |
| `ATTRIBUTE_12` | VARCHAR2 | |
| `ATTRIBUTE_13` | VARCHAR2 | |
| `ATTRIBUTE_14` | VARCHAR2 | |
| `ATTRIBUTE_15` | VARCHAR2 | |

### Common ACTION_CODE → Attribute Meanings

| ACTION_CODE | Description | Key Attributes |
|-------------|-------------|----------------|
| `NATIVE_JAVASCRIPT_CODE` | Execute JavaScript | `ATTRIBUTE_01` = JS code |
| `NATIVE_EXECUTE_PLSQL_CODE` | Execute PL/SQL | `ATTRIBUTE_01` = PL/SQL, `ATTRIBUTE_02` = items to submit, `ATTRIBUTE_03` = items to return |
| `NATIVE_SET_VALUE` | Set Value | `ATTRIBUTE_01` = set type, `ATTRIBUTE_02` = value/SQL, `ATTRIBUTE_03` = items to submit |
| `NATIVE_SHOW` | Show | (uses affected elements) |
| `NATIVE_HIDE` | Hide | (uses affected elements) |
| `NATIVE_ENABLE` | Enable | (uses affected elements) |
| `NATIVE_DISABLE` | Disable | (uses affected elements) |
| `NATIVE_REFRESH` | Refresh | (uses affected elements) |
| `NATIVE_SUBMIT_PAGE` | Submit Page | `ATTRIBUTE_01` = request, `ATTRIBUTE_02` = validate |
| `NATIVE_CONFIRM` | Confirm | `ATTRIBUTE_01` = message |
| `NATIVE_ALERT` | Alert | `ATTRIBUTE_01` = message |
| `NATIVE_CLEAR` | Clear | (uses affected elements) |
| `NATIVE_ADD_CLASS` | Add Class | `ATTRIBUTE_01` = CSS class |
| `NATIVE_REMOVE_CLASS` | Remove Class | `ATTRIBUTE_01` = CSS class |
| `NATIVE_OPEN_REGION` | Open Region | (uses affected region) |
| `NATIVE_CLOSE_REGION` | Close Region | (uses affected region) |

### Metadata
| Column | Type | Notes |
|--------|------|-------|
| `COMPONENT_COMMENT` | VARCHAR2 | Action comment |
| `LAST_UPDATED_BY` | VARCHAR2 | Developer |
| `LAST_UPDATED_ON` | DATE | Timestamp |

---

## APEX_APPLICATION_PAGE_PROC (61 columns)

> **CRITICAL:**
> - Ordering column is `EXECUTION_SEQUENCE`, NOT `PROCESS_SEQUENCE`
> - Error message column is `PROCESS_ERROR_MESSAGE`, NOT `ERROR_MESSAGE`

### Identity
| Column | Type | Notes |
|--------|------|-------|
| `APPLICATION_ID` | NUMBER | FK |
| `PAGE_ID` | NUMBER | FK |
| `PROCESS_ID` | NUMBER | Internal ID |
| `PROCESS_NAME` | VARCHAR2 | Process name |
| `EXECUTION_SEQUENCE` | NUMBER | **Order of execution** (NOT process_sequence) |
| `PROCESS_POINT` | VARCHAR2 | AFTER_SUBMIT, BEFORE_HEADER, ON_DEMAND, etc. |
| `REGION_ID` | NUMBER | FK to associated region |

### Source
| Column | Type | Notes |
|--------|------|-------|
| `PROCESS_TYPE` | VARCHAR2 | NATIVE_PLSQL, NATIVE_FORM_DML, NATIVE_CLOSE_WINDOW, etc. |
| `PROCESS_TYPE_PLUGIN_NAME` | VARCHAR2 | Plugin internal name |
| `PROCESS_SOURCE` | CLOB | PL/SQL code or configuration |
| `PROCESS_SOURCE_TYPE` | VARCHAR2 | Source type code |

### Request / Condition
| Column | Type | Notes |
|--------|------|-------|
| `PROCESS_WHEN_BUTTON_ID` | NUMBER | Execute when this button clicked |
| `PROCESS_WHEN_TYPE` | VARCHAR2 | Condition type |
| `PROCESS_WHEN` | VARCHAR2 | Condition expression |
| `CONDITION_TYPE` | VARCHAR2 | Server condition type |
| `CONDITION_EXPRESSION1` | VARCHAR2 | Server condition expr 1 |
| `CONDITION_EXPRESSION2` | VARCHAR2 | Server condition expr 2 |

### Messages
| Column | Type | Notes |
|--------|------|-------|
| `PROCESS_SUCCESS_MESSAGE` | VARCHAR2 | Success message |
| `PROCESS_ERROR_MESSAGE` | VARCHAR2 | **Error message** (NOT error_message) |

### Metadata
| Column | Type | Notes |
|--------|------|-------|
| `AUTHORIZATION_SCHEME` | VARCHAR2 | Auth scheme |
| `BUILD_OPTION` | VARCHAR2 | Build option |
| `COMPONENT_COMMENT` | VARCHAR2 | Process comment |
| `LAST_UPDATED_BY` | VARCHAR2 | Developer |
| `LAST_UPDATED_ON` | DATE | Timestamp |

---

## APEX_APPLICATION_PAGE_VAL (35 columns)

### Identity
| Column | Type | Notes |
|--------|------|-------|
| `APPLICATION_ID` | NUMBER | FK |
| `PAGE_ID` | NUMBER | FK |
| `VALIDATION_ID` | NUMBER | Internal ID |
| `VALIDATION_NAME` | VARCHAR2 | Validation name |
| `VALIDATION_SEQUENCE` | NUMBER | Execution order |
| `VALIDATION_TYPE` | VARCHAR2 | NATIVE_SQL_EXPRESSION, NATIVE_PLSQL_EXPRESSION, NATIVE_FUNCTION_BODY, etc. |

### Source
| Column | Type | Notes |
|--------|------|-------|
| `VALIDATION_EXPRESSION1` | VARCHAR2 | Main expression |
| `VALIDATION_EXPRESSION2` | VARCHAR2 | Secondary expression |
| `VALIDATION_ERROR_MESSAGE` | VARCHAR2 | Error message shown |

### Association
| Column | Type | Notes |
|--------|------|-------|
| `ASSOCIATED_ITEM` | VARCHAR2 | Associated page item name |
| `EXECUTION_SEQUENCE` | NUMBER | Execution order |
| `WHEN_BUTTON_PRESSED` | VARCHAR2 | Execute on button |

### Conditions
| Column | Type | Notes |
|--------|------|-------|
| `CONDITION_TYPE` | VARCHAR2 | Condition type |
| `CONDITION_EXPRESSION1` | VARCHAR2 | Condition expr 1 |
| `CONDITION_EXPRESSION2` | VARCHAR2 | Condition expr 2 |
| `AUTHORIZATION_SCHEME` | VARCHAR2 | Auth scheme |

### Metadata
| Column | Type | Notes |
|--------|------|-------|
| `COMPONENT_COMMENT` | VARCHAR2 | Comment |
| `LAST_UPDATED_BY` | VARCHAR2 | Developer |
| `LAST_UPDATED_ON` | DATE | Timestamp |

---

## APEX_APPLICATION_PAGE_BRANCHES (27 columns)

> **CRITICAL:** The ordering column is `PROCESS_SEQUENCE`, NOT `BRANCH_SEQUENCE`.

### Identity
| Column | Type | Notes |
|--------|------|-------|
| `APPLICATION_ID` | NUMBER | FK |
| `PAGE_ID` | NUMBER | FK |
| `BRANCH_ID` | NUMBER | Internal ID |
| `BRANCH_NAME` | VARCHAR2 | Branch name |
| `PROCESS_SEQUENCE` | NUMBER | **Execution order** (NOT branch_sequence) |
| `BRANCH_POINT` | VARCHAR2 | AFTER_PROCESSING, BEFORE_COMPUTATION, etc. |

### Target
| Column | Type | Notes |
|--------|------|-------|
| `BRANCH_TYPE` | VARCHAR2 | REDIRECT_URL, BRANCH_TO_PAGE, etc. |
| `BRANCH_ACTION` | VARCHAR2 | URL or target page expression |

### Conditions
| Column | Type | Notes |
|--------|------|-------|
| `CONDITION_TYPE` | VARCHAR2 | Condition type |
| `CONDITION_EXPRESSION1` | VARCHAR2 | Condition expr 1 |
| `CONDITION_EXPRESSION2` | VARCHAR2 | Condition expr 2 |
| `AUTHORIZATION_SCHEME` | VARCHAR2 | Auth scheme |
| `BUILD_OPTION` | VARCHAR2 | Build option |

### Metadata
| Column | Type | Notes |
|--------|------|-------|
| `COMPONENT_COMMENT` | VARCHAR2 | Comment |
| `LAST_UPDATED_BY` | VARCHAR2 | Developer |
| `LAST_UPDATED_ON` | DATE | Timestamp |

---

## Other Useful Views

### APEX_APPLICATION_LOVS
| Column | Notes |
|--------|-------|
| `APPLICATION_ID` | FK |
| `LOV_NAME` | Shared LOV name |
| `LOV_ID` | Internal ID |
| `LOV_TYPE` | STATIC, DYNAMIC |
| `LOV_QUERY` | SQL query for dynamic LOVs |
| `LIST_OF_VALUES_NAME` | Alias for LOV_NAME |

### APEX_APPLICATION_PAGE_RPT_COLS
| Column | Notes |
|--------|-------|
| `APPLICATION_ID` | FK |
| `PAGE_ID` | FK |
| `REGION_NAME` | Report region name |
| `COLUMN_ALIAS` | Column alias from SQL |
| `HEADING` | Column heading text |
| `DISPLAY_SEQUENCE` | Column order |
| `COLUMN_IS_HIDDEN` | Yes/No |
| `COLUMN_FORMAT_MASK` | Format mask |
| `COLUMN_ALIGNMENT` | LEFT/CENTER/RIGHT |
| `COLUMN_LINK_TEXT` | Link text template |
| `COLUMN_LINK` | URL for column link |

### APEX_APPLICATION_LIST_ENTRIES
| Column | Notes |
|--------|-------|
| `APPLICATION_ID` | FK |
| `LIST_NAME` | Navigation list name |
| `ENTRY_TEXT` | Menu/list entry label |
| `ENTRY_TARGET` | Target URL |
| `ENTRY_IMAGE` | Icon class |
| `LIST_ENTRY_PARENT_ID` | FK for hierarchy |
| `DISPLAY_SEQUENCE` | Order |
| `CONDITION_TYPE` | Condition type |

### APEX_APPLICATION_STATIC_FILES
| Column | Notes |
|--------|-------|
| `APPLICATION_ID` | FK |
| `FILE_NAME` | File name |
| `MIME_TYPE` | MIME type |
| `FILE_CONTENT` | BLOB content |
| `FILE_SIZE` | Size in bytes |
| `CREATED_BY` | Creator |
| `CREATED_ON` | Creation date |
| `UPDATED_BY` | Last updater |
| `UPDATED_ON` | Last update date |

### APEX_WORKSPACE_STATIC_FILES
| Column | Notes |
|--------|-------|
| `WORKSPACE` | Workspace name |
| `FILE_NAME` | File name |
| `MIME_TYPE` | MIME type |
| `FILE_CONTENT` | BLOB content |
| `FILE_SIZE` | Size in bytes |
| `CREATED_BY` | Creator |
| `CREATED_ON` | Creation date |
| `LAST_UPDATED_BY` | Last updater |
| `LAST_UPDATED_ON` | **Last update date** (NOT updated_on) |

---

## Common ORA-00904 Errors — Never Again

| Wrong Name | Correct Name | View |
|------------|-------------|------|
| `REGION_TEMPLATE` | `TEMPLATE` | `APEX_APPLICATION_PAGE_REGIONS` |
| `REGION_TEMPLATE_NAME` | `TEMPLATE` | `APEX_APPLICATION_PAGE_REGIONS` |
| `REGION_COMMENT` | `COMPONENT_COMMENT` | `APEX_APPLICATION_PAGE_REGIONS` |
| `ITEM_COMMENT` | `COMPONENT_COMMENT` | `APEX_APPLICATION_PAGE_ITEMS` |
| `BUTTON_COMMENT` | `COMPONENT_COMMENT` | `APEX_APPLICATION_PAGE_BUTTONS` |
| `BUTTON_CONDITION` | `COMPONENT_COMMENT` | `APEX_APPLICATION_PAGE_BUTTONS` |
| `PROCESS_SEQUENCE` | `EXECUTION_SEQUENCE` | `APEX_APPLICATION_PAGE_PROC` |
| `ERROR_MESSAGE` | `PROCESS_ERROR_MESSAGE` | `APEX_APPLICATION_PAGE_PROC` |
| `BRANCH_SEQUENCE` | `PROCESS_SEQUENCE` | `APEX_APPLICATION_PAGE_BRANCHES` |
| `FIRE_ON_INITIALIZATION` | `EXECUTE_ON_PAGE_INIT` | `APEX_APPLICATION_PAGE_DA_ACTS` |
| `REGION_NAME` (items) | `REGION` | `APEX_APPLICATION_PAGE_ITEMS` |
| `UPDATED_ON` | `LAST_UPDATED_ON` | `APEX_WORKSPACE_STATIC_FILES` |
| `CSS_INLINE` | `INLINE_CSS` | `APEX_APPLICATION_PAGES` |
| `PAGE_COMMENT` | `COMPONENT_COMMENT` | `APEX_APPLICATION_PAGES` |
| `VALIDATION_COMMENT` | `COMPONENT_COMMENT` | `APEX_APPLICATION_PAGE_VAL` |
| `DA_COMMENT` | `COMPONENT_COMMENT` | `APEX_APPLICATION_PAGE_DA` |

---

## Standard Verified Query Examples

### 1. List all regions on a page with template and source
```sql
SELECT region_id,
       region_name,
       static_id,
       source_type,
       template,
       display_sequence,
       display_position,
       component_comment
FROM   apex_application_page_regions
WHERE  application_id = :APP_ID
AND    page_id = :PAGE_ID
ORDER  BY display_sequence;
```

### 2. List all items with their region and type
```sql
SELECT item_name,
       display_as,
       display_as_code,
       region,           -- NOT region_name
       label,
       is_required,
       lov_named_lov,
       display_sequence,
       condition_type,
       component_comment
FROM   apex_application_page_items
WHERE  application_id = :APP_ID
AND    page_id = :PAGE_ID
ORDER  BY region, display_sequence;
```

### 3. List all processes with execution order
```sql
SELECT process_name,
       process_type,
       execution_sequence,  -- NOT process_sequence
       process_point,
       process_error_message,  -- NOT error_message
       process_success_message,
       condition_type,
       component_comment
FROM   apex_application_page_proc
WHERE  application_id = :APP_ID
AND    page_id = :PAGE_ID
ORDER  BY execution_sequence;
```

### 4. List all Dynamic Actions with their actions
```sql
SELECT da.dynamic_action_name,
       da.dynamic_action_event,
       da.triggering_element_type,
       da.triggering_element,
       act.action_name,
       act.action_code,
       act.execute_on_page_init,  -- NOT fire_on_initialization
       act.event_result,
       act.affected_elements_type,
       act.affected_elements,
       act.attribute_01,
       act.attribute_02
FROM   apex_application_page_da da
JOIN   apex_application_page_da_acts act
       ON  act.application_id = da.application_id
       AND act.page_id = da.page_id
       AND act.dynamic_action_id = da.dynamic_action_id
WHERE  da.application_id = :APP_ID
AND    da.page_id = :PAGE_ID
ORDER  BY da.display_sequence, act.action_sequence;
```

### 5. List all buttons on a page
```sql
SELECT button_name,
       label,
       region,
       button_position,
       button_action,
       button_is_hot,
       button_sequence,
       condition_type,
       component_comment
FROM   apex_application_page_buttons
WHERE  application_id = :APP_ID
AND    page_id = :PAGE_ID
ORDER  BY button_sequence;
```

### 6. Read CLOB source from region (PL/SQL pattern)
```sql
-- For regions with large SQL/PL/SQL source
SELECT region_name,
       DBMS_LOB.GETLENGTH(sql_query) AS sql_length,
       DBMS_LOB.SUBSTR(sql_query, 4000, 1) AS sql_first_4k
FROM   apex_application_page_regions
WHERE  application_id = :APP_ID
AND    page_id = :PAGE_ID
AND    source_type = 'NATIVE_SQL_REPORT';
```

### 7. Find all pages modified today
```sql
SELECT page_id, page_name, last_updated_by, last_updated_on
FROM   apex_application_pages
WHERE  application_id = :APP_ID
AND    TRUNC(last_updated_on) = TRUNC(SYSDATE)
ORDER  BY last_updated_on DESC;
```

### 8. Search for text across all page components
```sql
-- Search in regions
SELECT 'REGION' AS component_type, page_id, region_name AS component_name
FROM   apex_application_page_regions
WHERE  application_id = :APP_ID
AND    UPPER(sql_query) LIKE '%' || UPPER(:SEARCH_TEXT) || '%'
UNION ALL
-- Search in processes
SELECT 'PROCESS', page_id, process_name
FROM   apex_application_page_proc
WHERE  application_id = :APP_ID
AND    UPPER(process_source) LIKE '%' || UPPER(:SEARCH_TEXT) || '%'
UNION ALL
-- Search in DA actions
SELECT 'DA_ACTION', page_id, action_name
FROM   apex_application_page_da_acts
WHERE  application_id = :APP_ID
AND    UPPER(attribute_01) LIKE '%' || UPPER(:SEARCH_TEXT) || '%'
ORDER  BY 1, 2;
```
