-- =============================================
-- FASE 2: STORED PROCEDURE
-- Un procedimiento almacenado es lógica de negocio
-- que vive dentro de la base de datos.
-- Ventaja: se ejecuta en el servidor, no en Python,
-- y cualquier aplicación puede llamarlo igual.
-- =============================================

-- ─────────────────────────────────────────────
-- PROCEDURE: crear_amistad(id1, id2)
-- Recibe los IDs de dos usuarios y crea una solicitud
-- de amistad entre ellos, pero SOLO si no existe ya.
--
-- Flujo del procedimiento:
--   Paso 1 — Declarar una variable "existente" para guardar el conteo.
--   Paso 2 — Buscar si ya hay una fila en amistades con esos dos IDs,
--             en cualquier dirección (A→B o B→A).
--   Paso 3 — Si existente > 0: avisar y salir sin insertar nada.
--   Paso 4 — Si no existe: insertar la amistad en estado PENDIENTE.
--
-- El CHECK de la tabla ya se encarga de rechazar id1 = id2,
-- así que el procedimiento no necesita verificar eso.
-- ─────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE crear_amistad(id1 INT, id2 INT)
LANGUAGE plpgsql
AS $$
DECLARE
    -- Variable que recibirá el resultado del COUNT
    existente INT;
BEGIN
    -- ── Paso 2: buscar en ambas direcciones ──────────────────────────
    -- A→B: solicitante=id1, receptor=id2
    -- B→A: solicitante=id2, receptor=id1
    -- Si alguna de las dos existe, el COUNT será >= 1.
    SELECT COUNT(*) INTO existente
    FROM amistades
    WHERE (usuario_solicitante_id = id1 AND usuario_receptor_id = id2)
       OR (usuario_solicitante_id = id2 AND usuario_receptor_id = id1);

    -- ── Paso 3: si ya existe, avisar y salir ─────────────────────────
    -- RAISE NOTICE no lanza un error; solo envía un mensaje
    -- que la GUI puede leer y mostrar en amarillo.
    IF existente > 0 THEN
        RAISE NOTICE 'Ya existe una solicitud entre los usuarios % y %', id1, id2;
        RETURN;
    END IF;

    -- ── Paso 4: crear la solicitud en estado PENDIENTE ───────────────
    -- El receptor deberá aceptarla para que pase a ACEPTADA.
    INSERT INTO amistades (usuario_solicitante_id, usuario_receptor_id, estado)
    VALUES (id1, id2, 'PENDIENTE');

    RAISE NOTICE 'Solicitud de amistad creada entre usuarios % y %', id1, id2;
END;
$$;


-- ─────────────────────────────────────────────
-- PROCEDURE: aceptar_amistad(id1, id2)
-- Cambia el estado de una solicitud PENDIENTE
-- a ACEPTADA, completando el ciclo de amistad.
--
-- Flujo del procedimiento:
--   Paso 1 — Buscar si existe una fila PENDIENTE entre id1 e id2
--             en cualquier dirección (A→B o B→A).
--   Paso 2 — Si no existe solicitud pendiente: avisar y salir.
--   Paso 3 — Si existe: hacer UPDATE a ACEPTADA.
-- ─────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE aceptar_amistad(id1 INT, id2 INT)
LANGUAGE plpgsql
AS $$
DECLARE
    filas_actualizadas INT;
BEGIN
    -- ── Paso 3: actualizar PENDIENTE → ACEPTADA en ambas direcciones ──
    UPDATE amistades
    SET estado = 'ACEPTADA'
    WHERE estado = 'PENDIENTE'
      AND (
          (usuario_solicitante_id = id1 AND usuario_receptor_id = id2)
       OR (usuario_solicitante_id = id2 AND usuario_receptor_id = id1)
      );

    -- GET DIAGNOSTICS captura cuántas filas afectó el UPDATE
    GET DIAGNOSTICS filas_actualizadas = ROW_COUNT;

    -- ── Paso 2: si no encontró ninguna solicitud pendiente ────────────
    IF filas_actualizadas = 0 THEN
        RAISE NOTICE 'No existe solicitud PENDIENTE entre los usuarios % y %', id1, id2;
        RETURN;
    END IF;

    RAISE NOTICE 'Amistad entre usuarios % y % aceptada exitosamente', id1, id2;
END;
$$;
