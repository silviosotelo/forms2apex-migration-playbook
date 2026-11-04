# forms2apex

Skill de Claude Code para **migrar formularios Oracle Forms 6i (`.fmb`) y reportes Oracle Reports (`.rdf`) a Oracle APEX 20.2**
(Oracle 12.1), con la lógica en packages PL/SQL, y para verificar o corregir migraciones ya hechas.

## Qué trae
- **Flujo de trabajo con compuertas** (`SKILL.md`): preparación → auditoría → mapa de la lógica → construcción → verificación → cierre → pase.
- **Extractor sin Oracle** (`scripts/extraer_fmb_rdf.py`): saca triggers, program units, SQL y referencias de un `.fmb`/`.rdf` con solo Python 3,
  sin Oracle Forms, sin Java y sin Forms2XML. Medido contra Forms2XML: 20/20 a 54/56 triggers según el módulo.
- **Scripts de apoyo**: parchar un export de página APEX con conteos (`export_apex.py`), comparar el package en disco contra lo compilado
  (`comparar_package.py`), diff columna a columna antes/después de guardar (`diff_columnas.sql`).
- **Referencias**: paridad Forms→APEX, gotchas de `wwv_flow_api` y APEX 20.2, patrones de UI (listado + ficha), reportes `.rdf` → JasperReports,
  pase a producción, APIs de APEX/Oracle, internals `wwv_flow_*`, mapeo Forms→APEX.
- **Plantillas**: auditoría, estado, tabla de estado, package.
- **Perfiles** (`profiles/`): lo que cambia de un cliente a otro (bases, seguridad, estilo visual, reportes, rutas) vive en un perfil, no en la skill.

## Instalación
Copiar esta carpeta a `~/.claude/skills/forms2apex/`. Para un cliente nuevo: copiar `profiles/_plantilla.md` a
`~/.claude/forms2apex-profiles/<cliente>.md` y completarla; un archivo `.forms2apex-profile` (`profile: <cliente>`) en el proyecto lo selecciona.

## Límite honesto del extractor
Recupera la **lógica**. No recupera propiedades de items, canvases ni posiciones: eso solo lo entrega Forms2XML (Oracle Forms 12c). La skill
indica cómo completar lo que falta (diccionario de la base, usuario) y exige anotarlo como «sin verificar» cuando no se pueda confirmar.
