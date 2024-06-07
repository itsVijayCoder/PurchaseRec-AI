from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://susanoox:<password>@developement.yojlbid.mongodb.net/?retryWrites=true&w=majority&appName=Developement"

def mongo_connect():
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        print('Connected to MongoDB !!')
        return client
    except Exception as e:
        print('Error connecting to MongoDB: ', e)