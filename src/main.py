import os 
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

embedding_function = HuggingFaceEmbeddings
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
client = MongoClient(MONGO_URI)
db = client['rag_db']
collection = db['docs']
print(f'Connected to database')

vector_store = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=embedding_model,
    index_name='vector_index'
)
print('Ready for vector search')

query = input('Enter query: ')
results = vector_store.similarity_search(query, k=3)

print(results)