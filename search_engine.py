from common_helper import create_embedding
import openai
import os
from dotenv import load_dotenv
load_dotenv()

class SearchEngine:
    def __init__(self, milvus_client, milvus_collection_name):
      self.milvus_client = milvus_client
      self.milvus_collection_name = milvus_collection_name
  
    def query_milvus(self, embedding):
        result_count = 5
        print(f"=query_milvus================{self.milvus_collection_name}============={embedding}")
        result = self.milvus_client.search(
            collection_name=self.milvus_collection_name,
            data=[embedding],
            limit=result_count,
            output_fields=["path", "text"],
            search_params={"metric_type": "IP","params": {}}
        )
            
  
        list_of_knowledge_base = list(map(lambda match: match['entity']['text'], result[0]))
        list_of_sources = list(map(lambda match: match['entity']['path'], result[0]))
        # print(result)
        return {
            'list_of_knowledge_base': list_of_knowledge_base,
            'list_of_sources': list_of_sources
        }
  
    def query_vector_db(self, embedding):
        return self.query_milvus(embedding)
  
    def ask_chatgpt(self, knowledge_base, user_query):
        system_content = """You are an AI assistant for Help LA Rebuild. Your role is to retrieve and summarize information from the provided database of curated resources including official weblinks, PDF’s, and verified information related to the LA wildfires. 
        Your role is to listen to the user, understand their needs, process their question and retrieve information from the database to assist them in finding correct resources that answer their question.
        You structure responses with direct answers and links to each resource and suggest follow-up steps if relevant. 
        Answer all questions simply and correctly, providing accurate, efficient, helpful, and friendly replies at all times. 
        If a query is ambiguous, ask for clarification and if no relevant resource is found in the database, ask the user if their question is related to LA wildfire recovery.
        Only answer questions using information found in the database provided and nothing else. 
        Log all queries to improve future responses.
        """
  
        user_content = f"""
            Knowledge Base:
            ---
            {knowledge_base}
            ---
            User Query: {user_query}
            Answer:
        """
        system_message = {"role": "system", "content": system_content}
        user_message = {"role": "user", "content": user_content}
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
        client = openai.Client(api_key=OPENAI_API_KEY)
        chatgpt_response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            system_message,
            user_message
        ]
        )
        print(f"response of OpanAI===/n{chatgpt_response.choices[0].message.content}")
        # chatgpt_response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613", messages=[system_message, user_message])
        return chatgpt_response.choices[0].message.content
  
    def search(self, user_query):
        embedding = create_embedding(user_query)
        print("embedging======================")
        result = self.query_vector_db(embedding)
        print("result======================")
  
        print("sources")
        for source in result['list_of_sources']:
            print(source)
  
        knowledge_base = "\n".join(result['list_of_knowledge_base'])
        response = self.ask_chatgpt(knowledge_base, user_query)
  
        return {
            'sources': result['list_of_sources'],
            'response': response
        }
  