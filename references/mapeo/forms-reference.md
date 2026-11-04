# Oracle Forms 6i Structure Reference

## Module Structure

A Forms 6i module (.fmb) contains:

- **Module**: General definition, windows, canvases, menus, parameters
- **Blocks**:
  - Data Blocks: based on tables/views or queries
  - Control Blocks: no database base, used for UI and parameters
- **Items**: Fields of different types (text, number, date, checkbox, list, etc.)
- **Triggers**: At module, block, and item level (by event)
- **Program Units**: PL/SQL procedures and functions
- **Record Groups and LOVs**: Reusable lists and queries for value selection

## Forms2XML Extraction

Migration uses Forms2XML to convert .fmb files to XML. The extraction must include all elements for complete analysis:

```bash
# Convert Forms module to XML
frmf2xml.bat MODULE=myform.fmb OUTPUT_FILE=myform.xml
```

The XML contains the complete metadata model of the form.

## Trigger Categories

### Navigation & Focus
| Trigger | Fires When |
|---|---|
| WHEN-NEW-FORM-INSTANCE | Form opens |
| WHEN-NEW-BLOCK-INSTANCE | User enters a block |
| WHEN-NEW-RECORD-INSTANCE | Cursor moves to new record |
| WHEN-NEW-ITEM-INSTANCE | Cursor moves to new item |

### Query & Data Processing
| Trigger | Fires When |
|---|---|
| PRE-QUERY | Before query execution |
| POST-QUERY | After each row is fetched |
| PRE-INSERT | Before INSERT DML |
| POST-INSERT | After INSERT DML |
| PRE-UPDATE | Before UPDATE DML |
| POST-UPDATE | After UPDATE DML |
| PRE-DELETE | Before DELETE DML |
| POST-DELETE | After DELETE DML |
| ON-CLEAR-DETAILS | Master-detail: when master changes |

### Validation
| Trigger | Fires When |
|---|---|
| WHEN-VALIDATE-ITEM | User leaves a field |
| WHEN-VALIDATE-RECORD | User leaves a record |

### Keys & Commands
| Trigger | Fires When |
|---|---|
| KEY-COMMIT | User presses Ctrl+S (save) |
| KEY-EXIT | User presses Ctrl+Q (exit) |
| WHEN-BUTTON-PRESSED | Button click |
| WHEN-CHECKBOX-CHANGED | Checkbox state changes |
| WHEN-RADIO-CHANGED | Radio button selection changes |

### Messages & Errors
| Trigger | Fires When |
|---|---|
| ON-ERROR | Oracle error occurs |
| ON-MESSAGE | Forms message is displayed |

## Best Practices for XML Interpretation

1. Treat XML as a metadata model (don't copy 1:1 the Forms experience)
2. Identify "pure UI" blocks vs. data blocks with real DML
3. Separate validation, navigation, and business logic triggers for proper APEX mapping
4. Extract Record Group queries to create dynamic Shared LOVs in APEX
5. Focus on trigger semantics, not exact implementation
6. Identify common patterns across forms for reusable APEX components

## Common Forms Patterns and APEX Equivalents

### Search Form Pattern
```
Forms: Query-only data block with WHERE clause from control block items
APEX:  Search region (Static Content) + Interactive Report with bind variables
```

### Master-Detail Pattern
```
Forms: Two data blocks with ON-CLEAR-DETAILS, coordination properties
APEX:  Master-Detail page pattern, FK relationship in region source
```

### LOV with Validation Pattern
```
Forms: Record Group + LOV + WHEN-VALIDATE-ITEM
APEX:  Shared LOV + Select List/Popup LOV item + item validation
```

### Modal Entry Pattern
```
Forms: Separate window/canvas shown programmatically
APEX:  Modal Dialog page or Inline Dialog region
```
