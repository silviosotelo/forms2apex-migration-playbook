---
name: migrar-formulario
description: Playbook de proceso para migrar un formulario Oracle Forms 6i a APEX en la app 400 de Santa Clara (DEVNEW/SANTA), y para verificar o corregir una migración ya hecha cuando llega un ticket. Usala cuando el pedido sea "migrá el formulario X a APEX", "seguí con la migración de X", "verificá la migración de X", "el formulario X del SC+ no funciona", cualquier trabajo sobre los .fmb de anamnesis, sobre páginas de la app 400, o sobre los packages PKG_* de esas migraciones. Define fases, reglas duras de lo permitido y prohibido, cómo se audita, cómo se prueba (matriz de casos y método), cómo se cierra y cómo se verifica en producción. Complementa a oracle-apex-dev y oracle-apex-migrate, que aportan el conocimiento de las APIs.
---

# Migrar un formulario Forms 6i → APEX (app 400)

Playbook destilado de las migraciones **72, 827, 926, 1808, 6201, 6212, 6252 y 6143**. **Esta skill es el proceso y la
única puerta de entrada**: las otras tres son bibliotecas que se consultan desde acá.

| Necesitás | Dónde está |
|---|---|
| El proceso, las reglas, la verificación, el cierre | **esta skill** |
| APIs de APEX (PL/SQL, JS, vistas, versiones) | `/oracle-apex-dev` |
| Mapeo conceptual Forms→APEX (bloques, triggers, LOVs) | `/oracle-apex-migrate` |
| Conversores `.fmb`/`.rdf` → XML, plantilla de package, internals `wwv_flow_*`, JasperReports | `/oracle-forms-migration` (`tools/`, `templates/`, `references/`) |
| Tablas `wwv_flow_*` columna por columna, errores comunes del proyecto | `Migraciones/GUIA-MIGRACION-FORMS-APEX.md` |
| Estado de cada formulario del proyecto | `Migraciones/WORKFLOW-MIGRACION-FORMS-APEX.md` |
| Patrones de UI de listado + ficha, botonera flotante, guardado sin pérdida de datos | `references/patrones-ui-form.md` |

Para convertir el `.fmb`: el `frmf2xml.bat` de Oracle Forms 12c desde **PowerShell** con `ORACLE_HOME` seteado
es el que funciona; el conversor bundled de `/oracle-forms-migration` falla por falta de `frmjapi.dll` nativa.

## Arranque inmediato

1. Invocar `/oracle-apex-dev` y `/oracle-apex-migrate`.
2. **PASO −1 — verificar el punto de partida antes de tocar nada:**
   - **¿Ya está migrado?** `PROGRAMA.ID_PAGE_APEX IS NULL` no alcanza: la misma función puede estar migrada
     desde otro módulo con otro id y otro nombre. Buscar por **descripción** en `PROGRAMA` y por nombre/alias
     entre las páginas de la app. Si existe, **avisar antes de construir**.
   - **¿Es el `.fmb` correcto?** Si hay varias copias, comparar (`md5sum` + diff estructural) y validar el
     fuente contra la base: si usa una columna que no existe en `ANAMNESIS`, es de otra base.
   - **Los fuentes son de sólo lectura.** Se **copian** a local antes de procesar; nunca se modifican ni se
     mueven en el servidor. Si el archivo no está donde corresponde, **parar y avisar**, no ampliar la búsqueda
     por cuenta propia.
3. **Verificar contra qué base estás**: `SELECT SYS_CONTEXT('USERENV','SERVER_HOST')` → `desa` = DEVNEW,
   `db12c-prod` = SANTA. El MCP puede informar una base y ejecutar en otra, y puede cambiar solo a mitad de
   sesión: repetir el chequeo **inmediatamente antes de cada DML**.
