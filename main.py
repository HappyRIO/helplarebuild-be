import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymilvus import MilvusClient

from search_engine import SearchEngine
# from indexer import Indexer

load_dotenv()

milvus_client = MilvusClient(
    uri=os.getenv("MILVUS_URI"),
    token=os.getenv("MILVUS_TOKEN")
)
milvus_collection_name = os.getenv("MILVUS_COLLECTION_NAME")

# indexer = Indexer(milvus_client, milvus_collection_name)
searchEngine = SearchEngine(milvus_client, milvus_collection_name)
print("running-----")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Include OPTIONS method
    allow_headers=["*"],
)

class Msg(BaseModel):
    msg: str

@app.get("/")
async def root():
    return {"message": "/search"}

@app.post("/search")
async def search(inp: Msg):
    result = searchEngine.search(inp.msg)
    return result

# @app.post("/create_index")
# async def create_index(inp: Msg):
#     result = indexer.index_website(inp.msg)
#     return { "message": "Indexing complete" }