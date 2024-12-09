from pymongo import MongoClient
from config.settings import (
    MONGO_HOST,
    MONGO_PORT,
    MONGO_DB,
    MONGO_COLLECTION,
    MONGO_DB_USER,
    MONGO_DB_PASSWORD,
    STRUCTURED_JSON_PATH,
)
import json


def initialize_mongodb():
    """
    Initialize MongoDB connection and return the database object.
    """
    try:
        # Include username and password in the MongoDB URI
        # mongo_uri = (
        #     f"mongodb://{MONGO_DB_USER}:{MONGO_DB_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
        # )
        
        mongo_uri_anna = f"mongodb://{MONGO_HOST}:{MONGO_PORT}"
        mongo_uri_anna_v2 = (f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
        # client = MongoClient(mongo_uri)
        
        
        client = MongoClient(host=MONGO_HOST,
                     port=MONGO_PORT, 
                     username=MONGO_DB_USER, 
                     password=MONGO_DB_PASSWORD,
                    authSource="admin")
        db = client[MONGO_DB]
        print("MongoDB initialized successfully.")
        return db
    except Exception as e:
        print(f"Error initializing MongoDB: {e}")
        return None


def fetch_article(db, article_number: str):
    """
    Fetch an article by its number.

    Args:
        db: MongoDB database object.
        article_number (str): The number of the article.

    Returns:
        dict: The article document or None if not found.
    """
    try:
        collection = db[MONGO_COLLECTION]
        article = collection.find_one({"article_number": article_number})
        return article
    except Exception as e:
        print(f"Error fetching article: {e}")
        return None


def insert_data(db):
    """
    Insert data into the MongoDB collection from a structured JSON file.

    Args:
        db: MongoDB database object.
    """
    try:
        collection = db[MONGO_COLLECTION]

        # Read data from the JSON file
        with open(STRUCTURED_JSON_PATH, 'r', encoding="utf-8") as file:
            data = json.load(file)

        # Clear existing data in the collection
        collection.delete_many({})
        print("Cleared existing data from the collection.")

        # Insert new data
        collection.insert_many(data)
        print("Data inserted successfully from the JSON file.")
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")

def create_index(db):
    """
    Create an index on the `article_number` field to optimize queries.
    
    Args:
        db: MongoDB database object.
    """
    try:
        collection = db[MONGO_COLLECTION]
        
        # Check existing indexes
        existing_indexes = collection.index_information()
        if "article_number_1" in existing_indexes:
            print("Index on `article_number` already exists.")
            return

        # Create a single-field index on article_number
        collection.create_index("article_number", unique=True)
        print("Index created on `article_number` field.")
    except Exception as e:
        print(f"Error creating index: {e}")

