import redis, os
from dotenv import load_dotenv

load_dotenv()

def redis_connect():
    try: 
        client = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), password=os.getenv("REDIS_PWD"))
        client.ping()
        print('Successfully connected to redis !')
        return client
    except Exception as e:
        print('Error connecting to redis: ', e)