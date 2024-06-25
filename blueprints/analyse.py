from apiflask import APIBlueprint, Schema, HTTPTokenAuth
from apiflask.fields import Integer, String, List, Nested
from databases.mongo import mongo_instance
from middleware.auth import auth_middleware
import uuid, datetime
from flask_cors import CORS
from flask import request
from controllers.analyse import execute_analyse
from helpers.mongo import cursor_to_dict
import threading

analyse_blueprint = APIBlueprint('analyse', __name__, tag = 'Analyse')
CORS(analyse_blueprint)

mongo_client = mongo_instance()
mongo_database = mongo_client.get_database("procure-sense")
analyse_collection = mongo_database.get_collection("analyse")

@analyse_blueprint.before_request
def middleware():
    if request.method == 'OPTIONS':
        return

    session_data = auth_middleware()
    if session_data is None:
        return { 'message': 'Unauthorized' }, 401
    else:
        request.user = session_data

class FetchAnalyseQuery(Schema):
    id = String(required=True)

class EditAnalyse(Schema):
    id = String(required=True)
    name = String(required=True)
    description = String(required=True)
    tags = List(String(required=True))

class RPScopeOfWork(Schema):
    index = Integer(required=True)
    quantity = Integer(required=True)
    description = String(required=True)

class PScopeOfWork(Schema):
    quantity = Integer(required=True)
    description = String(required=True)
    taxes = String(required=True)
    unit_price = String(required=True)
    total_price = String(required=True)
    price_before_taxes = String(required=True)

class RPContactInformation(Schema):
    raisedBy = String(required=True)
    contactDetail = String(required=True)

class PContactInformation(Schema):
    submittedBy = String(required=True)
    contactDetail = String(required=True)

class EditRP(Schema):
    id = String(required=True)
    companyName = String(required=True)
    companyAddress = String(required=True)
    releaseDate = String(required=True)
    contactInformation = Nested(RPContactInformation)
    deliveryTerms = List(String(required=True))
    paymentTerms = List(String(required=True))
    termsConditions = List(String(required=True))
    scopeOfWork = List(Nested(RPScopeOfWork))

class Proposal(Schema):
    companyAddress = String(required=True)
    companyName = String(required=True)
    contactInformation = Nested(PContactInformation)
    submissionDate = String(required=True)
    companyWebsite = String(required=True)
    companyEmail = String(required=True)
    deliveryTerms = List(String(required=True))
    paymentTerms = List(String(required=True))
    termsConditions = List(String(required=True))
    scopeOfWork = List(Nested(PScopeOfWork))
    keyBenefits = List(String(required=True))
    proposalImplementation = List(String(required=True))

class EditProposal(Schema):
    id = String(required=True)
    p_analyse = List(Nested(Proposal))

class APIHeader(Schema):
    Authorization = String(required=True)

@analyse_blueprint.get('/all')
@analyse_blueprint.input(APIHeader, location='headers')
def fetch_all_analyse(headers_data):
    try:
        user_id = request.user.get('id')
        projection = { 
            'name': True, 
            'id': True, 
            'description': True, 
            'created_at': True,
            'updated_at': True,
            'status': True,
            'stage': True,
            '_id': False 
        }
        analyse_data = analyse_collection.find(filter = { 'user_id': user_id }, projection = projection ).sort('updated_at', -1)
        analyse_data = cursor_to_dict(analyse_data)
        total_count = len(analyse_data) 

        return { 'message': 'Analyse fetched.', 'data': analyse_data, 'total': total_count }, 200
    except Exception as e:
        return { 'message': 'Error while fetching analyse !', 'error': str(e) }, 500

@analyse_blueprint.get('')
@analyse_blueprint.input(APIHeader, location='headers')
@analyse_blueprint.input(FetchAnalyseQuery, location='query')
def fetch_analyse_by_id(query_data, headers_data):
    try:
        id = query_data.get('id')
        user_id = request.user.get('id')
        print(f'User ID: {user_id}')
        analyse = analyse_collection.find_one(filter = { 'user_id': user_id, 'id': id }, projection = { '_id': False,})

        if not analyse:
            return { 'message': 'Analyse not found !' }, 404
        
        return { 'message': 'Request for proposal fetched.', 'data': analyse }, 200
    
    except Exception as e:
        print(e)
        return { 'message': 'Error while fetching analyse !' }, 500

