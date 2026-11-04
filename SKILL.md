---
name: forms2apex
description: Migrar formularios Oracle Forms 6i (.fmb) y reportes Oracle Reports (.rdf) a Oracle APEX 20.2 con la lógica en packages PL/SQL, y verificar o corregir migraciones ya hechas. Trae el flujo completo (auditoría, construcción, verificación, cierre, pase a producción), referencias de APIs de APEX y de internals wwv_flow_*, plantillas y scripts, y extrae triggers, program units y SQL de un .fmb/.rdf SIN necesitar Oracle Forms, Java ni Forms2XML. Usala siempre que el pedido sea migrar, portar, convertir, auditar, arreglar o dar paridad a un formulario o reporte de Oracle Forms/Reports en APEX, aunque no nombre la skill: "migrá el formulario X", "pasá este .fmb a APEX", "convertí este .rdf", "el formulario migrado no se comporta como el original", "verificá la migración", o cualquier trabajo con .fmb, .rdf, triggers de Forms, wwv_flow_api o paridad Forms→APEX.
---

# forms2apex — migrar Oracle Forms 6i / Reports a Oracle APEX 20.2

Una migración está terminada cuando **hace lo mismo que el original, probado en el navegador contra datos reales** — no cuando
existe una página o compila un package. Esta skill es el camino para llegar ahí sin que se pierda ningún trigger, ni datos al guardar.

Destino fijo: **APEX 20.2 sobre Oracle 12.1**. Todo lo que no esté documentado para esas versiones se marca
`VERIFICATION REQUIRED` y se prueba en la base antes de usarlo.

## 0. Antes de empezar: el perfil del cliente

Lo que cambia de un cliente a otro (bases, ids de la aplicación, seguridad, estilo visual, reportes, rutas) **no está en esta skill**:
vive en un **perfil**. Resolvelo así, en este orden:

1. Archivo `.forms2apex-profile` en la raíz del proyecto con una línea `profile: <nombre>`.
2. Si no existe, buscá `~/.claude/forms2apex-profiles/<nombre>.md` (o el único `.md` que haya ahí).
3. Si no hay perfil, **no inventes valores**: copiá `profiles/_plantilla.md`, completala con el usuario (preguntá solo lo que no se
   pueda leer del proyecto o de la base) y guardala donde diga el punto 2.

Leé el perfil entero antes de la primera consulta a la base. Cuando esta skill dice «según el perfil», es ahí.

## 1. Mapa de recursos (se cargan solo cuando la fase los pide)

| Necesitás | Archivo |
|---|---|
| Sacar la lógica de un `.fmb` / `.rdf` | `scripts/extraer_fmb_rdf.py` · `references/conversion-fmb-rdf.md` |
| Dónde vive la lógica en Forms; trampas de paridad | `references/paridad-forms.md` |
| Matriz de pruebas, método, qué NO cuenta como verificación | `references/verificacion.md` |
| `wwv_flow_api`, DA, IR, parchar una página existente | `references/gotchas-apex.md` · `scripts/export_apex.py` |
| Listado + ficha, navegación, botonera, guardado sin pérdida de datos | `references/patrones-ui-form.md` |
| Reporte `.rdf` → JasperReports | `references/reportes-rdf.md` · `references/internals/jasperreports.md` |
| Pase a producción y verificación en producción | `references/produccion.md` |
| Tablas `wwv_flow_*`, template ids, vistas del diccionario | `references/internals/apex-internals.md` · `references/guia-wwv-flow.md` |
| APIs de APEX (PL/SQL, JS, IR/IG, Oracle DB) | `references/apex-api/00-indice-apis-apex.md` |
| Mapeo conceptual Forms → APEX (bloques, triggers, LOVs, built-ins) | `references/mapeo/00-indice-mapeo-forms-apex.md` · `references/internals/forms-mapping.md` |
| Esqueletos: auditoría, estado, package, tabla de estado | `plantillas/` |
| Probar que «Guardar sin tocar nada» no pierde datos | `scripts/diff_columnas.sql` |
| Verificar que el `.sql` del package == lo compilado | `scripts/comparar_package.py` |

## 2. Cómo entra el formulario: del binario al análisis

El `.fmb` y el `.rdf` son binarios propietarios. Hay dos caminos; el árbol de decisión es este:

