from pymongo import MongoClient
from config.settings import MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_AUTH_SOURCE

def initialize_mongodb():
    try:
        mongo_uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/?authSource={MONGO_AUTH_SOURCE}"
        client = MongoClient(mongo_uri)
        db = client[MONGO_DB]
        print("MongoDB initialized successfully.")
        return db
    except Exception as e:
        print(f"Error initializing MongoDB: {e}")
