# APEX JavaScript API Reference — All Namespaces (Comprehensive)

## Namespace Index

`apex.server` · `apex.item` · `apex.region` · `apex.page` · `apex.message` · `apex.navigation` · `apex.debug` · `apex.util` · `apex.lang` · `apex.locale` · `apex.theme` · `apex.event` · `apex.da` · `apex.actions` · `apex.storage` · `apex.env`

---

## apex.server — AJAX and Server Communication

| Method | Returns | Description |
|--------|---------|-------------|
| `process(pName, pData, pOptions)` | Promise | Call On-Demand PL/SQL process |
| `plugin(pAjaxIdentifier, pData, pOptions)` | Promise | Call plug-in AJAX function |
| `pluginUrl(pAjaxIdentifier, pData)` | string | GET URL for plug-in |
| `url(pData, pPage)` | string | GET URL for current page |
| `loadScript(pOptions, callback)` | Promise | Load JS file dynamically |
| `chunkText(pText)` | string\|Array | Split text into chunks (for p_clob_01) |

### pData Properties
| Property | Type | Description |
|----------|------|-------------|
| `pageItems` | string/jQuery/Array | CSS selector, jQuery, or array of item names to submit |
| `x01..x20` | string | Scalar parameters (maps to `apex_application.g_x01..g_x20`) |
| `f01..f20` | Array | Array parameters (maps to `apex_application.g_f01..g_f20`) |
| `p_clob_01` | string | CLOB parameter (maps to `apex_application.g_clob_01`) |

### pOptions Properties
| Property | Type | Description |
|----------|------|-------------|
| `success` | function(data) | Success callback |
| `error` | function(jqXHR, textStatus, errorThrown) | Error callback |
| `complete` | function | Always runs after success/error |
| `dataType` | string | `'json'`, `'text'`, `'html'` |
| `loadingIndicator` | string/jQuery | Element to show spinner on |
| `loadingIndicatorPosition` | string | `'before'`, `'after'`, `'prepend'`, `'append'`, `'centered'`, `'page'` |
| `refreshObject` | jQuery | Region element to trigger apexbeforerefresh/apexafterrefresh on |
| `queue` | object | `{name: 'queueName', action: 'wait'|'replace'|'lazyWrite'}` |
| `target` | Element | Event target for error handling |
| `async` | boolean | Default true. Set false for synchronous (discouraged) |

```javascript
// Standard AJAX process call
apex.server.process('VALIDATE_CI', {
    x01: apex.item('P10_CI').getValue(),
    x02: apex.item('P10_TIPO_DOC').getValue(),
    pageItems: '#P10_CONTRATO_ID'
}, {
    dataType: 'json',
    success: function(data) {
        if (data.success) {
            apex.item('P10_CI').setValidity(true);
            apex.message.showPageSuccess(data.message);
        } else {
            apex.item('P10_CI').setValidity(false, data.message);
        }
    },
    error: function(jqXHR, textStatus) {
        console.error('AJAX error:', textStatus);
    },
    loadingIndicator: '#R_DATOS_CLIENTE',
    loadingIndicatorPosition: 'centered'
});

// Send CLOB data
var bigData = JSON.stringify(largeObject);
apex.server.process('SAVE_BIG_DATA', {
    p_clob_01: bigData,
    x01: 'metadata'
}, {
    dataType: 'json',
    success: function(data) { /* ... */ }
});

// Plugin AJAX
apex.server.plugin(ajaxIdentifier, {x01: 'param', pageItems: '#P10_ID'}, {
    success: function(data) { }
});

// Build URL only (no call)
var url = apex.server.url({x01: 'param', p_request: 'MY_PROCESS'});
```

---

## apex.item — Item Manipulation

