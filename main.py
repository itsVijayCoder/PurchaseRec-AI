from fastapi import FastAPI, UploadFile, File
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid, json
from typing import List

from app.database.mongo import mongo_connect
from app.database.redis import redis_connect
from app.helpers.run import run_temp_file_generation, run_temp_file_deletion
from app.controllers.ingest import ingest_rp_document, ingest_p_document
from app.controllers.analyse import execute_analysis

app = FastAPI()

origins = [ "http://localhost", "http://localhost:8000" ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mongo_client = mongo_connect()
redis_client = redis_connect()

mongo_database = mongo_client.get_database("procure-sense")
user_collection = mongo_database.get_collection("user")
mongo_collection = mongo_database.get_collection("analysis")

@app.post("/api/v1/login", tags=["Authentication"], name="Home")
async def login():
    try:
        return JSONResponse(content={"message": "User logged in successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=410, detail=str(e))

@app.post("/api/v1/register", tags=["Authentication"], name="Register")
async def register():
    return JSONResponse(content={"message": "User registered successfully"}, status_code=200)


class InitAnalysis(BaseModel):
    analysisName: str
    analysisDescription: str
    analysisTags: List[str]

@app.post("/api/init-analyse", tags=["Analyse"], name="Initialize analysis")
async def init_analyze(payload: InitAnalysis):
    try:
        mongo_collection = mongo_database.get_collection("analysis")
        payload = payload.dict()
        analysisId = str(uuid.uuid4())
        analysis = {
            "analysisId": analysisId,
            "analysisName": payload.get('analysisName'),
            "analysisDescription": payload.get('analysisDescription'),
            "analysisTags": payload.get('analysisTags'),
        }
        try:
            response = mongo_collection.insert_one(analysis)
            return JSONResponse(content={"analysisId": analysisId}, status_code=200)
        
        except Exception as e:
            raise HTTPException(status_code=410, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=410, detail=str(e))

@app.post("/api/ingest-rp", tags=["Ingest"], name="Ingest request for proposal")
async def ingest_rp(analysisId: str, file: UploadFile):
    try:
        temp_file_path = await run_temp_file_generation(file)
        request_for_proposal = ingest_rp_document(temp_file_path)
        await run_temp_file_deletion(temp_file_path)

        mongo_collection.find_one_and_update({ "namespace": "poc" }, {"$set": {"result": request_for_proposal}})

        return JSONResponse(content={
            "message": "Request for proposal ingested successfully",
            "data": request_for_proposal
        }, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=410, detail=str(e))

@app.post("/api/ingest-p", tags=["Ingest"], name="Ingest proposal")
async def ingest_p(analysisId: str, files: List[UploadFile]):
    try:
        proposals = []

        for file in files:
            temp_file_path = await run_temp_file_generation(file)
            proposal = ingest_p_document(temp_file_path)
            proposals.append(proposal)
            await run_temp_file_deletion(temp_file_path)

        mongo_collection.find_one_and_update({ "analysisId": analysisId }, {"$set": {"proposals": proposals}})

        return JSONResponse(content={
            "message": "Proposals ingested successfully",
            "data": proposals
        }, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=410, detail=str(e))

@app.post("/api/start-analyse", tags=["Analyse"], name="Start analysis")
async def start_analyse(analysisId: str):
    try:
        analysis = mongo_collection.find_one({ "analysisId": analysisId })

        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        request_for_proposal = analysis.get("resquestForProposal")
        proposals = analysis.get("proposals")

        if request_for_proposal is None or proposals is None:
            raise HTTPException(status_code=410, detail="Request for proposal and proposals are required to start analysis")

        analysis_result = execute_analysis(request_for_proposal, proposals)

        mongo_collection.find_one_and_update({ "analysisId": analysisId }, {"$set": {"analysisResult": analysis_result}})

        return JSONResponse(content={
            "message": "Analysis completed successfully"
        }, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=410, detail=str(e))

@app.post("/api/get-analysis", tags=["Analyse"], name="Get analysis")
async def get_analysis(analysisId: str):
    try:
        analysis = mongo_collection.find_one({ "analysisId": analysisId })
        if analysis:
            analysis['_id'] = str(analysis['_id'])
            return JSONResponse(content={
                "message": "Analysis fetched successfully",
                "data": analysis
            }, status_code=200)
        else:
            return JSONResponse(content={
                "message": "Analysis not found",
                "data": {}
            }, status_code=404)
    
    except Exception as e:
        raise HTTPException(status_code=410, detail=str(e))