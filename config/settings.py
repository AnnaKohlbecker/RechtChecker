from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE")
MONGO_DB_USER = os.getenv("MONGO_DB_USER")
MONGO_DB_PASSWORD = os.getenv("MONGO_DB_PASSWORD")

# PostgreSQL
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DB = os.getenv("PG_DB")
PG_TABLE = os.getenv("PG_TABLE")
PG_SCHEMA = os.getenv("PG_SCHEMA")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

# Neo4j
NEO4J_HOST = os.getenv("NEO4J_HOST")
NEO4J_PORT = os.getenv("NEO4J_PORT")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# MinIO
MINIO_HOST = os.getenv("MINIO_HOST")
MINIO_PORT = os.getenv("MINIO_PORT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

# Redis
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
# HF_API_EMBEDDINGS_URL = os.getenv("HF_API_EMBEDDINGS_URL")
