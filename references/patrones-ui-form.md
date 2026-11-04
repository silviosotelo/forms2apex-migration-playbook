# Patrones de UI para páginas migradas (rediseño 6001, 03/11/2026)

Salieron de rehacer el listado y la ficha de **Contrato Cliente** (páginas 977 / 991, DESA02). Se aplican a
cualquier formulario con *listado + ficha*. Referencias vivas: **977** (IR + filtros), **991** (ficha como página con
navegación y botonera flotante), **1470** (botonera flotante original, DEVNEW).

## 1. Listado = IR + región de filtros (nunca IG)
- Región **Filtros**: `Blank with Attributes` + `region-con-bordes borde-primario` + `<h5>` en `p_plug_source`
  (`attribute_02 => 'HTML'`). Items con field template floating, grid de 12 (`p_begin_on_new_line` + `p_colspan`),
  botones **FILTRAR** (submit) y **LIMPIAR** dentro de la misma región.
- Botón en posición `BODY` de una región Blank: sin `p_grid_new_column => 'Y'` se apila en su propia fila.
- El IR **abre vacío**; FILTRAR llena una **colección** llamando al package de lectura que el Forms ya usaba
  (`sp_listar` → `COL_LISTA_…`). El IR hace `join` de la colección contra la tabla viva, así refresca con datos
  actuales al volver de la ficha (con la foto de la colección quedaría desactualizado).
- Tope de filas: lo fija el package (acá 100 con filtro, 30 con sólo palabra clave). Declararlo, no ocultarlo.
- Resaltados de fila (Cancelados/Inactivos…) = `create_worksheet_condition` tipo `HIGHLIGHT`.
- Lápiz de edición = `p_detail_link` del worksheet hacia la ficha con `CR,<página>`.
- **Probar cada filtro** contra la base (conteo SQL = filas del IR) y el LOV de cada filtro contra la columna que el
  package compara (en el 6001 el LOV Estado devolvía el id y el package comparaba texto: 0 filas siempre).

## 2. Ficha = página normal, no modal
- Quitar `p_page_mode => MODAL` y `p_dialog_*`; botón «Volver al listado» (`REDIRECT_PAGE` a la 977, **sin** clear
  cache para conservar filtros y colección); `p_warn_on_unsaved_changes => 'N'`.
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
- Cada sección de la ficha = región con marco: `region-con-bordes borde-primario` (o `fondo-gris` para datos
  derivados) + `p_plug_header => '<h5>Título</h5>'`. Items sueltos sin marco = no migrado.
- Un acordeón *Collapsible* que arranca cerrado se ve como una barra vacía: pasarlo a `Blank with Attributes`
  siempre abierto con `<h5>`.
- Tabs (Region Display Selector): CSS canónico del playbook (pestaña activa violeta `#522583`).
- **Hueco en blanco bajo la pestaña corta**: el selector fija inline `min-height` = pestaña más alta. Corregir con
  `.t-TabsRegion-items { min-height: 0 !important; }` en el Inline CSS de la página.

## 5. Botonera flotante (copia fiel de la 1470 / 1118)
- Región `Buttons` con **static id `regionBotones`** y clases `region-con-bordes borde-primario`, **al final** de la
  página (secuencia alta). Botones dentro: Volver / Anterior | **badge de estado** | Siguiente / Guardar.
- **CSS tal cual la 1470** (no inventar offsets): `#regionBotones.fixed-bottom { position: fixed; bottom: 20px;
  right: 16px; left: 64px; z-index: 999 !important; background: #e6f4f2; box-shadow …; transition: left …, bottom … }`,
  `body:not(.js-navCollapsed) #regionBotones.fixed-bottom { left: 295px }`, media mobile (`left:16px !important`) y
  tablet (`left:200px`). La clase del menú expandido es `js-navExpanded`; colapsado `js-navCollapsed`.
- **JS tal cual la 1470**: `SC.botoneraFlotante("regionBotones")` (`window.SC = window.SC || {}` si la página no la
  define): quita `fixed-bottom` para medir, flota mientras `getBoundingClientRect().top > innerHeight − 20`, se acomoda
  al llegar; escucha scroll, resize, cambios de clase del `body`, `apexafterrefresh`, `apexafterclosedialog`.
  **No** reemplazar por cálculos propios del margen (probado: `getBoundingClientRect().right` del menú miente durante
  la animación y la barra queda tapada).
- Altura baja: `padding: 6px 12px`, botones en una fila (`display:flex` en `.t-ButtonRegion-wrap`, la columna central
  `flex: 1 1 auto`).

## 6. Badge de estado en la botonera
- Ítem **Display Only** (`P…_ESTADO`) en la región de botones, label oculto; el DA «Setear color de estado» le pone al
  `span#P…_ESTADO_DISPLAY` la clase = valor (ACTIVO, INACTIVO…).
- CSS: pastilla `border-radius:999px`, `display:block; width:100%` dentro de la columna central que crece (ocupa **todo
  el espacio libre entre los botones**); colores por estado: ACTIVO `#2e7d32`, INACTIVO `#c62828`, CANCELADO `#6b7280`,
  PENDIENTE `#ef6c00`, ANULADO `#3b3b3b`. Estilar **solo** `#…_DISPLAY`: el `span` genérico alcanza también al
  `…_error_placeholder` y aparece una barra de color debajo. Ocultar ese placeholder.
