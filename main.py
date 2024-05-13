from fastapi import FastAPI, UploadFile, File
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
import uuid

from database.mongo import mongo_connect
from helpers.run import run_temp_file_generation, run_temp_file_deletion
from controllers.ingest import ingest_rp_document, ingest_p_document

app = FastAPI()
mongo_client = mongo_connect()

mongo_database = mongo_client.get_database("procure-sense")
mongo_collection = mongo_database.get_collection("analysis")

@app.post("/api/init-analyse", tags=["Analyse"], name="Initialize analysis")
async def init_analyze(analysisType: str, analysisName: str, analysisDescription: str, analysisTags: list):
    try:
        analysisId = str(uuid.uuid4())
        analysis = {
            "analysisId": analysisId,
            "analysisType": analysisType,
            "analysisName": analysisName,
            "analysisDescription": analysisDescription,
            "analysisTags": analysisTags
        }
        try:
            response = mongo_collection.insert_one(analysis)
            return JSONResponse(content={"analysisId": analysisId}, status_code=200)
        
        except Exception as e:
            raise HTTPException(status_code=410, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=410, detail=str(e))

@app.post("/api/ingest-rp", tags=["Ingest"], name="Ingest request for proposal")
async def ingest_rp(analysisId: str, file: UploadFile = File()):
    try:
        temp_file_path = await run_temp_file_generation(file)
        result = ingest_rp_document(temp_file_path)

        mongo_collection.find_one_and_update({ "analysisId": analysisId }, {"$set": {"rpData": result}})

        await run_temp_file_deletion(temp_file_path)

    
    except ValueError as e:
        raise HTTPException(status_code=410, detail=str(e))

@app.post("/api/ingest-p", tags=["Ingest"], name="Ingest proposal")
async def ingest_p(analysisId: str, file: UploadFile = File()):
    try:
        temp_file_path = await run_temp_file_generation(file)
        result = ingest_p_document(temp_file_path)
        mongo_collection.find_one_and_update({ "analysisId": analysisId }, {"$set": {"pContent": result}})
    
    except ValueError as e:
        raise HTTPException(status_code=410, detail=str(e))

@app.post("/api/start-analyse", tags=["Analyse"], name="Start analysis")
async def start_analyse(analysisId: str):
    pass

@app.post("/api/analyse-result", tags=["Analyse"], name="Get analysis result")
async def analyse_result(analysisId: str):
    pass