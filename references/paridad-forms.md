# FASE 2 — Dónde vive la lógica en Forms y cómo mapearla sin perder paridad

## El mapa

| Trigger / elemento | Qué contiene | Dónde va en APEX |
|---|---|---|
| **KEY-COMMIT** | **El núcleo**: validaciones de negocio + toda la contabilidad | Validaciones de página + proceso After Submit que llama al package |
| **WHEN-NEW-FORM-INSTANCE** | `VERIFICA_PROGRAMA` (seguridad) + alta con parámetros desde otro form | Authorization Scheme (según el perfil) + package invocado desde el form llamador |
| **POST-QUERY** | Lookups (`CGFK$QRY_*`) que llenan campos informativos | Proceso Before Header con el package de lectura |
| **WHEN-VALIDATE-ITEM** | Validaciones **y fórmulas** de item | Validaciones `FUNC_BODY_RETURNING_ERR_TEXT` o DA Change |
| **WHEN-NEW-BLOCK-INSTANCE** | Limpieza del bloque detalle al volver al filtro | Control equivalente en el proceso que escribe |
| **KEY-CREREC** | Defaults del alta | Defaults en el proceso Before Header |
| **WHEN-BUTTON-PRESSED** | Llama a program units | Botón + proceso/Ajax que llama al package |
| **Program units** | Se comparten entre forms hermanos | Packages `PKG_<MODULO>_LECTURA` / `_ESCRITURA` |
| **Alertas de confirmación** | "preguntar una vez y aplicar al resto" | Flags de corrida + modo `p_solo_validar` |

## El layout condicional también se migra

El `.fmb` no sólo tiene un layout estático: tiene **comportamiento dinámico** que hay que listar y portar.
Buscá en triggers y program units todos los `SET_ITEM_PROPERTY` (`VISIBLE`, `ENABLED`, `NAVIGABLE`,
`UPDATE_ALLOWED`, `REQUIRED`), `SHOW_VIEW` / `HIDE_VIEW` y los `GO_ITEM`/`GO_BLOCK` condicionales.

Cada uno tiene equivalente en APEX: condición del item, Dynamic Action de Show/Hide/Enable/Disable, o
`read_only` condicionado. **Contá los casos del form y contá los de la página**: si el form tenía N y la página
tiene menos, esa lógica no se migró. Anotá ese número en la auditoría en la fase de análisis, porque después no
hay contra qué comparar sin re-derivarlo todo.

Es el tipo de gap que no aparece en ninguna consulta a la base ni en `apex_describe_page`: sólo se ve
comparando el form contra la pantalla.

## Trampas de paridad (todas costaron una migración)

**El `Comment` del bloque en el XML miente.** Es residuo del generador de Designer. La verdad es
`QueryDataSourceName`. En un formulario migrado, el bloque de detalle de una orden de pago decía en el `Comment`
que se basaba en la tabla de detalle de otro documento, y era falso.

**Una regla que parece inventada puede estar en el form hermano.** En un caso, las validaciones de firmas no
estaban en el `.fmb` que se migraba pero sí en el `KEY-COMMIT` de su form hermano. Antes de descartar una regla,
buscala en los hermanos.

**Los flags se replican DONDE el form los pone, no donde parecen correctos.** En un form hermano, el flag
`V_BAND` se marcaba al *encontrar* la orden, no al *generar* el asiento: por eso una orden de cierto tipo no
contabilizaba y tampoco daba error. Moverlo al lugar "lógico" rompía todos los cheques del formulario principal.

**Una asignación programática en Forms SÍ dispara el WHEN-VALIDATE-ITEM al commit** (el ítem queda CHANGED). Si
un program unit asigna un monto y nunca asigna el IVA, el IVA lo calcula el WVI: portá esa fórmula también. Así
se escapó el IVA de una función «Distribuir» en una migración. Para confirmarlo, mirá los datos históricos que
dejó el Forms.

**Una validación agregada en APEX puede contradecir una regla copiada del Forms.** Una migración exigía
categoría destino (el Forms no la exige: pasa `NVL(:ID_CAT1,:ID_CAT)`) y a la vez, como el Forms, prohibía
elegirla para el titular. Resultado: ningún lote con titular se podía procesar, en producción, durante meses.
**Antes de agregar un "obligatorio", buscá si hay otra regla que impida cargar ese dato.**