| Method | Returns | Description |
|--------|---------|-------------|
| `getValue()` | string/Array | Current value (array for multi-value items) |
| `setValue(pValue, pDisplayValue, pSuppressChangeEvent)` | void | Set value |
| `show(pShowRow)` | void | Show item (and row if true) |
| `hide(pHideRow)` | void | Hide item (and row if true) |
| `enable()` | void | Enable item |
| `disable()` | void | Disable item |
| `setFocus()` | void | Set keyboard focus |
| `isEmpty()` | boolean | True if empty/null |
| `isChanged()` | boolean | True if changed since page load |
| `isDisabled()` | boolean | True if disabled |
| `getValidity()` | object | `{valid: bool, valueMissing: bool, ...}` |
| `setValidity(pValidity, pMessage)` | void | Set/clear inline validation error |
| `displayValueFor(pValue)` | string | Get display value for a return value |
| `refresh()` | void | Refresh LOV / cascading LOV |
| `addValue(pValue)` | void | Add value to multi-select |
| `removeValue(pValue)` | void | Remove value from multi-select |

### Properties
| Property | Type | Description |
|----------|------|-------------|
| `element` | jQuery | jQuery element of the item |
| `node` | jQuery | Same as element |
| `id` | string | Item name/ID |

```javascript
// Read/write values
var id   = apex.item('P10_ID').getValue();
var name = $v('P10_NAME');                   // shorthand
$s('P10_NAME', 'New value');                 // shorthand

// Select list: set return + display value
apex.item('P10_TIPO').setValue('A', 'Activo');

// Suppress change event (3rd arg)
apex.item('P10_TIPO').setValue('A', null, true);

// Visibility and state
apex.item('P10_CAMPO').show();      // show item only
apex.item('P10_CAMPO').show(true);  // show item + label row
apex.item('P10_CAMPO').hide(true);  // hide item + label row
apex.item('P10_CAMPO').enable();
apex.item('P10_CAMPO').disable();

// Validation
apex.item('P10_CI').setValidity(false, 'CI is required');
apex.item('P10_CI').setValidity(true);  // clear error
if (!apex.item('P10_CI').getValidity().valid) { /* ... */ }

// Check states
if (apex.item('P10_CI').isEmpty()) { /* ... */ }
if (apex.item('P10_CI').isChanged()) { /* ... */ }
if (apex.item('P10_CI').isDisabled()) { /* ... */ }

// Refresh cascading LOV
apex.item('P10_SUBTIPO').refresh();

// Multi-value items
apex.item('P10_TAGS').addValue('NEW_TAG');
apex.item('P10_TAGS').removeValue('OLD_TAG');

// Access DOM element
var $el = apex.item('P10_CI').element;
var domNode = apex.item('P10_CI').node[0];
```

---

## apex.region — Region Manipulation

| Method | Returns | Description |
|--------|---------|-------------|
| `refresh()` | void | Refresh region data |
| `focus()` | void | Focus the region |
| `widget()` | jQuery | Get underlying jQuery widget |
| `call(methodName, ...args)` | varies | Call widget method |
| `create(pType, pOptions)` | void | Create region (static method) |
| `destroy()` | void | Destroy region |
| `findClosest(pElement)` | region | Find closest region to element |
| `isRegion(pStaticId)` | boolean | Check if region exists |
| `alternateLoadingIndicator` | function | Custom loading indicator |

### Properties
| Property | Type | Description |
|----------|------|-------------|
| `element` | jQuery | jQuery element of region |
| `type` | string | Region type |
| `parentRegionStaticId` | string | Parent region static ID |

```javascript
// Refresh Interactive Report or Classic Report
apex.region('orders_ir').refresh();

// Interactive Report widget methods
var $widget = apex.region('orders_ir').widget();
$widget.interactiveReport('action_reset');
$widget.interactiveReport('addFilter', 'STATUS', 'EQ', 'ACTIVE');

// Interactive Grid — full model access
var ig      = apex.region('emp_ig').widget().interactiveGrid('getViews', 'grid');
var model   = ig.model;
var records = ig.getSelectedRecords();
var record  = records[0];
var salary  = model.getValue(record, 'SALARY');
model.setValue(record, 'SALARY', 5000);

// IG: iterate all records
model.forEach(function(record) {
    var name = model.getValue(record, 'ENAME');
});

// IG: add new row
var newRec = model.insertNewRecord();
model.setValue(newRec, 'ENAME', 'New Employee');

// IG: delete selected
var sel = ig.getSelectedRecords();
sel.forEach(function(rec) { model.deleteRecord(rec); });

// IG: save changes
apex.region('emp_ig').widget().interactiveGrid('getActions').invoke('save');

// IG: get all changed records
var changes = model.getChanges();

// Scroll to region
apex.region('additional_data').element[0].scrollIntoView({behavior: 'smooth'});

// Check if region exists
if (apex.region.isRegion && apex.region.isRegion('my_region')) { /* ... */ }
// Or simply:
if (apex.region('my_region')) { /* ... */ }
```

