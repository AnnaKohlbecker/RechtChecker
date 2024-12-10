from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

# PostgreSQL
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DB = os.getenv("PG_DB")
PG_SCHEMA = os.getenv("PG_SCHEMA")
PG_TABLE = os.getenv("PG_TABLE")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

# Neo4j
NEO4J_HOST = os.getenv("NEO4J_HOST")
NEO4J_PORT = os.getenv("NEO4J_PORT")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# MinIO
MINIO_HOST = os.getenv("MINIO_HOST")
MINIO_PORT = os.getenv("MINIO_PORT")
MINIO_USER = os.getenv("MINIO_USER")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")

# Redis
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

JSON_PATH = os.getenv("JSON_PATH")
STRUCTURED_JSON_PATH = os.getenv("STRUCTURED_JSON_PATH")