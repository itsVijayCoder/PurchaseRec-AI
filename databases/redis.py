import redis, os
from dotenv import load_dotenv

load_dotenv()

try:
    print(os.getenv('REDIS_HOST'), os.getenv('REDIS_PORT'), os.getenv('REDIS_PWD'))
    client = redis.Redis(host = os.getenv('REDIS_HOST'), port = os.getenv('REDIS_PORT'), password = os.getenv('REDIS_PWD'))
    print('Connected to Redis !!')

except Exception as e:
    print('Error connecting to Redis: ', e)
    
def redis_instance():
    return client