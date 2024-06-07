from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

try:
    client = MongoClient(os.getenv('MONGO_URI'), server_api=ServerApi('1'))
    print('Connected to MongoDB !!')
    
except Exception as e:
    print('Error connecting to MongoDB: ', e)

def mongo_instance():
    return client