---

## apex.page — Page Control

| Method | Returns | Description |
|--------|---------|-------------|
| `submit(pOptions)` | void | Submit the page |
| `validate(pOptions)` | boolean | Trigger client-side validation |
| `isChanged()` | boolean | True if unsaved changes exist |
| `cancelSubmit()` | void | Cancel a pending page submit |
| `confirm(pMessage, pCallback)` | void | Confirm before submit |
| `warnOnUnsavedChanges(pMessage, pExclude)` | void | Enable unsaved changes warning |
| `cancelWarnOnUnsavedChanges()` | void | Disable unsaved changes warning |

```javascript
// Submit with string (request value)
apex.page.submit('SAVE');

// Submit with options
apex.page.submit({
    request:      'DELETE',
    validate:     true,
    showWait:     true,
    set: {
        'P10_ACTION': 'DELETE',
        'P10_ID': itemId
    },
    submitIfEnter: event
});

// Cancel submit (inside before-submit handler)
if (!isValid) {
    apex.page.cancelSubmit();
}

// Check for unsaved changes
if (apex.page.isChanged()) {
    // prompt user
}

// Validate without submitting
if (apex.page.validate()) {
    // all validations pass
}

// Enable unsaved-changes warning
apex.page.warnOnUnsavedChanges('You have unsaved changes.');
apex.page.cancelWarnOnUnsavedChanges();  // disable it
```

---

## apex.message — User Notifications

| Method | Returns | Description |
|--------|---------|-------------|
| `showPageSuccess(pMessage)` | void | Green success banner |
| `hidePageSuccess()` | void | Hide success banner |
| `showErrors(pErrors)` | void | Show error messages |
| `clearErrors()` | void | Clear all errors |
| `alert(pMessage, pCallback)` | void | Alert dialog |
| `confirm(pMessage, pCallback)` | void | Confirmation dialog |
| `setThemeHooks(pHooks)` | void | Customize message display |
| `addVisibilityCheck(pFunction)` | void | Add custom visibility check |

### Error Object Format
```javascript
{
    type:     'error',           // 'error' or 'warning'
    location: 'page',           // 'page', 'inline', or ['page','inline']
    pageItem: 'P10_CI',         // required for inline location
    message:  'Error text',     // the message
    unsafe:   false             // true = allow HTML in message
}
```

```javascript
// Success message
apex.message.showPageSuccess('Record saved successfully.');

// Page-level error
apex.message.showErrors([{
    type:     'error',
    message:  'An error occurred while saving',
    location: 'page'
}]);

// Field-level error
apex.message.showErrors([{
    type:     'error',
    message:  'Value is not valid',
    location: 'inline',
    pageItem: 'P10_CI',
    unsafe:   false
}]);

// Both page + inline at once
apex.message.showErrors([{
    type:     'error',
    message:  'CI is invalid',
    location: ['page', 'inline'],
    pageItem: 'P10_CI'
}]);

// Multiple errors
apex.message.showErrors([
    {type: 'error', location: 'page',   message: 'General error'},
    {type: 'error', location: 'inline', pageItem: 'P10_CI',   message: 'CI invalid'},
    {type: 'error', location: 'inline', pageItem: 'P10_NAME', message: 'Name required'}
]);

apex.message.clearErrors();

// Confirmation dialog
apex.message.confirm('Delete this record?', function(ok) {
    if (ok) { apex.page.submit('DELETE'); }
});

// Alert dialog
apex.message.alert('Process completed.', function() {
    apex.region('data_ir').refresh();
});

// Theme hooks (customize error display)
apex.message.setThemeHooks({
    beforeShow: function(pMsgType, pMessages$) { /* ... */ },
    beforeHide: function(pMsgType, pMessages$) { /* ... */ }
});
```

---

## apex.navigation — Navigation and Dialogs

