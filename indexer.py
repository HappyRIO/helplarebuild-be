import os
from dotenv import load_dotenv
# from pymilvus import MilvusClient

from webpage_checker import WebPageChecker
from webpage_indexer import WebContentProcessor

class Indexer:
    def __init__(self, milvus_client, milvus_collection_name):
        load_dotenv()
              
        
        self.excel_file = os.getenv("URL_FILE_PATH")
        self.milvus_client = milvus_client
        self.milvus_collection = milvus_collection_name

    def run_indexers(self):
        if not self.excel_file or not self.milvus_collection:
            raise ValueError("Missing required environment variables: URL_FILE_PATH or MILVUS_COLLECTION")

        # Initialize indexers
        webpage_checker = WebPageChecker(self.excel_file)
        webpage_indexer = WebContentProcessor(self.excel_file, self.milvus_client, self.milvus_collection)

        # Run webpage checker first to validate URLs
        webpage_checker.url_checker()
        
        # Index valid webpages
        webpage_indexer.process_urls()