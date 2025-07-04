import os
import json
from dotenv import load_dotenv
from services.mongo import MongoDBClient
from services.reranker import RerankRetriever
from services.log import LOGGER
from services.chain import GetCheckQuery

from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import ChatGoogleGenerativeAI
from sentence_transformers import CrossEncoder
from langchain.prompts import PromptTemplate
from datetime import datetime

logger = LOGGER.get_logger()
load_dotenv()

client = MongoDBClient.get_client()
db = client['documents']
collection = db['test']

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
logger.info("Initialized embedding model")

reranker = CrossEncoder("BAAI/bge-reranker-base")
logger.info("Initialized reranker model")

API_KEY = os.getenv('GEMINI_KEY')
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=API_KEY)
logger.info("Initialized Gemini Flash 2.0 LLM")

check_query = GetCheckQuery.get_class(llm=llm)

async def handle_query(query: str):
    try:
        logger.info(f"Handling query: {query}")

        cquery = check_query.invoke(query)
        if not cquery['is_valid']: return cquery['reason']

        vectorstore = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embedding_model,
            index_name='vindex',
            embedding_key='embedding'
        )
        logger.info('Vector Store initialized')

        custom_prompt = PromptTemplate(
            input_variables= ['context', 'question', 'date'],
            template= ''' Provide a concise answer in plain text format 
            without markdown or special formatting. Follow these rules:
            1. Use only the context provided
            2. Answer in 1-3 short sentences
            3. Avoid line breaks
            4. Prioritize factual accuracy over completeness
            5. Allow for very basic questions such as greetings(assume other basic questions) to be answered manually even if its 
            does not match context (highest priority)
            6. If you feel the context has no match with query then give response accordingly 
            7. Make sure to use the current date if the query requires it and answer questions based on it
            8. If the query is not there in context then just say Could not find relevant information (least priority)

            Context: {context}
            Query: {question}
            Current Date: {date} '''
        )

        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        reranked_retriever = RerankRetriever(retriever=retriever, reranker=reranker, top_k=5)
        logger.info("Reranked retriever configured")

        # chain = RetrievalQA.from_chain_type(
        #     llm = llm, 
        #     retriever = reranked_retriever, 
        #     return_source_documents = True,
        #     chain_type = 'stuff',
        #     chain_type_kwargs = {
        #         'prompt': custom_prompt,
        #         'document_prompt': PromptTemplate(
        #             input_variables=['page_content'],
        #             template='{page_content}'
        #         )
        #     }
        # )
        # logger.info("RetrievalQA chain created")

        # res = chain.invoke({"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        # logger.info(res['result'])
        # return res

        docs = reranked_retriever.invoke(query)
        context = '\n'.join([doc.page_content for doc in docs])
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prompt = custom_prompt.format(context=context, question=query, date=date)
        response = llm.invoke(prompt)

        logger.info(f'AI Response: {response.content}')
        return response.content
    
    except Exception as e:
        logger.error(f"Error during query handling: {str(e)}", exc_info=True)
        raise

# Deploy for few days