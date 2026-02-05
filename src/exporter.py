import chromadb
import time, json
import asyncio
import random
from fastapi import FastAPI
from datetime import datetime, timedelta, timezone
from prometheus_client import Gauge, Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

app = FastAPI()
# Connect to chronodb
client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_collection("us_solar_leads")

# Prometheus metrics
total_docs_gauge = Gauge("chroma_total_docs", "Total documents in collection")
high_income_gauge = Gauge("chroma_high_income", "Total leads with income > 75k")
latency_gauge = Gauge("chroma_query_latency", "Latency of vector search vector in ms")
status_gauge = Gauge("chroma_exporter_status", "Exporter status (1 = ok, 0 = error)")
total_docs_counter = Counter("chroma_doc_counter", "Count docs for rating")

last_total_docs = None

async def exporter():
    global last_total_docs
    while True:
        try:
            # Total Documents Count
            total_docs = collection.count()
            total_docs_gauge.set(total_docs)

            # Metadata Distribution
            income_limit = 75000
            lead_incomes = collection.get(where={"income": { "$gt": income_limit}})
            high_income_gauge.set(len(lead_incomes["ids"]))

            # Heartbeat/Latency
            start = time.time()
            # Test query to capture latency
            test_query = collection.query(query_texts=["Time taken"], n_results=1)
            latency = (time.time() - start) * 1000
            latency_gauge.set(round(latency, 2))

            status_gauge.set(1)

            if last_total_docs is None:
                last_total_docs = total_docs
            else:
                new_docs = total_docs - last_total_docs
                if new_docs > 0:
                    total_docs_counter.inc(new_docs)
                last_total_docs = total_docs        

        except Exception as e:
            print("Exporter error: ", e)
            status_gauge.set(0)

        # Wait 5s
        await asyncio.sleep(5)

# Simulate new leads for visualization
async def simulate_incoming_leads():
    while True:
        try:
            # Get latest ids
            cnt = collection.get()
            latest_id = len(cnt["ids"])

            # Simulate 1-3 new leads
            new_docs = random.randint(1, 3)
            for i in range(new_docs):
                documents = [f"This is info of lead-{latest_id + i}"]
                metadatas = [{"income": random.randint(10000, 100000),
                          "created_at": datetime.now(timezone.utc).isoformat()}]
                
                ids = [f"This is a lead-{latest_id + i}"]
                collection.add(documents=documents, metadatas=metadatas, ids=ids)
                total_docs_counter.inc(1)
                print(f"Added lead-{latest_id + i}, counter now: {total_docs_counter._value._value}")
        except Exception as e:
            print("Simulate error:", e)
        await asyncio.sleep(5)

# Start background task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(exporter())
    asyncio.create_task(simulate_incoming_leads())

# Get endpoint
@app.get("/metrics")
def get_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }