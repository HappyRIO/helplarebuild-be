import os
from dotenv import load_dotenv
import math
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pymilvus import MilvusClient
from common_helper import create_embedding

load_dotenv()

class PDFProcessor:
    def __init__(self, pdf_dir, milvus_client, model_chunk_size = 8192):
        self.pdf_dir = pdf_dir
        self.bucket_name = os.getenv('BUCKET_NAME')
        self.model_chunk_size = model_chunk_size
        self.milvus_collection_name = os.getenv('MILVUS_COLLECTION_NAME')
        self.milvus_client = milvus_client

    def read_single_pdf(self, file_path):
        text = ''
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text

    def add_pdf_to_vectordb(self, content, path):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.model_chunk_size,
            chunk_overlap=math.floor(self.model_chunk_size / 10)
        )

        docs = text_splitter.create_documents([content])

        for doc in docs:
            embedding = create_embedding(doc.page_content)
            self.insert_embedding(embedding, doc.page_content, path)

    def insert_embedding(self, embedding, text, path):
        url = 'https://storage.googleapis.com/' + self.bucket_name + '/' + path
        row = {
            'vector': embedding,
            'text': text,
            'path': url
        }

        self.milvus_client.insert(self.milvus_collection_name, data=[row])
        print(f"Inserted into collection: {self.milvus_collection_name} - Path: {path}")

    def read_pdf_files(self):
        for filename in os.listdir(self.pdf_dir):
            if filename.endswith('.pdf'):
                file_path = os.path.join(self.pdf_dir, filename)
                text = self.read_single_pdf(file_path)
                self.add_pdf_to_vectordb(text, filename)


# Initialize parameters and create an instance of the PDFProcessor class
pdf_dir = 'pdf'
# model_chunk_size = 8192

bucket_name = os.getenv('BUCKET_NAME')
milvus_collection_name = os.getenv('MILVUS_COLLECTION_NAME')
milvus_uri = os.getenv('MILVUS_URI')
milvus_token = os.getenv('MILVUS_TOKEN')
milvus_client = MilvusClient(uri=milvus_uri, token=milvus_token)

pdf_processor = PDFProcessor(pdf_dir, milvus_client)
pdf_processor.read_pdf_files()
