# Gotchas de APEX 20.2 / `wwv_flow_api` y cómo corregir una página existente

## Setup obligatorio antes de cualquier `create_*`

```plsql
wwv_flow_api.set_security_group_id(p_security_group_id => <id del workspace>);  -- según el perfil
wwv_flow.g_flow_id := <id de la aplicación>;                                      -- según el perfil
wwv_flow.g_user    := '<usuario de trabajo>';
```

Sin esto los `create_*` **fallan en silencio**: no hay error y no hay componente.

## Las que fallan sin dar error

- **`create_worksheet_rpt`: `p_report_columns` usa NOMBRES de columna, no identificadores.** Con `'A:B:C'` el IR
  renderiza las filas sin ninguna columna y no da error. Correcto: `'ID_CLIENTE:NOMBRE:MONTO'`.
- **`p_column_identifier` está limitado a 10 caracteres** (`ORA-12899` con nombres largos): usar `A`, `B`, `C`…
- **`p_column_type` es NOT NULL** (`'STRING'`/`'NUMBER'`/`'DATE'`) → sin él, `ORA-01400`.
- **`p_column_link_checksum_type`** acepta `'1'`/`'2'`/`'3'` (sesión = `'3'`), no `'SESSION'`.
- **Regiones `Blank with Attributes`**: el nombre no se renderiza; el `<h5>` va en el *source* **con
  `attribute_02 => 'HTML'`** (con el default `'TEXT'` sale escapado como texto literal).
- **`p_button_cattributes` con `onclick` se ignora en botones SUBMIT**: APEX lo sobrescribe. Para confirmar una
  operación irreversible: botón `DEFINED_BY_DA` + DA con `apex.message.confirm`.
- **Crear un IR programáticamente necesita 4 piezas**: región (`NATIVE_IR`), worksheet, worksheet columns y
  default report (`APXWS_DEFAULT`). Si falta una, `ORA-01403` al renderizar.
- **`create_page` sobre un id existente no falla**: verificá que el número esté libre antes.
- **Nunca condicionar el proceso *Form - Initialization*** (aplica los defaults de todos los items).
- **Nunca cambiar `source_type` de `REGION_SOURCE_COLUMN` a `STATIC`/`EXPRESSION`** para "meter un default":
  rompe el mapeo item↔columna y el Page Designer muestra `Column (Error) … (Invalid)`.
- **Defaults de fecha**: `TRUNC(SYSDATE)` o `SYSDATE`, nunca `to_date(sysdate, 'DD/MM/YYYY')`.

## Interactive Report: el encabezado fijo y los plugins

El IR tiene **Fixed Header = PAGE por defecto**. Con un plugin de agrupación de columnas del IR, el `thead`
clonado pasa a medir **dos filas** pero el cuerpo se corre sólo una → **la primera fila queda tapada después de
cada refresco**. Síntoma engañoso: el paginador dice "1 - N" y se ve una fila menos. Solución:
`p_fixed_header => 'NONE'` en `create_worksheet`.

## Dynamic Actions: lo que no se puede y cómo se resuelve

- `wwv_flow_api` **sólo expone `create_page_da_action`**: llamarla con el id de una acción existente **no falla y
  no cambia nada**. No hay `update` ni `remove`.
- Si el esquema de trabajo **no ve** `APEX_200200.WWV_FLOW_*` (ORA-00942), tampoco hay `UPDATE` directo.
- **"Items to Submit" es la trampa clásica**: si el PL/SQL del DA lee `:P_X` pero la lista dice `:P_Y`, el item
  llega **NULL** (más aún si es no persistente) y el DA guarda vacío sin error. Es de los bugs que más se repiten.
- Los DA que escriben una colección deben **guardarse contra un `SEQ_ID` válido**: si el item está vacío o la
  colección se recreó, `update_member_attribute` tira `ORA-20103` (y las cascadas de LOVs lo disparan solas al
  cambiar un filtro). Guardá la condición: colección existe **y** seq no nulo **y** seq dentro del rango.
