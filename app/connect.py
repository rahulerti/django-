#connect  with mongodb database using pymongo+                                                                                                                  +           +
from pymongo import MongoClient


def get_db():
    client = MongoClient("mongodb+srv://debnathrahul45795:rahul18182112@mongotoutube.hedlq.mongodb.net/") #you can write like this too db = MongoClient("mongodb://localhost:27017/")["your_db_name"]
    db = client["for_test"]
    
    return db