**Los reemplazos de "bloque del Forms" por colecciones pierden la limpieza del bloque.** El Forms vacía el
detalle al volver al filtro (`WHEN-NEW-BLOCK-INSTANCE`) y re-consulta después de procesar. En APEX, además, un
error en un proceso After Submit **hace rollback** y deshace el `create_or_truncate_collection`: la grilla queda
mostrando el lote anterior mientras el filtro ya apunta a otro registro, y el botón de proceso trabajaría sobre
datos ajenos. El proceso que escribe **tiene que verificar que la colección corresponde al filtro**, y la
colección se re-arma al terminar (equivalente al `trae_clientes` del Forms).

**Maestro-detalle con un solo `COMMIT_FORM`: el detalle en edición NO es la tabla.** En el `.fmb` las líneas se
arman en el bloque y llegan a la base juntas con la cabecera (KEY-COMMIT + PRE-COMMIT "Cabecera sin Detalle"); un
`DELETE_RECORD` sobre un registro nuevo no es un DELETE. Si la migración graba cada "Aplicar" al instante, Quitar y
cualquier "Distribuir" que saque líneas pasan a ser DELETE reales, y un trigger de detalle que prohíbe borrar en
estado ACTIVO los rechaza para todos (hallazgo real en una migración de contratos). Patrón: colección como bloque
(`det_cargar` al abrir, aplicar/quitar/editar/distribuir sobre la colección, `det_guardar` dentro de
Crear/Guardar); la página del picker lee la cabecera del estado de sesión para poder armar un registro nuevo antes
de crearlo; Cancelar con cambios pregunta. Antes de decidir el diseño, grepeá `COMMIT_FORM|KEY-COMMIT|PRE-COMMIT` y
los triggers del detalle.

**Código muerto**: revisá si la llamada está comentada (`---generar_asiento;`). No lo migres, pero confirmá con
análisis de llamadores que nadie lo usa; no por intuición.

**`USER` y `VERIFICA_PROGRAMA` filtran por usuario de BD** → inservibles desde APEX; usar `V('APP_USER')`.
Buscá **todos** los objetos que los usan, no sólo el trigger obvio.

**Pero no arregles media cadena de `USER`.** Si una tabla temporal se llena con `USER` y la lee un procedure
compartido con `USER` hardcodeado (que no podés tocar), escribir con `V('APP_USER')` deja al consumidor sin filas
**en silencio**. Usá `USER` en los dos extremos y declará la degradación: desde APEX `USER` es
**`APEX_PUBLIC_USER`**, igual para todos los usuarios. Una migración de servicios adicionales perdía los
servicios por esto.

**Los procedures legacy comparan fechas contra literales de texto** (`p_fecha >= '01/01/2017'`): dependen del
`NLS_DATE_FORMAT` de la sesión y desde APEX explotan con `ORA-01843`. Fijalo antes de llamarlos.

**Un formulario de proceso no es un CRUD.** Cuando el form es masivo (lote + marcar + generar): IR = el lote,
modal = editar una fila, botones del proceso en una región de botones.

**Procedures compartidos con `commit` interno.** Si uno falla a mitad del lote, lo anterior **ya quedó escrito**
y el `rollback` del package no lo deshace: un procedure de generación de cuotas por cliente, los `GEN_ASIENTO_*`
de contabilidad, un procedure que genera contratos desde otro contrato y una carga a tabla temporal de cálculo
(esta última hace `delete` sin `WHERE` + commit). Es paridad con el Forms: **se documenta, no se "arregla"**, y se
avisa al usuario que ante un error a mitad de lote hay que revisar qué quedó procesado.

**Revisá los secuenciadores por tabla (`CG_CODE_CONTROLS`) del circuito.** Pueden estar por debajo del `MAX(id)`
real y reventar con `ORA-00001` recién en la escritura final (pasó con la secuencia de una tabla de servicios
adicionales y se detectó lo mismo con la de tarifas en otra migración). No es problema de la migración, pero la
bloquea.

**Un campo sin columna (`DatabaseItem=false`) que el usuario carga y el form consume DESPUÉS, en otro punto, es una pieza más del circuito.**
En una migración de órdenes de pago, el detalle pedía banco / nro / fecha de cheque; la migración los validaba y
los descartaba porque `GRABA_CHEQUE` (que los guarda en la tabla de pagos tras el pago) vivía en el
**form llamador** y nadie lo había migrado. Para cada item no-DB del `.fmb`: grepear **quién lo lee**
(`:BLOQUE.ITEM` en todos los triggers y program units de AMBOS forms del circuito) y comprobar en la base —con
datos históricos— que el dato destino se llena (`COUNT` de filas enlazadas). **«Equivalente» no se escribe sin
haber encontrado el consumidor.**

