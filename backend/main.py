from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from backend.core.config import settings
from backend.api.routers import chat, ingest

# Implement IP based Rate Limiting (Protects external APIs)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)

# Apply limits
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["Chat"])
app.include_router(ingest.router, prefix=f"{settings.API_V1_STR}/ingest", tags=["Ingest"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Georgia Tech RAG Chatbot API is running."}
