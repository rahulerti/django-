#connect  with mongodb database using pymongo+                                                                                                                      +           +
from pymongo import MongoClient

def get_db():
    client = MongoClient("mongodb://localhost:27017/") #you can write like this too db = MongoClient("mongodb://localhost:27017/")["your_db_name"]
    db = client["your_db_name"]
    return db
