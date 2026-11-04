# FASE 4 — Verificación: matriz, método y lo que no cuenta

## 0. Paso preventivo (antes de abrir el navegador)

**Grepear cada parámetro/item del Forms contra el package, la página y el JRXML.** Si un parámetro del form no
aparece en ninguno de los tres, es un bug seguro: quedó desconectado. Cuesta un minuto y ahorra una ronda entera
de QA.

Lo mismo con los **ítems condicionales**: listá del `.fmb` cada `SET_ITEM_PROPERTY`, `SHOW_VIEW`, `HIDE_VIEW`
(visible / enabled / navigable) y verificá que cada uno tenga su equivalente en la página (condición de item,
Dynamic Action o `apex_util.set_session_state`). Si el form tenía N comportamientos dinámicos y la página tiene
menos, esa lógica no se migró.

## 1. La matriz obligatoria

Antes de declarar terminado, cubrí estas filas y **escribí el resultado de cada una** en la auditoría.
Si una fila no se puede cubrir en el ambiente, se declara como no verificada; no se asume.

| Grupo | Qué probar |
|---|---|
| Camino principal | El flujo completo, de punta a punta, con datos reales |
| Variantes del negocio | Cada rama del `IF` del Forms: tipos de documento/contrato distintos, mismo origen vs distinto destino, con y sin grupo |
| Fechas | La rama "hoy o anterior" **y** la de fecha futura (suelen escribir en tablas distintas) |
| Montos y monedas | La moneda alternativa, aunque el ambiente no tenga datos (ver punto 3) |
| Volumen / agrupación | Más de un registro por grupo y más de un grupo en el mismo lote |
| Rechazos | **Un caso negativo por cada validación**: que bloquee es la prueba, que guarde no alcanza |
| Bloqueos del negocio | Deuda, estado inválido, permiso de parámetro, registro inexistente |
| Idempotencia | Volver a procesar lo ya procesado: ¿qué pasa? |
| Seguridad | Con un rol sin permiso: la página no abre y los `ON_DEMAND` no responden |
| Impresión | `200 application/pdf` en el Network tab y PDF comparado contra el original de `RWRUN60` |

Ejemplo real (una migración de cambio de categoría masivo): 8 caminos + 5 rechazos. Los que **más** bugs
revelaron fueron la fecha futura y el grupo beneficiario que no contemplaba la categoría de un integrante.

### El recorrido de QA, en orden

Cuando la pantalla ya está construida, recorrela como usuario final en este orden. Cada paso tiene su propia
forma de fallar:

1. **Discovery** — abrir la página, ver que carga sin error y con la autorización puesta.
2. **Items** — cada filtro: default correcto, LOV con datos, formato de fecha, obligatoriedad.
3. **Listado con datos** — que traiga filas reales y que las columnas muestren lo que dicen mostrar.
4. **Botones** — uno por uno, con click real. Que hagan algo **y** que ese algo se vea en la base.
5. **Casos borde** — sin datos, con un solo registro, con el filtro vacío, con valores extremos.
6. **Consola JS** — sin errores. Un `ReferenceError` en el onload aborta todo el resto en silencio.
7. **Visual** — comparar contra una página de referencia de la app (referencia, no molde) y contra el form.
8. **Performance** — que una consulta típica no tarde de más; si tarda, mirar el plan antes de entregar.
9. **Comparación contra el original** — el form o el reporte, con los **mismos parámetros**. Bloqueante.
10. **Diff paramétrico** — por cada filtro opcional, correr **dos veces** cambiando sólo ese filtro y exigir que
    el resultado **cambie** (dos PDFs con hash distinto, o dos conteos distintos). Si no cambia, ese parámetro
    no está conectado, aunque la pantalla no dé error. Bloqueante.

**"PASS con observaciones" no existe.** O pasa, o hay algo que corregir y volver a correr el ciclo completo.
(Lo que **no** es parte del pedido pero se descubre —defectos latentes, decisiones funcionales— va como *observación
declarada* en el informe con recomendación, no como un PASS ni escondido.)

**Pedidos de corrección con capturas (documento con anotaciones del usuario):** reproducir primero el estado actual en
el navegador, igual a la captura, y recién después tocar nada; muchas anotaciones comparten una causa raíz
(en un caso, "Monto 0" y "no trae la serie" eran el mismo item Per Request). Cada nota queda mapeada a su resolución y a la
evidencia (tabla nota → resolución → estado).

## 2. Método

**Navegador real, con clicks reales.** Disparar un botón con `elem.click()` desde `evaluate` **no ejecuta** las
acciones del Dynamic Action. Usar el click del MCP de navegador (evento "trusted").

**Nunca "verificar" un botón llamando a su función JS a mano.** En un caso, el DA de un modal ejecutaba
`this.triggeringElement` en lugar de la función `agregarFormaPago()`; la prueba "pasaba" porque llamaba a la función
directamente. **Si el click real no responde, eso es el bug**, no una limitación del navegador.

**Ledger antes/después.** Antes de procesar, guardá el estado de las tablas del circuito (filas por estado,
montos, fechas de egreso, contadores de cuotas, estado del contrato). Después, compará. Sin foto previa no hay
verificación, hay impresión.

**"No se ve" se mide en el DOM.** Un "desaparece el titular" era el encabezado fijo del IR tapando la
primera fila tras cada refresco (Fixed Header + plugin de agrupación de columnas). La pista estaba en el
paginador: decía "1 - 2" con una sola fila visible. Medí con `getBoundingClientRect` y confirmá con
`elementFromPoint` que la fila recibe el click; una captura no alcanza.

