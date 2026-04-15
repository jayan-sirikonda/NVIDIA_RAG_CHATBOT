from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.services.nvidia_service import generate_embeddings_documents
from backend.services.vector_store import vector_store
from backend.api.models import Document
from typing import List

# Using a standard chunk size suitable for QA
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

async def ingest_documents(documents: List[Document]) -> dict:
    """Chunk documents, generate embeddings, and store in FAISS."""
    all_chunks = []
    metadatas = []
    
    # Semantic chunking via LangChain's RecursiveCharacterTextSplitter
    for doc in documents:
        chunks = text_splitter.split_text(doc.text)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            meta = doc.metadata.copy()
            meta["text"] = chunk  # Store text in metadata for retrieval
            meta["chunk_id"] = i
            metadatas.append(meta)
            
    # Process in batches if there are many chunks to respect NIM limits
    BATCH_SIZE = 50 
    total_embeddings = []
    for i in range(0, len(all_chunks), BATCH_SIZE):
        batch_chunks = all_chunks[i:i + BATCH_SIZE]
        embeddings = await generate_embeddings_documents(batch_chunks)
        total_embeddings.extend(embeddings)
        
    await vector_store.add_embeddings(total_embeddings, metadatas)
    
    return {"status": "success", "chunks_added": len(all_chunks)}
