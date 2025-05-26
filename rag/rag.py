import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains import RetrievalQA
from langchain_mongodb import MongoDBAtlasVectorSearch
from pprint import pprint
from langchain.chains import RetrievalQA
from langchain_core.retrievers import BaseRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
from sentence_transformers import CrossEncoder
from pydantic import Field
from typing import List
from langchain_core.documents import Document

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print('Initialized Embedding Model')

reranker = CrossEncoder('BAAI/bge-reranker-base')
print('Initialized Reranker Model')

load_dotenv()
MONGO_URI = 'mongodb+srv://goravjhabakh1301:rarr9Zkq42OJ5csB@rag.1vunq22.mongodb.net/' #os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['rag']
collection = db['documents']
print('Initialized database')

class RerankRetriever(BaseRetriever):
    retriever: BaseRetriever = Field(...)
    reranker: CrossEncoder = Field(...)
    top_k: int = 3

    def _get_relevant_documents(self, query: str) -> List[Document]:
        initial_docs = self.retriever.get_relevant_documents(query)
        pairs = [(query, doc.page_content) for doc in initial_docs]
        scores = self.reranker.predict(pairs)
        reranked = sorted(zip(scores, initial_docs), key=lambda x: x[0], reverse=True)
        return [doc for _, doc in reranked[:self.top_k]]

vectorstore = MongoDBAtlasVectorSearch(collection, embedding_model, index_name='sample', embedding_key='embedding')
print('Initialized search functionality')

key = os.getenv('GEMINI_KEY')
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
reranked_retriever = RerankRetriever(retriever=retriever, reranker=reranker, top_k=3)

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=key)
chain = RetrievalQA.from_chain_type(llm = llm, retriever = reranked_retriever, return_source_documents = True)

query = input('Query: ')
print('Retrieving data...')
result = chain.invoke(query)

with open('rag/output.md','w',encoding='utf-8') as md:
    md.write(result['result'])