- Sólo se actualiza al guardar/recargar, no al cambiar el selector (igual que el original).

## 7. Guardado: trampas que PIERDEN datos (revisar SIEMPRE en una ficha migrada)
1. **Items ocultos no reasignados** en el proceso Guardar: cada guardado deja en NULL las columnas que el `UPDATE` del
   package escribe pero la página no manda (en el 6001: `monto_plus`, `visacion_plus`, `utilizacion_plus`,
   `contribucion`, `vta_adicional`, `id_prom2`…). Comparar **columna por columna** `rc.<col> :=` de la página contra el
   `SET` del `UPDATE` del package y contra el `SELECT … INTO` del Initialize.
2. **Items `disabled` no viajan en el submit**: una sección deshabilitada por DA (`NATIVE_DISABLE`) se guarda como NULL.
   Habilitarlos con `apex.item(n).enable()` en una acción del DA Guardar **antes** del `SUBMIT_PAGE`.
3. **DAs con `execute_on_page_init = 'Y'` que ponen NULL/valores fijos** (`NATIVE_SET_VALUE`) pisan el registro al
   *abrirlo*. Pasarlas a `'N'` (siguen actuando al cambiar el campo).
4. `UPDATE` de package por fila completa (`SET ROW`, o columnas de más): que no pise lo que la página no edita
   (`obs`, `*_ubicacion`, `*_fact_web`…).
5. **Triggers de tabla que se disparan con un `UPDATE` sin cambios** (6001): el trigger `ACTUALIZA_CONTRATO_DIRECCION` pisa
   `id_barrio`, `id_ciudad` y `factura_tel` del contrato con los de la dirección en **cada** `UPDATE` de `DIRECCIONES_CONTRATO`.
   Si el proceso de la página llama a un `sp_guardar_*` que actualiza siempre, un «Guardar sin cambios» destruye datos del padre.
   Revisar `user_triggers` de **todas** las tablas que escribe el guardado y hacer que el `UPDATE` solo ocurra si algo cambió
   (comparación null-safe columna por columna contra la fila guardada, sin distinguir mayúsculas si el package las fuerza).
6. **Defaults de item sobre registros existentes**: un `p_item_default` estático se aplica también cuando el registro trae NULL
   (en el 6001 `% a Facturar`=100 bloqueaba 838 contratos por un `CHECK`). Para campos que el Forms solo defaultea en NEW usar
   `p_item_default_type=>'EXPRESSION'` con `CASE WHEN :PXX_ID IS NULL THEN … END`.
7. **Prueba obligatoria**: respaldo de la fila en tabla → abrir y **Guardar sin tocar nada** → diff de **todas** las
   columnas contra el respaldo (`dbms_xmlgen.getxmltype` + `XMLTABLE` + `FULL OUTER JOIN`; 0 diferencias) → editar
   los campos señalados y verificar en la base → restaurar y borrar el respaldo al cerrar.

## 8. Re-import de una página: cómo NO perder componentes
- Export → `replace` con **fragmento único verificado** (`cnt(...) = 1`) → ejecutar bloque por bloque.
- **Un bloque exportado puede superar 32.767 caracteres**: `dbms_lob.substr` trunca en silencio y se pierde la cola
  (en la 991: 7 procesos y 12 DA, sin ningún error). Copiar con `dbms_lob.createtemporary` + `dbms_lob.copy` y
  `execute immediate <clob>`; no filtrar bloques por `instr(…,'end;')` en minúscula.
- **Antes de ejecutar, contar** `create_page_process`, `create_page_da_event`, `create_page_da_action`,
  `create_page_item`, `create_page_button` y abortar si no coinciden con lo esperado. Guardar siempre el export previo
  en `respaldo_pre_fix/` (de ahí se reconstruye lo perdido).
- Un componente nuevo se agrega como bloque `begin … end;` insertado en el export (nunca `INSERT` a `WWV_FLOW_*`).
- Variables locales: nombres de tabla ≤ 30 caracteres en 12.1; `ANAMNESIS` no ve `APEX_200200.WWV_FLOW_*`.

## 9. Listados con filtros: grilla de 12
- Agregar un item a la región de filtros puede empujar los botones a la columna 13 y la **página entera** muestra «El componente
  X no se puede presentar… columna 13» (no hay error en consola). Contar los `p_colspan` de la fila de los botones; si no entra,
  el item nuevo va en una fila propia (`p_begin_on_new_line=>'Y'`) junto a FILTRAR / LIMPIAR.

## 10. Pruebas con Playwright en estas fichas
- Un LOV modal (`PLUGIN_MHO.MODAL_LOV`) no es un `<select>`: no tiene `<option>`; setear el valor con `apex.item().setValue()` y
  confirmar con el botón; los `apex.message.confirm` se apilan si se hace clic dos veces (usar `.last()`).
- Los DA que llaman a funciones lentas (`buscar_saldo_cliente_ci`) dejan `apex_wait_overlay` y todo clic falla por timeout: para
  probar el resto, setear el valor con `document.getElementById(id).value = …` (no dispara el `change` de APEX) y declarar lo no probado.
- Un resultado de `oracle_query` de más de ~200.000 caracteres se **trunca** en el archivo guardado (JSON roto): exportar páginas
  grandes en tandas de ≤ 30 chunks de 3.000 caracteres y rearmar con un script que verifique que no falten números de chunk.