4. Ubicar `Migraciones/<nro> - <nombre>/`. Si no hay `_fmb.xml`, generarlo con `frmf2xml.bat` desde PowerShell.
5. Leer las memorias `migracion_*` de los **formularios hermanos** (buscar por nombre de tabla, no por número).
6. Leer `Migraciones/WORKFLOW-MIGRACION-FORMS-APEX.md` para el **estado** del circuito y qué migraciones hay.
7. Si la migración va a durar varias horas o sesiones, usar `/goal <condición verificable>` para no cortar
   (por ejemplo: *"fases 1-5 terminadas y la matriz de verificación en PASS sin observaciones"*).

## Qué significa "migrado" (definición de terminado)

1. **Paridad funcional**: cada trigger, program unit, LOV y validación del `.fmb` tiene equivalente o está
   documentado como "no aplica en web".
2. **Paridad de datos**: mismos procedures compartidos, mismos parámetros, mismos defaults. Si el Forms pasa
   `:IMPORTE`, la migración pasa el importe, no `NULL`.
3. **UI estándar**: floating labels, grid de 12, `region-con-bordes`, CSS de la app. Items sueltos = no migrado.
4. **Seguridad aplicada**: authorization scheme en página, botones y procesos `ON_DEMAND`.
5. **Probado** con la matriz de `references/verificacion.md`, incluidos los negativos.
6. **Documentado**: auditoría, estado, package en disco, memoria.

Frases contra el autoengaño:

- **"existe" no es "migrado"** — las páginas del 926 ya estaban y eran un CRUD vacío.
- **"compila" no es "anda"** — el 6143 estaba en producción sin poder procesar un solo caso con titular.
- **"anda" no es "anda como el Forms"** — esa es la comparación que vale.
- **"PDF generado" no es "PDF con datos"** — abrilo y miralo; el archivo pesa y termina en `%%EOF` igual.
- **"no crasheó" no es "hizo lo que tenía que hacer"**.
- **"salió el toast de error" no es "se bloqueó la acción"** — verificá en la base que no escribió.
- **"no hay error en consola" no es "el botón hizo algo"**.

**No se declaran pendientes técnicos.** Si algo no funciona, no está entregado. Lo único que se entrega abierto
son **decisiones funcionales** que no le corresponden a quien migra, y van listadas como tales.

## Reglas duras

| Tema | Permitido | Prohibido |
|---|---|---|
| Oracle/APEX | MCP `oracle-apex` | `sqlplus` ad-hoc, scripts sueltos, clientes Oracle por `Bash` |
| Componentes APEX | `wwv_flow_api` con setup previo | `INSERT` directo a `WWV_FLOW_*` |
| Atributos sin API | `UPDATE` de una sola columna, verificando antes con `all_arguments`. Si el modo auto lo bloquea (6212), el camino es el **re-import** de `references/gotchas-apex.md`, sin buscar otro atajo | `UPDATE` masivo |
| Inspección | `apex_describe_page`, `apex_get_page_source`, `apex_export` | `SELECT` a `apex_application_*` |
| Items de Form Region | `source_type = REGION_SOURCE_COLUMN` | Cambiarlo para "meter un default" |
| *Form - Initialization* | Dejarlo activo siempre | Condicionarlo (mata todos los defaults) |
| Impresión | `pkg_jasperreports_server.descarga_reporte` desde Ajax Callback **de la página** | `RWRUN60` en caliente, blobs a mano, Application Process global |
| Permisos y roles | Reportar lo que esté mal | Tocarlos, o quitar esquemas para destrabar un botón |
| Controles nuevos | Proponerlos en la auditoría | Implementarlos (locks, validaciones extra) |
| Producción | Sólo si el usuario lo pide; lectura y verificación | Pasar cambios por iniciativa propia u ofrecerlo |
| Errores | Mensaje real al usuario | `exception when others then null` |

