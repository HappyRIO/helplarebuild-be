import os
from dotenv import load_dotenv
load_dotenv()

bucket_name = os.getenv('BUCKET_NAME')
print(bucket_name)