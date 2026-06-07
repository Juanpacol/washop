# =============================================
# ORQUESTADOR ETL
# Este archivo coordina los 4 pasos del ETL
# en el orden correcto. No contiene lógica propia;
# solo llama a cada módulo y reporta el progreso.
#
# ETL = Extract, Transform, Load
#   Extract  → sacar datos de PostgreSQL
#   Transform → restructurar para cada motor NoSQL
#   Load     → insertar en MongoDB, Cassandra y Redis
#
# Uso: cd etl && python run_etl.py
# =============================================

import sys
import os

# ─────────────────────────────────────────────
# Fix de encoding para Windows
# En Windows, la consola puede usar CP1252 (español)
# en lugar de UTF-8. Al imprimir tildes o ñ, falla.
# Forzar UTF-8 evita el UnicodeEncodeError.
# ─────────────────────────────────────────────
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Asegurar que Python encuentre los módulos del directorio etl/
sys.path.insert(0, os.path.dirname(__file__))

from pg_extractor     import extract_all
from mongo_loader     import load_to_mongo
from cassandra_loader import load_to_cassandra
from redis_cache      import load_to_redis


def main():
    print("=" * 50)
    print("  ETL Políglota — Red Social Académica")
    print("=" * 50)

    # ── Paso 1: Extraer de PostgreSQL ─────────────────────────────────
    # extract_all() devuelve un diccionario con 4 listas:
    # usuarios, publicaciones, comentarios y feed.
    # Este mismo diccionario se pasa a los tres pasos siguientes.
    print("\n[1/4] Extrayendo datos de PostgreSQL...")
    data = extract_all()
    print(f"      {len(data['usuarios'])} usuarios, "
          f"{len(data['publicaciones'])} publicaciones, "
          f"{len(data['comentarios'])} comentarios extraídos.")

    # ── Paso 2: Cargar en MongoDB ─────────────────────────────────────
    # Crea documentos enriquecidos con autor y comentarios embebidos.
    print("\n[2/4] Cargando en MongoDB...")
    load_to_mongo(data)

    # ── Paso 3: Cargar en Cassandra ───────────────────────────────────
    # Puede tardar si Cassandra acaba de arrancar (60-90s de inicio).
    # wait_for_cassandra() dentro del módulo maneja la espera.
    print("\n[3/4] Cargando en Cassandra (puede tardar si acaba de arrancar)...")
    load_to_cassandra(data)

    # ── Paso 4: Cargar en Redis ───────────────────────────────────────
    # Cachea el feed, los likes y el total de usuarios por 5 minutos.
    print("\n[4/4] Cargando en Redis...")
    load_to_redis(data)

    print("\n" + "=" * 50)
    print("  ETL completado exitosamente.")
    print("=" * 50)


if __name__ == "__main__":
    main()
