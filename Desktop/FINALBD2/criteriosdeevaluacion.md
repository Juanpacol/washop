# Criterios de Evaluación — Mapa de Implementación

Cada criterio de la rúbrica del examen final apunta exactamente al archivo y línea donde está implementado.

---

## Criterio 1 — Integridad SQL (15%)

> *"Aplicación correcta de ALTER TABLE, restricciones de Llaves Foráneas (FK) e inclusión funcional de CHECK restrictivo contra duplicados propios."*

### Script inicial sin restricciones
El enunciado entrega las tablas sin FK ni CHECK. Ese estado inicial está en:

- [sql/01_schema.sql](sql/01_schema.sql) — tablas `usuarios`, `publicaciones`, `comentarios`, `amistades` sin ninguna restricción de integridad. Replica exactamente el script del enunciado.

### ALTER TABLE que agrega las FK y CHECK
Todo lo que pide este criterio está en un solo archivo:

- [sql/02_alter_constraints.sql](sql/02_alter_constraints.sql)

| Restricción | Línea | Qué hace |
|---|---|---|
| `ALTER TABLE publicaciones` — FK | [línea 21](sql/02_alter_constraints.sql#L21) | Conecta `autor_id` con `usuarios` |
| `ALTER TABLE comentarios` — FK usuario | [línea 35](sql/02_alter_constraints.sql#L35) | Conecta `usuario_id` con `usuarios` |
| `ALTER TABLE comentarios` — FK publicacion | [línea 41](sql/02_alter_constraints.sql#L41) | Conecta `publicacion_id` con `publicaciones` |
| `ALTER TABLE amistades` — FK solicitante | [línea 64](sql/02_alter_constraints.sql#L64) | Conecta `usuario_solicitante_id` con `usuarios` |
| `ALTER TABLE amistades` — FK receptor | [línea 70](sql/02_alter_constraints.sql#L70) | Conecta `usuario_receptor_id` con `usuarios` |
| `CHECK chk_estado_valido` | [línea 77](sql/02_alter_constraints.sql#L77) | Solo permite `'ACEPTADA'` o `'PENDIENTE'` |
| `CHECK chk_no_auto_amistad` | [línea 83](sql/02_alter_constraints.sql#L83) | Impide que un usuario se agregue a sí mismo |

Todas las FK usan `ON DELETE CASCADE`: si se borra un usuario, sus publicaciones, comentarios y amistades desaparecen automáticamente.

---

## Criterio 2 — Lógica de Negocio (15%)

> *"Procedimiento almacenado preventivo de errores 'crear_amistad' y vistas analíticas agregadas (feed, pendientes, aceptados)."*

### Stored Procedure

- [sql/03_procedures.sql](sql/03_procedures.sql)

| Elemento | Línea | Qué hace |
|---|---|---|
| Declaración del procedure | [línea 24](sql/03_procedures.sql#L24) | `CREATE OR REPLACE PROCEDURE crear_amistad(id1, id2)` |
| Verificación preventiva de duplicado | [línea 35](sql/03_procedures.sql#L35) | `SELECT COUNT(*) INTO existente` — busca la amistad en ambas direcciones (A→B y B→A) |
| Bloque de protección | [línea 43](sql/03_procedures.sql#L43) | `IF existente > 0 THEN RAISE NOTICE` — si ya existe, avisa sin insertar |
| Inserción si no existe | [línea 50](sql/03_procedures.sql#L50) | Inserta en estado `PENDIENTE` solo cuando no hay duplicado |

### Vistas analíticas

- [sql/04_views.sql](sql/04_views.sql)

| Vista | Línea | Qué muestra |
|---|---|---|
| `solicitudes_pendientes` | [línea 18](sql/04_views.sql#L18) | Amistades con estado `PENDIENTE`, con nombre de ambas personas |
| `amistades_consolidadas` | [línea 34](sql/04_views.sql#L34) | Amistades con estado `ACEPTADA` |
| `feed_noticias` | [línea 60](sql/04_views.sql#L60) | Publicaciones con autor, likes y conteo de comentarios |
| `LEFT JOIN comentarios` | [línea 69](sql/04_views.sql#L69) | LEFT porque una publicación puede tener cero comentarios sin desaparecer del feed |
| `COUNT + GROUP BY` | [línea 66–70](sql/04_views.sql#L66) | Cuenta los comentarios de cada publicación y los agrupa |

---

## Criterio 3 — Script Python y Conectores (30%)

> *"Estructura del código limpia, manejo óptimo de conexiones concurrentes y sesiones activas sin caídas."*

### Configuración centralizada

- [etl/config.py](etl/config.py) — todas las cadenas de conexión en un solo lugar. Si cambia un puerto o contraseña, se modifica aquí y se propaga a todos los módulos.

### Conector PostgreSQL (psycopg2)

- [etl/pg_extractor.py](etl/pg_extractor.py)

| Elemento | Línea | Qué hace |
|---|---|---|
| Conexión a PostgreSQL | [línea 26](etl/pg_extractor.py#L26) | `psycopg2.connect(**POSTGRES_CONFIG)` |
| `RealDictCursor` | [línea 40](etl/pg_extractor.py#L40) | Convierte cada fila en un diccionario `{columna: valor}` en lugar de una tupla |
| Extracción de las 4 entidades | [línea 43–52](etl/pg_extractor.py#L43) | `SELECT *` de usuarios, publicaciones, comentarios y la vista `feed_noticias` |

### Conector MongoDB (pymongo)

- [etl/mongo_loader.py](etl/mongo_loader.py)

| Elemento | Línea | Qué hace |
|---|---|---|
| Conexión a MongoDB | [línea 53](etl/mongo_loader.py#L53) | `MongoClient(MONGO_URI)` |
| Carga de usuarios | [línea 59](etl/mongo_loader.py#L59) | `insert_many` de 50 documentos planos |
| Construcción de documentos enriquecidos | [línea 85–102](etl/mongo_loader.py#L85) | Cada publicación lleva el autor embebido y el arreglo de comentarios adentro |
| Carga de publicaciones | [línea 102](etl/mongo_loader.py#L102) | `insert_many` de 50 documentos con autor y comentarios embebidos |

### Conector Cassandra (cassandra-driver)

- [etl/cassandra_loader.py](etl/cassandra_loader.py)

| Elemento | Línea | Qué hace |
|---|---|---|
| Espera activa de inicialización | [línea 46](etl/cassandra_loader.py#L46) | `wait_for_cassandra()` — reintenta 15 veces con 10s de pausa porque Cassandra tarda ~60s en arrancar |
| Conexión al cluster | [línea 49](etl/cassandra_loader.py#L49) | `Cluster(CASSANDRA_HOSTS)` |
| Inserción con prepared statement | [línea 112](etl/cassandra_loader.py#L112) | `session.execute(insert_stmt, (...))` — más eficiente que SQL repetido |

### Conector Redis (redis-py)

- [etl/redis_cache.py](etl/redis_cache.py)

| Elemento | Línea | Qué hace |
|---|---|---|
| Conexión a Redis | [línea 23](etl/redis_cache.py#L23) | `redis.Redis(host, port, db)` |
| Caché del feed | [línea 30](etl/redis_cache.py#L30) | `setex("cache:feed_noticias", 300, json.dumps(...))` |
| Contadores de likes | [línea 42](etl/redis_cache.py#L42) | Una clave por publicación: `likes:publicacion:{id}` |
| Total de usuarios | [línea 50](etl/redis_cache.py#L50) | `setex("cache:total_usuarios", 300, 50)` |

### Orquestador ETL

- [etl/run_etl.py](etl/run_etl.py) — coordina los 4 pasos en secuencia: extraer → MongoDB → Cassandra → Redis.

---

## Criterio 4 — Arquitectura Políglota (20%)

> *"Migración efectiva y mapeo lógico idéntico en MongoDB, Cassandra y persistencia veloz en Redis."*

### MongoDB — documento enriquecido

- [etl/mongo_loader.py — línea 85](etl/mongo_loader.py#L85)

En lugar de guardar solo el ID del autor, el documento de MongoDB lleva el autor completo adentro junto con el arreglo de comentarios. Así una sola lectura devuelve todo sin JOINs:

```
publicacion {
  "texto_contenido": "...",
  "autor": { "nombre": "Ana Silva", "pais": "Chile" },
  "comentarios": [ { "contenido": "...", "usuario_id": 3 } ]
}
```

### Cassandra — tabla optimizada por usuario

- [etl/cassandra_loader.py — línea 85](etl/cassandra_loader.py#L85)

La tabla `timeline_usuarios` tiene:
- **Partition key** `usuario_id` → todos los posts de un usuario viven en el mismo nodo
- **Clustering key** `fecha_publicacion DESC` → llegan ordenados sin `ORDER BY`
- Definido en [línea 93](etl/cassandra_loader.py#L93): `PRIMARY KEY (usuario_id, fecha_publicacion, id_publicacion)`

### Redis — caché de alta velocidad

- [etl/redis_cache.py — línea 22](etl/redis_cache.py#L22)

Tres tipos de datos cacheados con TTL de 5 minutos:
- Feed completo como JSON (`cache:feed_noticias`)
- Contador de likes por publicación (`likes:publicacion:{id}`)
- Total de usuarios (`cache:total_usuarios`)

---

## Criterio 5 — Supervisión y Uso de JSON (20%)

> *"Manipulación del formato estructurado como medio estandarizado de transformación de datos (ETL)."*

### JSON como formato de intercambio en el ETL

| Punto | Archivo | Línea | Qué hace |
|---|---|---|---|
| Extracción como dicts | [etl/pg_extractor.py](etl/pg_extractor.py) | [40](etl/pg_extractor.py#L40) | `RealDictCursor` convierte filas SQL en dicts Python (base del JSON) |
| Serialización a JSON para Redis | [etl/redis_cache.py](etl/redis_cache.py) | [33](etl/redis_cache.py#L33) | `json.dumps(data["feed"])` guarda el feed como texto JSON |
| Documentos JSON en MongoDB | [etl/mongo_loader.py](etl/mongo_loader.py) | [85](etl/mongo_loader.py#L85) | Los dicts Python se insertan directamente como documentos BSON/JSON |
| Visualización JSON en GUI | [gui/main_window.py](gui/main_window.py) | [633](gui/main_window.py#L633) | `json.dumps(d, indent=2)` muestra cada documento formateado con colores |

### Visualización interactiva en la GUI

- [gui/main_window.py — línea 618](gui/main_window.py#L618) — pestaña MongoDB: muestra los documentos JSON con syntax highlighting manual (`_json_html`), coloreando claves, strings, números y booleanos de forma diferente.

### ETL disparado desde la GUI con log en tiempo real

- [gui/main_window.py — línea 212](gui/main_window.py#L212) — `EtlWorker(QThread)`: el ETL corre en un hilo paralelo y cada línea que imprime aparece en pantalla en tiempo real mediante señales `pyqtSignal`.

---

## Resumen de archivos por criterio

| Criterio | Archivos principales |
|---|---|
| 1 · Integridad SQL | `sql/01_schema.sql`, `sql/02_alter_constraints.sql` |
| 2 · Lógica de negocio | `sql/03_procedures.sql`, `sql/04_views.sql` |
| 3 · Python y conectores | `etl/config.py`, `etl/pg_extractor.py`, `etl/mongo_loader.py`, `etl/cassandra_loader.py`, `etl/redis_cache.py`, `etl/run_etl.py` |
| 4 · Arquitectura políglota | `etl/mongo_loader.py`, `etl/cassandra_loader.py`, `etl/redis_cache.py` |
| 5 · Uso de JSON | `etl/redis_cache.py`, `etl/mongo_loader.py`, `gui/main_window.py` |
