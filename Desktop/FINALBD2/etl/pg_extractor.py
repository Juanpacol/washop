# =============================================
# FASE 3 — EXTRACCIÓN DESDE POSTGRESQL
# Técnica: Zero-shot
# Las consultas son SQL estándar directo;
# no se necesitan ejemplos previos porque
# el lenguaje es determinista y sin ambigüedad.
# =============================================

import os
import psycopg2
import psycopg2.extras
from config import POSTGRES_CONFIG

# ─────────────────────────────────────────────
# Fix de encoding para Windows
# En Windows con locale español, psycopg2 puede
# recibir mensajes de error en Latin-1 y fallar
# al decodificarlos como UTF-8.
# Forzar UTF-8 en la conexión evita ese error.
# ─────────────────────────────────────────────
os.environ.setdefault("PGCLIENTENCODING", "UTF8")


def get_connection():
    """Crea y retorna una conexión a PostgreSQL usando los datos de config.py."""
    return psycopg2.connect(**POSTGRES_CONFIG)


def extract_all() -> dict:
    """
    Extrae todas las entidades de PostgreSQL y las retorna como listas de dicts.

    RealDictCursor hace que cada fila llegue como un diccionario
    {columna: valor} en lugar del tuple (valor1, valor2, ...) por defecto.
    Eso permite acceder a los datos por nombre: fila["nombre"] en vez de fila[0].
    """
    conn = get_connection()

    # RealDictCursor: filas como dicts → fácil de pasar a MongoDB y Cassandra
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # ── Extraer tabla completa de usuarios ───────────────────────────
    cur.execute("SELECT * FROM usuarios;")
    usuarios = [dict(r) for r in cur.fetchall()]

    # ── Extraer publicaciones ─────────────────────────────────────────
    cur.execute("SELECT * FROM publicaciones;")
    publicaciones = [dict(r) for r in cur.fetchall()]

    # ── Extraer comentarios ───────────────────────────────────────────
    cur.execute("SELECT * FROM comentarios;")
    comentarios = [dict(r) for r in cur.fetchall()]

    # ── Extraer la vista feed_noticias (creada en Fase 2) ────────────
    # Esta vista ya tiene el JOIN y el COUNT calculados por PostgreSQL.
    # Se reutiliza aquí para cachear el resultado en Redis (Paso 4).
    cur.execute("SELECT * FROM feed_noticias;")
    feed = [dict(r) for r in cur.fetchall()]

    cur.close()
    conn.close()

    # Retornar todo en un solo diccionario para pasarlo entre módulos
    return {
        "usuarios":      usuarios,
        "publicaciones": publicaciones,
        "comentarios":   comentarios,
        "feed":          feed,
    }
