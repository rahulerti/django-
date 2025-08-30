from pymongo import MongoClient

def get_user():
    client = MongoClient("mongodb+srv://debnathrahul45795:rahul18182112@mongotoutube.hedlq.mongodb.net/")
    db = client["user_db"]  # Use the database name from your settings
    return db