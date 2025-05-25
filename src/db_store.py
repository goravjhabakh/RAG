import os 
from dotenv import load_dotenv
from pymongo import MongoClient
from md import convert_to_markdown
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

pdf_folder = 'docs'
markdown_folder = 'markdown'

# Convert the documents to markdown
# convert_to_markdown(pdf_folder, markdown_folder)

# Load the markdown files using langchain
loader = DirectoryLoader(markdown_folder, glob='*.md')
documents = loader.load()

print(f'Loaded {len(documents)} documents')

# Chunking
text_spliiter = RecursiveCharacterTextSplitter(
    chunk_size = 200,
    chunk_overlap = 100,
    length_function = len,
    add_start_index = True
)

chunks = text_spliiter.split_documents(documents)
print(f'Split {len(documents)}documents into {len(chunks)} chunks')

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
vector_store.add_documents(chunks)
print('Embeddings stored in MongoDB Atlas')