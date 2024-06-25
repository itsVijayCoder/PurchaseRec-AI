import jwt, os
from dotenv import load_dotenv

load_dotenv()

def encode_jwt(payload):
    return jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm='HS256')

def decode_jwt(token):
    return jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
