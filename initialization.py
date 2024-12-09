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
from config.settings import EMBEDDING_MODEL
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
    raw_data_path = "data/GG.txt"
    chunked_data_path = "data/GG_chunks.json"
    structured_data_path = "data/GG_structured.json"
    delimiter = "GG Art"
    if not os.path.exists(chunked_data_path):
        chunk_text_delimiter(input_path=raw_data_path, output_path=chunked_data_path, delimiter=delimiter)
    if not os.path.exists(structured_data_path):
        preprocess_articles(input_path=chunked_data_path, output_path=structured_data_path)
    else:
        print("Data initialized.")
    return structured_data_path
    
def initialize_dbs(reset, data_path):
    print("\n*** Initialize Databases ***")
    # Initialize Databases (Postgres, MongoDB, Redis, MinIO)
    # redis_conn = initialize_redis()
    embedding_path = "data/articles_with_embeddings.json"
    initialize_postgresql(reset=reset, data_path=data_path, embedding_model=EMBEDDING_MODEL, embedding_path=embedding_path)
    # mongo_db = initialize_mongodb()
    # minio_conn = initialize_minio()