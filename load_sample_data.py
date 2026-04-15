import asyncio
import json
from backend.services.ingest_service import ingest_documents
from backend.api.models import Document
import os

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Synthetic Georgia Tech Data
GT_DATA = [
    {
        "text": "The Georgia Institute of Eq Technology, commonly referred to as Georgia Tech, is a public research university and institute of technology in Atlanta, Georgia. It is part of the University System of Georgia.",
        "metadata": {"source": "Georgia Tech Overview", "category": "General"}
    },
    {
        "text": "The College of Computing at Georgia Tech is a leading college for computer science and related fields. It offers programs such as the top-ranked Master of Science in Computer Science (MSCS), including the popular Online Master of Science in Computer Science (OMSCS).",
        "metadata": {"source": "College of Computing", "category": "Academics"}
    },
    {
        "text": "Georgia Tech's mascot is Buzz, a yellow jacket. The official colors are Tech Gold and White, although Navy Blue is often used as a secondary color.",
        "metadata": {"source": "Student Life & Traditions", "category": "General"}
    },
    {
        "text": "To apply for undergraduate admission at Georgia Tech, prospective students can use the Common Application. Key factors for admission include academic rigor, GPA, standardized test scores (if required), extracurricular activities, and application essays. Early Action is available for both in-state and out-of-state students.",
        "metadata": {"source": "Undergraduate Admissions", "category": "Admissions"}
    },
    {
        "text": "Georgia Tech's library, the Price Gilbert Memorial Library and Crosland Tower, recently underwent a massive renovation. It is part of the Library Next project. Wait, the library does not hold many physical books on site anymore! It moved most of its collection to the Library Service Center operated jointly with Emory University, allowing for more study spaces.",
        "metadata": {"source": "Campus Facilities", "category": "Campus"}
    }
]

async def load_synthetic_data():
    print("Initializing Qdrant Vector Store with Synthetic GT Data...")
    docs = [Document(text=item["text"], metadata=item["metadata"]) for item in GT_DATA]
    
    try:
        result = await ingest_documents(docs)
        print(f"Success! {result}")
        print("Knowledge base ready. You can now run the backend server.")
    except Exception as e:
        print(f"Error during ingestion: {e}")
        print("Note: Ensure you have exported the NVIDIA_API_KEY environment variable.")

if __name__ == "__main__":
    asyncio.run(load_synthetic_data())
