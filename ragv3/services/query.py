import os
from dotenv import load_dotenv
from services.mongo import MongoDBClient
from services.reranker import RerankRetriever
from logs.main import LOGGER

from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import ChatGoogleGenerativeAI
from sentence_transformers import CrossEncoder

logger = LOGGER.get_logger()

client = MongoDBClient.get_client()
db = client['documents']
collection = db['collection1']

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
logger.info("Initialized embedding model")

reranker = CrossEncoder("BAAI/bge-reranker-base")
logger.info("Initialized reranker model")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key='AIzaSyChpkk6wgOTqcaz8RummEoy5q3bJoaY-c8')
logger.info("Initialized Gemini Flash 2.0 LLM")

async def handle_query(query: str):
    try:
        logger.info(f"Handling query: {query}")

        vectorstore = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embedding_model,
            index_name='vindex',
            embedding_key='embedding'
        )
        logger.info('Vector Store initialized')

        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        reranked_retriever = RerankRetriever(retriever=retriever, reranker=reranker, top_k=5)
        logger.info("Reranked retriever configured")

        chain = RetrievalQA.from_chain_type(llm = llm, retriever = reranked_retriever, return_source_documents = True)
        logger.info("RetrievalQA chain created")

        res = chain.invoke(query)
        return res
    
    except Exception as e:
        logger.error(f"Error during query handling: {str(e)}", exc_info=True)
        raise