**Probá después de un refresco, no sólo en la carga.** Muchos bugs de UI sólo aparecen cuando el IR se
re-renderiza por un DA. Un contador de `apexafterrefresh` ayuda a ver cuántos refrescos dispara cada acción.

**Ciclo DML completo por cada camino, después de cualquier cambio de proceso.** Si reemplazaste el Form DML,
ningún `SAVE` anterior probó tu código: repetí alta, edición, borrado y **reabrí** para ver que persistió.

**Popup LOV y modales**: el buscador del Popup LOV se renderiza en el documento TOP aunque el item esté dentro de
un iframe, y queda un input viejo oculto en el DOM (filtrar por `offsetParent !== null` y tomar el último).
Los diálogos apilados dejan iframes viejos: usar siempre el último.

**Contabilidad**: probá el caso que SÍ genera asiento y el que NO debe generar ni fallar. Los `GEN_ASIENTO_*` son
idempotentes (sólo insertan en `NO_DATA_FOUND`) y hacen **COMMIT interno**.

**Si tocaste roles, relogueate**: la tabla de permisos del usuario se arma al login.

**Probá las escrituras con un usuario que los triggers no eximan.** Varios triggers del esquema tienen
`IF NVL(V('APP_USER'),USER) != '<usuario del esquema dueño>'` (por ejemplo el trigger de detalle de pagos de una
prepaga): con el usuario dueño del esquema el borrado "anda" y además le infla el saldo a la factura. Grepeá el
nombre del usuario dueño del esquema en los triggers de las tablas del circuito. Si sólo hay credenciales del
dueño para el navegador, cada escritura se prueba también por SQL con
`apex_session.create_session(p_app_id=><id_app>, p_page_id=>N, p_username=>'<usuario real>')` + package +
`rollback`, devolviendo el resultado con `raise_application_error`.

## 3. Cuando el ambiente no tiene el dato

El ambiente de desarrollo casi nunca tiene el caso raro. Dos caminos legítimos:

**a) Prueba sintética contra el package.** Abrí una sesión APEX desde PL/SQL y armá la colección a mano:

```plsql
apex_session.create_session(p_app_id => <id_app>, p_page_id => <n>, p_username => '<usuario>');
apex_collection.create_or_truncate_collection('<COLL>');
apex_collection.add_member(p_collection_name => '<COLL>', p_c001 => '…', p_c002 => '…');
<package>.<procedure>(…);   -- y capturás el error esperado
apex_collection.delete_collection('<COLL>');
apex_session.delete_session(v('APP_SESSION'));
```

Así se verificó, en una migración, la regla "todos los integrantes deben pasar al nuevo contrato" con dos clientes
en el mismo lote, caso que **no existía** en el ambiente de desarrollo (todos los contratos activos tenían un solo
cliente).

**b) Sembrar el dato mínimo**, clonando uno existente y cambiando sólo lo necesario (una tarifa en dólares, por
ejemplo). Con **id explícito** si el secuenciador está desfasado. Anotarlo en el ledger con la marca de que **no
va a producción**, y avisar si queda referenciado por datos de prueba (entonces no se puede borrar).

## 4. Antes de cambiar código compartido: buscar los llamadores

- **Base**: `oracle_dependencies(<objeto>, used_by)` (o la consulta equivalente que permita el canal del perfil).
- **Aplicación**: el export completo de la app **NO trae las páginas** (devuelve sólo componentes compartidos,
  ~20 MB sin una sola página). Hay que pedirlas explícitamente:

```plsql
-- ids sacados de apex_describe_application
for i in 1 .. ids.count loop comps.extend; comps(comps.count) := 'PAGE:' || ids(i); end loop;
l := apex_export.get_application(p_application_id => <id_app>, p_split => false, p_components => comps);
-- luego dbms_lob.instr sobre l(1).contents
```

**Siempre con un control positivo** (un texto que sabés que existe, por ejemplo el alias de la página). Si el
control da cero, lo roto es tu búsqueda, no el resultado. En una migración esto evitó asumir que otra página de
cambio de plan masivo usaba el mismo package: no lo usaba.

## 5. Lo que NO cuenta como verificación

- Que compile.
- Que `apex_describe_page` muestre el componente: la metadata puede estar perfecta y la página rota.
- Llamar a la función JS del botón en lugar de clickearlo.
- Un `SELECT` que devuelve filas sin haber mirado qué muestra la pantalla.
- "Debería funcionar porque el código es el mismo".
- Contar páginas o filas sin mirar el contenido.

## Barrido de "todos los forms que usa"
- Reconvertí el `.fmb` a XML y busqué `CALL_FORM|OPEN_FORM|NEW_FORM|RUN_PRODUCT` en **todos** los program units y triggers; después leí a su vez el código de cada form llamado con la misma búsqueda.
- **Llamadores del form:** grepear el nombre en los `.fmb` binarios del repositorio de formularios (leer los bytes como latin1 y buscar con regex; con ~1.700 archivos tarda ~1 min). Sólo así se confirma qué ramas del form son alcanzables (en un caso, la rama `P_ID_ORDEN = 0` no lo era).
- Para cada `CALL_FORM`, listar **parámetro por parámetro** lo que pasa el original y comprobar que la migración lo cubre. En un caso faltaba `P_FECHA` (valor inicial de la fecha del talón); el inventario inicial tenía todo en ❌ de borrador y nadie lo había contrastado.
- Un botón del Forms que "no hace nada" cuando no se cumple una condición (`IF forma = 2`) **no puede** abrir un diálogo vacío en APEX.
