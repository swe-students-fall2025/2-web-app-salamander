import os
from pymongo import MongoClient

client = None

def get_db():
    """
    Return handle to the MongoDB database
    """
    global client
    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME", "job_trackr")

    if client is None: client = MongoClient(uri)

    return client[db_name]