**Los defaults pueden calcularse en el form llamado, no en el llamador.** En esa misma migración el form no pasaba
el parámetro de la disponibilidad (caja/banco), pero el form de pago la calculaba en `WHEN-NEW-FORM-INSTANCE` a
partir de otros parámetros. Concluir «el `.fmb` no la carga» mirando sólo los `ADD_PARAMETER` fue un error que se
arrastró a tres documentos. Leer **todo** el `WHEN-NEW-FORM-INSTANCE` y `CARGAR_REG_NUEVO` del form llamado.

**Medir el uso real antes de elegir qué probar.** Una migración se probó con el concepto más simple (un anticipo);
el uso dominante eran otros dos conceptos, con miles de detalles históricos. Un `GROUP BY concepto` sobre el
detalle histórico dice dónde está el riesgo en 1 consulta. Con la misma consulta se sabe si un caso de la
migración se dispara «de más»: en ese formulario el canje sólo ocurría con una forma de pago puntual (unos pocos
cientos de casos sobre miles) y la migración lo hacía siempre.

**Una validación con condición `Never` está apagada.** `apex_describe_page` no lo muestra: en el export,
`p_validation_condition_type=>'NEVER'`. Contarlas en la auditoría (en una página, las 7 validaciones estaban
apagadas, incluida la de «cabecera sin detalle»).

**Probar cada caso en el dominio donde la LOV lo ofrece.** En una migración, ciertos conceptos sólo existían para
una de las sucursales (según la vista que alimenta la LOV): una prueba con un `setValue` forzado en una orden de
la otra sucursal es fuera de dominio y no cuenta. Filtrar la LOV con SQL antes de armar el caso.

**Comparar un export vivo contra el esperado = conjunto de sentencias, no bytes.** Partir ambos por `\nwwv_flow_api.`, normalizar lo mecánico («Exported By», los separadores `end;\n/\nbegin` que APEX reparte
por tamaño) y comparar MD5 por sentencia como multiconjunto; el orden de procesos/validaciones sale ordenado por secuencia y no cambia nada. En SQL: `WITH FUNCTION` + `dbms_obfuscation_toolkit.md5`
(`dbms_crypto` puede no estar accesible desde el canal de acceso a Oracle) y devolver una fila por sentencia (la salida de un MCP suele cortar cada celda a ~60 caracteres).

**«Probado por script» no es «probado con el botón».** En una migración, «Eliminar» nunca funcionó: el botón llamaba `apex.confirm(htmldb_delete_message, …)` y esa variable no existe en la página (ReferenceError mudo); se había probado mandando el mismo request con `apex.submit` y se culpó al `confirm()` nativo. Probar cada botón con su clic y mirar el diálogo: en APEX 20.2 la confirmación aparece como `[role=alertdialog]` en el `document` **de arriba** (no en el iframe del modal). Revisar `grep htmldb_delete_message` en los exports.

**Un item Per Request que otra página lee deja la validación inerte sin error** (una página leía el item de sucursal de la página vecina = nulo, y `NO_DATA_FOUND → NULL`). Al auditar una validación, forzar el caso que debería bloquear (una forma de pago y una sucursal concretas) y ver que bloquea.

**Probar roles sin sus claves:** `apex_session.create_session(<id_app>, <pág>, '<usuario>')` + el procedimiento de armado de permisos que fije el perfil + la consulta de permisos por programa (`I`|`U`|`D`) por usuario con un solo rol. `apex_authorization.is_authorized` devuelve lo mismo para todos en ese bloque: no usarlo. Declarar que no se probó el login ni la UI con usuarios reales.

**Un FK de asiento puede mentir:** un trigger de detalle de asiento reemplaza el plan de cuentas por el vigente a la fecha del asiento (plan de cuentas con `vigencia_desde/hasta`) y el mensaje de la rutina de inserción imprime el plan viejo; el FK falla porque el plan nuevo no tiene fila en la tabla de cuentas por sucursal para esa sucursal. Depurar con un trigger `BEFORE INSERT` autónomo temporal que registre `:new`.

## Cómo leer el `.fmb`

`frmf2xml.bat` (Oracle Forms 12c, en el `ORACLE_HOME` del middleware) desde **PowerShell**, con `ORACLE_HOME`
seteado. El texto de triggers y program units viene en los **atributos** `TriggerText` / `ProgramUnitText`, con
entidades (`&#10;`, `&#9;`, `&apos;`) que hay que decodificar **dos veces** si el XML las trae escapadas.
Algunos program units aparecen sin texto en el volcado: buscalos por nombre dentro del XML crudo.
