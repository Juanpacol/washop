# =============================================
# FASE 3 — CARGA EN MONGODB
# Técnica: Few-shot
# Se muestra el documento objetivo exacto antes
# de escribir el código que lo genera para todas
# las publicaciones. El "shot" guía la estructura.
# =============================================
#
# DOCUMENTO OBJETIVO (el "shot"):
# {
#   "_id": 1,
#   "texto_contenido": "Estudiar bases de datos es fascinante",
#   "likes_contador": 15,
#   "fecha_publicacion": "2025-02-01",
#   "autor": {
#     "id_usuario": 25,
#     "nombre": "Fernando Castillo",
#     "pais": "Chile"
#   },
#   "comentarios": [
#     {"contenido": "Totalmente de acuerdo!", "usuario_id": 3, "fecha": "2025-02-02"},
#     {"contenido": "Muy buen punto", "usuario_id": 7, "fecha": "2025-02-03"}
#   ]
# }
#
# El código a continuación generaliza este patrón para las 50 publicaciones.
# =============================================

import datetime
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB


# ─────────────────────────────────────────────
# Fix de serialización de fechas
# PostgreSQL devuelve fechas como objetos Python
# datetime.date, pero MongoDB (BSON) no puede
# guardarlos directamente → los convertimos a string.
# ─────────────────────────────────────────────
def _serializar(valor):
    """Convierte datetime.date y datetime.datetime a string ISO."""
    if isinstance(valor, (datetime.date, datetime.datetime)):
        return str(valor)
    return valor


def _limpiar_doc(doc: dict) -> dict:
    """Aplica _serializar a todos los valores de un diccionario."""
    return {clave: _serializar(v) for clave, v in doc.items()}


def load_to_mongo(data: dict) -> None:
    client = MongoClient(MONGO_URI)
    db     = client[MONGO_DB]

    # ── Colección usuarios: documentos planos ─────────────────────────
    # drop() borra la colección si ya existe, para reiniciar limpio.
    db.usuarios.drop()
    db.usuarios.insert_many([_limpiar_doc(u) for u in data["usuarios"]])

    # ── Índice auxiliar para buscar autores en O(1) ───────────────────
    # En lugar de recorrer la lista por cada publicación,
    # construimos un diccionario {id_usuario: datos_usuario}.
    usuarios_idx = {u["id_usuario"]: u for u in data["usuarios"]}

    # ── Agrupar comentarios por publicación ───────────────────────────
    # Recorremos todos los comentarios UNA sola vez y los organizamos
    # en un diccionario {publicacion_id: [lista de comentarios]}.
    # Esto evita recorrer la lista de comentarios 50 veces (una por publicación).
    comentarios_por_pub: dict[int, list] = {}
    for c in data["comentarios"]:
        pid = c["publicacion_id"]
        comentarios_por_pub.setdefault(pid, []).append({
            "contenido":  c["contenido"],
            "usuario_id": c["usuario_id"],
            "fecha":      str(c["fecha_comentario"]),
        })

    # ── Construir documentos enriquecidos (patrón few-shot aplicado) ──
    # Para cada publicación: buscar su autor en usuarios_idx (O(1))
    # y sus comentarios en comentarios_por_pub (O(1)).
    # Resultado: un documento autocontenido, sin necesidad de JOINs.
    docs_pub = []
    for p in data["publicaciones"]:
        pid   = p["id_publicacion"]
        autor = usuarios_idx.get(p["autor_id"], {})
        docs_pub.append({
            "_id":               pid,
            "texto_contenido":   p["texto_contenido"],
            "likes_contador":    p["likes_contador"],
            "fecha_publicacion": str(p["fecha_publicacion"]),
            "autor": {
                "id_usuario": autor.get("id_usuario"),
                "nombre":     autor.get("nombre"),
                "pais":       autor.get("pais"),
            },
            # Si la publicación no tiene comentarios, la lista queda vacía []
            "comentarios": comentarios_por_pub.get(pid, []),
        })

    db.publicaciones.drop()
    db.publicaciones.insert_many(docs_pub)

    client.close()
    print(f"[MongoDB] {len(data['usuarios'])} usuarios, {len(docs_pub)} publicaciones cargadas.")
