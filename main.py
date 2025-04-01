import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pymilvus import MilvusClient
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

from search_engine import SearchEngine
from indexer import Indexer

milvus_client = MilvusClient(
            uri=os.getenv("MILVUS_URI"),
            token=os.getenv("MILVUS_TOKEN")
        )
milvus_collection_name = os.getenv("MILVUS_COLLECTION_NAME")

indexer = Indexer(milvus_client, milvus_collection_name)
searchEngine = SearchEngine(milvus_client, milvus_collection_name)

print("✅ Server is running...")

### API for indexing & AI search
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Include OPTIONS method
    allow_headers=["*"],
)

class Msg(BaseModel):
    msg: str

@app.post("/api/search")
async def search(inp: Msg):
    search_result = searchEngine.search(inp.msg)

    return search_result

@app.post("/api/create_index")
async def create_index(inp: Msg):
    indexer.index_website(inp.msg)
    return {"message": "✅ Indexing complete"}

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")
