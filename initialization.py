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
from utils.docker_utils import start_docker
from db.postgres import initialize_postgresql,insert_documents_pg
from db.mongodb import initialize_mongodb
from db.redis import initialize_redis
from utils.file_utils import chunk_text_delimiter, preprocess_articles
from models.embeddings import process_articles_with_embeddings
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

# def initialize_postgresql():
#     try:
#         conn = psycopg2.connect(
#             dbname="postgres",
#             user=PG_USER,
#             password=PG_PASSWORD,
#             host=PG_HOST,
#             port=PG_PORT,
#         )
#         conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
#         cur = conn.cursor()

#         # Create the database if it doesn't exist
#         cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{PG_DB}';")
#         if not cur.fetchone():
#             cur.execute(f"CREATE DATABASE {PG_DB};")

#         conn.close()

#         # Connect to the new database and create the table
#         conn = psycopg2.connect(
#             dbname=PG_DB, user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
#         )
#         cur = conn.cursor()

#         # Enable vector extension
#         cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

#         # Create table
#         cur.execute(
#             """
#             CREATE TABLE IF NOT EXISTS items (
#                 id SERIAL PRIMARY KEY,
#                 embedding VECTOR(1024),
#                 document TEXT
#             );
#         """
#         )
#         conn.commit()
#         print("PostgreSQL initialized successfully.")
#         # Connect to PostgreSQL
#         return conn
#     except Exception as e:
#         print(f"Error initializing PostgreSQL: {e}")
#     finally:
#         if cur:
#             cur.close()
#         if conn:
#             conn.close()

# def initialize_mongodb():
#     try:
#         mongo_uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/?authSource={MONGO_AUTH_SOURCE}"
#         client = MongoClient(mongo_uri)
#         db = client[MONGO_DB]
#         print("MongoDB initialized successfully.")
#         return db
#     except Exception as e:
#         print(f"Error initializing MongoDB: {e}")
#         return None

# def initialize_redis():
#     redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
#     print("Redis initialized successfully.")
#     return redis_client

# def initialize_minio():
#     endpoint = f"{MINIO_HOST}:{MINIO_PORT}"
    
#     # Initialize the Minio client
#     minio_client = Minio(
#         endpoint, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False
#     )
#     print("MinIO initialized successfully.")
#     return minio_client


# def load_data(file_path):
#     try:
#         with open(file_path, "r") as file:
#             return json.load(file)
#     except FileNotFoundError:
#         print(f"Error: The file '{file_path}' was not found.")
#     except json.JSONDecodeError:
#         print(f"Error: Failed to decode JSON from '{file_path}'.")
#     return None

# def insert_data_in_mongo(data, mongo_db):
#     """Insert data into MongoDB, handling oversized documents and non-dictionary data."""
#     try:
#         collection_name = "linkedin_jobs"
#         collection = mongo_db[collection_name]

#         # Preprocess data
#         data = preprocess_data(data)

#         for doc in data:
#             try:
#                 # Handle oversized documents
#                 if not (len(bson.BSON.encode(doc)) <= 16793598):
#                     print("Splitting oversized document...")
#                     split_docs = split_large_document(doc)
#                     collection.insert_many(split_docs)
#                     print(f"Inserted {len(split_docs)} split parts of an oversized document.")
#                 else:
#                     collection.insert_one(doc)
#                 print(f"Inserted data in MONGODB successfully.")
#             except BulkWriteError as bwe:
#                 print(f"Bulk write error: {bwe.details}")
#             except Exception as e:
#                 print(f"Error inserting document: {e}")
#     except Exception as e:
#         print(f"An error occurred while inserting data into MongoDB: {e}")


# def generate_response(pg_conn, user_query, chat_history):
#     """
#     Generate a response for a user query by combining context and chat history.
#     """
#     # Retrieve the context
#     context = retrieve_context(pg_conn, user_query)

#     # Ensure only one system message exists
#     if not any(msg["role"] == "system" for msg in chat_history):
#         system_message = (
#             "You are a helpful assistant knowledgeable about technology and databases. "
#             "Use the context below to answer queries."
#         )
#         chat_history.insert(0, {"role": "system", "content": system_message})

#     # Add the relevant context as its own message
#     if context:
#         chat_history.append(
#             {"role": "system", "content": f"Relevant Context: {context}"}
#         )

#     # Add the user's query
#     chat_history.append({"role": "user", "content": user_query})

