# Patrones de UI para páginas migradas

Salieron de rehacer el listado y la ficha de un maestro con detalle (un contrato de cliente). Se aplican a
cualquier formulario con *listado + ficha*. Las páginas de referencia vivas (listado IR + filtros, ficha como
página con navegación y botonera flotante, botonera original) **las fija el perfil** (secciones «Estilo visual» y
«Páginas de referencia»): se copian, no se inventan. Los valores exactos de CSS, JS y clases salen del perfil
(sección Estilo visual); acá se describe el patrón y por qué.

## 1. Listado = IR + región de filtros (nunca IG)
- Región **Filtros**: `Blank with Attributes` + clase de marco primario del perfil + `<h5>` en `p_plug_source`
  (`attribute_02 => 'HTML'`). Items con field template floating, grid de 12 (`p_begin_on_new_line` + `p_colspan`),
  botones **FILTRAR** (submit) y **LIMPIAR** dentro de la misma región.
- Botón en posición `BODY` de una región Blank: sin `p_grid_new_column => 'Y'` se apila en su propia fila.
- El IR **abre vacío**; FILTRAR llena una **colección** llamando al package de lectura que el Forms ya usaba
  (el `sp_listar` del original → una colección de lista). El IR hace `join` de la colección contra la tabla viva,
  así refresca con datos actuales al volver de la ficha (con la foto de la colección quedaría desactualizado).
- Tope de filas: lo fija el package (p. ej. 100 con filtro, 30 con sólo palabra clave). Declararlo, no ocultarlo.
- Resaltados de fila (Cancelados/Inactivos…) = `create_worksheet_condition` tipo `HIGHLIGHT`.
- Lápiz de edición = `p_detail_link` del worksheet hacia la ficha con `CR,<página>`.
- **Probar cada filtro** contra la base (conteo SQL = filas del IR) y el LOV de cada filtro contra la columna que el
  package compara (ejemplo real: el LOV Estado devolvía el id y el package comparaba texto → 0 filas siempre).

## 2. Ficha = página normal, no modal
- Quitar `p_page_mode => MODAL` y `p_dialog_*`; botón «Volver al listado» (`REDIRECT_PAGE` a la página del listado,
  **sin** clear cache para conservar filtros y colección); `p_warn_on_unsaved_changes => 'N'`.
- Título dinámico: región Breadcrumb con nombre `&PXXX_TITULO.`, ítem oculto cargado en un proceso `BEFORE_HEADER`
  (`SELECT … INTO :PXXX_TITULO`; **PL/SQL no admite un `SELECT` dentro de una expresión**).
- Mismo `required_role` que el listado.

## 3. Navegar entre registros del listado filtrado
- Proceso `BEFORE_HEADER` con `LAG/LEAD/ROW_NUMBER/COUNT` **sobre la colección** ordenado como el IR (id DESC):
  deja `PXXX_ID_ANTERIOR`, `PXXX_ID_SIGUIENTE` y agrega « (n de N)» al título. Sin registro en la colección → sin botones.
- Botones **Anterior / Siguiente** `REDIRECT_URL` a la misma página con `CR,<pág>:PXXX_ID:&PXXX_ID_ANTERIOR.`,
  condición `ITEM_IS_NOT_NULL`. Van **dentro de la botonera flotante** (posiciones `REGION_TEMPLATE_PREVIOUS` /
  `NEXT`), no arriba en el título (quedaban chicos y fuera de vista).
- Las páginas con protección de URL `C` exigen checksum: abrirlas siempre por el enlace del listado, no por URL a mano.

## 4. Regiones, tabs y marcos
- Cada sección de la ficha = región con marco (clase de marco primario del perfil, o la de fondo gris para datos
  derivados) + `p_plug_header => '<h5>Título</h5>'`. Items sueltos sin marco = no migrado.
- Un acordeón *Collapsible* que arranca cerrado se ve como una barra vacía: pasarlo a `Blank with Attributes`
  siempre abierto con `<h5>`.
- Tabs (Region Display Selector): el CSS de pestañas canónico lo da el perfil (pestaña activa con el color primario).
- **Hueco en blanco bajo la pestaña corta**: el selector fija inline `min-height` = pestaña más alta. Corregir
  anulando ese `min-height` sobre `.t-TabsRegion-items` (con `!important`, porque el estilo inline gana) en el
  Inline CSS de la página.

## 5. Botonera flotante
Patrón (el código exacto lo da el perfil; se copia de la página de referencia, no se reescribe):
- Región de botones con un **static id propio** y el marco del perfil, **al final** de la página (secuencia alta).
  Botones dentro: Volver / Anterior | **badge de estado** | Siguiente / Guardar.
- **Región fija al pie**: `position: fixed` con `bottom` y `right` chicos, `z-index` alto y `left` igual al ancho
  del menú lateral para **respetar el menú**; el `left` cambia según el menú esté expandido o colapsado (clases
  `js-navExpanded` / `js-navCollapsed` en el `body`), con `transition` sobre `left`/`bottom`, más un ajuste para
  tablet y otro para móvil (`left` mínimo). No inventar offsets: se copian de la referencia.
