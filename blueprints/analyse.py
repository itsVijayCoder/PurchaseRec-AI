from apiflask import APIBlueprint, Schema, HTTPTokenAuth
from apiflask.fields import String
from databases.mongo import mongo_instance
from middleware.auth import auth_middleware
import uuid
from flask import request

analyse_blueprint = APIBlueprint('analyse', __name__, tag = 'Analyse')

mongo_client = mongo_instance()
mongo_database = mongo_client.get_database("procure-sense")
analyse_collection = mongo_database.get_collection("analyse")

@analyse_blueprint.before_app_request
def middleware():
    session_data = auth_middleware()
    if session_data is None:
        return { 'message': 'Unauthorized' }, 401
    else:
        request.user = session_data

@analyse_blueprint.post('/init')
def analyse_init():
    return { 'message': 'Analyse endpoint.' }, 200
