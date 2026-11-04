# Interactive Grid - APEX 20.2 JavaScript API

## Access
```javascript
var grid = apex.region('region_static_id').widget().interactiveGrid('getViews', 'grid');
var model = grid.model;
```

## Core Methods

### Region Level
```javascript
// Refresh
apex.region('empGrid').widget().interactiveGrid('refresh');

// Get views
var views = apex.region('empGrid').widget().interactiveGrid('getViews');

// Get active view
var activeView = apex.region('empGrid').widget().interactiveGrid('getActiveView');
```

### Model Operations
```javascript
var grid = apex.region('empGrid').widget().interactiveGrid('getViews', 'grid');
var model = grid.model;

// Get record
var record = model.getRecord(recordId);

// Get/Set value
var val = model.getValue(record, 'SALARY');
model.setValue(record, 'SALARY', 5000);

// Get selected records
var selected = grid.view$.grid('getSelectedRecords');

// Refresh grid view
grid.view$.grid('refresh');
```

## Selected Records Processing
```javascript
function processSelectedEmployees() {
    var grid = apex.region('employees').widget().interactiveGrid('getViews', 'grid');
    var selected = grid.view$.grid('getSelectedRecords');

    if (selected.length === 0) {
        apex.message.showErrors([{
            type: 'error', location: 'page',
            message: 'No employees selected'
        }]);
        return;
    }

    var ids = [];
    selected.forEach(function(rec) {
        ids.push(grid.model.getValue(rec, 'EMPLOYEE_ID'));
    });

    apex.server.process('PROCESS_EMPLOYEES', {
        x01: JSON.stringify(ids)
    }, {
        dataType: 'json',
        success: function(data) {
            apex.message.showPageSuccess('Processed ' + ids.length + ' employees');
            apex.region('employees').widget().interactiveGrid('refresh');
        }
    });
}
```

## Events
```javascript
// Selection change
$(document).on('interactivegridselectionchange', function(event, data) {
    if (data.region && data.region.staticId === 'empGrid') {
        var selectedCount = data.selectedRecords.length;
        console.log('Selected: ' + selectedCount);
    }
});
```

## Column Types
| Type | Display As |
|------|-----------|
| Text | NATIVE_TEXT_FIELD |
| Number | NATIVE_NUMBER_FIELD |
| Date | NATIVE_DATE_PICKER |
| Checkbox | NATIVE_SINGLE_CHECKBOX |
| Select List | NATIVE_SELECT_LIST |
| Link | NATIVE_LINK |

## APEX 20.2 Notes
- IG has known bugs for data entry in APEX 20.2
- Prefer Classic Report + Form pattern for data entry
- IG works well for read-only display with inline editing for simple fields
