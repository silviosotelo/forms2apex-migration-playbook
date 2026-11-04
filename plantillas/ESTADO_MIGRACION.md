# <NRO> – <NOMBRE> · Estado de la migración

**Estado:** <en construcción | listo en el ambiente de desarrollo, pase manual pendiente | en producción, verificado el dd/mm/aaaa>
**Origen:** <migración nueva | ticket NNNN>

## Qué hace el formulario

<2-4 líneas en lenguaje de negocio: qué resuelve, para quién, qué escribe>

## Qué se hizo

<si es corrección: las causas reales del problema, en lenguaje de negocio, numeradas>
<si es migración nueva: las piezas construidas y las decisiones de diseño relevantes>

## Piezas

| Pieza | Archivo |
|---|---|
| Package (spec + body completo) | `<carpeta de packages>/PKG_<…>.sql` |
| Página(s) APEX (export) | `f<ID_APP>_page_<NNNN>_<NOMBRE>_FINAL.sql` |
| Respaldo de lo previo | `respaldo_pre_fix/` |
| Auditoría + resolución + ledger | `AUDITORIA_FMB_vs_APEX.md` |
| Capturas | `*.png` |

## Cobertura de pruebas

<resumen de la matriz: qué caminos se ejecutaron y contra qué datos; qué quedó sin probar>

## Pase a producción (manual — lo hace el usuario)

0. Respaldar la página en producción y confirmar que existen ahí, con el mismo id, los componentes compartidos:
   <listar esquemas y LOVs con su id>
1. Compilar el package.
2. Importar el export de la página **desde App Builder**.
3. Probar <el caso concreto> sin procesar.

## Riesgos operativos que conviene avisar

<comportamientos heredados del Forms que el usuario debe conocer: commits internos, procesos parciales, etc.>

## Decisiones abiertas (no las decide quien migra)

- <decisión funcional 1>
- <permisos / roles>
