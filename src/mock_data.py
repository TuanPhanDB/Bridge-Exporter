import chromadb 
import random
import time
from datetime import datetime, timedelta, timezone

#Connect to chronodb
client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_or_create_collection("us_solar_leads")

num_docs = 100
documents = []
metadatas = []
ids = []

for i in range(num_docs):
    doc_id = f"This is a lead-{i}"
    income = random.randint(10000, 100000)
    created_at = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))

    documents.append(f"This is info of lead-{i}")
    metadatas.append({
        "income": income,
        "created_at": created_at.isoformat()
    })
    ids.append(doc_id)

#Add data to collection
collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

print("Data added.")