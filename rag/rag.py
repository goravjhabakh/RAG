import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains import RetrievalQA
from langchain_mongodb import MongoDBAtlasVectorSearch
from pprint import pprint
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print('Initialized Embedding Model')

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['rag']
collection = db['documents']
print('Initialized database')

vectorstore = MongoDBAtlasVectorSearch(collection, embedding_model, index_name='sample', embedding_key='embedding')
print('Initialized search functionality')

key = os.getenv('GEMINI_KEY')
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=key)
chain = RetrievalQA.from_chain_type(llm = llm, retriever = retriever, return_source_documents = True)

query = input('Query: ')
print('Retrieving data...')
result = chain.invoke(query)

with open('rag/output.md','w',encoding='utf-8') as md:
    md.write(result['result'])