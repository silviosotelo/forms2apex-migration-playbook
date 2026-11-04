-- diff_columnas.sql
-- Prueba obligatoria de "Guardar sin tocar nada": compara TODAS las columnas de una fila contra su respaldo.
-- Detecta lo que el guardado de una ficha migrada pisa sin avisar (items ocultos sin reasignar, items
-- deshabilitados que no viajan en el submit, triggers de tabla, defaults aplicados sobre filas existentes).
--
-- Reemplazar los marcadores y ejecutar por partes (el cliente/MCP del proyecto no soporta SQL*Plus):
--   <TABLA>       tabla (o vista) de la ficha
--   <CLAVE>       columna clave
--   <VALOR>       valor de la clave del registro de prueba (con comillas si es texto)
--   <TABLA_BKP>   nombre del respaldo, de hasta 30 caracteres en Oracle 12.1 (p. ej. ZZ_BKP_<TABLA>_<N>)
--
-- 1) RESPALDO (antes de abrir la ficha)
--    CREATE TABLE <TABLA_BKP> AS SELECT * FROM <TABLA> WHERE <CLAVE> = <VALOR>;
--
-- 2) En el navegador: abrir el registro y pulsar Guardar SIN modificar nada.
--
-- 3) DIFF: devuelve una fila por cada columna que cambio. Resultado esperado: 0 filas.
WITH a AS (
  SELECT x.col, x.val
    FROM XMLTABLE('/ROWSET/ROW/*'
           PASSING dbms_xmlgen.getxmltype('SELECT * FROM <TABLA_BKP>')
           COLUMNS col VARCHAR2(128) PATH 'name()', val VARCHAR2(4000) PATH '.') x
), b AS (
  SELECT x.col, x.val
    FROM XMLTABLE('/ROWSET/ROW/*'
           PASSING dbms_xmlgen.getxmltype('SELECT * FROM <TABLA> WHERE <CLAVE> = <VALOR>')
           COLUMNS col VARCHAR2(128) PATH 'name()', val VARCHAR2(4000) PATH '.') x
)
SELECT NVL(a.col, b.col) AS columna, a.val AS antes, b.val AS despues
  FROM a FULL OUTER JOIN b ON a.col = b.col
 WHERE DECODE(a.val, b.val, 0, 1) = 1;   -- DECODE trata NULL = NULL como igual
--
-- 4) Si hay diferencias: comparar cada columna distinta contra el SET del UPDATE del package y contra lo
--    que asigna el proceso Guardar de la pagina (ver references/patrones-ui-form.md, "Guardado sin perdida").
--
-- 5) RESTAURAR Y LIMPIAR al cerrar. Ojo con los triggers de la tabla: restaurar primero las tablas HIJAS o
--    las que alimentan al trigger, y despues la tabla padre; si no, el trigger vuelve a pisar la fila.
--    UPDATE <TABLA> SET ROW = (SELECT b FROM <TABLA_BKP> b) WHERE <CLAVE> = <VALOR>;
--    DROP TABLE <TABLA_BKP>;
