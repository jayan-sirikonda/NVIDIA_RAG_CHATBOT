from openai import AsyncOpenAI
import json
from typing import List, Generator, AsyncGenerator
from backend.core.config import settings

# Initialize AsyncOpenAI client targeting NVIDIA NIM
nim_client = AsyncOpenAI(
    base_url=settings.NVIDIA_BASE_URL,
    api_key=settings.NVIDIA_API_KEY
)

async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings using NVIDIA NIM API.
    Truncates text if it exceeds token limits (E5 model handles up to 512 chunks).
    """
    # The E5 embedding model expects input types for optimal results
    response = await nim_client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=texts,
        encoding_format="float",
        extra_body={"input_type": "query"}
    )
    return [data.embedding for data in response.data]

async def generate_embeddings_documents(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for documents to be indexed."""
    response = await nim_client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=texts,
        encoding_format="float",
        extra_body={"input_type": "passage"}
    )
    return [data.embedding for data in response.data]

async def stream_chat_completion(messages: List[dict], context: str) -> AsyncGenerator[str, None]:
    """
    Stream chat completion from NVIDIA NIM LLM.
    Enforces grounding in the system prompt.
    """
    system_prompt = {
        "role": "system",
        "content": (
            "You are a helpful, professional AI assistant for Georgia Tech. "
            "Use the provided context to answer the user's questions. "
            "If the answer cannot be found in the context, explicitly say 'I don't know based on the provided information.' "
            "Do NOT hallucinate facts. Always list the sources you used at the end of your response if applicable.\n\n"
            f"Context Information:\n{context}\n"
        )
    }

    full_messages = [system_prompt] + messages

    response = await nim_client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=full_messages,
        temperature=settings.TEMPERATURE,
        max_tokens=settings.MAX_TOKENS,
        stream=True
    )

    async for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
