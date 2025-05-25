import os 
from dotenv import load_dotenv
from pymongo import MongoClient
from md import convert_to_markdown
from langchain_community.document_loaders import DirectoryLoader

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

pdf_folder = 'docs'
markdown_folder = 'markdown'

convert_to_markdown(pdf_folder, markdown_folder)

loader = DirectoryLoader(markdown_folder, glob='*.md')
documents = loader.load()

with open('test.txt','w',encoding='utf-8') as f:
    f.write(documents)