**Antes de crear una página**, verificá que el número esté libre: `create_page` sobre un id existente no falla y
las regiones se cuelgan de la página ajena. **Antes de cambiar código compartido**, buscá los llamadores
(`oracle_dependencies` + export de todas las páginas, ver `references/verificacion.md`).

## Fases

### FASE 1 — Auditoría antes de tocar nada
`AUDITORIA_FMB_vs_APEX.md` con leyenda `✅ migrado · ⚠️ parcial · ❌ falta · ➖ no aplica · ➕ agregado`.
Secciones: bloques, items, triggers de item, triggers de form, program units, LOVs/Record Groups, reporte,
seguridad, UI. Hallazgos numerados **H-1, H-2…** con severidad. La tabla de resolución va **al mismo archivo**.
Auditá contra el **export vivo** (`apex_export`), no contra los `.sql` locales: trae condiciones de botones,
`required_role` y código de los DA que `apex_describe_page` no muestra.
Plantilla: `plantillas/AUDITORIA_FMB_vs_APEX.md`.

### FASE 2 — Dónde vive la lógica en Forms
Mapa de triggers, trampas de paridad y los errores que costaron migraciones enteras:
**leer `references/paridad-forms.md`**.

### FASE 3 — Construcción (en este orden)
0. **Compuerta anti-overengineering**: ¿hace falta un package de verdad? Si la pantalla es un CRUD simple que
   resuelve un Form + IR nativo, usá eso. El package es para la **lógica de negocio** del Forms, no por reflejo.
   Los TYPEs y funciones auxiliares van **dentro del spec del package**, nunca sueltos en el esquema.
1. **Package primero**: toda la lógica en `PKG_*`, probado por SQL con casos sintéticos antes de tocar una página.
2. **Páginas después**: patrón obligatorio **IR (listado + filtros) → Form modal**. Nunca Interactive Grid para
   carga, nunca un Form como página de entrada.
3. **Estilo, no opcional**: floating labels, `#WORKSPACE_IMAGES#`, grid de 12 con `item_sequence` acompañando el
   orden visual, `region-con-bordes` + `<h5>`, `dialog_width` ~1000, Inline CSS canónico.
   **Sin HTML armado a mano**: grillas = IR (acciones como columnas de enlace), fichas/resultados = Display Only,
   archivos = File Browse, avisos en texto plano. Las reglas de negocio se copian tal cual, sin "mejorarlas".
4. **Ajax callbacks en la PÁGINA**, nunca como Application Process.
5. **Impresión = siempre JasperReports Server**. Si la pantalla imprime un `.rdf`, **leer
   `references/reportes-rdf.md`** antes de empezar: PDF de referencia con `RWRUN60`, verificación de que el PDF
   tiene datos, errores conocidos y su causa, coordenadas, JRXML e integración por Ajax Callback de la página.
6. **Seguridad al final** (`pkg_apex_autorizacion.pr_generar_todo`), con los **mismos roles del Forms**, y
   protegiendo también los `ON_DEMAND` (se invocan por URL aunque el botón esté oculto).

**Rediseño de listado y ficha** (IR + filtros sobre colección, ficha como página con navegación Anterior/Siguiente entre
los registros filtrados, regiones con marco, tabs, botonera flotante, badge de estado, y las trampas de guardado que
pierden datos): **leer `references/patrones-ui-form.md`** — patrón de referencia 6001 (páginas 977/991) y 1470.

Gotchas de `wwv_flow_api` y APEX 20.2, y cómo **corregir una página que ya existe** (re-import server-side, la
única vía cuando no hay API para DA/IR/JS): **leer `references/gotchas-apex.md`**.

