from helpers.jwt import decode_jwt
from databases.redis import redis_instance
from flask import request

redis_client = redis_instance()

def auth_middleware():
    session_token = request.headers.get('Authorization')

    if session_token is None:
        return None

    session_token = session_token.replace('Bearer ', '')
    session_exist = redis_client.hgetall(f'ps-session:{session_token}')

    if session_exist is None:
        return None
    
    session_data = decode_jwt(session_token)

    return session_data