- **Cascadas de LOVs**: al cambiar el padre, APEX limpia el hijo y eso dispara `change` → corre el DA del hijo.
  Abrir un popup con `setValue` también lo dispara: usar el tercer parámetro (`setValue(v, null, true)`) para
  suprimirlo cuando sólo estás fijando contexto.

## Corregir una página existente: re-import server-side

Es la vía oficial (la que usa el propio APEX al importar) y la única disponible para DA, IR, JS y LOVs:

1. `apex_export.get_application(<id de la aplicación>, p_components => apex_t_varchar2('PAGE:<n>'))` → CLOB del
   export actual.
2. Aplicar reemplazos **validando el conteo de ocurrencias**; abortar si no coincide. Usar `dbms_lob.copy` para
   cortar y pegar (`dbms_lob.substr` trunca a 32.767).
3. **Dry-run**: el mismo bloque terminando en `raise_application_error` con la longitud resultante, para
   compararla con la del export modificado local.
4. Ejecutar: quitar líneas de SQL*Plus (`prompt`, `set`, `whenever`, `/`), envolver en
   `begin … exception when others then rollback; raise; end;` y `execute immediate`.
5. **Verificar re-exportando y haciendo `diff`** contra el esperado.

Diferencias inocuas al comparar exports: `Exported By`, el orden de algunos atributos,
`p_report_list_mode=>'TABS'` que agrega `create_worksheet` por defecto, y la copia embebida de las **LOVs
compartidas** (cada ambiente trae su propia definición).

**Guardá siempre el export previo** antes de importar. Se pierden los reportes IR privados de los usuarios.

## Leer cosas grandes sin quemar contexto

`apex_export` dentro de un `WITH FUNCTION` + `CONNECT BY` en trozos de 3000 caracteres: el resultado grande lo
guarda el MCP en un archivo y se procesa desde ahí. Sirve para exports de página, de componentes
(`LOV:<id>`, `AUTHORIZATION:<id>` — que el MCP no expone) y para búsquedas sobre todas las páginas.

## Seguridad

Los esquemas de autorización, su convención de nombres y el paquete que los genera **son del perfil** (sección
Seguridad). Lo que vale en general:

- Si el generador de permisos filtra por el **tipo de programa** (p. ej. sólo los marcados como APEX), un programa
  que quedó con el tipo de Forms/Reports no da acceso a nadie aunque el esquema exista.
- La descripción del programa APEX suele ser la **única** relación con el programa Forms: respetar la convención
  del perfil.
- Los botones de alta/edición/baja dependen además de los permisos por rol de la tabla de programas del perfil.
- Proteger los `ON_DEMAND` es obligatorio: se invocan por URL aunque el botón esté oculto.
- El generador puede asignar a los `ON_DEMAND` cuyo nombre suena a DML (GUARDAR, ANULAR, ELIMINAR, AGREGAR,
  IMPRIMIR…) el esquema de botón y al resto el de menú; el resumen que informa puede no contar los primeros: no
  es que falten.
- El mensaje de salida de un generador así trae un resumen aunque todo salga bien; no hacer `raise` con él
  (deshace lo generado).
- **Cada re-import de una página borra sus `required_role` y esquemas**: volver a correr el generador sobre esa
  página al final (el recorrido automático no ve las páginas abiertas con `apex_page.get_url` dentro de procesos).
  Los permisos se cargan al **login**: una sesión abierta antes de crear el programa recibe «Privilegios
  insuficientes».

## IR y File Browse

- IR con máscara `DOWNLOAD:TABLA:BLOB:PK...`: la PK tiene que venir en el query **con su nombre real**. Si se la
  aliasa (p. ej. `id_adjunto as id`), el IR anda con 0 filas y con filas muestra "No se ha encontrado
  ningún dato" (ORA-01403).
- File Browse 20.2 con `accept`: el navegador descarta lo que no coincide (files.length = 0). Validar igual en el
  servidor.

## Páginas que se hablan entre sí, Ajax, IR y miles

