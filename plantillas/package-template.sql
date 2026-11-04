-- Template: PKG_<ENTITY>
-- Un solo paquete por entidad. Queries, DML, validaciones y lógica juntos.
-- BULK operations obligatorias. Sin COMMIT interno.

CREATE OR REPLACE PACKAGE PKG_<ENTITY> AS

  -- === QUERIES ===

  FUNCTION get_lista(
    p_fecha_desde  DATE     DEFAULT NULL,
    p_fecha_hasta  DATE     DEFAULT NULL,
    p_filtro1      NUMBER   DEFAULT NULL,
    p_filtro2      VARCHAR2 DEFAULT NULL,
    p_estado       VARCHAR2 DEFAULT NULL
  ) RETURN SYS_REFCURSOR;

  FUNCTION get_detalle(p_id NUMBER) RETURN SYS_REFCURSOR;

  -- === DML ===

  PROCEDURE guardar(
    p_id       IN OUT NUMBER,  -- NULL = insert, NOT NULL = update
    p_campo1   VARCHAR2,
    p_campo2   NUMBER,
    p_campo3   DATE,
    p_usuario  VARCHAR2
  );

  PROCEDURE eliminar(p_id NUMBER);

  -- === VALIDACIONES ===

  PROCEDURE validar(
    p_id       NUMBER,
    p_campo1   VARCHAR2,
    p_campo2   NUMBER
  );  -- raise_application_error si falla

  -- === LÓGICA DE NEGOCIO ===

  PROCEDURE procesar(p_id NUMBER, p_usuario VARCHAR2);
  PROCEDURE anular(p_id NUMBER, p_usuario VARCHAR2);

  -- === BULK ===

  PROCEDURE procesar_lote(p_ids IN sys.odcinumberlist, p_usuario VARCHAR2);

END PKG_<ENTITY>;
/

CREATE OR REPLACE PACKAGE BODY PKG_<ENTITY> AS

  -- === QUERIES ===

  FUNCTION get_lista(
    p_fecha_desde  DATE     DEFAULT NULL,
    p_fecha_hasta  DATE     DEFAULT NULL,
    p_filtro1      NUMBER   DEFAULT NULL,
    p_filtro2      VARCHAR2 DEFAULT NULL,
    p_estado       VARCHAR2 DEFAULT NULL
  ) RETURN SYS_REFCURSOR IS
    v_cursor SYS_REFCURSOR;
  BEGIN
    OPEN v_cursor FOR
      SELECT t.id, t.campo1, t.campo2,
             TO_CHAR(t.fecha, 'DD/MM/YYYY') AS fecha_fmt,
             TO_CHAR(t.importe, 'FM999G999G999G990D00') AS importe_fmt,
             CASE t.estado
               WHEN 'A' THEN '<span style="color:green;font-weight:bold">Activo</span>'
               WHEN 'I' THEN '<span style="color:red">Inactivo</span>'
             END AS estado_html
      FROM <table> t
      WHERE (p_fecha_desde IS NULL OR t.fecha >= p_fecha_desde)
        AND (p_fecha_hasta IS NULL OR t.fecha <= p_fecha_hasta)
        AND (p_filtro1 IS NULL OR t.id_filtro1 = p_filtro1)
        AND (p_filtro2 IS NULL OR t.filtro2 LIKE '%' || p_filtro2 || '%')
        AND (p_estado IS NULL OR t.estado = p_estado)
      ORDER BY t.fecha DESC, t.id DESC;
    RETURN v_cursor;
  END;

  FUNCTION get_detalle(p_id NUMBER) RETURN SYS_REFCURSOR IS
    v_cursor SYS_REFCURSOR;
  BEGIN
    OPEN v_cursor FOR
      SELECT * FROM <table> WHERE id = p_id;
    RETURN v_cursor;
  END;

  -- === DML ===

  PROCEDURE guardar(
    p_id       IN OUT NUMBER,
    p_campo1   VARCHAR2,
    p_campo2   NUMBER,
    p_campo3   DATE,
    p_usuario  VARCHAR2
  ) IS
  BEGIN
    validar(p_id, p_campo1, p_campo2);

    IF p_id IS NULL THEN
      INSERT INTO <table> (campo1, campo2, campo3, usuario_alta, fecha_alta)
      VALUES (p_campo1, p_campo2, p_campo3, p_usuario, SYSDATE)
      RETURNING id INTO p_id;
    ELSE
      UPDATE <table>
      SET campo1 = p_campo1,
          campo2 = p_campo2,
          campo3 = p_campo3,
          usuario_modif = p_usuario,
          fecha_modif = SYSDATE
      WHERE id = p_id;

      IF SQL%ROWCOUNT = 0 THEN
        raise_application_error(-20001, 'Registro no encontrado: ' || p_id);
      END IF;
    END IF;
  END;

  PROCEDURE eliminar(p_id NUMBER) IS
  BEGIN
    DELETE FROM <table> WHERE id = p_id;
    IF SQL%ROWCOUNT = 0 THEN
      raise_application_error(-20002, 'Registro no encontrado: ' || p_id);
    END IF;
  END;

  -- === VALIDACIONES ===

  PROCEDURE validar(
    p_id       NUMBER,
    p_campo1   VARCHAR2,
    p_campo2   NUMBER
  ) IS
  BEGIN
    IF p_campo1 IS NULL THEN
      raise_application_error(-20010, 'Campo1 es obligatorio');
    END IF;
    IF p_campo2 < 0 THEN
      raise_application_error(-20011, 'Campo2 no puede ser negativo');
    END IF;
    -- Validación de unicidad
    DECLARE
      v_count NUMBER;
    BEGIN
      SELECT COUNT(*) INTO v_count FROM <table>
      WHERE campo1 = p_campo1 AND (p_id IS NULL OR id != p_id);
      IF v_count > 0 THEN
        raise_application_error(-20012, 'Ya existe un registro con ese Campo1');
      END IF;
    END;
  END;

  -- === LÓGICA DE NEGOCIO ===

  PROCEDURE procesar(p_id NUMBER, p_usuario VARCHAR2) IS
  BEGIN
    UPDATE <table>
    SET estado = 'P', fecha_proceso = SYSDATE, usuario_proceso = p_usuario
    WHERE id = p_id AND estado = 'A';

    IF SQL%ROWCOUNT = 0 THEN
      raise_application_error(-20020, 'No se puede procesar: estado inválido');
    END IF;
  END;

  PROCEDURE anular(p_id NUMBER, p_usuario VARCHAR2) IS
  BEGIN
    UPDATE <table>
    SET estado = 'X', fecha_anulacion = SYSDATE, usuario_anulacion = p_usuario
    WHERE id = p_id AND estado IN ('A', 'P');

    IF SQL%ROWCOUNT = 0 THEN
      raise_application_error(-20021, 'No se puede anular: estado inválido');
    END IF;
  END;

  -- === BULK ===

  PROCEDURE procesar_lote(p_ids IN sys.odcinumberlist, p_usuario VARCHAR2) IS
  BEGIN
    FORALL i IN 1..p_ids.COUNT
      UPDATE <table>
      SET estado = 'P', fecha_proceso = SYSDATE, usuario_proceso = p_usuario
      WHERE id = p_ids(i) AND estado = 'A';

    IF SQL%ROWCOUNT = 0 THEN
      raise_application_error(-20030, 'No se procesaron registros');
    END IF;
  END;

END PKG_<ENTITY>;
/
