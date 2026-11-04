# Migraciones Forms 6i → APEX (app 400) — índice y estado

> **El proceso completo está en `SKILL.md`** (esta misma skill). Este archivo es el **índice y el estado del circuito**:
> qué formulario está en qué etapa. Se actualiza al cerrar cada migración.

## Cómo arrancar

1. Seguir `SKILL.md` (proceso, reglas, verificación, cierre y pase a producción).
2. Consultar `references/apex-api/` (APIs de APEX) y `references/mapeo/` (mapeo Forms→APEX).
3. Verificar la base: `SELECT SYS_CONTEXT('USERENV','SERVER_HOST')` → `desa` = DEVNEW, `db12c-prod` = SANTA.

Contenido de la skill:

| Archivo | Contenido |
|---|---|
| `SKILL.md` | Fases, reglas duras, definición de terminado, autonomía, buenos/malos hábitos |
| `references/paridad-forms.md` | Mapa de triggers y las trampas de paridad que costaron migraciones |
| `references/verificacion.md` | Matriz obligatoria de casos, método de prueba, pruebas sintéticas, llamadores |
| `references/gotchas-apex.md` | `wwv_flow_api`, IR, DAs, re-import server-side de una página existente |
| `references/reportes-rdf.md` | `.rdf` → PDF de referencia → JRXML: errores conocidos, coordenadas, integración |
| `references/produccion.md` | Checklist del pase a SANTA y verificación en producción |
| `references/patrones-ui-form.md` | Listado IR + ficha, navegación entre registros, botonera flotante, badge, guardado sin pérdida de datos |
| `references/apex-api/`, `references/mapeo/`, `references/internals/` | APIs de APEX, mapeo Forms→APEX, internals `wwv_flow_*`, JasperReports |
| `plantillas/` | Esqueletos de `AUDITORIA_FMB_vs_APEX.md` y `ESTADO_MIGRACION.md` |

Referencia **técnica** complementaria (tablas `wwv_flow_*` columna por columna, plantilla de package,
integración JasperReports, parsing del XML de Forms): `references/guia-wwv-flow.md`.

## Estado de las migraciones