- **JS que mide y flota**: quita la clase de fijado para medir la posición natural, flota mientras
  `getBoundingClientRect().top > innerHeight − margen` y se acomoda en su lugar al llegar al final de la página;
  escucha scroll, resize, cambios de clase del `body`, `apexafterrefresh` y `apexafterclosedialog`.
  **No** reemplazar por cálculos propios del margen (probado: `getBoundingClientRect().right` del menú miente durante
  la animación y la barra queda tapada).
- Altura baja: poco padding vertical, botones en una fila (`display:flex` en `.t-ButtonRegion-wrap`, la columna
  central `flex: 1 1 auto` para que el badge ocupe el espacio libre).

## 6. Badge de estado en la botonera
- Ítem **Display Only** (`P…_ESTADO`) en la región de botones, label oculto; un DA «Setear color de estado» le pone al
  `span#P…_ESTADO_DISPLAY` la **clase = valor** del estado (ACTIVO, INACTIVO…).
- CSS: pastilla (`border-radius:999px`), `display:block; width:100%` dentro de la columna central que crece (ocupa **todo
  el espacio libre entre los botones**); un color de fondo por estado (verde para activo, rojo para inactivo, gris
  para cancelado, naranja para pendiente, gris oscuro para anulado, como ejemplo; los colores reales son del
  perfil). Estilar **solo** `#…_DISPLAY`: el `span` genérico alcanza también al
  `…_error_placeholder` y aparece una barra de color debajo. Ocultar ese placeholder.
- Sólo se actualiza al guardar/recargar, no al cambiar el selector (igual que el original).

## 7. Guardado: trampas que PIERDEN datos (revisar SIEMPRE en una ficha migrada)
1. **Items ocultos no reasignados** en el proceso Guardar: cada guardado deja en NULL las columnas que el `UPDATE` del
   package escribe pero la página no manda (ejemplo real: media docena de columnas auxiliares de montos y
   contribuciones de la ficha). Comparar **columna por columna** `rc.<col> :=` de la página contra el
   `SET` del `UPDATE` del package y contra el `SELECT … INTO` del Initialize.
2. **Items `disabled` no viajan en el submit**: una sección deshabilitada por DA (`NATIVE_DISABLE`) se guarda como NULL.
   Habilitarlos con `apex.item(n).enable()` en una acción del DA Guardar **antes** del `SUBMIT_PAGE`.
3. **DAs con `execute_on_page_init = 'Y'` que ponen NULL/valores fijos** (`NATIVE_SET_VALUE`) pisan el registro al
   *abrirlo*. Pasarlas a `'N'` (siguen actuando al cambiar el campo).
4. `UPDATE` de package por fila completa (`SET ROW`, o columnas de más): que no pise lo que la página no edita
   (observaciones, ubicaciones, indicadores de factura web, etc.).
5. **Triggers de tabla que se disparan con un `UPDATE` sin cambios**: un trigger de la tabla de direcciones de la ficha
   pisaba en el registro padre el barrio, la ciudad y el teléfono de facturación con los de la dirección en **cada**
   `UPDATE` de esa tabla. Si el proceso de la página llama a un `sp_guardar_*` que actualiza siempre, un «Guardar sin
   cambios» destruye datos del padre. Revisar `user_triggers` de **todas** las tablas que escribe el guardado y hacer
   que el `UPDATE` solo ocurra si algo cambió (comparación null-safe columna por columna contra la fila guardada, sin
   distinguir mayúsculas si el package las fuerza).
6. **Defaults de item sobre registros existentes**: un `p_item_default` estático se aplica también cuando el registro trae NULL
   (ejemplo real: un porcentaje por defecto en 100 bloqueaba cientos de registros por un `CHECK`). Para campos que el Forms
   solo defaultea en NEW usar `p_item_default_type=>'EXPRESSION'` con `CASE WHEN :PXX_ID IS NULL THEN … END`.
7. **Prueba obligatoria**: respaldo de la fila en tabla → abrir y **Guardar sin tocar nada** → diff de **todas** las
   columnas contra el respaldo (`dbms_xmlgen.getxmltype` + `XMLTABLE` + `FULL OUTER JOIN`; 0 diferencias) → editar
   los campos señalados y verificar en la base → restaurar y borrar el respaldo al cerrar.

## 8. Re-import de una página: cómo NO perder componentes
- Export → `replace` con **fragmento único verificado** (`cnt(...) = 1`) → ejecutar bloque por bloque.
- **Un bloque exportado puede superar 32.767 caracteres**: `dbms_lob.substr` trunca en silencio y se pierde la cola
  (ejemplo real: 7 procesos y 12 DA perdidos en una ficha, sin ningún error). Copiar con `dbms_lob.createtemporary` + `dbms_lob.copy` y
  `execute immediate <clob>`; no filtrar bloques por `instr(…,'end;')` en minúscula.
