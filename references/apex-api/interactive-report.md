# Interactive Report - APEX 20.2 JavaScript API

## Access
```javascript
var region = apex.region('region_static_id');
```

## Core Methods

### refresh()
```javascript
apex.region('employees').refresh();
```

### applyFilter()
```javascript
// Equal
apex.region('employees').applyFilter('DEPARTMENT_ID', '=', '10');

// Range
apex.region('employees').applyFilter('SALARY', '>=', '50000');
apex.region('employees').applyFilter('SALARY', '<=', '100000');

// LIKE
apex.region('employees').applyFilter('FIRST_NAME', 'LIKE', '%John%');

// IN
apex.region('employees').applyFilter('DEPARTMENT_ID', 'IN', '10,20,30');
```

### clearFilter()
```javascript
apex.region('employees').clearFilter();
```

### getSelectedRecords()
```javascript
var selected = apex.region('employees').getSelectedRecords();
```

### Action Reset
```javascript
apex.region('empReport').widget().interactiveReport('action_reset');
```

## Common Patterns

### Filter by Item Value
```javascript
function filterByDepartment() {
    var deptId = apex.item('P10_DEPARTMENT_ID').getValue();
    if (!deptId) {
        apex.region('employees').clearFilter();
    } else {
        apex.region('employees').applyFilter('DEPARTMENT_ID', '=', deptId);
    }
}
```

### Dynamic Search
```javascript
function searchEmployees() {
    var searchTerm = apex.item('P10_SEARCH').getValue();
    if (!searchTerm) {
        apex.region('employees').clearFilter();
        return;
    }
    apex.region('employees').applyFilter('FIRST_NAME', 'LIKE', '%' + searchTerm + '%');
}
```

### Date Range Filter
```javascript
function filterByDateRange() {
    var fromDate = apex.item('P10_FROM_DATE').getValue();
    var toDate = apex.item('P10_TO_DATE').getValue();
    var region = apex.region('employees');

    region.clearFilter();
    if (fromDate) { region.applyFilter('HIRE_DATE', '>=', fromDate); }
    if (toDate)   { region.applyFilter('HIRE_DATE', '<=', toDate); }
}
```

### Process Selected Rows
```javascript
function processSelectedRows() {
    var selected = apex.region('employees').getSelectedRecords();
    if (selected.length === 0) {
        apex.message.showErrors([{
            type: 'error', location: 'page',
            message: 'No rows selected'
        }]);
        return;
    }
    apex.server.process('PROCESS_ROWS', {
        pageItems: '#P10_SELECTED_IDS'
    }, {
        dataType: 'json',
        success: function() {
            apex.message.showPageSuccess('Processed ' + selected.length + ' rows');
            apex.region('employees').refresh();
        }
    });
}
```

## IR vs IG Comparison

| Aspect | Interactive Report | Interactive Grid |
|--------|-------------------|-----------------|
| Inline editing | No | Yes |
| Validation | Limited | Full client+server |
| Saved views | Yes | Yes |
| Performance | Good | Very good |
| Data entry | Not supported | Supported (buggy in 20.2) |
| Recommended for | Read-only reports | New applications |
