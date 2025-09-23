# Makes backend.api a Python package
import os
from pymongo import MongoClient
from config.config import Config

mongo_client = None
mongo_db = None

def get_mongo_db():
    global mongo_client, mongo_db
    if mongo_db is None:
        uri = Config.MONGO_URI
        mongo_client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        db_name = Config.MONGO_DB_NAME
        mongo_db = mongo_client[db_name]
    return mongo_db
