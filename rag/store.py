import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_mongodb import MongoDBAtlasVectorSearch

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print('Initialized Embedding Model')

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['rag']
collection = db['documents']
print('Initialized database')

# Load data
loader = DirectoryLoader('rag/docs', show_progress=True)
data = loader.load()
print('Loaded the data from documents')

# Split into chunks 
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", "!", "?", " ", ""]
)
documents = text_splitter.split_documents(data)
print(f'Split {len(data)} documents into {len(documents)} chunks')

vectorstore = MongoDBAtlasVectorSearch.from_documents(documents, embedding=embedding_model, collection=collection)
print('Stored data in database')

# After loading the chunks we need to create search index in mongo atlas in chrome