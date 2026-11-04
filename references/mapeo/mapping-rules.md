# Oracle Forms 6i to APEX 20.2 Mapping Rules

## Modules -> Applications & Pages

- A `.fmb` module can become:
  - A standalone APEX application; or
  - A logical subset of pages within a larger application.
- Main entry forms with complex menus map to:
  - Home/dashboard pages + APEX navigation lists.
- Modal windows/messages -> APEX Modal Dialog pages when semantics are truly modal.

## Blocks -> APEX Regions

| Forms Block Type | APEX Region |
|---|---|
| Data block (table/view) | Classic Report + Form or Interactive Report |
| Master-detail blocks | Master-Detail pattern (Report + Form, FK relationship) |
| Control block (no base table) | Static Content region, global items, or parameter pages |
| Non-database block (UI only) | Static Content region with items sourced from Null/Static |

## Items -> Page Items

| Forms Item | APEX Item |
|---|---|
| Text (VARCHAR2) | Text Field (respecting max length) |
| Number | Number Field (with format mask + validations) |
| Date | Date Picker |
| Checkbox/Radio/List | Checkbox/Radio/Select List + Shared LOV |
| Display (computed) | Display Only + PL/SQL function |
| Hidden | Hidden item or Application Item |

## Record Groups / LOVs -> Shared LOVs

| Forms | APEX |
|---|---|
| Record Group with SELECT | Dynamic Shared LOV |
| Static Record Group | Static Shared LOV |
| Reused Record Group | Single Shared LOV referenced by many items |

## Triggers -> Processes, Validations & Dynamic Actions

### Navigation & Focus Triggers
| Forms Trigger | APEX Equivalent |
|---|---|
| WHEN-NEW-FORM-INSTANCE | Before Header process |
| WHEN-NEW-BLOCK-INSTANCE | Region load / DA on page load |
| WHEN-NEW-RECORD-INSTANCE | DA on IG/report row selection |
| WHEN-NEW-ITEM-INSTANCE | DA Focus event (simplify for web) |

### Query & Data Processing Triggers
| Forms Trigger | APEX Equivalent |
|---|---|
| PRE-QUERY | Region source query adjustments |
| POST-QUERY | Computed columns in SQL or region source |
| PRE/POST-INSERT | Packaged PL/SQL from page process |
| PRE/POST-UPDATE | Packaged PL/SQL from page process |
| PRE/POST-DELETE | Packaged PL/SQL from page process |
| ON-CLEAR-DETAILS | Master-detail relationship config |

### Validation Triggers
| Forms Trigger | APEX Equivalent |
|---|---|
| WHEN-VALIDATE-ITEM | APEX item validation or DA Change + AJAX |
| WHEN-VALIDATE-RECORD | Record-level validation |

### Key & Command Triggers
| Forms Trigger | APEX Equivalent |
|---|---|
| KEY-COMMIT | SAVE button + submit process |
| KEY-EXIT | CANCEL button + branch |
| WHEN-BUTTON-PRESSED | Dynamic Action Click + PL/SQL/AJAX |
| WHEN-CHECKBOX-CHANGED | Dynamic Action Change |
| WHEN-RADIO-CHANGED | Dynamic Action Change |

### Message & Error Triggers
| Forms Trigger | APEX Equivalent |
|---|---|
| ON-ERROR | `apex.message.showErrors()` + `apex_debug.error()` |
| ON-MESSAGE | `apex.message.showPageSuccess()` + `apex_debug.message()` |

### Priority Rules
1. Pure data validation -> APEX validations or DB constraints first
2. Navigation/UI focus changes -> Dynamic Actions or simplify for web
3. DML or program unit calls -> PL/SQL packages called from processes/AJAX

## Program Units -> Packages

- ALL Forms program units migrate to database packages
- APEX only calls packaged procedures/functions (NEVER inline PL/SQL)
- Refactor cross-cutting utilities into dedicated packages

## Security Mapping

| Forms Security | APEX Security |
|---|---|
| Menu-based security | Authorization Schemes on pages/regions |
| Role/RESP-based logic | Authorization Schemes + `pkg_security.has_permission` |
| Parameter-based security | Session state + Application Items |
| Row-level security | Views or VPD policies |
