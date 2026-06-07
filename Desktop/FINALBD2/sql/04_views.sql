-- =============================================
-- FASE 2: VISTAS ANALÍTICAS
-- Una vista es una consulta guardada con nombre.
-- En lugar de escribir el SELECT cada vez,
-- se hace SELECT * FROM nombre_vista.
-- =============================================

-- ─────────────────────────────────────────────
-- VISTA 1: solicitudes_pendientes
-- Muestra las solicitudes de amistad que todavía
-- no han sido aceptadas ni rechazadas.
--
-- Usa dos JOINs a la tabla usuarios con alias distintos
-- (u1 y u2) para obtener el nombre de cada persona:
--   u1 = quien envió la solicitud
--   u2 = quien la recibió
-- ─────────────────────────────────────────────
CREATE OR REPLACE VIEW solicitudes_pendientes AS
SELECT
    a.id_amistad,
    u1.nombre AS solicitante,   -- nombre de quien la envió
    u2.nombre AS receptor,      -- nombre de quien la recibió
    a.fecha_amistad
FROM amistades a
JOIN usuarios u1 ON a.usuario_solicitante_id = u1.id_usuario
JOIN usuarios u2 ON a.usuario_receptor_id   = u2.id_usuario
WHERE a.estado = 'PENDIENTE';   -- solo las que aún no fueron procesadas

-- ─────────────────────────────────────────────
-- VISTA 2: amistades_consolidadas
-- Igual que la anterior pero filtra solo las ACEPTADAS.
-- Representa las amistades reales ya confirmadas.
-- ─────────────────────────────────────────────
CREATE OR REPLACE VIEW amistades_consolidadas AS
SELECT
    a.id_amistad,
    u1.nombre AS usuario_a,
    u2.nombre AS usuario_b,
    a.fecha_amistad
FROM amistades a
JOIN usuarios u1 ON a.usuario_solicitante_id = u1.id_usuario
JOIN usuarios u2 ON a.usuario_receptor_id   = u2.id_usuario
WHERE a.estado = 'ACEPTADA';

-- ─────────────────────────────────────────────
-- VISTA 3: feed_noticias
-- La vista más compleja. Combina tres tablas y agrega datos.
--
-- Decisiones de diseño:
--   • JOIN con usuarios: para mostrar el nombre del autor, no su ID.
--   • LEFT JOIN con comentarios: LEFT porque una publicación puede
--     tener cero comentarios. Con JOIN normal, esas publicaciones
--     desaparecerían del feed.
--   • COUNT(c.id_comentario): cuenta cuántos comentarios tiene cada
--     publicación. El resultado se muestra como "total_comentarios".
--   • GROUP BY: necesario porque usamos COUNT. Agrupa todos los
--     comentarios de cada publicación antes de contarlos.
--   • ORDER BY fecha DESC: las publicaciones más recientes primero.
-- ─────────────────────────────────────────────
CREATE OR REPLACE VIEW feed_noticias AS
SELECT
    u.nombre                   AS autor,
    p.texto_contenido,
    p.fecha_publicacion,
    p.likes_contador,
    COUNT(c.id_comentario)     AS total_comentarios
FROM publicaciones p
JOIN usuarios u         ON p.autor_id       = u.id_usuario
LEFT JOIN comentarios c ON c.publicacion_id = p.id_publicacion
GROUP BY u.nombre, p.texto_contenido, p.fecha_publicacion, p.likes_contador
ORDER BY p.fecha_publicacion DESC;
