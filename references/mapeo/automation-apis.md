# Programmatic APEX 20.2 Generation APIs

## Context

To accelerate migration, PL/SQL scripts can create pages, regions and items based on a blueprint derived from Forms XML. This uses internal APEX APIs that are not officially supported.

## Internal APIs

### Page Creation
```plsql
-- INTERNAL / UNSUPPORTED API - VERIFICATION REQUIRED IN TARGET APEX 20.2 ENVIRONMENT
wwv_flow_api.create_page(
    p_id             => <page_id>,
    p_flow_id        => <app_id>,
    p_name           => 'Page Name',
    p_page_mode      => 'NORMAL',  -- or 'MODAL_DIALOG'
    p_step_title     => 'Page Title'
);
```

### Region Creation
```plsql
-- INTERNAL / UNSUPPORTED API - VERIFICATION REQUIRED
wwv_flow_api.create_page_plug(
    p_id                    => <unique_id>,
    p_flow_id               => <app_id>,
    p_page_id               => <page_id>,
    p_plug_name             => 'Region Name',
    p_region_name           => 'static_id',     -- maps to STATIC_ID in APEX views
    p_plug_template         => <template_id>,    -- resolve dynamically
    p_plug_display_sequence => 10,
    p_plug_source           => 'SELECT ... FROM ...',
    p_plug_source_type      => 'NATIVE_SQL_REPORT',
    p_plug_display_point    => 'BODY',
    p_escape_on_http_output => 'N'
);
```

### Item Creation
```plsql
-- INTERNAL / UNSUPPORTED API - VERIFICATION REQUIRED
wwv_flow_api.create_page_item(
    p_id             => <unique_id>,
    p_flow_id        => <app_id>,
    p_flow_step_id   => <page_id>,
    p_name           => 'P<page>_FIELD_NAME',
    p_display_as     => 'NATIVE_TEXT_FIELD',
    p_item_sequence  => 10,
    p_item_plug_id   => <region_id>,
    p_prompt         => 'Field Label',
    p_placeholder    => 'Placeholder text'
);
```

### Button Creation
```plsql
-- INTERNAL / UNSUPPORTED API - VERIFICATION REQUIRED
wwv_flow_api.create_page_button(
    p_id              => <unique_id>,
    p_flow_id         => <app_id>,
    p_flow_step_id    => <page_id>,
    p_button_name     => 'SAVE',
    p_button_sequence => 10,
    p_button_plug_id  => <region_id>
);
```

### Other Internal APIs
- `wwv_flow_imp_page.create_page`
- `wwv_flow_imp_page.create_page_plug`
- `wwv_flow_imp_page.create_region_column`

## Template ID Resolution

Template IDs change between instances/workspaces. Always resolve by name:

```sql
-- Region templates
SELECT template_id, template_name
FROM apex_application_templates
WHERE application_id = :app_id
AND template_type = 'Region'
AND template_name = 'Standard';

-- Inline Dialog template
SELECT template_id
FROM apex_application_templates
WHERE application_id = :app_id
AND template_type = 'Region'
AND template_name = 'Inline Dialog';

-- Page templates
SELECT template_id, template_name
FROM apex_application_templates
WHERE application_id = :app_id
AND template_type = 'Page';
```

## Key Column Mappings

| APEX View Column | WWV_FLOW_PAGE_PLUGS Column | Notes |
|---|---|---|
| STATIC_ID | REGION_NAME | NOT `region_attributes_substitution` |
| TEMPLATE | PLUG_TEMPLATE | Template ID (number) |
| REGION_NAME (display) | PLUG_NAME | Visible name |
| CSS Classes | REGION_CSS_CLASSES | CSS class list |

## Setup Required

```plsql
BEGIN
    -- Set workspace context (required before any wwv_flow_api call)
    apex_util.set_security_group_id(<workspace_id>);

    -- ... create_page_plug, create_page_item, etc. ...

    COMMIT;
END;
```

## Best Practices

1. Generate scripts only when explicitly requested
2. Always include warning comments about unsupported APIs
3. Execute in a test workspace first
4. Resolve all template IDs dynamically (never hardcode)
5. Use unique IDs that don't conflict with existing components

## Supported Alternatives

- APEX export/import as standard artifacts
- `APEX_EXPORT` / `APEX_APPLICATION_INSTALL` for cloning/installing apps