| Method | Returns | Description |
|--------|---------|-------------|
| `redirect(pUrl)` | void | Redirect browser to URL |
| `openInNewWindow(pUrl, pWindowName, pOptions)` | Window | Open URL in new tab/window |
| `dialog(pUrl, pOptions, pCssClasses, pRegion)` | void | Open page as modal dialog |
| `dialog.close(pReload, pSetItems)` | void | Close current dialog |
| `dialog.cancel(pIsEscapeClose)` | void | Cancel dialog without reload |
| `popup(pOptions)` | Window | Open popup window |

### dialog pOptions
| Property | Type | Description |
|----------|------|-------------|
| `title` | string | Dialog title |
| `height` | number | Dialog height in px |
| `width` | number | Dialog width in px |
| `maxWidth` | number | Maximum width |
| `modal` | boolean | Modal (true) or modeless (false) |
| `resizable` | boolean | Allow resizing |
| `closeText` | string | Close button label |

```javascript
// Simple redirect
apex.navigation.redirect('f?p=400:946:' + $v('pInstance') + '::::P946_ID:' + id);

// Open in new window
apex.navigation.openInNewWindow('f?p=400:200:' + $v('pInstance'));

// Open modal dialog
apex.navigation.dialog(
    'f?p=400:954:' + $v('pInstance') + '::::P954_ID:' + v_id,
    {
        title:    'Manage Emails',
        height:   500,
        width:    800,
        modal:    true,
        resizable: true
    }
);

// Close dialog and trigger refresh on caller page
apex.navigation.dialog.close(true, {action: 'refresh', id: v_id});

// Cancel dialog (no reload, no data)
apex.navigation.dialog.cancel();

// Popup window
apex.navigation.popup({
    url:    'f?p=400:950:' + $v('pInstance'),
    name:   'REPORT',
    width:  1000,
    height: 700
});
```

---

## apex.event — Custom Events

| Method | Description |
|--------|-------------|
| `trigger(pElement, pEvent, pData)` | Fire DOM event on element |

**APEX Standard Events:**
- `apexbeforepagesubmit` — before page submit
- `apexafterpagesubmit` — after page submit (rarely used)
- `apexbeforerefresh` — before region refresh
- `apexafterrefresh` — after region refresh
- `apexwindowresized` — window resize complete
- `apexreadyend` — page fully loaded
- `apexaftershow` — after dialog shown
- `apexafterclose` — after dialog closed (on parent page)
- `apexafterclosedialog` — synonym for above

```javascript
// Trigger change on an item (fires Dynamic Actions)
apex.event.trigger('#P10_TIPO', 'change');

// Trigger custom event with data
apex.event.trigger(document, 'myCustomEvent', {id: 123, action: 'refresh'});

// Listen to region refresh
$('#my_region').on('apexafterrefresh', function() {
    console.log('Region refreshed');
});

// Listen for dialog close (on calling page)
$(document).on('apexafterclosedialog', function(event, data) {
    if (data && data.action === 'refresh') {
        apex.region('orders_ir').refresh();
    }
});

// jQuery event binding (common pattern)
$('#P10_TIPO').on('change', function() {
    var val = apex.item('P10_TIPO').getValue();
    apex.item('P10_SUBTIPO').show(val === 'A');
});
```

---

## apex.da — Dynamic Action API

### Context Properties (inside "Execute JavaScript Code" action)
| Property | Type | Description |
|----------|------|-------------|
| `this.affectedElements` | jQuery | Affected DOM elements |
| `this.triggeringElement` | Element | Element that triggered the DA |
| `this.data` | object | Event data |
| `this.browserEvent` | Event | Original browser event |
| `this.resumeCallback` | function | Callback to continue DA chain |
| `this.action` | object | Current action definition |
| `this.action.attribute01..15` | string | Custom attribute values |

### Methods
| Method | Description |
|--------|-------------|
| `apex.da.resume(pCallback, pResult)` | Resume async DA execution |
| `apex.da.cancel()` | Cancel DA execution |
| `apex.da.handleAjaxErrors(jqXHR, textStatus, errorThrown)` | Standard AJAX error handler |

