import os
import openai
import numpy as np
from dotenv import load_dotenv
load_dotenv()

client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
def create_embedding(text):
    print("embedding================================")
    embedding = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text,
        encoding_format="float"
    )

    embeddings_array = np.array([data.embedding for data in embedding.data])

    return embeddings_array[0]
