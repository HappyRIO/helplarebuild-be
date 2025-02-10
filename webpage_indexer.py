import os
import math
import pandas as pd
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pymilvus import MilvusClient
from common_helper import create_embedding

class WebContentProcessor:
    def __init__(self, excel_file, milvus_client, collection_name, model_chunk_size=8192):
        self.excel_file = excel_file
        self.milvus_client = milvus_client
        self.collection_name = collection_name
        self.failed_urls = []
        self.model_chunk_size = model_chunk_size

    def read_urls_from_excel(self):
        """Reads URLs from the specified Excel file and returns them as a list."""
        df = pd.read_excel(self.excel_file, header=None)
        return df["URL"].tolist()

    def scrape_web_page(self, url):
        """Scrapes the content from a webpage or PDF and returns the extracted text."""
        if url.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(url)
        else:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup.get_text(separator='\n')  # Extract text, separating with newlines
            else:
                print(f"Failed to retrieve content from {url}, status code: {response.status_code}")
                self.failed_urls.append(url)
                return ''

    def extract_text_from_pdf(self, url):
        """Downloads a PDF and extracts text from it."""
        response = requests.get(url)
        if response.status_code == 200:
            temp_pdf_path = 'temp.pdf'
            with open(temp_pdf_path, 'wb') as f:
                f.write(response.content)
            text = self.read_pdf(temp_pdf_path)
            os.remove(temp_pdf_path)  # Remove the temporary PDF file after reading
            return text
        else:
            print(f"Failed to retrieve PDF from {url}, status code: {response.status_code}")
            return ''

    def read_pdf(self, file_path):
        """Reads a PDF file and returns the extracted text."""
        text = ''
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        except Exception as e:
            print(f"Error reading PDF file: {e}")
        return text

    def add_content_to_vectordb(self, content, url):
        """Process content and add embeddings to the vector database."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.model_chunk_size,
            chunk_overlap=math.floor(self.model_chunk_size / 10)
        )
        
        docs = text_splitter.create_documents([content])
        
        for doc in docs:
            embedding = create_embedding(doc.page_content)
            self.insert_embedding(embedding, doc.page_content, url)

    def insert_embedding(self, embedding, text, url):
        """Inserts the embedding and associated text into the vector database."""
        row = {
            'vector': embedding,
            'text': text,
            'path': url
        }
        
        self.milvus_client.insert(self.collection_name, data=[row])
        print(f"Inserted into collection: {self.collection_name} - URL: {url}")

    def process_urls(self):
        urls = self.read_urls_from_excel()
        for url in urls:
            content = self.scrape_web_page(url)
            if content:
                self.add_content_to_vectordb(content, url)

# if __name__ == "__main__":
#     excel_file = 'first.xlsx'
#     milvus_client = MilvusClient(uri="https://in03-db4abcb440194ad.serverless.gcp-us-west1.cloud.zilliz.com",
#                                   token="5187d07c9a94be76400415936a302c0ffb8e4fb7fe52c9f6493eadedd1b01c22a82a1efc7beef2ce838d9875ba70d191cf3820d6")
#     collection_name = "helplarebuild"
    
#     processor = WebContentProcessor(excel_file, milvus_client, collection_name)
#     processor.process_urls()
