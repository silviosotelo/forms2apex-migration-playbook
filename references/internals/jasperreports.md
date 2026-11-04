# JasperReports Server + APEX Integration

## Arquitectura
```
APEX Page (Button click)
  -> AJAX Callback (apex.server.process)
    -> PL/SQL (pkg_jasperreports.descarga_reporte)
      -> JasperReports Server REST API
        -> PDF/Excel/HTML
          -> Download al browser
```

## REST API de JasperReports Server

### Login
```
POST /jasperserver/rest_v2/login
Content-Type: application/x-www-form-urlencoded
j_username=<user>&j_password=<pass>
```
Retorna JSESSIONID cookie.

### Ejecutar Reporte
```
GET /jasperserver/rest_v2/reports/<report_uri>.<format>?<params>
Cookie: JSESSIONID=<session>
```
Formatos: pdf, xlsx, html, csv, docx, rtf, odt, ods, pptx

## PL/SQL Package de Integración

```sql
CREATE OR REPLACE PACKAGE pkg_jasperreports AS
  PROCEDURE descarga_reporte(
    p_report_uri  VARCHAR2,
    p_format      VARCHAR2 DEFAULT 'pdf',
    p_parameters  VARCHAR2 DEFAULT NULL,
    p_filename    VARCHAR2 DEFAULT 'reporte'
  );
END;
/

CREATE OR REPLACE PACKAGE BODY pkg_jasperreports AS

  gc_server_url  CONSTANT VARCHAR2(200) := '<configurar_url_jasper>';
  gc_username    CONSTANT VARCHAR2(50)  := '<configurar_user>';
  gc_password    CONSTANT VARCHAR2(50)  := '<configurar_pass>';

  FUNCTION get_mime_type(p_format VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    RETURN CASE LOWER(p_format)
      WHEN 'pdf'  THEN 'application/pdf'
      WHEN 'xlsx' THEN 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      WHEN 'html' THEN 'text/html'
      WHEN 'csv'  THEN 'text/csv'
      WHEN 'docx' THEN 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ELSE 'application/octet-stream'
    END;
  END;

  FUNCTION login RETURN VARCHAR2 IS
    v_response CLOB;
    v_cookie   VARCHAR2(500);
  BEGIN
    apex_web_service.g_request_headers.DELETE;
    apex_web_service.g_request_headers(1).name := 'Content-Type';
    apex_web_service.g_request_headers(1).value := 'application/x-www-form-urlencoded';

    v_response := apex_web_service.make_rest_request(
      p_url         => gc_server_url || '/rest_v2/login',
      p_http_method => 'POST',
      p_body        => 'j_username=' || gc_username || '&j_password=' || gc_password
    );

    FOR i IN 1..apex_web_service.g_headers.COUNT LOOP
      IF LOWER(apex_web_service.g_headers(i).name) = 'set-cookie'
         AND INSTR(apex_web_service.g_headers(i).value, 'JSESSIONID') > 0 THEN
        v_cookie := REGEXP_SUBSTR(apex_web_service.g_headers(i).value, 'JSESSIONID=[^;]+');
        EXIT;
      END IF;
    END LOOP;
    RETURN v_cookie;
  END;

  PROCEDURE descarga_reporte(
    p_report_uri  VARCHAR2,
    p_format      VARCHAR2 DEFAULT 'pdf',
    p_parameters  VARCHAR2 DEFAULT NULL,
    p_filename    VARCHAR2 DEFAULT 'reporte'
  ) IS
    v_cookie VARCHAR2(500);
    v_url    VARCHAR2(4000);
    v_blob   BLOB;
  BEGIN
    v_cookie := login();
    IF v_cookie IS NULL THEN
      raise_application_error(-20001, 'No se pudo autenticar en JasperReports Server');
    END IF;

    v_url := gc_server_url || '/rest_v2/reports' || p_report_uri || '.' || LOWER(p_format);
    IF p_parameters IS NOT NULL THEN
      v_url := v_url || '?' || p_parameters;
    END IF;

    apex_web_service.g_request_headers.DELETE;
    apex_web_service.g_request_headers(1).name := 'Cookie';
    apex_web_service.g_request_headers(1).value := v_cookie;

    v_blob := apex_web_service.make_rest_request_b(p_url => v_url, p_http_method => 'GET');

    IF apex_web_service.g_status_code != 200 THEN
      raise_application_error(-20002, 'Error HTTP ' || apex_web_service.g_status_code);
    END IF;

    OWA_UTIL.MIME_HEADER(get_mime_type(p_format), FALSE);
    HTP.P('Content-Disposition: attachment; filename="' || p_filename || '.' || LOWER(p_format) || '"');
    HTP.P('Content-Length: ' || DBMS_LOB.GETLENGTH(v_blob));
    OWA_UTIL.HTTP_HEADER_CLOSE;
    WPG_DOCLOAD.DOWNLOAD_FILE(v_blob);
    apex_application.stop_apex_engine;
  END;
END;
/
```

