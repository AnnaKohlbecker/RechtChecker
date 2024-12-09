import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pymongo import MongoClient
import ollama
import time
import subprocess
import json
import bson
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from minio import Minio
from dotenv import load_dotenv
import os
import redis
from config.settings import CHUNKED_DATA_PATH, EMBEDDING_MODEL, RAW_DATA_PATH, STRUCTURED_DATA_PATH
from utils.docker_utils import start_docker
from db.postgres import initialize_postgresql
from db.mongodb import initialize_mongodb
from db.redis import initialize_redis
from utils.file_utils import chunk_text_delimiter, preprocess_articles
from models.llm_client import LLMClient

# Database Configuration
load_dotenv()

# PostgreSQL
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

# MongoDB
MONGO_DB_USER = os.getenv("MONGO_DB_USER")
MONGO_DB_PASSWORD = os.getenv("MONGO_DB_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE")

# Redis
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

# MinIO
MINIO_HOST = os.getenv("MINIO_HOST")
MINIO_PORT = os.getenv("MINIO_PORT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

def initialize_docker_and_containers():
    print("\n*** Initialize Docker And Containers ***")
    start_docker()
    
def initialize_data():
    print("\n*** Initialize Data ***")
    delimiter = "GG Art"
    if not os.path.exists(CHUNKED_DATA_PATH):
        chunk_text_delimiter(input_path=RAW_DATA_PATH, output_path=CHUNKED_DATA_PATH, delimiter=delimiter)
    if not os.path.exists(STRUCTURED_DATA_PATH):
        preprocess_articles(input_path=CHUNKED_DATA_PATH, output_path=STRUCTURED_DATA_PATH)
    else:
        print("Data initialized.")    