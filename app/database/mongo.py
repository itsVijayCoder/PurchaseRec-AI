from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

def mongo_connect():
    try:
        client = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))
        client.admin.command('ping')
        print("Successfully connected to MongoDB !")
        return client

    except Exception as e:
        print(e)
    