- **Storage = Per Request (`p_is_persistent=>'N'`) → el item no existe para OTRA página ni para un Ajax posterior.**
  Todo item que otra página lea (`:P_MONTO` de una página hija leído desde otra) tiene que ser Per Session. Síntomas:
  default en 0, callback que devuelve `{}`, validación que "pasa" en silencio. Un item **sin región** nunca calcula su
  default (usar `PLSQL_EXPRESSION`). Revisar `grep p_is_persistent` en el export al auditar páginas hijas.
- **`apex.server.process` manda a `error()` todo JSON con clave `"error"`** (`textStatus==='APEX'`, mensaje en el 3.er
  parámetro). Probar el callback con `fetch` para ver la respuesta cruda antes de culpar al servidor.
- **`apex_page.get_url` dentro de un modal** devuelve `javascript:apex.navigation.dialog.close(...)`; para
  `window.open` usar `p_plain_url => TRUE`. Y no pasar textos libres (concepto con `/`) por URL `f?p=`: se escapan y
  corren los valores.
- **El IR guarda las columnas por sesión**: tras re-importar, probar con una sesión **nueva**; avisar al usuario que se
  reconecte. `p_report_columns` lleva **nombres de columna**.
- **La máscara numérica solo formatea al renderizar.** Separador en vivo: DA `change` + `apex.locale.formatNumber(n, mask).trim()`
  con `setValue(v, null, true)`. No poner máscara en items que alimentan `TO_NUMBER` ni formatear con `TO_CHAR` lo que
  viaja por URL a otro item numérico (ORA-01722 con NLS `',.'`).
- **Un default nuevo en un Form Region** (p. ej. un proveedor = 1) puede **activar condiciones** que dependían de que el
  item estuviera vacío (aparecía un botón en el alta): buscar las referencias al item antes de defaultearlo y probar
  que el default **no pisa** un registro existente (abrir uno de otra sucursal/proveedor).
- **Corrección masiva de una página**: conviene armar una pequeña librería propia (generadores de bloques + comparador
  contra la página viva). Cada ronda parte del export **vivo**; el MCP corta cada resultado en 200 K caracteres
  (volcar en tandas) y `STANDARD_HASH` no existe en PL/SQL.
- **Probar el pago/DML de punta a punta con datos propios** y mirar la base: en el ambiente de desarrollo los datos
  copiados de producción pueden solaparse (series de cheques, por ejemplo) y dar duplicados que no son bug del código.

## Consolas con diálogos anidados y callbacks

- **`JSON_VALUE` no es función PL/SQL en 12.1** (PLS-00306): un proceso `ON_DEMAND` con error de compilación devuelve **HTTP 200 vacío**.
  Leer el JSON con `select json_value(v, '$.ruta'), … into … from dual` (ruta literal). Para ver el cuerpo crudo:
  `apex.server.process(…, {dataType: 'text'})`.
- **`apex_page.get_url` se calcula al renderizar la página padre**: si el diálogo destino todavía no existe devuelve un
  `dialog.close(true, …)` genérico y la modal sale "standalone". Crear la hija y **reabrir** el padre antes de sospechar del patrón.
- **Cierre de diálogos:** `NATIVE_DIALOG_CANCEL` y la X **no** disparan `apexafterclosedialog` en el padre; `apex.navigation.dialog.close(true)`
  sí. Para resincronizar al volver: DA (`JQUERY_SELECTOR` `body`, evento `apexafterclosedialog`) → proceso `AJAX_ESTADO`. Para que el hijo le pida al
  padre abrir otro diálogo (p. ej. al generar un documento), dejar un id en un item de sesión (`apex_util.set_session_state`), cerrar con `close(true)` y que el
  padre lo lea y lo limpie en el `AJAX_ESTADO`.
- **El `id` HTML de un botón es `B<id>`**, no su nombre: para tocarlo por JS, `p_button_static_id`. ☑/☐ salen "¿" (base no Unicode): columna oculta +
  `<span class="fa fa-check-square-o">`.
