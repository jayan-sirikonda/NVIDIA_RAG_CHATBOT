from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.api.models import IngestRequest
from backend.services.ingest_service import ingest_documents

router = APIRouter()

@router.post("/", status_code=202)
async def ingest_endpoint(request: IngestRequest, background_tasks: BackgroundTasks):
    if not request.documents:
        raise HTTPException(status_code=400, detail="Documents list cannot be empty")
        
    # Queue ingestion job rather than blocking request
    background_tasks.add_task(ingest_documents, request.documents)
    return {"status": "accepted", "message": f"Processing {len(request.documents)} documents in background."}
