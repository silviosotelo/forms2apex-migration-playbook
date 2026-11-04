# Del `.fmb` / `.rdf` al análisis

El proceso de migración, las reglas y el estilo están en `SKILL.md`. Acá solo está **cómo obtener el contenido del binario**.

Los `.fmb` (Forms) y `.rdf` (Reports) 6i son binarios propietarios con la cabecera `ROS.60050`. Hay tres rutas; se elige según lo que haya instalado:

| Ruta | Requiere | Qué entrega |
|---|---|---|
| **A. Forms2XML** (`frmf2xml`) | Oracle Forms 12c (`frmf2xml.bat`) o los `.jar` + `frmjapi.dll` | **Todo**: lógica y propiedades (tipo/longitud/obligatorio de cada item, LOV asociada, canvases, relaciones, alertas) |
| **B. Extractor** (`scripts/extraer_fmb_rdf.py`) | Solo Python 3 | La **lógica**: triggers (con su dueño), program units, SQL, referencias `:BLOQUE.ITEM`, llamadas a otros módulos |
| **C. Reportes con RWCON60** | Oracle Reports 6i (`RWCON60.EXE`) | Coordenadas y queries del `.rdf` (`.rex`); ver `reportes-rdf.md` |

Si no tenés Oracle, **la ruta B alcanza para auditar y migrar la lógica**; las propiedades de los items se completan con el diccionario de
la base y con el usuario (ver «Qué completar a mano»).

## Ruta A — Forms2XML

- Desde **PowerShell**, con `ORACLE_HOME` apuntando a la instalación de Forms 12c: `frmf2xml.bat <modulo>.fmb` genera `<modulo>_fmb.xml`.
- El conversor basado en `.jar` (`frmjdapi.jar`, `frmxmltools.jar`, `xmlparserv2.jar`) falla si falta la librería nativa `frmjapi.dll`.
- **Copiar el `.fmb` a una carpeta sin espacios** antes de convertir; los conversores fallan con espacios en la ruta.
- Para `.rdf`, el `rdf2xml.jar` de terceros depende de clases de Oracle Reports que no vienen en el jar (`oracle.reports.utility.Rdf2Xml`): sin el
  middleware no corre. Usá la ruta B.
- El XML tiene el espacio de nombres `http://xmlns.oracle.com/Forms`; los elementos relevantes son `FormModule`, `Block`, `Item`, `Trigger`
  (`TriggerText`), `ProgramUnit` (`ProgramUnitText`), `RecordGroup`, `LOV`, `Canvas`, `Window`, `Alert`.

## Ruta B — Extractor sin Oracle

```
python scripts/extraer_fmb_rdf.py MODULO.fmb              # escribe MODULO_extracto.md y .json junto al archivo
python scripts/extraer_fmb_rdf.py MODULO.fmb -o salida    # carpeta de salida
python scripts/extraer_fmb_rdf.py REPORTE.rdf             # reportes: PL/SQL de los triggers y SQL de las queries
python scripts/extraer_fmb_rdf.py MODULO.fmb --verificar OTRO_fmb.xml   # mide cuánto recupera contra un XML de Forms2XML
```

**Cómo funciona**: el formato guarda el texto en claro, con prefijos de longitud. Cada trigger termina con su nombre y su dueño
(`WHEN-BUTTON-PRESSED (BLOQUE.ITEM)`); los program units van con un largo de 2 bytes; las queries son cadenas que empiezan con `SELECT`/`WITH`.
El script reconstruye esas estructuras y, además, arma el mapa de referencias `:BLOQUE.ITEM` que usa el código.

**Fiabilidad medida** contra Forms2XML en tres formularios reales:

| Formulario | Triggers | Program units |
|---|---|---|
| A (56 triggers, 35 PU) | 54/56 | 33/35 |
| B (48 triggers, 30 PU) | 47/48 | 29/30 |
| C (20 triggers, 14 PU) | 20/20 | 12/14 |

Los pocos que faltan son program units con bytes binarios incrustados o bibliotecas estándar de Forms. **Tomalo como extracto de auditoría,
no como espejo exacto**: antes de declarar «el Forms no tiene X», buscá también el nombre con `strings`/`grep` sobre el binario, y si dudás, confirmalo con el usuario.
Para repetir la medición sobre un archivo propio, usá `--verificar` con cualquier XML disponible.

### Qué NO recupera (y cómo se completa a mano)
| Falta | Cómo se completa |
|---|---|
| Tipo, longitud y obligatoriedad de cada item | `all_tab_columns` de la tabla base del bloque + la pantalla original o el usuario |
| LOV asociada a cada item, columnas de retorno | Los SQL del extracto (record groups) + preguntar qué LOV usa cada campo |
| Qué items son de pantalla vs. de base (`Database Item`, `Calculated`, `Formula`) | Preguntar al usuario; las fórmulas calculadas suelen verse como asignaciones en los triggers |
| Canvases, tabs, posiciones, orden de tabulación | Capturas del formulario original; son decisión de diseño en la web |
| Relaciones master-detail y su criterio | `all_constraints` (FK) y los `WHERE` del extracto |
| Alertas y mensajes | Los textos que aparecen como argumento de `MESSAGE(...)`/`SHOW_ALERT` en los triggers |

Todo lo que no se pueda confirmar se anota en la auditoría como **«propiedad sin verificar»**, nunca como supuesto.

## Reglas de manejo
- Los fuentes originales son de **solo lectura**: copiar a local, procesar la copia, no modificar ni mover nada en el servidor.
- Guardar el extracto/XML junto a la migración (`<nro> - <nombre>/`): es la base de la auditoría y sobrevive a una compactación de contexto.
- Si hay varias copias del `.fmb`, comparar hash y validar el fuente contra la base (una columna inexistente delata que es de otra base).

## Siguientes pasos
- `references/paridad-forms.md` — dónde vive la lógica en Forms y las trampas de paridad.
- `references/internals/forms-mapping.md` y `references/mapeo/` — equivalencias Forms → APEX.
- `plantillas/package-template.sql` — esqueleto del package.