def execute_analyse_background_task(rp_analyse, p_analyse, user_id, id):
    try: 
        analyse_result = execute_analyse(rp_analyse, p_analyse)
        analyse_collection.find_one_and_update({ "id": id, "user_id": user_id  }, {"$set": { "analyse": analyse_result, "status": "completed", 'stage': 5, "updated_at": str(datetime.datetime.now())}})
    except Exception as e:
        print(e)
        analyse_collection.find_one_and_update({ "id": id, "user_id": user_id  }, {"$set": { "status": "failed", 'stage': 5, "updated_at": str(datetime.datetime.now())}})

@analyse_blueprint.put('')
@analyse_blueprint.input(APIHeader, location='headers')
@analyse_blueprint.input(FetchAnalyseQuery, location='query')
def start_analyse(query_data, headers_data):
    try:
        id = query_data.get('id')
        user_id = request.user.get('id')

        analyse = analyse_collection.find_one(filter = { 'user_id': user_id, 'id': id }, projection = { '_id': False })
        
        if not analyse:
            return { 'message': 'Analyse not found !' }, 404
        
        rp_analyse = analyse.get('rp_analyse')
        p_analyse = analyse.get('p_analyse')
        status = analyse.get('status')

        if status == 'completed':
            return { 'message': 'Analyse already completed !' }, 200

        if not rp_analyse or not p_analyse:
            return { 'message': 'Request for proposal file or Proposal file not found !' }, 404

        analyse_collection.find_one_and_update({ "id": id, "user_id": user_id  }, {"$set": { "status": "processing", 'stage': 6, "updated_at": str(datetime.datetime.now())}})

        try:
            thread = threading.Thread(target=execute_analyse_background_task, args=(rp_analyse, p_analyse, user_id, id))
            thread.start()
            return { 'message': 'Analysing started successfully !' }, 201
        
        except Exception as e:
            print(e)
            return { 'message': 'Error while starting analysing !' }, 500

    except Exception as e:
        print(e)
        return { 'message': 'Error while analysing !' }, 500

@analyse_blueprint.get('/rp')
@analyse_blueprint.input(APIHeader, location='headers')
@analyse_blueprint.input(FetchAnalyseQuery, location='query')
def fetch_rp(query_data, headers_data):
    try:
        id = query_data.get('id')
        user_id = request.user.get('id')

        analyse = analyse_collection.find_one(filter = { 'user_id': user_id, 'id': id }, projection = { '_id': False })

        if not analyse or not analyse['rp_analyse']:
            return { 'message': 'Request for proposal file not found !' }, 404
        
        analyse_data = {
            'name': analyse['name'],
            'description': analyse['description'],
            'tags': analyse['tags']
        }

        return { 'message': 'Request for proposal fetched.', 'data': { 'rp': analyse['rp_analyse'], 'analyse': analyse_data } }, 200
    
    except Exception as e:
        print(e)
        return { 'message': 'Error while fetching request for proposal !' }, 500

@analyse_blueprint.get('/p')
@analyse_blueprint.input(APIHeader, location='headers')
@analyse_blueprint.input(FetchAnalyseQuery, location='query')
def fetch_p(query_data, headers_data):
    try:
        id = query_data.get('id')
        user_id = request.user.get('id')

        analyse = analyse_collection.find_one(filter = { 'user_id': user_id, 'id': id }, projection = { '_id': False,})

        if not analyse or not analyse['p_analyse']:
            return { 'message': 'Proposal file not found !' }, 404
        
        return { 'message': 'Proposal fetched.', 'data': analyse['p_analyse'] }, 200
    
    except Exception as e:
        print(e)
        return { 'message': 'Error while fetching proposals !' }, 500

