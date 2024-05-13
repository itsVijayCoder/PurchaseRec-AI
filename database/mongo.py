from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://susanoox:gETm2aR5YOM8vczW@developement.yojlbid.mongodb.net/?retryWrites=true&w=majority&appName=Developement"

def mongo_connect():
    client = MongoClient(uri, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB !")
        return client

    except Exception as e:
        print(e)

    