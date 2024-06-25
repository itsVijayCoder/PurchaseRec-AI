from apiflask import APIBlueprint, Schema
from apiflask.fields import File, String, List
from apiflask.validators import FileSize, FileType
from databases.mongo import mongo_instance
from middleware.auth import auth_middleware
from helpers.run import run_file_generation, run_file_deletion
import uuid, datetime, json
from flask import request
from bson import ObjectId
from flask_cors import CORS

from controllers.ingest import ingest_rp_document, ingest_p_document

ingest_blueprint = APIBlueprint('ingest', __name__, tag = 'Ingest')
CORS(ingest_blueprint)

mongo_client = mongo_instance()
mongo_database = mongo_client.get_database("procure-sense")
analyse_collection = mongo_database.get_collection("analyse")

@ingest_blueprint.before_request
def middleware():
    if request.method == 'OPTIONS':
        return
        
    session_data = auth_middleware()
    if session_data is None:
        return { 'message': 'Unauthorized' }, 401
    else:
        request.user = session_data

class IngestRFP(Schema):
    file = File(required=True, validate=[FileType(['.pdf']), FileSize(max='8 MB')])

class IngestProposal(Schema):
    file = List(File(required=True, validate=[FileType(['.pdf']), FileSize(max='8 MB')]))
    id = String(required=True)

class APIHeader(Schema):
    Authorization = String(required=True)

@ingest_blueprint.post('/rp')
@ingest_blueprint.input(APIHeader, location='headers')
@ingest_blueprint.input(IngestRFP, location='form_and_files')
def ingest_rp(form_and_files_data, headers_data):
    try:
        file = form_and_files_data['file']
        file_path = run_file_generation(file)
        
        rp_analyse = ingest_rp_document(file_path)

        run_file_deletion(file_path)

        try: 
            new_analyse_id = str(uuid.uuid4())
            new_analyse = {
                'user_id': str(request.user['id']),
                'status': 'pending',
                'stage': 2,
                'id': new_analyse_id,
                'tags': rp_analyse['tags'],
                'name': rp_analyse['name'],
                'description': rp_analyse['description'],
                'rp_analyse': {
                    'companyName': rp_analyse['companyName'],
                    'companyAddress': rp_analyse['companyAddress'],
                    'releaseDate': rp_analyse['releaseDate'],
                    'contactInformation': {
                        'raisedBy': rp_analyse['contactInformation']['raisedBy'],
                        'contactDetail': rp_analyse['contactInformation']['contactDetail']
                    },
                    'deliveryTerms': rp_analyse['deliveryTerms'],
                    'paymentTerms': rp_analyse['paymentTerms'],
                    'termsConditions': rp_analyse['termsConditions'],
                    'scopeOfWork': rp_analyse['scopeOfWork']
                },
                'created_at': str(datetime.datetime.now()),
                'updated_at': str(datetime.datetime.now())
            }
            analyse_collection.insert_one(new_analyse)
            return { 'message': f'File uploaded successfully !', 'data': { 'id': new_analyse_id } }, 201
        
        except Exception as e:
            print(e)
            return { 'message': 'Error while uploading file. Please try again !' }, 410
    
    except Exception as e:
        print(e)
        return { 'message': 'Internal server error. Please try again !' }, 500


@ingest_blueprint.post('/p')
@ingest_blueprint.input(APIHeader, location='headers')
@ingest_blueprint.input(IngestProposal, location='form_and_files')
def ingest_proposal(form_and_files_data, headers_data):
    try:
        files = form_and_files_data['file']
        id = form_and_files_data['id']
        user_id = request.user['id']
        proposal_analyse = []

        for file in files:
            file_path = run_file_generation(file)
            
            analyse = ingest_p_document(file_path)
            proposal_analyse.append(analyse)

            run_file_deletion(file_path)

        try:
            analyse_collection.find_one_and_update({ "id": id, "user_id": user_id }, { "$set": { "p_analyse": proposal_analyse, 'updated_at': str(datetime.datetime.now()), 'stage': 4 }})
            return { 'message': f'File uploaded successfully !', 'data': { 'id': id } }, 201

        except Exception as e:
            print(e)
            return { 'message': 'Error while uploading file. Please try again !' }, 410
    
    except Exception as e:
        print(e)
        return { 'message': 'Internal server error. Please try again !' }, 500