# FASE 6 — Pase a producción y verificación

Los ambientes, conexiones, URLs y particularidades de producción salen del perfil del cliente («Pase a producción»).

## Quién hace qué

El pase **lo hace el usuario**, siempre, después de probar él mismo lo migrado. No se ofrece, no se pregunta y
no se ejecuta por iniciativa propia. Tu trabajo es dejarlo listo y, **si te lo piden**, verificarlo.

## Checklist del pase (va en `ESTADO_MIGRACION.md`)

1. **Respaldar** la página actual en producción (export) antes de importar.
2. **Confirmar que existen en producción, con el mismo id**, los componentes compartidos que la página referencia por
   número: authorization schemes y LOVs. Si no coinciden, la página queda sin autorización o el import falla.
   Se listan en el export con su id (`p_required_role`, `p_named_lov`, `p_rpt_named_lov`).
3. **Compilar el package** (spec + body). Si la spec no cambió, alcanza el body.
4. **Importar la página desde App Builder** (maneja el workspace id; el script exportado trae el del ambiente de
   desarrollo, que puede no ser el de producción).
5. **Regenerar la seguridad** de la página según el perfil (permisos/roles del programa), si el modelo del cliente
   la lleva en tablas propias.
6. **Prueba de humo: abrir y guardar sin cambios** un registro existente, para confirmar que la página carga y que
   el camino de guardado no revienta antes de que lo use nadie.
7. **Probar el caso del ticket sin procesar** (el que originó la migración o la corrección) antes de avisarle al
   área usuaria.
8. **Avisar** al área usuaria una vez verificado.

## Verificación en producción (sólo lectura)

Conectarse a producción **sólo si el usuario lo pide**. Al terminar, **devolver la conexión del cliente/MCP al
ambiente de desarrollo** (el archivo de última conexión del MCP queda apuntando a donde te conectaste, y puede
guardar la contraseña en claro).

Pasos:

1. `oracle_disconnect` primero (su mensaje dice de dónde salías realmente), después `oracle_connect`, después
   **confirmar el host real** con `SYS_CONTEXT('USERENV','SERVER_HOST')` contra el valor que fije el perfil. No
   confiar en el "Target:" del connect.
2. **Package**: `VALID`, misma cantidad de líneas que en desarrollo, marcadores de cada corrección presentes y las
   validaciones viejas ausentes (`user_source` + `user_errors`).
3. **Página**: exportarla de producción y hacer `diff` contra el archivo entregado. Diferencias esperables: el
   exportador y las LOVs compartidas embebidas. Cualquier otra cosa es que el import no entró.
4. **Componentes compartidos**: exportar cada `AUTHORIZATION:<id>` y `LOV:<id>` y confirmar nombre.
5. **Permisos**: el registro del programa y sus roles (tablas de seguridad según el perfil) y los roles del usuario
   que reportó el problema, para confirmar que puede entrar y ver los botones.
6. **Navegador**: entrar a la página, consultar datos reales y verificar el síntoma reportado.
   **Nunca ejecutar el botón que escribe** (Procesar, Guardar, Generar). Mover items, abrir LOVs y consultar sólo
   tocan la colección de la sesión, que es descartable; el botón de proceso toca datos de clientes reales.
7. **Declarar explícitamente** que el camino de escritura no se ejecutó en producción, y que está verificado en
   desarrollo con el mismo código.

## Datos del ambiente de producción

Según el perfil: URL de la aplicación y formato del friendly URL, dónde corre ORDS (puede no estar en el servidor
de la base), comportamientos conocidos del servidor (p. ej. un `apex_authentication.logout` que devuelve error) y de
dónde se obtienen las credenciales de prueba.

## Después de verificar

- Actualizar `ESTADO_MIGRACION.md` y la auditoría con la sección de verificación en producción (qué se comprobó
  y qué no).
- Actualizar la memoria de la migración: de "pase pendiente" a "en producción, verificado el <fecha>".
- Si el ticket lo originó, redactar la respuesta para el ticket: qué fallaba, qué se corrigió, qué tiene que
  hacer el área usuaria y qué decisiones quedan abiertas.

## Trampas del pase vía utl_http + dbms_sql (6201, 7/11/2026)
- Un procedure temporal que hace `utl_http` debe ser `AUTHID CURRENT_USER`: la ACL de red de ANAMNESIS va por rol; con derechos de definidor da ORA-24247 (el bloque anónimo sí funciona).
- Servidor único Python en la PC (POST guarda, GET sirve; `norm` para CRLF→LF) en un puerto libre (el 8765 puede tener un receptor viejo). No guardar `storageState` de Playwright en la carpeta servida. Cerrar y borrar al terminar.
- Comparar el export de SANTA con el de la base fuente byte a byte (`apex_export` componente por componente, POST al receptor, `diff`): es la prueba más fuerte de que seguridad y LOV viajaron.

## El archivo del package en disco no es la fuente del pase (71, 7/11/2026)
- Un parche hecho solo en la base (compilado por el MCP, sin tocar el `.sql`) deja el archivo **desfasado**: el 71 pasó a producción con la versión vieja y se detectó al comparar huellas. Antes de pasar un package, sacar el texto de `user_source` de la base probada (con `create or replace ` delante) y comparar `sum(ora_hash(text||'|'||line))` base contra base; recién ahí cargarlo. Si el cliente MCP compila sin comentarios ni líneas en blanco, la huella solo vale base contra base (no contra el archivo); para localizar una diferencia, hash por línea normalizada en tramos.
- Después del pase, reemplazar el archivo de la carpeta por el compilado y dejar el anterior en `respaldo_pre_fix/`.
- Las decisiones funcionales abiertas se preguntan **antes** del pase con una pregunta cerrada cada una (función de base, LOV, reportes, roles): el 6201 se pasó sin sorpresas porque se resolvieron antes.
