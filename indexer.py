import os
from dotenv import load_dotenv
from pymilvus import MilvusClient

from webpage_checker import WebPageChecker
from webpage_indexer import WebContentProcessor

load_dotenv()

# milvus_client = MilvusClient(
#     uri=os.getenv("MILVUS_URI"),
#     token=os.getenv("MILVUS_TOKEN")
# )
milvus_client = MilvusClient(uri="https://in03-db4abcb440194ad.serverless.gcp-us-west1.cloud.zilliz.com",
                                  token="5187d07c9a94be76400415936a302c0ffb8e4fb7fe52c9f6493eadedd1b01c22a82a1efc7beef2ce838d9875ba70d191cf3820d6")

excel_file = os.getenv("URL_FILE_PATH")
milvus_collection = os.getenv("MILVUS_COLLECTION")

def run_indexers():
    # Initialize indexers
    webpage_checker = WebPageChecker(excel_file)
    webpage_indexer = WebContentProcessor(excel_file, milvus_client, milvus_collection)
    # pdf_indexer = PDFIndexer()

    # Run webpage checker first to validate URLs
    webpage_checker.url_checker()

    # Index valid webpages
    webpage_indexer.process_urls()

if __name__ == "__main__":
    run_indexers()
