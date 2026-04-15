from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any
from backend.core.config import settings
import uuid
import os

class QdrantVectorStore:
    def __init__(self, dimension: int = 1024, collection_name: str = "georgia_tech_knowledge"):
        self.dimension = dimension
        self.collection_name = collection_name
        
        # Connect to Docker Qdrant if URL is set, else local memory/disk mode
        if settings.QDRANT_URL:
            self.client = AsyncQdrantClient(url=settings.QDRANT_URL)
        else:
            os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
            self.client = AsyncQdrantClient(path=settings.VECTOR_DB_PATH)

    async def initialize_collection(self):
        """Ensure collection exists."""
        exists = await self.client.collection_exists(self.collection_name)
        if not exists:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE),
            )

    async def add_embeddings(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        """Asynchronously insert embeddings into Qdrant."""
        if not embeddings:
            return
            
        await self.initialize_collection()
            
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=emb,
                payload=meta
            )
            for emb, meta in zip(embeddings, metadatas)
        ]
        
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    async def search(self, query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Asynchronously search top-k nearest neighbors."""
        await self.initialize_collection()
        
        search_result = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=k
        )
        
        results = []
        for hit in search_result.points:
            payload = hit.payload or {}
            payload["distance"] = hit.score
            results.append(payload)
            
        return results

# Singleton instance for API routes
vector_store = QdrantVectorStore()