- **Antes de ejecutar, contar** `create_page_process`, `create_page_da_event`, `create_page_da_action`,
  `create_page_item`, `create_page_button` y abortar si no coinciden con lo esperado. Guardar siempre el export previo
  en una carpeta de respaldo del proyecto (de ahí se reconstruye lo perdido).
- Un componente nuevo se agrega como bloque `begin … end;` insertado en el export (nunca `INSERT` a `WWV_FLOW_*`).
- Variables locales: nombres de tabla ≤ 30 caracteres en 12.1; si el esquema de trabajo no ve `APEX_200200.WWV_FLOW_*`,
  no hay alternativa de lectura directa: usar `apex_export`.

## 9. Listados con filtros: grilla de 12
- Agregar un item a la región de filtros puede empujar los botones a la columna 13 y la **página entera** muestra «El componente
  X no se puede presentar… columna 13» (no hay error en consola). Contar los `p_colspan` de la fila de los botones; si no entra,
  el item nuevo va en una fila propia (`p_begin_on_new_line=>'Y'`) junto a FILTRAR / LIMPIAR.

## 10. Pruebas con Playwright en estas fichas
- Un LOV modal de plugin (como el que fije el perfil) no es un `<select>`: no tiene `<option>`; setear el valor con `apex.item().setValue()` y
  confirmar con el botón; los `apex.message.confirm` se apilan si se hace clic dos veces (usar `.last()`).
- Los DA que llaman a funciones lentas (p. ej. una que busca el saldo de un cliente) dejan `apex_wait_overlay` y todo clic falla por timeout: para
  probar el resto, setear el valor con `document.getElementById(id).value = …` (no dispara el `change` de APEX) y declarar lo no probado.
- Un resultado de `oracle_query` de más de ~200.000 caracteres se **trunca** en el archivo guardado (JSON roto): exportar páginas
  grandes en tandas de ≤ 30 chunks de 3.000 caracteres y rearmar con un script que verifique que no falten números de chunk.

## 11. Ficha pasada de modal a página (lecciones del 6201, 7/11/2026)
- **Las URL de navegación se arman en el servidor**: `&APP_ID.`/`&SESSION.` no se sustituyen en el JS de página y una `f?p=` armada en el cliente no se traduce a URL amigable (rompe los modales y a veces da login). `apex_page.get_url(...)` en hidden items (`PXXX_URL_ANTERIOR/SIGUIENTE/LISTADO`) y JS `apex.navigation.redirect($v("PXXX_URL_..."))`. Los botones `REDIRECT_URL` con `javascript:fn('A')` sirven para pasar por una confirmación (detalle en memoria sin grabar).
- **Botón `SUBMIT` + DA Confirm no frena el submit** (el POST sale antes de responder): botón `DEFINED_BY_DA` y DA con Confirm -> Submit Page (como el «Aplicar promoción» de la 991). Probar con la lista de `request` (`page.on('request')`) que Cancelar no envía nada.
- Al sacar el modal hay que reemplazar el `NATIVE_CLOSE_WINDOW` por branches (`REQUEST_EQUALS_CONDITION`) que vuelvan a la misma ficha con `&success_msg=#SUCCESS_MSG#` (Guardar/Anular/Crear) o al listado (Eliminar) y agregar mensajes de éxito al proceso.
- Una ficha sobre una **colección de lista** (IR del listado) debe conservar el comportamiento previo del listado (si abría con datos, la colección se arma en `BEFORE_HEADER` cuando no existe; FILTRAR/LIMPIAR solo la borran) y declarar el tope.
- El rediseño de otra migración puede vivir solo en un ambiente (la 991 de DEVNEW era la vieja): estudiar la referencia en el ambiente donde está y en su export final.

## 12. Badges de estado dentro de la botonera flotante (6201, 7/11/2026)
- Si el estado/impreso/asentado son ítems *Display Only* dentro de la región de botones, cada contenedor `t-Form-fieldContainer--hiddenLabel` conserva un `.t-Form-labelContainer--hiddenLabel` con `min-height:32px` aunque el rótulo esté oculto: el contenedor mide 76 px (32 + 44) y el badge queda ~16 px más abajo que los botones. Un `display:none` sin `!important` no alcanza (el tema lo pisa). Arreglo en el CSS de la página: `#regionBotones .t-Form-fieldContainer { min-height:0 !important }` y `#regionBotones .t-Form-labelContainer, #regionBotones .t-Form-labelContainer--hiddenLabel { display:none !important; min-height:0 !important }`.
- **Se verifica midiendo, no mirando**: `getBoundingClientRect()` de botones y badges, centro vertical igual (±1 px), con menú colapsado y expandido, a 1366 y 1920, con un registro anulado y con uno nuevo (sin badges). Una captura no alcanza para ver 16 px.
- Compará siempre contra la ficha de referencia en el mismo ambiente: su badge ocupa la misma fila y está centrado con los botones.
