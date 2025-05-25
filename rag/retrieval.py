import os 
from pymongo import MongoClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print('Initialized Embedding Model')

client = MongoClient('mongodb+srv://goravjhabakh1301:rarr9Zkq42OJ5csB@rag.1vunq22.mongodb.net/')
db = client['sample_mflix']
collection = db['embedded_movies']
vectorstore = MongoDBAtlasVectorSearch(collection=collection, embedding=embedding_model, index_name = 'default')
print('Connected to Database')

query = input('Enter query: ')
results = vectorstore.similarity_search(query, k=3)
print(f'Got {len(results)} results')

with open('results.txt','w',encoding='utf-8') as f:
    for i,result in enumerate(results):
        f.write(f'Document {i+1}\n')
        f.write(f'Content: {result.page_content}\n\n')
print('Save results to results.txt')