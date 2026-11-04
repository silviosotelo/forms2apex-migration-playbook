# Auditoría <NRO> – <NOMBRE> (`<archivo>.fmb`) vs APEX 400 página <NNNN>

- **Fecha:** <dd/mm/aaaa> · **Base:** DEVNEW (`SERVER_HOST = desa`) · APEX 20.2
- **Origen del pedido:** <migración nueva | ticket NNNN: texto del reclamo>
- **Piezas APEX:** página(s) <…> · package <PKG_…> · colección <…> · programa APEX <…> (esquemas <…>)
- **Forms:** bloques <…> (vista/tabla base real según `QueryDataSourceName`), program units <…>
- **SANTA:** <no se consultó | verificado el dd/mm>

Leyenda: ✅ migrado · ⚠️ parcial · ❌ falta / roto · ➖ no aplica en web · ➕ agregado en APEX

---

## 1. Reproducción del problema (sólo si viene de un ticket)

| Paso | Resultado |
|---|---|

## 2. Bloques e items

| Forms | APEX | Estado |
|---|---|---|

## 3. Triggers de item / botones

| Forms | APEX | Estado |
|---|---|---|

## 4. Program units

| Forms | APEX | Estado |
|---|---|---|

## 5. LOVs y Record Groups

| Forms | APEX | Estado |
|---|---|---|

## 6. UI / IR

| Tema | Estado |
|---|---|

## 6b. Layout condicional

Casos de visibilidad/estado dinámico en el Forms (`SET_ITEM_PROPERTY`, `SHOW_VIEW`, `HIDE_VIEW`): **N = <…>**

| Item / canvas | Cuándo cambia en el Forms | Equivalente en APEX | Estado |
|---|---|---|---|

## 7. Seguridad

| Tema | Estado |
|---|---|

## 8. Hallazgos

| # | Sev. | Hallazgo | Acción |
|---|---|---|---|
| H-1 | | | |

## 9. Resolución

Cómo se aplicó: <package compilado / página creada / página re-importada server-side>.

| # | Qué se cambió | Dónde | Verificación en navegador (DEVNEW) |
|---|---|---|---|

### Matriz de casos

| Caso | Cómo se probó | Resultado |
|---|---|---|
| Camino principal | | |
| Variantes del negocio | | |
| Fecha futura | | |
| Moneda alternativa | | |
| Varios registros / grupos | | |
| Rechazos (uno por validación) | | |
| Bloqueos del negocio | | |
| Idempotencia | | |
| Seguridad | | |
| Impresión (PDF **con datos**, comparado contra el original página por página) | | |
| Diff paramétrico (cada filtro opcional cambia el resultado) | | |
| Consola JS sin errores | | |

### Ledger de datos de prueba (DEVNEW)

| Qué | Estado |
|---|---|

### Llamadores (si se cambió código compartido)

<resultado de oracle_dependencies + búsqueda sobre el export de todas las páginas, con control positivo>

### No verificado

- <lo que quedó sin probar y por qué>
