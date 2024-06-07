from apiflask import APIBlueprint, Schema, HTTPError
from apiflask.fields import String, Email
from databases.mongo import mongo_instance
from databases.redis import redis_instance
import uuid
from helpers.jwt import decode_jwt, encode_jwt

auth_blueprint = APIBlueprint('auth', __name__, tag='Authentication')

mongo_client = mongo_instance()
mongo_database = mongo_client.get_database("procure-sense")
user_collection = mongo_database.get_collection("users")

redis_client = redis_instance()
redis_expiry = 24 * 60 * 60

class LoginSchema(Schema):
    email = Email(required=True)
    password = String(required=True)

class RegisterSchema(Schema):
    email = Email(required=True)
    password = String(required=True)
    firstName = String(required=True)
    lastName = String(required=True)

@auth_blueprint.post('/login')
@auth_blueprint.input(LoginSchema)
def login(json_data):
    try:
        user = user_collection.find_one({'email': json_data.get('email')})

        if not user:
            return { 'message': 'User not found.' }, 404

        decoded_db_pwd = decode_jwt(user.get('password'))
        decoded_user_pwd = decode_jwt(json_data.get('password'))

        if decoded_db_pwd.get('password') != decoded_user_pwd.get('password'):
            return { 'message': 'Invalid password.' }, 401

        user = {
            'id': user.get('id'),
            'email': user.get('email'),
            'firstName': user.get('firstName'),
            'lastName': user.get('lastName')
        }
        session_token = encode_jwt(user)

        redis_client.hset(f'ps-session:{session_token}', mapping = user)
        redis_client.expire(f'ps-session:{session_token}', time = redis_expiry)

        return { 'message': 'Login successful.', 'data': {'token': session_token }}, 200

    except Exception as e:
        return { 'message': 'Error while logging in.', 'error': str(e) }, 500

@auth_blueprint.post('/register')
@auth_blueprint.input(RegisterSchema)
def register(json_data):
    try:
        user_exist = user_collection.find_one({'email': json_data.get('email')})

        if user_exist:
            return { 'message': 'User already exists.' }, 409

        new_user = {
            'id':  str(uuid.uuid4()),
            'email': json_data.get('email'),
            'password': json_data.get('password'),
            'firstName': json_data.get('firstName'),
            'lastName': json_data.get('lastName')
        }

        user_collection.insert_one(new_user)

        user = {
            'id': new_user.get('id'),
            'email': json_data.get('email'),
            'firstName': json_data.get('firstName'),
            'lastName': json_data.get('lastName')
        }
        session_token = encode_jwt(user)

        redis_client.hset(f'ps-session:{session_token}', mapping = user)
        redis_client.expire(f'ps-session:{session_token}', time = redis_expiry)

        return { 'message': 'User registered successfully.', 'data': {'token': session_token } }, 201

    except Exception as e:
        return { 'message': 'Error while registering user.', 'error': str(e) }, 500

