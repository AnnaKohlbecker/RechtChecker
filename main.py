from utils.docker_utils import start_docker
from db.postgres import initialize_postgresql,insert_documents_pg
from db.mongodb import initialize_mongodb
from db.redis import initialize_redis
from utils.file_utils import chunk_text_delimiter, preprocess_articles
from models.embeddings import process_articles_with_embeddings
from models.llm_client import LLMClient
from agents.manager_agent import ManagerAgent


STRUCTURED_DATA_PATH = "data/GG_structured.json"
EMBEDDING_MODEL = "mxbai-embed-large:latest"

def test_instruct_model(llm_client, query):
    try:
        instruct_model_name = "meta-llama/Llama-3.2-1B-Instruct"
        messages = [{"role": "user", "content": query}]
        instruct_response = llm_client.query_instruct(
            model=instruct_model_name,
            messages=messages,
            max_tokens=512,
            temperature=0.0
        )        
        print("Instruct Model Response:", instruct_response["choices"][0]["message"]["content"])
    except RuntimeError as e:
        print(e)
        
def test_chat_model(llm_client, query):
    try:
        chat_model_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-1B"
        chat_response = llm_client.query_chat(
            model_url=chat_model_url,
            inputs=query,
            max_tokens=100,
            temperature=0.1
        )        
        print("Chat Model Response:", chat_response)
    except RuntimeError as e:
        print(e)
        