```
¿Hay XML de Forms2XML del módulo?  ──sí──►  A) usarlo (es la única fuente de las PROPIEDADES: tipo de item,
        │                                      LOV asociada, canvases, relaciones master-detail, alertas)
        no
        ▼
¿Hay Oracle Forms 12c (frmf2xml.bat) o los .jar con frmjapi.dll?  ──sí──►  generar el XML y volver a A)
        │
        no
        ▼
B) python scripts/extraer_fmb_rdf.py ARCHIVO.fmb   (solo Python; sin Oracle, sin Java)
```

**Lo que da B** (probado contra Forms2XML en tres formularios reales: 54/56, 47/48 y 20/20 triggers; 33/35, 29/30 y 12/14 program
units): triggers con su dueño `BLOQUE.ITEM`, program units, todas las sentencias SQL (record groups, LOVs, reportes), el mapa de
referencias `:BLOQUE.ITEM`, y las llamadas a otros módulos. Con eso se audita toda la **lógica** del formulario.

**Lo que B no da**: propiedades de items (tipo, longitud, obligatorio), LOV asociada a cada item, canvases/posiciones, relaciones,
alertas. Esas se completan **leyendo la tabla y el diccionario de la base** y confirmando con el usuario; lo que no se pueda confirmar
va a la auditoría como «propiedad sin verificar», nunca como supuesto. Usá `--verificar XML` cuando haya un XML de otro módulo
equivalente para medir cuánto confiar. Detalle y uso en `references/conversion-fmb-rdf.md`.

Los fuentes originales son **solo lectura**: se copian a una carpeta local sin espacios antes de procesarlos.

## 3. Definición de terminado

1. **Paridad funcional**: cada trigger, program unit, LOV y validación del original tiene equivalente, o está documentado como «no aplica en web».
2. **Paridad de datos**: mismos procedures compartidos, mismos parámetros, mismos defaults. Si el Forms pasa `:IMPORTE`, la migración pasa el importe, no `NULL`.
3. **UI según el perfil** (floating labels, grilla de 12, marcos, CSS). Items sueltos con el label por defecto = no migrado.
4. **Seguridad aplicada** según el perfil: en página, botones y procesos `ON_DEMAND` (se invocan por URL aunque el botón esté oculto).
5. **Probado** con la matriz de `references/verificacion.md`, incluidos los casos negativos.
6. **Documentado**: auditoría, estado, package en disco, memoria.

Frases contra el autoengaño — cada una costó una migración:
- **«existe» no es «migrado»**: una página heredada puede ser un CRUD vacío.
- **«compila» no es «anda»**: se puede estar en producción sin poder procesar un solo caso.
- **«anda» no es «anda como el Forms»**: esa es la comparación que vale.
- **«PDF generado» no es «PDF con datos»**: abrilo; el archivo pesa y termina en `%%EOF` igual.
- **«salió el toast de error» no es «se bloqueó la acción»**: verificá en la base que no escribió.
- **«no hay error en consola» no es «el botón hizo algo»**.

**No se declaran pendientes técnicos.** Si algo no funciona, no está entregado. Lo único que se entrega abierto son
**decisiones funcionales** que no le corresponden a quien migra, listadas como tales y con una recomendación.

## 4. Reglas duras

| Tema | Permitido | Prohibido |
|---|---|---|
| Acceso a Oracle/APEX | El canal que fije el perfil (p. ej. un MCP) | Clientes ad-hoc o scripts sueltos si el perfil fija un canal |
| Componentes APEX | `wwv_flow_api` con el setup previo (`set_security_group_id`, `g_flow_id`) | `INSERT` directo a `WWV_FLOW_*` |
| Atributos sin API | `UPDATE` de una sola columna, tras verificar con `all_arguments` que no hay API; si no es posible, **re-import** (`gotchas-apex.md`) | `UPDATE` masivo |
| Inspección | Las vistas/herramientas de inspección de APEX y `apex_export` | `SELECT` a `apex_application_*` para auditar |
| Items de Form Region | `source_type = REGION_SOURCE_COLUMN` | Cambiarlo a `STATIC`/`EXPRESSION` para «meter un default» (rompe el mapeo item↔columna) |
| *Form - Initialization* | Dejarlo activo siempre | Condicionarlo (mata los defaults de todos los items) |
| Callbacks (imprimir, validar, calcular) | Proceso `ON_DEMAND` **de la página** | Application Process global por lógica de un solo formulario |
| Impresión | Lo que fije el perfil (por defecto: reporte servidor invocado por el callback de la página) | Generar el reporte en caliente con RWRUN60, blobs armados a mano |
| Permisos y roles | Reportar lo que esté mal | Tocarlos, o quitar esquemas para destrabar un botón |
| Controles nuevos | Proponerlos en la auditoría | Implementarlos (locks, validaciones extra) |
| Producción | Solo si el usuario lo pide; lectura y verificación | Pasar cambios por iniciativa propia u ofrecerlo |
| Errores | Mensaje real al usuario | `exception when others then null` |

