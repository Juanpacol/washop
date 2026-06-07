-- =============================================
-- SCRIPT INICIAL: RED SOCIAL (SIN RELACIONES)
-- Corresponde al punto de partida entregado
-- en el enunciado del examen final.
-- Las FK y el CHECK se agregan en 02_alter_constraints.sql
-- usando ALTER TABLE, tal como pide la Fase 1.
-- =============================================

-- 1. Tabla de Usuarios
CREATE TABLE usuarios (
    id_usuario     SERIAL PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    email          VARCHAR(100) UNIQUE NOT NULL,
    fecha_registro DATE DEFAULT CURRENT_DATE,
    pais           VARCHAR(50)
);

-- 2. Tabla de Publicaciones (Posts)
-- autor_id existe pero aún no tiene FK — campo huérfano de relación
CREATE TABLE publicaciones (
    id_publicacion    SERIAL PRIMARY KEY,
    texto_contenido   TEXT,
    fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    likes_contador    INT DEFAULT 0,
    autor_id          INT NOT NULL
);

-- 3. Tabla de Comentarios
-- usuario_id y publicacion_id existen pero sin FK — campos huérfanos
CREATE TABLE comentarios (
    id_comentario    SERIAL PRIMARY KEY,
    contenido        VARCHAR(255),
    fecha_comentario TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id       INT NOT NULL,
    publicacion_id   INT NOT NULL
);

-- 4. Tabla de Amistades (Relación Muchos a Muchos)
-- sin FK ni CHECK — permite auto-amistad y referencias inválidas
CREATE TABLE amistades (
    id_amistad             SERIAL PRIMARY KEY,
    fecha_amistad          DATE DEFAULT CURRENT_DATE,
    estado                 VARCHAR(20),
    usuario_solicitante_id INT NOT NULL,
    usuario_receptor_id    INT NOT NULL
);
