from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str
    content: str
    
class ChatRequest(BaseModel):
    messages: List[Message]
    
class Document(BaseModel):
    text: str
    metadata: dict = {}
    
class IngestRequest(BaseModel):
    documents: List[Document]
