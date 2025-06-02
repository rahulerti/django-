from pymongo import MongoClient

def get_user():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["user_db"]  # Use the database name from your settings
    return db