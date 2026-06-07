# =============================================
# CONFIGURACIÓN CENTRALIZADA DE CONEXIONES
# =============================================
# Todos los módulos del ETL importan sus datos
# de conexión desde este único archivo.
# Si cambia un puerto o contraseña, solo se
# modifica aquí y se propaga automáticamente.
# =============================================

# ─────────────────────────────────────────────
# PostgreSQL
# Puerto 5433 (no 5432) porque en Windows el
# PostgreSQL local ya ocupa el 5432.
# Docker mapea 5433 del host → 5432 del contenedor.
# ─────────────────────────────────────────────
POSTGRES_CONFIG = {
    "host":     "localhost",
    "port":     5433,
    "dbname":   "red_social",
    "user":     "bd2user",
    "password": "bd2pass",
}

# ─────────────────────────────────────────────
# MongoDB
# URI estándar. El nombre de la base de datos
# es "red_social", igual que en PostgreSQL.
# ─────────────────────────────────────────────
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB  = "red_social"

# ─────────────────────────────────────────────
# Cassandra
# Se conecta como lista de hosts para soportar
# clusters de varios nodos en producción.
# Keyspace = equivalente a "base de datos" en Cassandra.
# ─────────────────────────────────────────────
CASSANDRA_HOSTS    = ["localhost"]
CASSANDRA_PORT     = 9042
CASSANDRA_KEYSPACE = "red_social"

# ─────────────────────────────────────────────
# Redis
# Base de datos 0 (Redis permite tener varias
# bases numeradas dentro del mismo servidor).
# ─────────────────────────────────────────────
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB   = 0
