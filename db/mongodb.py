from pymongo import MongoClient
from config.settings import (
    MONGO_HOST,
    MONGO_PORT,
    MONGO_DB,
    MONGO_DB_USER,
    MONGO_DB_PASSWORD,
    MONGO_DB_AUTH_SOURCE,
    MONGO_COLLECTION,
    STRUCTURED_JSON_PATH,
)
import json


def initialize_mongodb():
    """
    Initialize MongoDB connection and return the database object.
    Tries default connection first, then falls back to URI-based connection with credentials.
    """
    try:
        # First attempt: standard connection string using environment variables
        client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
        db = client[MONGO_DB]
        print("MongoDB initialized successfully with default connection.")
        return db
    except Exception as e:
        print(f"Default connection failed: {e}")
        try:
            # Second attempt: URI-based connection with credentials
            uri = f"mongodb://{MONGO_DB_USER}:{MONGO_DB_PASSWORD}@{MONGO_HOST}/?authSource={MONGO_DB_AUTH_SOURCE}&authMechanism=SCRAM-SHA-256"
            client = MongoClient(uri)
            db = client[MONGO_DB_AUTH_SOURCE]
            print("MongoDB initialized successfully with URI-based connection.")
            return db
        except Exception as e:
            print(f"URI-based connection failed: {e}")
            return None

def reinitialize_with_uri():
    """
    Reinitialize the MongoDB connection using the URI-based credentials.

    Returns:
        db: MongoDB database object reinitialized with URI-based credentials.
    """
    try:
        uri = f"mongodb://{MONGO_DB_USER}:{MONGO_DB_PASSWORD}@{MONGO_HOST}/?authSource={MONGO_DB_AUTH_SOURCE}&authMechanism=SCRAM-SHA-256"
        client = MongoClient(uri)
        db = client[MONGO_DB_AUTH_SOURCE]
        print("Reinitialized MongoDB connection with URI-based credentials.")
        return db
    except Exception as e:
        print(f"Failed to reinitialize with URI-based connection: {e}")
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
        return db
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")

        if "requires authentication" in str(e):
            print("Reinitializing with URI-based connection due to authentication error.")
            db = reinitialize_with_uri()
            if db is not None:
                try:
                    collection = db[MONGO_COLLECTION]
                    collection.delete_many({})
                    print("Cleared existing data from the collection (URI-based connection).")
                    collection.insert_many(data)
                    print("Data inserted successfully from the JSON file (URI-based connection).")
                    return db
                except Exception as uri_exception:
                    print(f"Failed to insert data even with URI-based connection: {uri_exception}")
                    return None

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
            return db

        # Create a single-field index on article_number
        collection.create_index("article_number", unique=True)
        print("Index created on `article_number` field.")
        return db
    except Exception as e:
        print(f"Error creating index: {e}")

        if "requires authentication" in str(e):
            print("Reinitializing with URI-based connection due to authentication error.")
            db = reinitialize_with_uri()
            if db is not None:
                try:
                    collection = db[MONGO_COLLECTION]
                    existing_indexes = collection.index_information()
                    if "article_number_1" not in existing_indexes:
                        collection.create_index("article_number", unique=True)
                        print("Index created on `article_number` field (URI-based connection).")
                    return db
                except Exception as uri_exception:
                    print(f"Failed to create index even with URI-based connection: {uri_exception}")
                    return None

