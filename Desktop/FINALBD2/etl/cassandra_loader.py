# =============================================
# FASE 3 — CARGA EN CASSANDRA
# Técnica: CTD (Chain-Thought-Decomposition)
# El schema se diseña razonando paso a paso,
# donde cada paso depende del anterior.
# =============================================
#
# CTD Paso 1 — ¿Qué consulta necesitamos responder?
#   "Dame todas las publicaciones del usuario X,
#    ordenadas de más reciente a más antigua."
#
# CTD Paso 2 — ¿Cuál es la partition key?
#   → usuario_id
#   Cassandra guarda todos los datos de una partición
#   en el mismo nodo. Si la partition key es usuario_id,
#   todos los posts de un usuario viven juntos → lectura O(1).
#
# CTD Paso 3 — ¿Cuál es el clustering key?
#   → fecha_publicacion DESC
#   El clustering key define el orden físico dentro de la partición.
#   Con DESC, los posts más recientes quedan primero en disco,
#   así Cassandra los devuelve ordenados SIN necesitar ORDER BY.
#
# CTD Paso 4 — ¿Qué pasa si dos posts tienen la misma fecha?
#   → Agregar id_publicacion como tercer componente de la PK.
#   Garantiza unicidad incluso con timestamps idénticos.
#
# CTD Paso 5 — PRIMARY KEY resultante:
#   PRIMARY KEY (usuario_id, fecha_publicacion, id_publicacion)
#   WITH CLUSTERING ORDER BY (fecha_publicacion DESC, id_publicacion DESC)
# =============================================

import time
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
from config import CASSANDRA_HOSTS, CASSANDRA_PORT, CASSANDRA_KEYSPACE


# ─────────────────────────────────────────────
# Esperar a que Cassandra esté listo
# Cassandra tarda entre 60 y 90 segundos en
# inicializar después de arrancar el contenedor.
# Esta función reintenta la conexión hasta 15 veces
# con 10 segundos de pausa entre intentos.
# ─────────────────────────────────────────────
def wait_for_cassandra(max_retries: int = 15, delay: int = 10):
    for attempt in range(1, max_retries + 1):
        try:
            cluster = Cluster(
                CASSANDRA_HOSTS,
                port=CASSANDRA_PORT,
                load_balancing_policy=DCAwareRoundRobinPolicy(local_dc="datacenter1"),
            )
            session = cluster.connect()
            print("[Cassandra] Conexión establecida.")
            return cluster, session
        except Exception as e:
            print(f"[Cassandra] Intento {attempt}/{max_retries} fallido: {e}. Reintentando en {delay}s...")
            time.sleep(delay)
    raise RuntimeError("No se pudo conectar a Cassandra después de varios intentos.")


def load_to_cassandra(data: dict) -> None:
    cluster, session = wait_for_cassandra()

    # ── Crear keyspace (equivalente a "base de datos" en Cassandra) ───
    # SimpleStrategy con factor de replicación 1: un solo nodo (desarrollo).
    # En producción se usaría NetworkTopologyStrategy con factor >= 3.
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
    """)
    session.set_keyspace(CASSANDRA_KEYSPACE)

    # ── Recrear la tabla limpia ────────────────────────────────────────
    session.execute("DROP TABLE IF EXISTS timeline_usuarios")

    # ── Tabla resultado del CTD ───────────────────────────────────────
    # La PRIMARY KEY tiene tres partes:
    #   (usuario_id)              → partition key: agrupa por usuario
    #   (fecha_publicacion)       → clustering key: ordena por fecha
    #   (id_publicacion)          → desempate si dos posts son simultáneos
    # WITH CLUSTERING ORDER BY: le dice a Cassandra que almacene
    # físicamente en orden descendente para servir el timeline sin sorting.
    session.execute("""
        CREATE TABLE timeline_usuarios (
            usuario_id        INT,
            fecha_publicacion TIMESTAMP,
            id_publicacion    INT,
            texto_contenido   TEXT,
            likes_contador    INT,
            nombre_autor      TEXT,
            PRIMARY KEY (usuario_id, fecha_publicacion, id_publicacion)
        ) WITH CLUSTERING ORDER BY (fecha_publicacion DESC, id_publicacion DESC)
    """)

    # ── Índice O(1) para lookup de autores ────────────────────────────
    usuarios_idx = {u["id_usuario"]: u for u in data["usuarios"]}

    # ── Prepared statement: más eficiente que texto SQL repetido ─────
    # Cassandra compila la consulta una vez y la reutiliza para cada fila.
    insert_stmt = session.prepare("""
        INSERT INTO timeline_usuarios
            (usuario_id, fecha_publicacion, id_publicacion,
             texto_contenido, likes_contador, nombre_autor)
        VALUES (?, ?, ?, ?, ?, ?)
    """)

    # ── Insertar las 50 publicaciones ─────────────────────────────────
    for p in data["publicaciones"]:
        autor = usuarios_idx.get(p["autor_id"], {})
        session.execute(insert_stmt, (
            p["autor_id"],
            p["fecha_publicacion"],
            p["id_publicacion"],
            p["texto_contenido"],
            p["likes_contador"],
            autor.get("nombre", ""),
        ))

    print(f"[Cassandra] {len(data['publicaciones'])} filas insertadas en timeline_usuarios.")
    cluster.shutdown()