```javascript
// Inside DA "Execute JavaScript Code":

// Access affected elements
this.affectedElements.each(function() {
    var itemName = $(this).attr('id');
    apex.item(itemName).show();
});

// Access triggering element
var val = apex.item(this.triggeringElement.id).getValue();

// Async DA with resume (IMPORTANT pattern)
var self = this;
apex.server.process('MY_PROCESS', {x01: val}, {
    success: function(data) {
        // process result...
        apex.da.resume(self.resumeCallback, true);  // true = success
    },
    error: function(jqXHR, textStatus, errorThrown) {
        apex.da.handleAjaxErrors(jqXHR, textStatus, errorThrown);
        apex.da.resume(self.resumeCallback, false);  // false = failure
    }
});
return false;  // tell APEX to wait for resumeCallback

// Cancel DA chain
if (someCondition) {
    apex.da.cancel();
}
```

---

## apex.util — Utilities

| Method | Returns | Description |
|--------|---------|-------------|
| `escapeHTML(pStr)` | string | Escape HTML entities |
| `escapeHTMLAttr(pStr)` | string | Escape for HTML attributes |
| `escapeCSS(pStr)` | string | Escape for CSS selectors |
| `escapeRegExp(pStr)` | string | Escape for RegExp |
| `showSpinner(pContainer, pOptions)` | jQuery | Show loading spinner (returns spinner element) |
| `applyTemplate(pTemplate, pValues, pOptions)` | string | Apply `#KEY#` substitutions |
| `htmlBuilder()` | object | Create HTML builder for safe DOM generation |
| `toArray(pValue)` | Array | Convert value to array |
| `isEmpty(pValue)` | boolean | True if null/empty/undefined |
| `stripHTML(pStr)` | string | Remove HTML tags |
| `arrayEqual(pArray1, pArray2)` | boolean | Compare arrays |
| `debounce(pFunction, pDelay)` | function | Create debounced function |
| `getDateFromISO8601String(pStr)` | Date | Parse ISO date string |
| `invokeAfterPaint(pCallback)` | void | Run callback after next paint |
| `getTopApex()` | apex | Get apex from top window (for dialogs) |

```javascript
// XSS prevention
var safe = apex.util.escapeHTML(userInput);
var safeAttr = apex.util.escapeHTMLAttr(attrValue);
var safeCSS = apex.util.escapeCSS(dynamicId);  // for jQuery selectors

// Loading spinner
var spinner = apex.util.showSpinner($('#container'));
// ... async work ...
spinner.remove();

// Page-level spinner
var spinner = apex.util.showSpinner();

// Template substitution
var html = apex.util.applyTemplate(
    '<span class="badge #CSS_CLASS#">#STATUS#</span>',
    {STATUS: apex.util.escapeHTML(status), CSS_CLASS: 'u-success'}
);

// HTML builder (safe DOM generation)
var out = apex.util.htmlBuilder();
out.markup('<div')
   .attr('class', 'my-class')
   .attr('id', 'myDiv')
   .markup('>')
   .content(label)        // auto-escaped
   .markup('</div>');
$('#container').html(out.toString());

// Debounce (search-as-you-type)
var debouncedSearch = apex.util.debounce(function() {
    apex.region('results').refresh();
}, 300);
$('#P10_SEARCH').on('input', debouncedSearch);

// Strip HTML
var plainText = apex.util.stripHTML('<b>Hello</b> <em>World</em>');  // 'Hello World'

// ISO date parsing
var date = apex.util.getDateFromISO8601String('2024-01-15T10:30:00Z');

// Run after next paint (useful for DOM measurements)
apex.util.invokeAfterPaint(function() {
    var height = $('#myRegion').height();
});

// Access parent page apex from dialog
var parentApex = apex.util.getTopApex();
parentApex.region('parent_region').refresh();
```

---

## apex.debug — Client-side Debugging

| Method | Description |
|--------|-------------|
| `error(...)` | Log error message |
| `warn(...)` | Log warning |
| `info(...)` | Log info message |
| `trace(...)` | Log trace message |
| `log(...)` | General log (alias for info) |
| `message(pLevel, ...)` | Log at specific level |
| `getLevel()` | Get current debug level |
| `setLevel(pLevel)` | Set debug level |

**Level constants:** `apex.debug.LOG_LEVEL.OFF=0, .ERROR=1, .WARN=2, .INFO=4, .APP_TRACE=6, .ENGINE_TRACE=9`