## APEX — AJAX Callback Process
```sql
-- Process: DESCARGAR_REPORTE, Type: NATIVE_PLSQL, Point: AJAX_CALLBACK
BEGIN
  pkg_jasperreports.descarga_reporte(
    p_report_uri => apex_application.g_x01,
    p_format     => NVL(apex_application.g_x02, 'pdf'),
    p_parameters => apex_application.g_x03,
    p_filename   => NVL(apex_application.g_x04, 'reporte')
  );
END;
```

## APEX — JavaScript (Botón de descarga)
```javascript
function descargarReporte(reportUri, formato, params, filename) {
  var form = document.createElement('form');
  form.method = 'POST';
  form.action = 'f?p=' + $v('pFlowId') + ':' + $v('pFlowStepId') + ':' + $v('pInstance');
  form.target = '_blank';

  function addField(name, value) {
    var input = document.createElement('input');
    input.type = 'hidden'; input.name = name; input.value = value;
    form.appendChild(input);
  }

  addField('x01', reportUri);
  addField('x02', formato || 'pdf');
  addField('x03', params || '');
  addField('x04', filename || 'reporte');
  addField('p_instance', $v('pInstance'));
  addField('p_flow_id', $v('pFlowId'));
  addField('p_flow_step_id', $v('pFlowStepId'));
  addField('p_request', 'APPLICATION_PROCESS=DESCARGAR_REPORTE');

  document.body.appendChild(form);
  form.submit();
  document.body.removeChild(form);
}
```

## Oracle Reports -> JRXML Mapping

| Oracle Reports | JasperReports JRXML |
|----------------|---------------------|
| Data Model Query | `<queryString>` |
| User Parameter | `<parameter>` |
| Formula Column | `<variable>` con expression |
| Summary Column | `<variable calculation="Sum/Count/Avg">` |
| Group | `<group>` con header/footer bands |
| Header Section | `<title>` y `<pageHeader>` |
| Body Section | `<detail>` band |
| Trailer Section | `<summary>` y `<pageFooter>` |
| Boilerplate Text | `<staticText>` |
| Field | `<textField>` con `<textFieldExpression>` |
| Format Mask | attribute `pattern` en textField |
| Conditional Format | `<printWhenExpression>` |

## JRXML Template Base
```xml
<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports
              http://jasperreports.sourceforge.net/xsd/jasperreport.xsd"
              name="report_name" language="groovy"
              pageWidth="595" pageHeight="842"
              columnWidth="555" leftMargin="20" rightMargin="20"
              topMargin="20" bottomMargin="20">

  <parameter name="p_id" class="java.lang.Long"/>

  <queryString><![CDATA[
    SELECT col1, col2, col3 FROM table WHERE id = $P{p_id}
  ]]></queryString>

  <field name="COL1" class="java.lang.String"/>
  <field name="COL2" class="java.math.BigDecimal"/>

  <variable name="TOTAL" class="java.math.BigDecimal" calculation="Sum">
    <variableExpression><![CDATA[$F{COL2}]]></variableExpression>
  </variable>

  <title><band height="50">
    <staticText>
      <reportElement x="0" y="0" width="555" height="30"/>
      <textElement textAlignment="Center"><font size="16" isBold="true"/></textElement>
      <text><![CDATA[Título del Reporte]]></text>
    </staticText>
  </band></title>

  <columnHeader><band height="20">
    <staticText>
      <reportElement x="0" y="0" width="200" height="20"/>
      <textElement><font isBold="true"/></textElement>
      <text><![CDATA[Columna 1]]></text>
    </staticText>
  </band></columnHeader>

  <detail><band height="20">
    <textField><reportElement x="0" y="0" width="200" height="20"/>
      <textFieldExpression><![CDATA[$F{COL1}]]></textFieldExpression>
    </textField>
    <textField pattern="#,##0.00"><reportElement x="200" y="0" width="100" height="20"/>
      <textFieldExpression><![CDATA[$F{COL2}]]></textFieldExpression>
    </textField>
  </band></detail>

  <summary><band height="30">
    <textField pattern="#,##0.00">
      <reportElement x="200" y="0" width="100" height="20"/>
      <textElement textAlignment="Right"><font isBold="true"/></textElement>
      <textFieldExpression><![CDATA[$V{TOTAL}]]></textFieldExpression>
    </textField>
  </band></summary>
</jasperReport>
```