Antes de `create_page`, verificá que el número esté libre: sobre un id existente **no falla** y las regiones se cuelgan de la página ajena.
Antes de cambiar código compartido, buscá los llamadores (dependencias en la base + export de todas las páginas).

## 5. Flujo de trabajo — fases con compuerta

Cada fase termina con un **entregable** y una **condición para pasar a la siguiente**. Si la condición no se cumple, no se avanza.

| Fase | Qué se hace | Entregable | Compuerta para pasar |
|---|---|---|---|
| **0 Preparación** | Resolver el perfil (§0). Confirmar contra qué base estás **antes de cada DML** (el cliente puede informar una base y ejecutar en otra). ¿El formulario ya está migrado con otro id o nombre? Buscar por descripción y alias; si existe, avisar antes de construir. ¿Es el `.fmb` correcto (varias copias → comparar hash; validar columnas contra la base)? Extraer la lógica (§2). | Carpeta de trabajo `<nro> - <nombre>/` con el fuente copiado y el extracto/XML | Perfil resuelto, base verificada, fuente validado |
| **1 Auditoría** | `AUDITORIA_FMB_vs_APEX.md` con leyenda `✅ migrado · ⚠️ parcial · ❌ falta · ➖ no aplica · ➕ agregado`; secciones: bloques, items, triggers de item, triggers de form, program units, LOVs/record groups, reporte, seguridad, UI. Hallazgos numerados **H-1, H-2…** con severidad. Auditar contra el **export vivo** (`apex_export`), no contra los `.sql` locales. | Auditoría con tabla de resolución en el mismo archivo | Cada trigger/program unit/LOV del original aparece en la tabla |
| **2 Mapa de la lógica** | Leer `references/paridad-forms.md`: dónde vive la lógica en Forms y las trampas de paridad. Grepear cada parámetro del form contra el package, la página y el reporte. | Lista de reglas de negocio a copiar tal cual | Cada regla tiene dueño (package, validación, DA) |
| **3 Construcción** | (0) Compuerta anti-overengineering: ¿hace falta un package? Si Form + IR nativo lo resuelve, usalo; el package es para la **lógica de negocio**. (1) **Package primero**, probado por SQL con casos sintéticos antes de tocar una página. (2) Páginas: **IR (listado + filtros) → ficha**; nunca Interactive Grid para carga ni un Form como página de entrada (`patrones-ui-form.md`). (3) Estilo del perfil, sin HTML armado a mano. (4) Callbacks en la **página**. (5) Si hay `.rdf`: `reportes-rdf.md`. (6) Seguridad al final, con los **mismos roles del Forms**, también en los `ON_DEMAND`. | Package (spec + body) en disco, páginas, export final | Package probado; la página abre y renderiza |
| **4 Verificación** | **Barrido de paridad**: lista de TODOS los procesos, DA y regiones del original marcados CUBIERTO / DIFERENTE / FALTA con evidencia en el código nuevo. Matriz de casos con negativos, diff paramétrico (cada filtro opcional cambia el resultado), clicks reales en el navegador, ledger antes/después. Prueba obligatoria: **Guardar sin tocar nada** + `scripts/diff_columnas.sql` (0 diferencias). Ver `references/verificacion.md`. | Matriz de casos en la auditoría + ledger de datos de prueba | Todo en PASS; lo no probado, declarado |
| **5 Cierre** | Autocrítica (abajo), checklist de entrega, entregables, memoria, limpiar o documentar los datos de prueba. | Auditoría + `ESTADO_MIGRACION.md` + `.sql` en disco + export final | `scripts/comparar_package.py` da IGUALES; tabla de estado actualizada |
| **6 Pase** | `references/produccion.md`: checklist del pase y verificación sin ejecutar el botón que escribe. **El pase lo hace el usuario**: no lo ofrezcas ni lo preguntes. | Inventario del pase y plan de vuelta atrás | Lo dice el usuario |

**Falta de datos en el ambiente no es un cierre válido**: se arma el escenario (sintético contra el package, o sembrado y documentado) y se corre el flujo real.