def test_manager_agent():
    manager_agent = ManagerAgent()
    
    #Clear Redis cache
    manager_agent.clear_cache()
    
    german_questions = [
        # Neo4j
        "Welche Artikel werden im Artikel 13 referenziert?",
        "Gibt es Artikel auf die Artikel 12 referenziert?",
        "Welche Artikel verweisen auf Artikel 14?",
        "Welche Artikel sind mit Artikel 3 verknüpft?",
        "Gibt es Artikel, die auf Artikel 15 Bezug nehmen?",
        "Welche Artikel sind mit Artikel 100 verknüpft?",
        "Welche Verweise gibt es auf Artikel 3 des Grundgesetzes?",
        "Kannst du mir zeigen, welche Artikel Bezug auf Artikel 13 nehmen?",

        # MongoDB
        "Was versteht man unter Artikel 16?",
        "Erkläre mir Artikel 5 des Grundgesetzes.",
        "Fass Artikel 10 aus dem Grundgesetz zusammen.",
        "Was bedeutet Artikel 11 im Grundgesetz?",
        "Erkläre den Inhalt von Artikel 13.",
        "Kannst du mir eine kurze Zusammenfassung von Artikel 4 geben?",

        # MinIO
        "Gib mir Artikel 3 als PDF.",
        "Lade Artikel 7 als PDF herunter.",
        "Zeig mir Artikel 15 als PDF.",
        "Kannst du Artikel 18 als PDF bereitstellen?",
        "Ich brauche Artikel 6 in einer PDF-Datei.",
        "Gibt es Artikel 9 in PDF-Form?",

        # Postgres
        "Ich werde auf der Arbeit gezwungen etwas zu tun, was ich nicht möchte. Habe ich Recht?",
        "Mein Chef will mich ohne Grund feuern. Was kann ich tun?",
        "Ich wurde auf der Arbeit beleidigt. Was sind meine Rechte?",
        "Darf mein Arbeitgeber mich ohne Vorwarnung entlassen?",
        "Ich fühle mich in meiner Nachbarschaft diskriminiert. Was kann ich tun?",
        "Welche Rechte habe ich, wenn ich in der Öffentlichkeit gefilmt werde?",

        # None
        "Was ist das Wetter morgen in Paris?",
        "Wie heißt die Mutter von Kevin?",
        "Wie alt bist du?",
        "Balabalabalabalabalba?",
        "No",
        "Wie viele Kilometer sind es von Berlin nach München?",
        "Wann wurde das erste Auto erfunden?",
        "Kannst du mir ein Rezept für Apfelkuchen geben?",
    
        # Redis
        "Ich werde auf der Arbeit gezwungen etwas zu tun, was ich nicht möchte. Habe ich Recht?",
        "Mein Chef will mich ohne Grund feuern. Was kann ich tun?",
        "Ich wurde auf der Arbeit beleidigt. Was sind meine Rechte?",
        "Darf mein Arbeitgeber mich ohne Vorwarnung entlassen?",
        "Ich fühle mich in meiner Nachbarschaft diskriminiert. Was kann ich tun?",
        "Welche Rechte habe ich, wenn ich in der Öffentlichkeit gefilmt werde?",
    ]
    
    # english_questions = [
    #     # Neo4j
    #     "Which articles refer to Article 12?",
    #     "Which articles are linked to Article 8?",
    #     "Are there any articles that reference Article 20?",
    #     "Which articles are connected to Article 14?",
    #     "What references exist to Article 1 of the Basic Law?",
    #     "Can you show me which articles refer to Article 19?",

    #     # MongoDB
    #     "What does Article 16 mean?",
    #     "Explain Article 5 of the Basic Law to me.",
    #     "Summarize Article 10 of the Basic Law.",
    #     "What is the meaning of Article 11 in the Basic Law?",
    #     "Explain the content of Article 13.",
    #     "Can you give me a brief summary of Article 4?",

    #     # MinIO
    #     "Give me Article 3 as a PDF.",
    #     "Download Article 7 as a PDF.",
    #     "Show me Article 15 as a PDF.",
    #     "Can you provide Article 18 as a PDF?",
    #     "I need Article 6 in a PDF file.",
    #     "Is Article 9 available in PDF format?",

    #     # Postgres
    #     "I am being forced to do something at work that I don’t want to do. Do I have rights?",
    #     "My boss wants to fire me without reason. What can I do?",
    #     "I was insulted at work. What are my rights?",
    #     "Can my employer fire me without prior warning?",
    #     "I feel discriminated against in my neighborhood. What can I do?",
    #     "What are my rights if I am filmed in public?",
        
    #     # Redis
    #     "I am being forced to do something at work that I don’t want to do. Do I have rights?",
    #     "My boss wants to fire me without reason. What can I do?",
    #     "I was insulted at work. What are my rights?",
    #     "Can my employer fire me without prior warning?",
    #     "I feel discriminated against in my neighborhood. What can I do?",
    #     "What are my rights if I am filmed in public?",

    #     # None
    #     "What’s the weather in Paris tomorrow?",
    #     "What is Kevin’s mother’s name?",
    #     "How old are you?",
    #     "Balabalabalabalabalba?",
    #     "No",
    #     "How many kilometers is it from Berlin to Munich?",
    #     "When was the first car invented?",
    #     "Can you give me a recipe for apple pie?",
    # ]

    questions = german_questions

    # Process each question
    for question in questions:
        print(f"Question: {question}")
        response = manager_agent.handle_query(question)
        print(f"{response}\n")
            
def main(): 
    
    test_manager_agent()
    
    # llm_client = LLMClient()
    # test_instruct_model(llm_client, "Fass mir bitte Artikel 6 aus dem Grundgesetz zusammen.")
    # test_chat_model(llm_client, "Fass mir bitte Artikel 6 aus dem Grundgesetz zusammen.")

    # pg_conn = initialize_postgresql(reset=True)

    # if not pg_conn:
    #     print("Failed to initialize PostgreSQL. Exiting.")
    #     return

    # # Process structured articles and generate embeddings
    # articles_with_embeddings = process_articles_with_embeddings(STRUCTURED_DATA_PATH, EMBEDDING_MODEL)

    # # Insert documents into PostgreSQL
    # insert_documents_pg(pg_conn, articles_with_embeddings)

    # pg_conn.close()
    # print("All articles processed and stored successfully.")
    
if __name__ == "__main__":
    main()

# import psycopg2
# from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
# from pymongo import MongoClient
# import ollama
# import time
# import subprocess
# import json
# import bson
# import psycopg2
# from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
# from pymongo import MongoClient
# from pymongo.errors import BulkWriteError
# from minio import Minio
# from dotenv import load_dotenv
# import os
# import redis

