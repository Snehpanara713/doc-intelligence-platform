from fastapi import FastAPI, HTTPException
from app.models.envelope import Envelope
from app.services.validation_service import validate_envelope
from app.services.matching_service import match_commodity
from app.services.pipeline_service import process_pipeline

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "doc-intel", "version": "1.0"}

@app.post("/validate")
async def validate(envelope: Envelope):
    try:
        return await validate_envelope(envelope)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.post("/match")
async def match(envelope: Envelope):
    return await match_commodity(envelope)

@app.post("/process")
async def process(envelope: Envelope):
    try:
        return await process_pipeline(envelope)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))