@analyse_blueprint.post('/edit/p')
@analyse_blueprint.input(APIHeader, location='headers')
@analyse_blueprint.input(EditProposal, location='json')
def edit_p(json_data, headers_data):
    try:
        user_id = request.user.get('id')
        id = json_data.get('id')
        p_analyse = json_data.get('p_analyse')

        analyse = analyse_collection.find_one(filter = { 'user_id': user_id, 'id': id })

        if not analyse:
            return { 'message': 'Analyse not found !' }, 404

        try:
            analyse_collection.find_one_and_update({ "id": id, "user_id": user_id  }, {"$set": { "p_analyse": p_analyse, "stage": 5, "updated_at": str(datetime.datetime.now()), "status": 'pending'}})
            return { 'message': 'Proposal edited successfully !' }, 201
        
        except Exception as e:
            print(e)
            return { 'message': 'Error while editing proposal !' }, 500

    except Exception as e:
        print(e)
        return { 'message': 'Error while editing proposal !' }, 500

@analyse_blueprint.post('/edit/rp')
@analyse_blueprint.input(APIHeader, location='headers')
@analyse_blueprint.input(EditRP, location='json')
def edit_rp(json_data, headers_data):
    try:
        user_id = request.user.get('id')
        id = json_data.get('id')

        analyse = analyse_collection.find_one(filter = { 'user_id': user_id, 'id': id })

        if not analyse:
            return { 'message': 'Analyse not found !' }, 404
        
        rp_analyse = {
            'companyName': json_data.get('companyName'),
            'companyAddress': json_data.get('companyAddress'),
            'releaseDate': json_data.get('releaseDate'),
            'deliveryTerms': json_data.get('deliveryTerms'),
            'paymentTerms': json_data.get('paymentTerms'),
            'termsConditions': json_data.get('termsConditions'),
            'scopeOfWork': json_data.get('scopeOfWork'),
            'contactInformation': json_data.get('contactInformation')
        }

        try:
            analyse_collection.find_one_and_update({ "id": id, "user_id": user_id  }, {"$set": { "rp_analyse": rp_analyse, "stage": 3, "updated_at": str(datetime.datetime.now()), "status": 'pending'}})
            return { 'message': 'Request for proposal edited successfully !' }, 201
        
        except Exception as e:
            print(e)
            return { 'message': 'Error while editing request for proposal !' }, 500

    except Exception as e:
        print(e)
        return { 'message': 'Error while editing request for proposal !' }, 500

@analyse_blueprint.post('/edit')
@analyse_blueprint.input(APIHeader, location='headers')
@analyse_blueprint.input(EditAnalyse, location='json')
def edit_analyse(json_data, headers_data):
    try:
        user_id = request.user.get('id')
        id = json_data.get('id')

        analyse = analyse_collection.find_one(filter = { 'user_id': user_id, 'id': id })

        if not analyse:
            return { 'message': 'Analyse not found !' }, 404

        try:
            analyse_collection.find_one_and_update({ "id": id, "user_id": user_id  }, {"$set": { "name": json_data.get('name'), "description": json_data.get('description'), "tags": json_data.get('tags'), "updated_at": str(datetime.datetime.now()), "status": 'pending', "stage": 3 }})
            return { 'message': 'Analyse edited successfully !' }, 201
        
        except Exception as e:
            print(e)
            return { 'message': 'Error while editing analyse !' }, 500

    except Exception as e:
        print(e)
        return { 'message': 'Error while editing analyse !' }, 500

@analyse_blueprint.delete('')
@analyse_blueprint.input(APIHeader, location='headers')
@analyse_blueprint.input(FetchAnalyseQuery, location='query')
def delete_analyse(query_data, headers_data):
    try:
        id = query_data.get('id')
        user_id = request.user.get('id')

        analyse = analyse_collection.find_one(filter = { 'user_id': user_id, 'id': id })

        if not analyse:
            return { 'message': 'Analyse not found !' }, 404

        try:
            analyse_collection.delete_one({ "id": id, "user_id": user_id })
            return { 'message': 'Analyse deleted successfully !' }, 200
        
        except Exception as e:
            print(e)
            return { 'message': 'Error while deleting analyse !' }, 500

    except Exception as e:
        print(e)
        return { 'message': 'Error while deleting analyse !' }, 500