- **Export oficial a disco por el MCP:** tabla temporal (crearla en un `execute` aparte) llena desde `apex_export` en trozos de 2.500 chars;
  `oracle_query` con **`format: json`** (en markdown las celdas salen truncadas). Lo grande se guarda en un archivo con **tope de 200 K chars que corta sin
  error**: partir por páginas, reconstruir con Python `-I` y comprobar que la longitud de cada página = `sum(length(chunk))`. No sirven los scripts
  `wwv_flow_api` de la transcripción: no traen los parches posteriores.
- **`NOT IN (select …)` sobre tablas grandes** (copiado del Forms) puede tardar minutos; `EXISTS`/`NOT EXISTS` equivalente cuando la columna no admite
  nulos (medir antes/después: 90 s → < 1 s con el mismo resultado). Si el original es lento por diseño, se reporta, no se "arregla" en la migración.

## Réplica exacta, parches por re-import y colecciones

- **Parchear una página = export → `replace` de un fragmento único → re-import.** `apex_export.get_application(p_components => 'PAGE:n')`; quitar los
  CR; partir por `\n/\n`; recortar cada bloque hasta el primer `begin`; `execute immediate`. Un `replace` cuyo fragmento no aparece **no falla**: comprobar
  siempre que cambió (`instr` antes y después) y, tras el parche, **leer el export** (un `swap` entre marcadores que conserva el marcador final duplicó un
  `elsif` en un proceso previo a la acción). Cada bloque del runner va en **un solo** `oracle_execute` (el estado de `import_begin` es de sesión); literales `q'~…~'` < 32 K,
  concatenar con `c := c || q'~…~'`.
- **Mantener el estado del Forms en el servidor, no en el cliente.** Variables de bloque / parámetros del Forms (total acumulado, acumuladores de la
  planilla, "id marcado", parámetros XML de entrada) van a items ocultos de sesión o a una colección de estado que escriben los procesos
  `ON_DEMAND`; el JS solo pinta lo que el servidor devuelve. Asignar un item por código **no dispara** el `WHEN-CHECKBOX-CHANGED` (en Forms tampoco dispara
  el WCC de un `:=`): el Marcar todo que "no recalcula" es el comportamiento original.
- **Colecciones con nombre fijo que leen procedures compartidos**: respetar nombre y columnas
  (`n001`, `c001`…) del contrato de la vista que las consume. Si el procedure lee una tabla por `SYS_CONTEXT('USERENV','SESSIONID')` y ORDS/APEX abre otra sesión de base por
  pedido, copiar las filas a la colección y vaciar la tabla **en el mismo pedido**.
- **Dos AJAX concurrentes sobre la misma colección** → `WWV_FLOW_COLLECTION_MEMBERS_PK`: pasa cuando un click llega mientras la consulta lenta del anterior sigue
  corriendo (doble click). No es bug del código; deshabilitar el botón mientras corre sería agregar un control que el Forms no tiene.
- **`TYPE` del body de un package va antes de cualquier subprograma** (`PLS-00103` si va después). `apex_collection.update_member_attribute` con un numérico
  posicional es ambiguo: usar `p_number_value =>`.
- **Probar la paridad de un SQL del Forms**: correr el texto literal y el propio y hacer `MINUS` en los dos sentidos (> 0 filas = diferencia). Si el literal
  es una consulta pesada (`IN (select …)` sin correlacionar sobre tablas grandes) puede no terminar por el MCP: poner **siempre** `fetch first` / pruebas con
  pocos ids, y si hay que cortar, `alter system kill session` (`TaskStop` no cancela la sesión de la base; el `kill` puede dar `ORA-00031` y reconectar solo).
- **Los ids de 18 dígitos que devuelve el MCP salen redondeados** (JSON numérico: los últimos dígitos cambian). Para anotar el id de un esquema,
  página o componente: `to_char(id)` en la consulta, o leerlo del export (`wwv_flow_api.id(…)`).
- **El MCP puede arrancar conectado a un ambiente que no es el de trabajo.** Antes de cualquier DDL/DML, `oracle_connect` al alias del ambiente de
  desarrollo que fije el perfil y verificar el host (`SERVER_HOST`).
- **El clasificador puede denegar `apex_get_page_source`** ("Modify Shared Resources"): no buscar el mismo resultado por otro camino de escritura; el
  export de `apex_export` por consulta y el navegador alcanzan para verificar.