### FASE 4 — Verificación
**Barrido de paridad obligatorio antes de cerrar**: lista de TODOS los procesos, DAs y regiones del original (o triggers
del `.fmb`) marcada uno por uno CUBIERTO / DIFERENTE / FALTA con evidencia en el código nuevo. Una revisión del código
nuevo contra la spec no alcanza: en la Visación v2 el circuito "1614 médico no prestador" estaba en la spec y no tenía
tarea, y lo encontró el usuario.
No alcanza el caso feliz. El paso preventivo (grepear cada parámetro del form contra el package, la página y el
JRXML), la matriz obligatoria de casos, el recorrido de QA en 10 pasos —incluido el **diff paramétrico**: cada
filtro opcional tiene que cambiar el resultado—, el método (clicks reales, ledger antes/después, medir en el
DOM, probar después de cada refresco), cómo probar cuando el ambiente no tiene datos, cómo buscar llamadores y
**qué no cuenta como verificación**: **leer `references/verificacion.md`**.

**Falta de datos en DEVNEW no es un cierre válido**: se arma el escenario (sintético contra el package, o
sembrado y documentado) y se corre el flujo real.

### FASE 5 — Cierre

**Autocrítica antes de entregar** (dos preguntas, por escrito, aunque sea una línea cada una):
1. **¿Qué falta capturar?** ¿Hubo algo que corregí sobre la marcha, algo que me sorprendió, algo que hice dos
   veces porque la primera estuvo mal? Si todavía no quedó en memoria, **escribirlo ahora**, antes de decir listo.
   Si el contexto se compactó durante la migración, **re-medir cada cifra y cada "el Forms hace X" antes de escribirlo en la auditoría**
   (consulta a la base, lectura del `.fmb`/package): en el 6212 el primer borrador del cierre traía afirmaciones sin respaldo ("probado con 6
   prestadores", un conteo que no incluía las NC propias) y salieron al verificar una por una.
2. **¿Qué regla que seguí resultó estar mal?** Si una memoria o una regla de esta skill dio un resultado
   incorrecto o quedó contradicha por el caso real, **corregir el cuerpo de esa memoria/regla ahora**: no alcanza
   con una nota suelta en el informe.

**Checklist de entrega al usuario final:**
- [ ] La página se llama como la conoce el negocio, sin ids de programa a la vista.
- [ ] Todo proceso largo tiene confirmación, spinner y mensaje con el conteo del resultado.
- [ ] Los patrones visuales están copiados de la app, no inventados.
- [ ] Si se pide manual: sólo cómo usarlo, sin portada de "esto es una migración".
- [ ] Cerrar listando lo que **falte o difiera** del form, visual y funcional. Si no falta nada, decirlo.

**Entregables:**
- `AUDITORIA_FMB_vs_APEX.md` con tabla de resolución, matriz de casos y **ledger de datos de prueba**.
- `ESTADO_MIGRACION.md` (plantilla en `plantillas/ESTADO_MIGRACION.md`).
- `.sql` en `Paquetes y Scripts PLSQL/` con **spec + body completo**, y el export final de la página.
  **Antes de cerrar, comprobar que el `.sql` del package == lo compilado**: tokenizar ambos (sin comentarios ni espacios, minúsculas fuera de
  literales) y comparar con `all_source`; el MCP descarta los `--` y los parches hechos solo en la base hacen divergir los archivos (en el 6212: 3
  tokens). El export de las páginas sale **de la base** (`apex_export`), no de los scripts que se mandaron (ver `references/gotchas-apex.md`).
- Si la migración crea un **programa APEX nuevo**, dejar `programa_<id>_seguridad.sql` (programa + roles + `pr_generar_todo`) para el pase.
- Respaldo de lo previo en `respaldo_pre_fix/` si tocaste algo existente.
- Memoria `migracion_<nro>_<nombre>` + una línea en `MEMORY.md`.
- Limpiar o documentar los datos de prueba; borrar tablas `tmp_*` creadas.
- Actualizar la tabla de estado en `Migraciones/WORKFLOW-MIGRACION-FORMS-APEX.md`.
- **Nunca ofrecer ni preguntar por el pase a SANTA**: lo hace el usuario.

### FASE 6 — Pase a producción y verificación
Checklist del pase y cómo verificar en SANTA **sin ejecutar el botón que escribe**:
**leer `references/produccion.md`**.

## Autonomía

**Avanzá sin preguntar** (es DEVNEW): packages, páginas, datos de prueba documentados, bugs del circuito que
migrás, seguridad del programa que migrás.

**Fuera de alcance**: permisos y roles, controles que el original no tiene, refactors. Migrar es reproducir,
incluidos los bugs. Sí entra lo necesario para que el código funcione igual desde APEX (NLS, cadena de `USER`).

**"Réplica exacta" es literal (6212, 07/10/2026: el usuario rechazó una entrega por esto).** No existe una "diferencia
menor a favor del usuario": completar campos que el Forms deja vacíos, validar lo que el Forms no valida, quitar o cambiar
un mensaje, recalcular un total que el Forms no recalcula, atrapar un error que el Forms deja volar, o rehacer un flujo sobre
otro backend **cambian la lógica** y se revierten. Solo se aceptan, y se declaran **en el mensaje de cierre**, las diferencias
que impone el medio web (no hay "registro actual", cada ventana es una página). Si el Forms llama un procedure standalone,
se llama ese mismo (buscar antes si ya tiene rama "Desde APEX"). Si el formulario destino de un botón no está migrado y el
pedido es "migración completa", se migra (o se dice claramente que falta y por qué); un aviso "todavía no migrado" no cuenta.

**Pará y preguntá** sólo ante: escrituras contables irreversibles, decisiones funcionales (se **reportan con
recomendación**, no se deciden), módulos ajenos, y cualquier cosa en producción.

Patrón que funcionó siempre: **documentar la decisión funcional como abierta y seguir con todo lo demás**.
Entregar el 95 % con 5 % declarado vale más que frenar el 100 %.

## Buenos y malos hábitos

| Buen hábito | Mal hábito |
|---|---|
| Auditar antes de tocar, con hallazgos numerados | Corregir primero y "después documento" |
| Comparar contra el `.fmb` en cada decisión | Decidir por lo que "tiene sentido" |
| Ledger antes/después de cada corrida | Mirar sólo el mensaje de éxito |
| Medir en el DOM lo que se ve | Sacar una captura y suponer |
| Probar el negativo de cada validación | Probar sólo que guarda |
| Escribir el gotcha en memoria apenas cuesta 2 intentos | Dejarlo para el final |
| Declarar lo no probado | Rellenar con "debería andar" |
| Verificar `SERVER_HOST` antes de cada DML (el MCP puede **arrancar en SANTA**: `oracle_connect` a DEVNEW primero) | Confiar en el "Target:" del connect |
| Reproducir el defecto del Forms y documentarlo como "heredado" | "Mejorarlo" y llamarlo "diferencia menor a favor del usuario" |
| Leer cada item del `.fmb` con su `Formula` / `CalculateMode` y cada trigger de bloque | Fiarse de un volcado que no los trae |
| Una consulta lenta del Forms no se mide por el MCP: se compara por lógica y se declara | Dejar una consulta de 30 min corriendo y bloqueando la base |
| Respaldar antes de re-importar o recompilar | Confiar en que "se puede volver atrás" |
| Reportar permisos mal configurados | Arreglarlos para destrabar el botón |

## Loop de automejora (obligatorio)

1. Cada gotcha que cueste más de 2 intentos se escribe en memoria **antes** de seguir.
2. Un hallazgo que corrige una creencia previa **actualiza la memoria vieja**, no crea una paralela.
3. Al cerrar, actualizá esta skill y el estado del circuito si el proceso cambió.
4. Usá el advisor antes de comprometerte a un enfoque, cuando un hallazgo cambia el alcance, y antes de declarar
   terminado (con el deliverable ya guardado en disco).
5. Nada de verdades sin verificar en memoria: si es inferencia, escribí "sin confirmar".
