-- =============================================
-- FASE 1: INGENIERÍA Y NORMALIZACIÓN EN SQL
-- =============================================
-- El script inicial (01_schema.sql) tiene las tablas
-- sin restricciones de integridad — campos huérfanos.
-- Este archivo aplica ALTER TABLE para agregar:
--   • Llaves Foráneas (FK) con ON DELETE CASCADE
--   • Restricciones CHECK de integridad de datos
--   • Índices de rendimiento en columnas de JOIN frecuente
-- =============================================


-- ─────────────────────────────────────────────
-- TABLA: publicaciones
-- Problema original: autor_id no tenía FK.
-- Un autor_id inválido podía insertarse sin error.
-- Solución: agregar FK que apunta a usuarios(id_usuario).
-- ON DELETE CASCADE: si el usuario se borra,
-- sus publicaciones también se eliminan automáticamente.
-- ─────────────────────────────────────────────
ALTER TABLE publicaciones
    ADD CONSTRAINT fk_pub_autor
        FOREIGN KEY (autor_id)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE;


-- ─────────────────────────────────────────────
-- TABLA: comentarios
-- Problema original: usuario_id y publicacion_id sin FK.
-- Podían existir comentarios de usuarios que no existían
-- o comentarios en publicaciones eliminadas.
-- Solución: dos FK con CASCADE para ambos campos.
-- ─────────────────────────────────────────────
ALTER TABLE comentarios
    ADD CONSTRAINT fk_com_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE;

ALTER TABLE comentarios
    ADD CONSTRAINT fk_com_publicacion
        FOREIGN KEY (publicacion_id)
        REFERENCES publicaciones(id_publicacion)
        ON DELETE CASCADE;


-- ─────────────────────────────────────────────
-- TABLA: amistades
-- Problema original: tres campos sin restricción.
--
--   1. usuario_solicitante_id y usuario_receptor_id sin FK:
--      Permitían amistades con usuarios inexistentes.
--
--   2. estado sin CHECK:
--      Podía contener cualquier texto ('RECHAZADA', 'xyz', etc.)
--      rompiendo la lógica de negocio.
--
--   3. Sin restricción de auto-amistad:
--      Un usuario podía agregarse a sí mismo.
--
-- Solución: dos FK con CASCADE + dos CHECK.
-- ─────────────────────────────────────────────
ALTER TABLE amistades
    ADD CONSTRAINT fk_am_solicitante
        FOREIGN KEY (usuario_solicitante_id)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE;

ALTER TABLE amistades
    ADD CONSTRAINT fk_am_receptor
        FOREIGN KEY (usuario_receptor_id)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE;

-- CHECK 1: el estado solo puede ser uno de dos valores válidos
ALTER TABLE amistades
    ADD CONSTRAINT chk_estado_valido
        CHECK (estado IN ('ACEPTADA', 'PENDIENTE'));

-- CHECK 2: nadie puede agregarse a sí mismo como amigo
-- Compara los dos IDs; si son iguales, PostgreSQL rechaza la fila
ALTER TABLE amistades
    ADD CONSTRAINT chk_no_auto_amistad
        CHECK (usuario_solicitante_id <> usuario_receptor_id);


-- ─────────────────────────────────────────────
-- ÍNDICES DE RENDIMIENTO
-- Sin índices, cada JOIN escanea toda la tabla (O(n)).
-- Con índices, PostgreSQL va directo a las filas (O(log n)).
-- Se crean en las columnas usadas frecuentemente en WHERE y JOIN.
-- ─────────────────────────────────────────────
CREATE INDEX idx_pub_autor   ON publicaciones(autor_id);
CREATE INDEX idx_com_pub     ON comentarios(publicacion_id);
CREATE INDEX idx_am_solicit  ON amistades(usuario_solicitante_id);
CREATE INDEX idx_am_receptor ON amistades(usuario_receptor_id);
