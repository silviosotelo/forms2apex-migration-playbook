# FASE 6 — Pase a producción (SANTA) y verificación

## Quién hace qué

El pase **lo hace el usuario**, siempre, después de probar él mismo lo migrado. No se ofrece, no se pregunta y
no se ejecuta por iniciativa propia. Tu trabajo es dejarlo listo y, **si te lo piden**, verificarlo.

## Checklist del pase (va en `ESTADO_MIGRACION.md`)

1. **Respaldar** la página actual de SANTA (export) antes de importar.
2. **Confirmar que existen en SANTA, con el mismo id**, los componentes compartidos que la página referencia por
   número: authorization schemes y LOVs. Si no coinciden, la página queda sin autorización o el import falla.
   Se listan en el export con su id (`p_required_role`, `p_named_lov`, `p_rpt_named_lov`).
3. **Compilar el package** (spec + body). Si la spec no cambió, alcanza el body.
4. **Importar la página desde App Builder** (maneja el workspace id; el script trae el de DEVNEW, 110000).
5. **Probar el caso del ticket sin procesar** antes de avisarle al área usuaria.

## Verificación en producción (sólo lectura)

Conectarse a SANTA **sólo si el usuario lo pide**. Al terminar, **devolver la conexión del MCP a DEVNEW**
(el archivo de última conexión del MCP queda apuntando a donde te conectaste, y guarda la contraseña en claro).

Pasos:

1. `oracle_disconnect` primero (su mensaje dice de dónde salías realmente), después `oracle_connect`, después
   **confirmar `SYS_CONTEXT('USERENV','SERVER_HOST') = 'db12c-prod'`**. No confiar en el "Target:" del connect.
2. **Package**: `VALID`, misma cantidad de líneas que DEVNEW, marcadores de cada corrección presentes y las
   validaciones viejas ausentes (`user_source` + `user_errors`).
3. **Página**: exportarla de SANTA y hacer `diff` contra el archivo entregado. Diferencias esperables: el
   exportador y las LOVs compartidas embebidas. Cualquier otra cosa es que el import no entró.
4. **Componentes compartidos**: exportar cada `AUTHORIZATION:<id>` y `LOV:<id>` y confirmar nombre.
5. **Permisos**: `PROGRAMA` (tipo `APEX`, `ID_PAGE_APEX` correcto), `PROGRAMA_ROL` y los roles del usuario que
   reportó el problema (`SYS.PRIVILIGES`), para confirmar que puede entrar y ver los botones.
6. **Navegador**: entrar a la página, consultar datos reales y verificar el síntoma reportado.
   **Nunca ejecutar el botón que escribe** (Procesar, Guardar, Generar). Mover items, abrir LOVs y consultar sólo
   tocan la colección de la sesión, que es descartable; el botón de proceso toca datos de clientes reales.
7. **Declarar explícitamente** que el camino de escritura no se ejecutó en producción, y que está verificado en
   DEVNEW con el mismo código.

## Datos del ambiente de producción

- App 400: `https://sistema.santaclara.com.py/santaclara/f?p=400:<pagina>`
  (el friendly URL duplica el segmento: `/santaclara/santaclara/r/sc/login`).
- **El ORDS de producción NO está en el server de la base**: corre en `192.168.41.12` / `.14` / `.114` detrás de
  nginx. El `192.168.41.23` es sólo la base.
- `apex_authentication.logout` devuelve **500** en ese servidor; la sesión de prueba caduca sola.
- Login con el usuario de base de PROD; la contraseña está en el `.env` del backend de e-sign.

## Después de verificar

- Actualizar `ESTADO_MIGRACION.md` y la auditoría con la sección de verificación en producción (qué se comprobó
  y qué no).
- Actualizar la memoria de la migración: de "pase pendiente" a "en producción, verificado el <fecha>".
- Si el ticket lo originó, redactar la respuesta para el ticket: qué fallaba, qué se corrigió, qué tiene que
  hacer el área usuaria y qué decisiones quedan abiertas.
