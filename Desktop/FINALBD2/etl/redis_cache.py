# =============================================
# FASE 3 — CACHÉ EN REDIS
# Redis es una base de datos en memoria (RAM).
# Leer de RAM es ~100x más rápido que leer de disco.
# Se usa para guardar temporalmente los datos más
# consultados, con un tiempo de expiración (TTL).
# =============================================

import json
import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_DB

# ─────────────────────────────────────────────
# TTL = Time To Live = tiempo de vida del caché
# 300 segundos = 5 minutos.
# Después de 5 minutos, Redis borra la clave automáticamente
# y la próxima consulta irá directo a PostgreSQL.
# ─────────────────────────────────────────────
CACHE_TTL = 300


def load_to_redis(data: dict) -> None:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

    # ── Clave 1: feed completo ────────────────────────────────────────
    # Guarda el feed_noticias completo como texto JSON.
    # Cuando la GUI pide el feed, lee esta clave en vez de
    # hacer el JOIN en PostgreSQL cada vez.
    # setex = SET con EXpiry (guarda con tiempo de vida).
    r.setex(
        "cache:feed_noticias",          # nombre de la clave
        CACHE_TTL,                       # expira en 5 minutos
        json.dumps(data["feed"], default=str)  # valor: JSON serializado
    )

    # ── Clave 2: contador de likes por publicación ────────────────────
    # Una clave separada para CADA publicación.
    # Formato: "likes:publicacion:1", "likes:publicacion:2", etc.
    # Permite actualizar el contador de una publicación específica
    # sin invalidar el caché de las demás.
    for p in data["publicaciones"]:
        r.setex(
            f"likes:publicacion:{p['id_publicacion']}",
            CACHE_TTL,
            p["likes_contador"]
        )

    # ── Clave 3: total de usuarios ────────────────────────────────────
    # Número simple para mostrar en el dashboard sin consultar la BD.
    r.setex("cache:total_usuarios", CACHE_TTL, len(data["usuarios"]))

    print(f"[Redis] Feed, {len(data['publicaciones'])} contadores de likes y total usuarios cacheados.")


def get_feed_from_cache() -> list | None:
    """
    Intenta leer el feed desde Redis.
    Si la clave expiró o no existe, retorna None
    y el llamador debe ir a PostgreSQL.
    """
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    raw = r.get("cache:feed_noticias")
    return json.loads(raw) if raw else None
