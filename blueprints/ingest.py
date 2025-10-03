from apiflask import APIBlueprint, Schema
from apiflask.fields import File, String, List
from apiflask.validators import FileSize, FileType
from databases.mongo import mongo_instance
from middleware.auth import auth_middleware
from helpers.run import run_file_generation, run_file_deletion
import uuid, datetime, json, os
from flask import request
from bson import ObjectId
from flask_cors import CORS
from langchain_openai import ChatOpenAI

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
        print(f"Processing file: {file.filename}")
        
        # Generate the temporary file
        file_path = run_file_generation(file)
        if not file_path:
            return { 'message': 'Failed to create temporary file for processing' }, 500
            
        print(f"Temporary file created at: {file_path}")
        
        try:
            print("Calling ingest_rp_document...")
            rp_analyse = ingest_rp_document(file_path)
            print("Document analysis completed successfully")
        except Exception as analysis_error:
            print(f"Document analysis error: {analysis_error}")
            # Clean up on error
            if file_path:
                run_file_deletion(file_path)
            return { 'message': f'Error analyzing document: {str(analysis_error)}' }, 500

        # Clean up temporary file
        try:
            if file_path:
                run_file_deletion(file_path)
                print("Temporary file deleted")
        except Exception as file_del_error:
            print(f"File deletion warning (non-critical): {file_del_error}")

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
            
            print("Saving analysis to MongoDB...")
            result = analyse_collection.insert_one(new_analyse)
            print(f"MongoDB insert result: {result.inserted_id}")
            
            return { 'message': f'File uploaded successfully!', 'data': { 'id': new_analyse_id } }, 201
        
        except Exception as db_error:
            print(f"Database error: {db_error}")
            import traceback
            print(traceback.format_exc())
            return { 'message': f'Error saving analysis to database: {str(db_error)}' }, 500
    
    except Exception as e:
        print(f"General error in ingest_rp: {e}")
        import traceback
        print(traceback.format_exc())
        return { 'message': f'Internal server error: {str(e)}' }, 500


@ingest_blueprint.post('/p')
@ingest_blueprint.input(APIHeader, location='headers')
@ingest_blueprint.input(IngestProposal, location='form_and_files')
def ingest_proposal(form_and_files_data, headers_data):
    try:
        files = form_and_files_data['file']
        print(f"Processing {len(files)} file(s)")
        id = form_and_files_data['id']
        print(f"Analysis ID: {id}")
        user_id = request.user['id']
        proposal_analyse = []
        
        # Track file paths for cleanup
        file_paths = []

        for index, file in enumerate(files):
            print(f"Processing file {index+1}/{len(files)}: {file.filename}")
            
            # Generate the temporary file
            file_path = run_file_generation(file, True)
            if not file_path:
                # Clean up any previously created files
                for path in file_paths:
                    run_file_deletion(path)
                return { 'message': f'Failed to create temporary file for processing file {file.filename}' }, 500
                
            print(f"Temporary file created at: {file_path}")
            file_paths.append(file_path)
            
            try:
                print(f"Analyzing file {index+1}/{len(files)}...")
                analyse = ingest_p_document(file_path)
                print(f"Analysis for file {index+1} completed successfully")
                proposal_analyse.append(analyse)
            except Exception as analysis_error:
                print(f"Document analysis error: {analysis_error}")
                # Clean up all files on error
                for path in file_paths:
                    run_file_deletion(path)
                return { 'message': f'Error analyzing document {file.filename}: {str(analysis_error)}' }, 500

        # Clean up all temporary files
        for path in file_paths:
            try:
                run_file_deletion(path)
            except Exception as file_del_error:
                print(f"File deletion warning (non-critical): {file_del_error}")
                
        print("All temporary files deleted")

        try:
            print("Saving analysis to MongoDB...")
            result = analyse_collection.find_one_and_update(
                { "id": id, "user_id": user_id }, 
                { "$set": { 
                    "p_analyse": proposal_analyse, 
                    'updated_at': str(datetime.datetime.now()), 
                    'stage': 4 
                }}
            )
            
            if not result:
                return { 'message': f'No analysis found with ID {id} for current user' }, 404
                
            print(f"MongoDB update successful for analysis ID: {id}")
            return { 'message': f'Files uploaded successfully!', 'data': { 'id': id } }, 201

        except Exception as db_error:
            print(f"Database error: {db_error}")
            import traceback
            print(traceback.format_exc())
            return { 'message': f'Error saving analysis to database: {str(db_error)}' }, 500
    
    except Exception as e:
        print(f"General error in ingest_proposal: {e}")
        import traceback
        print(traceback.format_exc())
        return { 'message': f'Internal server error: {str(e)}' }, 500

@ingest_blueprint.route('/diagnostic', methods=['GET'])
def diagnostic():
    try:
        # Test MongoDB connection
        mongo_status = "OK"
        try:
            result = mongo_client.admin.command('ping')
            mongo_details = "Connection successful"
        except Exception as mongo_error:
            mongo_status = "ERROR"
            mongo_details = str(mongo_error)
        
        # Test OpenAI connection
        openai_status = "OK"
        try:
            model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
            response = model.invoke("Return just the word 'connected' as a test")
            if "connect" not in response.content.lower():
                openai_status = "ERROR"
                openai_details = f"Unexpected response: {response.content}"
            else:
                openai_details = "Connection successful"
        except Exception as openai_error:
            openai_status = "ERROR"
            openai_details = str(openai_error)
            
        # Return diagnostic info
        return {
            "status": "Service diagnostic completed",
            "timestamp": str(datetime.datetime.now()),
            "services": {
                "mongodb": {
                    "status": mongo_status,
                    "details": mongo_details
                },
                "openai": {
                    "status": openai_status,
                    "details": openai_details
                }
            },
            "environment": {
                "mongodb_uri": os.getenv('MONGO_URI', 'Not set').replace(
                    os.getenv('MONGO_URI', '').split('@')[-1] if '@' in os.getenv('MONGO_URI', '') else '', 
                    '****'
                ),
                "openai_key": os.getenv('OPENAI_API_KEY', 'Not set')[:5] + "..." if os.getenv('OPENAI_API_KEY') else "Not set",
                "docker": "Running in container"
            }
        }
    except Exception as e:
        return {
            "status": "Diagnostic error",
            "error": str(e)
        }, 500