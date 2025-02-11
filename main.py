import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymilvus import MilvusClient

from search_engine import SearchEngine
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


load_dotenv()

milvus_client = MilvusClient(
    uri=os.getenv("MILVUS_URI"),
    token=os.getenv("MILVUS_TOKEN")
)
milvus_collection_name = os.getenv("MILVUS_COLLECTION_NAME")

searchEngine = SearchEngine(milvus_client, milvus_collection_name)

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
    result = searchEngine.search(inp.msg)
    return result

app.mount("/", StaticFiles(directory="static",html = True), name="static")