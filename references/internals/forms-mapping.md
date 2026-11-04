# Oracle Forms 6i -> APEX Mapping Completo

## Módulos -> Aplicaciones/Páginas
| Forms | APEX |
|-------|------|
| Module (.fmb) | Grupo de páginas dentro de la app |
| Main entry con menús | Home + navigation lists |
| Modal window | Modal Dialog page |
| Canvas/Window separado | Página separada o región |

## Bloques -> Regiones
| Forms Block | APEX Region |
|-------------|-------------|
| Data block (table/view) | IR (listado) + Form (CRUD) |
| Master-detail blocks | Master-Detail pattern, FK relationship |
| Control block (no base table) | Static Content, hidden items, parámetros |
| Non-database block (UI) | Static Content con items source NULL |

## Items -> Page Items
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

## Record Groups/LOVs -> Shared LOVs
| Forms | APEX |
|-------|------|
| Record Group con SELECT | Dynamic Shared LOV |
| Static Record Group | Static Shared LOV |
| Reused Record Group | Single Shared LOV referenciada por muchos items |

## Triggers -> Processes, Validations, DAs

### Navegación
| Trigger | APEX |
|---------|------|
| WHEN-NEW-FORM-INSTANCE | Before Header process |
| WHEN-NEW-BLOCK-INSTANCE | Region load / DA on page load |
| WHEN-NEW-RECORD-INSTANCE | DA on IG/report row selection |

### Query y Data
| Trigger | APEX |
|---------|------|
| PRE-QUERY | Ajustes al source query de la región |
| POST-QUERY | Columnas computadas en SQL |
| PRE/POST-INSERT/UPDATE/DELETE | PL/SQL empaquetado desde page process |
| ON-CLEAR-DETAILS | Config master-detail |

### Validación
| Trigger | APEX |
|---------|------|
| WHEN-VALIDATE-ITEM | Validation o DA Change + AJAX |
| WHEN-VALIDATE-RECORD | Validation a nivel record |

### Keys y Commands
| Trigger | APEX |
|---------|------|
| KEY-COMMIT | Botón SAVE + submit process |
| KEY-EXIT | Botón CANCEL + branch |
| WHEN-BUTTON-PRESSED | DA Click + PL/SQL/AJAX |
| WHEN-CHECKBOX-CHANGED | DA Change |
| WHEN-RADIO-CHANGED | DA Change |

### Mensajes
| Trigger | APEX |
|---------|------|
| ON-ERROR | apex.message.showErrors() + apex_debug.error() |
| ON-MESSAGE | apex.message.showPageSuccess() |

## Program Units -> Packages
- TODO va a paquetes de base de datos
- APEX solo llama procedimientos/funciones empaquetadas
- Refactorizar utilidades cross-cutting en paquetes dedicados

## Seguridad
| Forms | APEX |
|-------|------|
| Menu-based security | Authorization Schemes en pages/regions |
| Role/RESP-based | Auth Schemes + pkg_security.has_permission |
| Parameter-based | Session state + Application Items |
| Row-level | Views o VPD policies |

## XML de Forms — Claves para Parsing
- Block `DMLDataTargetName` = tabla base
- Block `QueryDataSourceName` = fuente de query (puede diferir del DML target)
- Item `DataType`: 1=CHAR, 2=NUMBER, 12=DATE, 23=INT, 96=CHAR(fixed)
- Item `ItemType`: 0=hidden, 2=text, 4=checkbox, 6=radio, 9=display, 12=list
- Trigger `TriggerText` = código PL/SQL fuente
- ProgramUnit `ProgramUnitText` = PL/SQL completo
- Coordenadas de layout son para Forms, adaptar para web (no copiar literal)

## Prioridad de Migración
1. Validación pura de datos -> APEX validations o DB constraints
2. Cambios de navegación/foco UI -> Dynamic Actions o simplificar para web
3. DML o llamadas a program units -> PL/SQL packages desde processes/AJAX