```javascript
apex.debug.info('Loading customer ID: %s', customerId);
apex.debug.warn('Unexpected null for field: %s', fieldName);
apex.debug.error('AJAX call failed:', errorObj);
apex.debug.trace('Detailed trace: %o', bigObject);

// Conditional debug
if (apex.debug.getLevel() >= apex.debug.LOG_LEVEL.INFO) {
    apex.debug.info('Detailed: %o', bigObject);
}
```

---

## apex.lang — Internationalization

| Method | Returns | Description |
|--------|---------|-------------|
| `getMessage(pKey)` | string | Get translated message by key |
| `formatMessage(pKey, ...)` | string | Get message with placeholder substitution |
| `hasMessage(pKey)` | boolean | Check if message key exists |
| `loadMessages(pMessages)` | void | Load message key/value object |
| `loadMessagesIfNeeded(pKeys, pCallback)` | void | Load from server if not cached |
| `addMessages(pMessages)` | void | Add messages (same as loadMessages) |
| `clearMessages()` | void | Clear all loaded messages |
| `format(pPattern, ...)` | string | Format string with %0, %1 placeholders |

```javascript
// Define messages
apex.lang.addMessages({
    'MSG_SAVING':  'Saving...',
    'MSG_SAVED':   'Saved successfully',
    'MSG_COUNT':   'Found %0 records in %1 seconds'
});

// Use messages
apex.message.showPageSuccess(apex.lang.getMessage('MSG_SAVED'));

// With placeholders
var msg = apex.lang.formatMessage('MSG_COUNT', totalRows, elapsed);

// Check existence
if (apex.lang.hasMessage('MSG_CUSTOM')) { /* ... */ }

// Format without pre-loaded messages
var text = apex.lang.format('%0 of %1 items selected', selected, total);
```

---

## apex.locale — Locale and Formatting

| Method | Returns | Description |
|--------|---------|-------------|
| `getLanguage()` | string | Current language code (e.g., 'es') |
| `getDecimalSeparator()` | string | Decimal char (',' or '.') |
| `getGroupSeparator()` | string | Thousands separator |
| `getCurrency()` | string | Currency symbol |
| `formatNumber(pValue, pFormat)` | string | Format number |
| `formatCompactNumber(pValue)` | string | Compact format (1K, 1M) |
| `getAbbrevDayNames()` | Array | Abbreviated day names |
| `getAbbrevMonthNames()` | Array | Abbreviated month names |
| `resourcesLoaded()` | Promise | Resolves when locale data loaded |
| `toNumber(pString)` | number | Parse locale-formatted string to number |
| `toCurrencyString(pValue)` | string | Format as currency |

```javascript
var lang    = apex.locale.getLanguage();           // 'es'
var decSep  = apex.locale.getDecimalSeparator();   // ','
var grpSep  = apex.locale.getGroupSeparator();     // '.'

// Format number
var str = apex.locale.formatNumber(1234567.89, '999G999G999D99');
var curr = apex.locale.toCurrencyString(1234567.89);

// Parse locale number back to JS number
var num = apex.locale.toNumber('1.234.567,89');

// Locale data
var months = apex.locale.getAbbrevMonthNames();  // ['Ene','Feb',...]
var days   = apex.locale.getAbbrevDayNames();    // ['Dom','Lun',...]
```

---

## apex.theme — Theme and UI

| Method | Returns | Description |
|--------|---------|-------------|
| `openRegion(pStaticId)` | void | Open Inline Dialog / Popup |
| `closeRegion(pStaticId)` | void | Close Inline Dialog / Popup |
| `popupFieldHelp(pItemId, pSessionId)` | void | Show item help popup |
| `defaultStickyTop()` | number | Get sticky-top default height |
| `scrollPageToItem(pItemName)` | void | Scroll page to item |
| `mq(pBreakpoint)` | MediaQueryList | Get media query for breakpoint |
| `modeToggle(pMode)` | void | Toggle light/dark mode |