### Autocrítica antes de entregar (dos preguntas, por escrito)
1. **¿Qué falta capturar?** ¿Algo que corregí sobre la marcha, que me sorprendió, que hice dos veces porque la primera estuvo mal? Si no quedó en memoria, escribirlo **ahora**. Si el contexto se compactó, **re-medir cada cifra y cada «el Forms hace X»** antes de ponerlo en la auditoría.
2. **¿Qué regla que seguí resultó estar mal?** Si una regla de esta skill o una memoria quedó contradicha por el caso real, **corregir el cuerpo de esa regla**, no dejar una nota suelta.

### Checklist de entrega al usuario final
- [ ] La página se llama como la conoce el negocio, sin ids de programa a la vista.
- [ ] Todo proceso largo tiene confirmación, spinner y mensaje con el conteo del resultado.
- [ ] Los patrones visuales están copiados de la aplicación, no inventados.
- [ ] Si se pide manual: solo cómo usarlo, sin portada de «esto es una migración».
- [ ] Cerrar listando lo que **falte o difiera** del form (visual y funcional). Si no falta nada, decirlo.

### Entregables
- `AUDITORIA_FMB_vs_APEX.md` (tabla de resolución, matriz de casos, **ledger de datos de prueba**) y `ESTADO_MIGRACION.md`.
- `.sql` del package con **spec + body completo**, y el export final de la página (sale **de la base**, no de los scripts que se mandaron).
- Respaldo de lo previo en `respaldo_pre_fix/` si tocaste algo existente.
- Si se crea un programa/aplicación nueva: el script de seguridad para el pase.

## 6. Autonomía

**Avanzá sin preguntar** en el ambiente de desarrollo: packages, páginas, datos de prueba documentados, bugs del circuito que migrás.

**Fuera de alcance**: permisos y roles, controles que el original no tiene, refactors. Migrar es reproducir, incluidos los bugs.
Sí entra lo necesario para que el código funcione igual desde APEX (NLS, la cadena de `USER`).

**«Réplica exacta» es literal.** No existe una «diferencia menor a favor del usuario»: completar campos que el Forms deja vacíos,
validar lo que no valida, quitar o cambiar un mensaje, recalcular un total que no recalcula, atrapar un error que el Forms deja volar,
o rehacer un flujo sobre otro backend **cambian la lógica** y se revierten. Solo se aceptan, y se declaran **en el mensaje de cierre**,
las diferencias que impone la web (no hay «registro actual»; cada ventana es una página). Si el Forms llama un procedure standalone, se
llama ese mismo. Si el formulario destino de un botón no está migrado y el pedido es «migración completa», se migra o se dice claramente
que falta y por qué.

**Pará y preguntá** solo ante: escrituras contables irreversibles, decisiones funcionales (se **reportan con recomendación**, no se
deciden), módulos ajenos y cualquier cosa en producción. Lo que funcionó siempre: documentar la decisión funcional como abierta y
seguir con todo lo demás.

## 7. Hábitos

| Buen hábito | Mal hábito |
|---|---|
| Auditar antes de tocar, con hallazgos numerados | Corregir primero y «después documento» |
| Comparar contra el `.fmb` en cada decisión | Decidir por lo que «tiene sentido» |
| Ledger antes/después de cada corrida | Mirar solo el mensaje de éxito |
| Medir en el DOM lo que se ve | Sacar una captura y suponer |
| Probar el negativo de cada validación | Probar solo que guarda |
| Reproducir el defecto del Forms y documentarlo como «heredado» | «Mejorarlo» y llamarlo diferencia menor |
| Leer cada item con su `Formula`/`CalculateMode` y cada trigger de bloque | Fiarse de un volcado que no los trae |
| Una consulta lenta del Forms se compara por lógica y se declara | Dejar una consulta de 30 min bloqueando la base |
| Respaldar antes de re-importar o recompilar | Confiar en que «se puede volver atrás» |
| Copiar la regla de habilitación del trigger del Forms (`HABILITA_*`) | Ponerla de memoria o como la describió alguien |
| Declarar lo no probado | Rellenar con «debería andar» |

## 8. Automejora (obligatorio)

1. Cada gotcha que cueste más de 2 intentos se escribe en memoria **antes** de seguir.
2. Un hallazgo que corrige una creencia previa **actualiza la memoria vieja**, no crea una paralela.
3. Al cerrar, actualizá esta skill (y la tabla de estado del proyecto) si el proceso cambió. Lo específico del cliente va al **perfil**, no acá.
4. Consultá al advisor antes de comprometerte a un enfoque, cuando un hallazgo cambia el alcance y antes de declarar terminado (con el entregable ya guardado).
5. Nada de verdades sin verificar en memoria: si es inferencia, escribí «sin confirmar».
