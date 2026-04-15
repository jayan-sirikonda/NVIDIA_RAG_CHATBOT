from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from backend.api.models import ChatRequest
from backend.services.nvidia_service import generate_embeddings, stream_chat_completion
from backend.services.vector_store import vector_store
from backend.services.cache import cache

router = APIRouter()

@router.post("/")
async def chat_endpoint(request: Request, body: ChatRequest):
    if not body.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty")
        
    user_query = body.messages[-1].content
    
    # 1. Check Semantic Cache
    cached_reply = await cache.get(user_query)
    if cached_reply:
         return StreamingResponse(
            (chunk for chunk in cached_reply),
            media_type="text/event-stream"
         )
    
    # 2. Retrieve context asynchronously via Qdrant
    try:
        query_embedding = (await generate_embeddings([user_query]))[0]
        search_results = await vector_store.search(query_embedding, k=5)
        
        context = ""
        for i, res in enumerate(search_results):
            source = res.get('source', 'Unknown Source')
            text = res.get('text', '')
            context += f"\n[Source {i+1}: {source}]\n{text}\n"
            
        if not context:
            context = "No relevant context found in the database."
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

    api_messages = [{"role": msg.role, "content": msg.content} for msg in body.messages]

    # Intercept chunks to save into cache seamlessly while streaming
    async def caching_streaming_generator():
        full_response_buffer = []
        async for chunk in stream_chat_completion(api_messages, context):
            full_response_buffer.append(chunk)
            yield chunk
        # Save aggregated string to Redis in background
        await cache.set(user_query, "".join(full_response_buffer))

    return StreamingResponse(
        caching_streaming_generator(),
        media_type="text/event-stream"
    )