## Parche de una página por re-import: más trampas

- **`REPLACE(clob, clob, clob)` en PL/SQL 12.1 corrompe el texto sin error** (el reemplazo quedó truncado y con restos del original dentro de un proceso). Para
  cortar/pegar usar `dbms_lob.instr` + `dbms_lob.copy` + `writeappend` (helper `splice(old,new,esperados)` que antes valida el conteo). Después del import, re-exportar y
  comparar contra el esperado como **multiconjunto de líneas** (el export reordena atributos; las diferencias legítimas son `p_required_role`/`p_security_scheme`).
- **Método «ops»** para no reenviar 80 KB: `difflib` línea a línea entre el export vivo y el esperado → bloque PL/SQL con `k(offset,len)` (copia del vivo con
  `dbms_lob.copy`) y `t(q'~…~')` (texto nuevo, < 28.000 chars por literal). Validar largo del vivo, largo del resultado y conteos de `create_*` antes de ejecutar; ejecutar
  bloque a bloque (`\n/\n`, recortar hasta `begin`) con `execute immediate <clob>`.
- **Una función local del bloque no se puede llamar dentro de un `SELECT`** (PLS-00231): el proceso On Demand devuelve **HTTP 200 vacío**. Probar cada callback tocado con
  `apex.server.process(n, {x01:…}, {dataType:'text'})` desde el navegador antes de dar nada por hecho.
- **Condiciones de DA con items de otra página** (items `P<otra página>_*` copiados de otro formulario): la DA nunca dispara y no hay error. Buscar en el export `P<otra página>_` al auditar.
- **`setValue("")` dispara `change`** y con él las DA encadenadas; para resetear campos usar `setValue("", null, true)`.
- Región **Classic Report** 20.2 = `create_report_region` + `create_report_columns` (`p_display_as=>'HIDDEN'` para columnas de ordenamiento); `p_parent_plug_id` la cuelga de un Inline Dialog.
- **Los botones y los items de una región comparten el orden por secuencia**: dejar `item_sequence` y `button_sequence` consistentes con el orden visual.
- `jasper_run_report_sync` del MCP puede dar 401; la prueba válida es el botón de la página (`200 application/pdf`), bajando el PDF con `fetch` desde el navegador.

## Items, DA y PL/SQL: gotchas generales

**APEX**
- **`p_item_css_classes` (p. ej. `apex_disabled`) cae en el contenedor `#<ITEM>_CONTAINER`, no en el `<input>`.** Un DA que hace `removeClass` sobre el input no la saca nunca;
  aplicar/quitar la clase y el `tabindex` sobre el contenedor.
- **Un DA con `execute_on_page_init='N'` no corre al abrir el registro.** Si habilitar/deshabilitar depende del valor cargado, las acciones necesitan `'Y'` (y que no pisen datos: ver patrones-ui-form 7.3).
- **Los items que un DA llena desde la etiqueta de un LOV llegan con entidades HTML** (`&#xF3;`): aplicar `utl_i18n.unescape_reference(:PXX_ITEM)` antes de guardar.
- **Un item numérico con máscara de coma decimal (`990D00`) no acepta el punto** en navegadores `es`: DA que reemplace `.` por `,` en el valor.
- **Los items deshabilitados por DA no viajan en el submit** (llegan NULL): habilitarlos en el DA de Guardar antes del `SUBMIT_PAGE`.

**PL/SQL / Oracle 12.1**
- **Errores de constraint → mensaje de negocio**: capturar `ORA-02290/02291/01400/01407/00001/12899/01438` en el proceso Guardar y traducirlos con una función del package que devuelve NULL si no conoce
  el error (entonces se re-lanza el original). El Forms mostraba mensajes propios; el ORA crudo no sirve al usuario.
- **Declarar las variables antes de las funciones/procedimientos anidados** (PLS-00103) y **nombres de objeto de hasta 30 caracteres** en 12.1 (ORA-00972).
- **Literales `q'[...]'`** para armar código dentro de strings: evitan el doble escape de comillas.