```javascript
// Open/close Inline Dialog (NEVER use jQuery UI .dialog())
apex.theme.openRegion('confirm_dialog');
apex.theme.closeRegion('confirm_dialog');

// Scroll to item
apex.theme.scrollPageToItem('P10_CI');

// Show field help popup
apex.theme.popupFieldHelp('P10_CI', $v('pInstance'));

// Responsive breakpoints
var mq = apex.theme.mq('tablet');  // 'phone', 'tablet', 'desktop'
if (mq.matches) { /* tablet or smaller */ }
```

---

## apex.storage — Client-side Storage

| Method | Returns | Description |
|--------|---------|-------------|
| `getCookie(pName)` | string | Read cookie value |
| `setCookie(pName, pValue)` | void | Set cookie |
| `getScopedLocalStorage(pOptions)` | Storage | Namespaced localStorage |
| `getScopedSessionStorage(pOptions)` | Storage | Namespaced sessionStorage |
| `hasLocalStorageSupport()` | boolean | True if localStorage available |
| `hasSessionStorageSupport()` | boolean | True if sessionStorage available |

```javascript
// Cookies
var val = apex.storage.getCookie('MY_COOKIE');
apex.storage.setCookie('MY_COOKIE', 'value');

// Scoped localStorage
var ls = apex.storage.getScopedLocalStorage({
    usePageId: false,   // share across pages
    useAppId:  true,    // scope to this app
    prefix:    'myComp'
});
ls.setItem('userPref', JSON.stringify({theme: 'dark', density: 'compact'}));
var pref = JSON.parse(ls.getItem('userPref') || '{}');
ls.removeItem('userPref');

// Session storage (lost when tab closes)
var ss = apex.storage.getScopedSessionStorage({useAppId: true, prefix: 'tmp'});
ss.setItem('lastSearch', searchTerm);
```

---

## apex.actions — Action Framework

| Method | Returns | Description |
|--------|---------|-------------|
| `add(pActions)` | void | Register action(s) |
| `remove(pName)` | void | Remove action |
| `invoke(pName, pFocusElement)` | void | Invoke action |
| `enable(pName)` | void | Enable action |
| `disable(pName)` | void | Disable action |
| `hide(pName)` | void | Hide action |
| `show(pName)` | void | Show action |
| `isEnabled(pName)` | boolean | True if enabled |
| `toggle(pName)` | void | Toggle state |
| `setLabel(pName, pLabel)` | void | Update label |
| `createContext(pTypeName, pElement)` | object | Create action context |
| `findContext(pTypeName, pElement)` | object | Find action context |
| `removeContext(pTypeName, pElement)` | void | Remove action context |
| `shortcutSupport(pElement)` | void | Enable keyboard shortcuts |

```javascript
// Register actions
apex.actions.add([{
    name:   'save-record',
    label:  'Save',
    icon:   'fa-save',
    shortcut: 'Ctrl+S',
    action: function(event, focusElement) {
        apex.page.submit('SAVE');
    }
}, {
    name:   'delete-record',
    label:  'Delete',
    icon:   'fa-trash-o',
    action: function() {
        apex.message.confirm('Delete?', function(ok) {
            if (ok) { apex.page.submit('DELETE'); }
        });
    }
}]);

// Invoke / control
apex.actions.invoke('save-record');
apex.actions.disable('delete-record');
apex.actions.enable('delete-record');

// IG actions context
var igActions = apex.region('emp_ig').widget().interactiveGrid('getActions');
igActions.invoke('save');
igActions.invoke('selection-add-row');
igActions.invoke('selection-delete');
```

---

## Legacy Globals

```javascript
$v('P10_ITEM')            // apex.item('P10_ITEM').getValue()
$s('P10_ITEM', 'value')   // apex.item('P10_ITEM').setValue('value')
$x('P10_ITEM')            // document.getElementById('P10_ITEM')
```

---

## apex.env — Environment Variables

```javascript
apex.env.APP_ID;        // Application ID (number)
apex.env.APP_PAGE_ID;   // Current page ID (number)
apex.env.APP_SESSION;   // Session ID (string)
apex.env.APP_USER;      // Current user (string)
```

---

## apex.jQuery / apex.gPageContext$

```javascript
// APEX's jQuery reference (use when page has multiple jQuery versions)
apex.jQuery('#myElement').show();

// Page context (for events scoped to current page in dialog scenarios)
apex.gPageContext$.on('apexafterrefresh', '#my_region', function() { /* ... */ });
```