# # Database Configuration
# load_dotenv()

# # PostgreSQL
# PG_HOST = os.getenv("PG_HOST")
# PG_PORT = os.getenv("PG_PORT")
# PG_DB = os.getenv("PG_DB")
# PG_USER = os.getenv("PG_USER")
# PG_PASSWORD = os.getenv("PG_PASSWORD")

# # MongoDB
# MONGO_DB_USER = os.getenv("MONGO_DB_USER")
# MONGO_DB_PASSWORD = os.getenv("MONGO_DB_PASSWORD")
# MONGO_HOST = os.getenv("MONGO_HOST")
# MONGO_PORT = os.getenv("MONGO_PORT")
# MONGO_DB = os.getenv("MONGO_DB")
# MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE")

# # Redis
# REDIS_HOST = os.getenv("REDIS_HOST")
# REDIS_PORT = os.getenv("REDIS_PORT")

# # MinIO
# MINIO_HOST = os.getenv("MINIO_HOST")
# MINIO_PORT = os.getenv("MINIO_PORT")
# MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
# MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")


# def start_docker():
#     commands = [
#         """start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe""",
#         "docker-compose down -v",
#         "docker-compose up -d",
#         "docker ps",
#     ]

#     for command in commands:
#         try:
#             result = subprocess.run(
#                 command,
#                 shell=True,
#                 check=True,
#                 text=True,
#                 capture_output=True,
#             )
#             print(f"Command '{command}' executed successfully:")
#             print(result.stdout)

#             if command == commands[0]:
#                 print("Loading...")
#                 time.sleep(30)
#             else:
#                 print("Loading...")
#                 time.sleep(10)

#         except subprocess.CalledProcessError as e:
#             print(f"Error occurred while executing '{command}':")
#             print(e.stderr)
#         except FileNotFoundError:
#             print(f"Command not found or not executable: '{command}'")
#     time.sleep(20)

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

# def chunk_grundgesetz(file_path, output_path):
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


# def test_model():
#     """
#     Test the LLM independently to ensure it can generate responses.
#     """

#     response = ollama.chat(
#         model="llama3.2",
#         messages=[{"role": "user", "content": "Hello, are you there?"}],
#     )
#     print("Minimal Test Response:", response)

#     response = ollama.chat(
#         model="llama3.2",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": "What is artificial intelligence?"},
#         ],
#     )
#     print("Model Test Response:", response)


# if __name__ == "__main__":
#     # Initialize Docker
#     start_docker()
    
#     # Initialize Databases (Postgres, MongoDB, Redis, MinIO)
#     pg_conn = initialize_postgresql()
#     mongo_db = initialize_mongodb()
#     redis_conn = initialize_redis()
#     minio_conn = initialize_minio()

#     # Load the data from JSON file
#     file_path = "data/GG.txt"
#     data = load_data(file_path)
    
#     input_file = "GG"
#     chunk_grundgesetz(input_file)

#     Insert Data in MongoDB
#     insert_data_in_mongo(data, mongo_db)

#     Indexing und Aggregation

#     Vector Datenbanken
#     insert_data_in_pg_as_vector(pg_conn)

#     Redis: In Memory Datenbank
#     insert_data_in_redis(redis_conn)
    
#     Feynman Technique

#     LLM Chatbot mit RAG

#     Min.IO Object Storage

    
#     # Insert Data
#     insert_data(pg_conn, mongo_db, redis_conn, minio_conn)

#     # Chatbot Interaction
#     chat_history = [
#         {
#             "role": "system",
#             "content": "You are a helpful assistant knowledgeable about technology and databases.",
#         }
#     ]
#     print("Chatbot ready. Type your queries below:")

#     while True:
#         user_query = input("You: ")
#         if user_query.lower() in ["exit", "quit"]:
#             break

#         response = generate_response(pg_conn, user_query, chat_history)
#         print(f"Assistant: {response}")

#     # Close connections
#     pg_conn.close()

#     except Exception as e:
#        print(f"An error occurred: {e}")
