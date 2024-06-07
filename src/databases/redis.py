import redis

def redis_connect():
    try:
        client = redis.Redis(host='redis-18483.c301.ap-south-1-1.ec2.redns.redis-cloud.com', port=18483, password='FG85zTUIbWBvHL9BB5d9cJusklEo1fWl')
        client.ping()
        print('Connected to Redis !!')
        return client
    except Exception as e:
        print('Error connecting to Redis: ', e)
        return None

def redis_disconnect(client):
    try: 
        client.connection_pool.disconnect()
        print('Disconnected from Redis !!')
    except Exception as e:
        print('Error disconnecting from Redis: ', e)
    