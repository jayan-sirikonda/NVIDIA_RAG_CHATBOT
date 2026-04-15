FROM python:3.11-slim

WORKDIR /app

# Install dependencies (FAISS needs libomp for parallel execution in some distros, though cpu is fine)
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the backend Application on port 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