#     # Debug: Print the full chat history
#     print("\n=== Chat History ===")
#     for message in chat_history:
#         print(f"{message['role']}: {message['content']}")
#     print("====================\n")

#     # Generate response
#     try:
#         response = ollama.chat(model="llama3.2", messages=chat_history)  # "llama3.1:8b"
#         print("Chat Response:", response)

#         # Extract assistant response
#         assistant_response = response.get("message", {}).get("content", "").strip()
#         if not assistant_response:
#             assistant_response = (
#                 "I'm sorry, I couldn't generate a response. Please try again."
#             )
#     except Exception as e:
#         print(f"Error during response generation: {e}")
#         assistant_response = (
#             "There was an error generating a response. Please try again later."
#         )

#     # Append assistant response to chat history
#     chat_history.append({"role": "assistant", "content": assistant_response})

#     return assistant_response


# # def test_model():
# #     """
# #     Test the LLM independently to ensure it can generate responses.
# #     """

# #     response = ollama.chat(
# #         model="llama3.2",
# #         messages=[{"role": "user", "content": "Hello, are you there?"}],
# #     )
# #     print("Minimal Test Response:", response)

# #     response = ollama.chat(
# #         model="llama3.2",
# #         messages=[
# #             {"role": "system", "content": "You are a helpful assistant."},
# #             {"role": "user", "content": "What is artificial intelligence?"},
# #         ],
# #     )
# #     print("Model Test Response:", response)

# def chunk_data(file_path, output_path):
#     """
#     Chunk the Grundgesetz into separate articles.

#     :param file_path: Path to the input .txt file containing the Grundgesetz.
#     :param output_path: Path to save the resulting chunks as a JSON file.
#     """
#     import json
    
#     # Read the file content
#     with open(file_path, 'r', encoding='utf-8') as file:
#         content = file.read()
    
#     # Split content into chunks using "GG Art" as the delimiter
#     chunks = content.split("GG Art")
    
#     # Process each chunk, re-add "GG Art" for the articles
#     processed_chunks = []
#     for i, chunk in enumerate(chunks):
#         if i == 0:
#             # Skip any introductory text before the first article
#             continue
#         article = f"GG Art{chunk.strip()}"
#         processed_chunks.append(article)
    
#     # Save chunks to a JSON file
#     with open(output_path, 'w', encoding='utf-8') as output_file:
#         json.dump(processed_chunks, output_file, ensure_ascii=False, indent=4)
    
#     print(f"Chunking complete! {len(processed_chunks)} articles processed and saved to {output_path}")



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
        print("Data already initialized.")
    
def initialize_dbs():
    print("\n*** Initialize Databases ***")
    # Initialize Databases (Postgres, MongoDB, Redis, MinIO)
    # redis_conn = initialize_redis()
    initialize_postgresql()
    # mongo_db = initialize_mongodb()
    # minio_conn = initialize_minio()
    
# llm_client = LLMClient()
# test_instruct_model(llm_client, "Fass mir bitte Artikel 6 aus dem Grundgesetz zusammen.")
# test_chat_model(llm_client, "Fass mir bitte Artikel 6 aus dem Grundgesetz zusammen.")

# pg_conn = initialize_postgresql(reset=True)

# if not pg_conn:
#     print("Failed to initialize PostgreSQL. Exiting.")
#     return

# pg_conn.close()
# print("All articles processed and stored successfully.")


# # Load the data from JSON file
# file_path = "data/GG.txt"
# data = load_data(file_path)

# input_file = "GG"
# chunk_data(input_file)

# Insert Data in MongoDB
# insert_data_in_mongo(data, mongo_db)

# Indexing und Aggregation

# Vector Datenbanken
# insert_data_in_pg_as_vector(pg_conn)

# Redis: In Memory Datenbank
# insert_data_in_redis(redis_conn)

# Feynman Technique

# LLM Chatbot mit RAG

# Min.IO Object Storage


# # Insert Data
# insert_data(pg_conn, mongo_db, redis_conn, minio_conn)

# # Chatbot Interaction
# chat_history = [
#     {
#         "role": "system",
#         "content": "You are a helpful assistant knowledgeable about technology and databases.",
#     }
# ]
# print("Chatbot ready. Type your queries below:")

# while True:
#     user_query = input("You: ")
#     if user_query.lower() in ["exit", "quit"]:
#         break

#     response = generate_response(pg_conn, user_query, chat_history)
#     print(f"Assistant: {response}")

# # Close connections
# pg_conn.close()

# except Exception as e:
#    print(f"An error occurred: {e}")