---

## SweetAlert2 (Swal) — Common in Custom APEX Apps

```javascript
// Confirmation
Swal.fire({
    title:              'Confirm?',
    text:               'This action cannot be undone',
    icon:               'warning',
    showCancelButton:   true,
    confirmButtonText:  'Yes, continue',
    cancelButtonText:   'Cancel',
    confirmButtonColor: '#3085d6',
    cancelButtonColor:  '#d33'
}).then(function(result) {
    if (result.isConfirmed) {
        apex.page.submit('SAVE');
    }
});

// Success toast (non-blocking)
Swal.fire({
    toast:             true,
    position:          'top-end',
    icon:              'success',
    title:             'Saved',
    showConfirmButton: false,
    timer:             3000
});

// Error
Swal.fire('Error', errorMessage, 'error');
```

---

## Common Patterns

### AJAX Callback (Full Pattern)

#### PL/SQL (On-Demand Process)
```plsql
DECLARE
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM   cliente
    WHERE  nro_documento = apex_application.g_x01
    AND    tipo_doc      = apex_application.g_x02;

    apex_json.open_object;
        apex_json.write('success', TRUE);
        apex_json.write('exists',  v_count > 0);
        apex_json.write('message', CASE WHEN v_count > 0 THEN 'Already exists' ELSE 'OK' END);
    apex_json.close_object;
EXCEPTION WHEN OTHERS THEN
    apex_json.open_object;
        apex_json.write('success', FALSE);
        apex_json.write('message', SQLERRM);
    apex_json.close_object;
END;
```

#### JavaScript (with debounce)
```javascript
var P10 = P10 || {};
P10.validateCI = apex.util.debounce(function(ci) {
    apex.server.process('VALIDATE_CI', {
        x01: ci,
        x02: apex.item('P10_TIPO_DOC').getValue()
    }, {
        dataType: 'json',
        success: function(data) {
            if (data.exists) {
                apex.item('P10_CI').setValidity(false, data.message);
            } else {
                apex.item('P10_CI').setValidity(true);
            }
        }
    });
}, 600);

$('#P10_CI').on('change', function() {
    P10.validateCI(this.value);
});
```

### IG Manipulation Pattern
```javascript
// Get IG model and manipulate data
var ig    = apex.region('emp_ig').widget().interactiveGrid('getViews', 'grid');
var model = ig.model;

// Read selected row value
var records = ig.getSelectedRecords();
if (records.length > 0) {
    var empName = model.getValue(records[0], 'ENAME');
    var empId   = model.getValue(records[0], 'EMPNO');
}

// Update all rows matching condition
model.forEach(function(record) {
    if (model.getValue(record, 'DEPT') === '10') {
        model.setValue(record, 'BONUS', 1000);
    }
});

// Programmatic save
apex.region('emp_ig').widget().interactiveGrid('getActions').invoke('save');

// Refresh IG
apex.region('emp_ig').refresh();
```

### Dialog Close and Refresh Pattern
```javascript
// In dialog page (after save process succeeds):
apex.navigation.dialog.close(true, {
    dialogPageId: $v('pFlowStepId'),
    action: 'saved',
    id: $v('P954_ID')
});

// In calling page (DA on "Dialog Closed" event):
var data = this.data;  // or event.originalEvent.data
if (data && data.action === 'saved') {
    apex.region('orders_ir').refresh();
    apex.message.showPageSuccess('Record saved.');
}
```

### Error Display After AJAX
```javascript
apex.server.process('SAVE_DATA', {
    x01: apex.item('P10_ID').getValue(),
    pageItems: '#P10_NAME,#P10_EMAIL'
}, {
    dataType: 'json',
    success: function(data) {
        apex.message.clearErrors();
        if (data.status === 'OK') {
            apex.message.showPageSuccess(data.message);
        } else if (data.errors) {
            // Server returns array of errors
            var errors = [];
            data.errors.forEach(function(e) {
                errors.push({
                    type:     'error',
                    location: e.item ? ['page','inline'] : 'page',
                    pageItem: e.item || undefined,
                    message:  e.message
                });
            });
            apex.message.showErrors(errors);
        }
    }
});
```