| Prog. | Form | Páginas | Programa APEX | Estado |
|---|---|---|---|---|
| **72** | `talon_cheque_det` | 1141 / 1142 | 1483 | Listo (DEVNEW) |
| **827** | `ORD_PAGO` | 1139 / 1140 / 1191 / 1205 / 1210 / 1211 | 1411 | Listo (DEVNEW); 06/10/2026: 12 ajustes del `.docx` + 4 defectos latentes aplicados y probados E2E (serie/nro de cheque, defaults, miles, firmas del PDF). Pase a SANTA pendiente. Ver `AJUSTES_827_2026-10-06.md`. **02/11/2026: auditoría completa contra el `.fmb`** (`AUDITORIA_FMB_vs_APEX_2026-11-02.md`): faltaba `GRABA_CHEQUE` (PAGO_CT de canje/tarjetas) y otras 4 piezas, corregidas y probadas en DEVNEW (`PKG_APEX_OP_CHEQUE_DET`); abiertas las 7 validaciones `Never` de la 1140 y la disponibilidad por defecto. **03/11/2026: pasado a DESA02 (datos de producción) y probado allí** los 6 conceptos (16, 17, 19, 20, 78, 79) con cheque real (talón + programa 72 + PDF del cheque) y efectivo, «Ver Asiento», anulación con contra-asiento y PDF de la OP; corregidos en DEVNEW y DESA02: botón «Eliminar» (1140/1191, usaba una variable inexistente), `imprimir_orden_pago` movido a proceso de la página 1140, validación de centro de costo de la 1211 (item per-request). Exports finales en `827 - Orden Pago/export_final_2026-11-03/`. **04/11/2026: paridad con el Forms aplicada y probada en DEVNEW y DESA02** (7 validaciones de la 1140 reactivadas, Disponibilidad Origen por parámetro 2190/2191, moneda del pago fija en Gs, campos no editables en OP/detalle existentes; script en `827 - Orden Pago/paridad_forms_2026-11-04/`). Abierto: quién avanza `SER_CHEQUE.ULT_NRO` (Tesorería) y fila `DET_CTA_SUC` 2/17/1/876 para usar los conceptos 19/20 |
| **926** | `talon_cheque` | 1156 / 1157 | 1484 | Listo (DEVNEW), 3 decisiones funcionales abiertas |
| **6201** | `pago_prepaga` | 1215 / 1216 / 1217 / 1219 | — | 23/09/2026: H-1…H-29 resueltos y probados en DEVNEW, incluidos los 5 recibos en Jasper y roles sincronizados. Listo para pase manual. Ver `ESTADO_MIGRACION.md` |
| **6252** | `generar_contrato_aut_otro_cto` | 1250 / 1251 | 6252 | Listo (DEVNEW), E2E en navegador; 3 decisiones abiertas |
| **6143** | `cambio_plan` | 1116 | 1384 | **En producción y verificado** el 23/09/2026 (ticket 7536); 2 decisiones abiertas |
| **6229** | `procesar_pago_masivo` | 1163 | 1480 | 03/11/2026, DESA02: migración vieja corregida. UI rehecha (marcos, grilla de 12, diálogo 1000 px, tabla de formas de pago como Classic Report), **error ORA-20999 «Bco.4-FP.7» resuelto** (los campos condicionales de la forma de pago quedaban pegados al cambiar de forma), botón **Imprimir Planilla** con `REP_ARC_EMPRESA` en Jasper (.160) + `PKG_REP_PAGO_MASIVO`, DA de cheque/tarjeta que nunca disparaba. Probado en navegador de punta a punta (proceso 4718 procesado). **Abiertas:** H-5 (nro de comprobante obligatorio como en el Forms) y H-7. Pase a SANTA pendiente. Ver `6229 - Procesar Pago Masivo/ESTADO_MIGRACION.md` |
| **6634** | `fr_rend_tesoreria` (pantalla de impresión «Recibos Tesoreria») | 1258 | 1492 | 03/11/2026, DESA02: página de filtros + validaciones del Forms, botón Visualizar por Jasper (`REP_REND_TESORERIA2`, `PKG_REP_REND_TESORERIA`), comparado contra RWRUN60. 04/11/2026: migrados también `REP_REND_TESORERIA` (el que sale por defecto, `PKG_REP_REND_TESORERIA_ORIG`) y `REP_TESOR_TIPO_CTO` + items Destino/Nuevo Reporte, PDF = original. **Abiertos:** denegación sin probar; filtros opcionales de los reportes nuevos sin comparar. El «duplicado» del ticket ST_8215 es de datos (recibos huérfanos), ver `DIAGNOSTICO_ST_8215…`. Pase a SANTA pendiente. Ver `6634 - fr_rend_tesoreria/ESTADO_MIGRACION.md` |
| **6205** | Visaciones v2 (piloto en paralelo a la 469/470/479, ya en APEX) | 1469 / 1470 / 1479 | 1486 | 25/09/2026: DEVNEW, servidor autoritativo (cálculo sellado), reglas tal cual la v1, UI nativa; revisión integral corregida. Listo para pase manual. Ver `6205 - Visaciones/v2/` |
| **6212** | `prestador_ord_pago_prepaga` | 1143 / 1144 / 1239–1248 (12 páginas; 1245 = planilla de OP) | 1487 (consola) + 1488 (planilla 941000) | 07/10/2026: DEVNEW, **réplica exacta del Forms** (se revirtieron las "mejoras" de la 1.ª entrega; defectos del Forms reproducidos y documentados). Consola + acciones 1 (factura, con FE), 2 (NC, con FE), 3 (planilla de OP, formulario 941000) y 5 (unificar) probadas E2E en navegador. **Botón 4 (Trans, formulario 941001)**: migrado en 941001 (12/10/2026). **833 no abre NC nuevas** (defecto ajeno H-18). Pase a SANTA pendiente. Ver `6212 - Prestador Orden Pago Prepaga/ESTADO_MIGRACION.md` |
| **941001** | `pago_trans_prest_prep` (botón 4 del 6212) | 1256 (transacción) / 1257 (retención); talón = 1157 del 926 | 1491 | 12/10/2026: **operativo en DEVNEW de punta a punta** (TRANS, asiento, talón desde la 1157 con Forzar, impresión, fecha de entrega, retención con PDF de Jasper, corte del sanatorio igual que el Forms (H-61), seguridad, export APEX). **19/10/2026, cheque por banco:** la 1157 imprime con el formato de cada banco (6 `REP_CHEQUE_*`, verificados contra RWRUN60 por texto y posición). **Abierto:** (1) decisión sobre los bancos sin formato (3, 8, 10, 32, 38, 43, 51, 53): el Forms marca IMPRESO y no imprime (H-62, heredado; hay ~2.800 talones afectados); (2) denegación de BOGADOD (tiene R_PREPAGA, que autoriza el 1491: reportar, no tocar); (3) el ZIP de export es del 12/10 y hay que re-exportarlo; (4) el 72 sigue con el genérico `rep_talon_cheque`. Import en desa02 descartado por directiva (todo en DEVNEW). **26/10/2026: ENTREGADO en DEVNEW** (barrido de paridad completo contra el .fmb, con H-65/H-66/H-67 corregidos; ZIP re-exportado el 26/10 con eso, camino de éxito de impresión probado en UI, H-62 heredado sin control nuevo). Declarado sin probar: denegación en navegador con usuarios sin roles (sin credenciales); BOGADOD PERMITIDO por R_PREPAGA (hallazgo de permisos). **26/10/2026: circuito 827 + 72 + 6212 + 926 + 941001 llevado a DESA02** (16 paquetes, 24 páginas, 5 programas; probado en navegador, incluida la impresión de cheque CONTINENTAL y de retención tras resubir los 8 reportes con datasource `desa02_anam`; DEVNEW ya no imprime esos 8. los 5 bancos restantes probados el 27/10 (PDF y botón Imprimir); denegación verificada en servidor. reporte del 827 (REP_ORD_PAGO_PROV_F) resubido a desa02_anam y probado el 27/10, con el proceso de aplicación imprimir_orden_pago que faltaba. 03/11/2026: clic real en Imprimir del 827 probado en navegador y OP con retención+detalle probada (retención de prueba sembrada y borrada). 04/11/2026: denegación probada en navegador con SANDOVALL (sin roles del circuito): 1139, 1143 y 1156 muestran «Privilegios insuficientes»; la 1256 es diálogo, no abre por URL y su usuario sin roles no llega a ninguna página que la abra). Pase a SANTA lo hace el usuario. Ver `941001 - Cargar Transaccion/ESTADO_MIGRACION.md` |
| **6001** | `contrato_cliente` (+ `Direcciones_contrato`) | 977 (listado) / 991 (ficha) | — | 03/11/2026, **DESA02**: migración vieja rehecha. 977 = IR + filtros sobre colección (tope 100); 991 = página con Anterior/Siguiente entre contratos filtrados, regiones con marco, botonera flotante (patrón 1470) y badge de estado. **Pérdida de datos al guardar corregida** (12 columnas ocultas, titular deshabilitado, direcciones) y bug del filtro Estado. **CERRADA en DESA02 (03/11/2026)**: decisiones A–E aprobadas e implementadas, matriz de pruebas en navegador + diff de columnas (auditoría sección 12). Hallazgos del cierre: el trigger `ACTUALIZA_CONTRATO_DIRECCION` pisaba barrio/ciudad/teléfono del contrato en cada guardado, y el default de `% a Facturar` bloqueaba 838 contratos. Sin migrar por decisión: cupón y asociación de contratos. Pase a SANTA: manual, lo hace el usuario. Patrones en la skill: `references/patrones-ui-form.md` |

Cada carpeta `<nro> - <nombre>/` tiene su `AUDITORIA_FMB_vs_APEX.md`, `ESTADO_MIGRACION.md`, el export de las
páginas y las capturas de antes y después.

Cadena real del circuito de tesorería: **827 paga con cheque → crea el `TALON_CHEQUE` → 926 lo consulta/edita y
contabiliza al poner fecha de entrega → 72 lo imprime.** Los tres van juntos.

## Al cerrar una migración

Actualizá **la tabla de arriba** y, si el proceso cambió, `SKILL.md` o su `references/`: el playbook es uno solo.
