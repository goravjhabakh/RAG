import os
from tqdm import tqdm 
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
import re
from transformers import GPT2TokenizerFast
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch

tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
print('Initialized Tokenizer Model')

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print('Initialized Embedding Model')

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')

# 1. Convert pdfs to markdown file
def convert_to_markdown(input_folder, output_folder):
    converter = PdfConverter(artifact_dict=create_model_dict())
    converted = 0
    print('Starting conversion from pdf to markdown...')
    res = []

    loop = tqdm(os.listdir(input_folder), desc='Conveting PDFs', unit='file')
    for doc in loop:
        output_path = os.path.join(output_folder,doc.replace('.pdf','.md'))
        res.append(output_path)
        if doc.replace('.pdf','.md') in os.listdir(output_folder): continue

        rendered = converter(os.path.join(input_folder,doc))
        text, metadata, images = text_from_rendered(rendered)

        with open(output_path,'w',encoding='utf-8') as md:
            md.write(text)
        converted += 1

    print(f'Converted {converted} to markdown')
    return res

# 2. Split the markdown files by headers
def split_by_headers(text, min_level=2):
    pattern = rf"\n(?=(#{{{min_level},}} ))"
    crude_sections = [s.strip() for s in re.split(pattern, text) if s.strip()]

    sections = []
    loop = tqdm(crude_sections, desc='Cleaning Header Sections', unit='section')
    for section in loop:
        lines = section.strip().splitlines()
        if not lines: continue
        if len(lines) > 1 or (len(lines) == 1 and not re.match(r"#+", lines[0])):
            sections.append(section)
    return sections

# 3. Token-based chunking with overlap
def chunk_by_tokens(text, max_tokens = 300, overlap = 50):
    tokens = tokenizer.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk = tokenizer.decode(tokens[start:end])
        chunks.append(chunk)
        start += max_tokens - overlap
    return chunks

def chunk_md(text, max_tokens = 300, overlap = 50, min_level = 2):
    headers_sections = split_by_headers(text, min_level=min_level)
    chunks = []
    for section in headers_sections:
        subchunk = chunk_by_tokens(section, max_tokens=max_tokens, overlap=overlap)
        chunks.extend(subchunk)
    return chunks

def store(chunks, embedding_model):
    client = MongoClient('mongodb+srv://goravjhabakh1301:rarr9Zkq42OJ5csB@rag.1vunq22.mongodb.net/')
    print(client)
    db = client['rag']
    collection = db['documents']
    print('Finished Setting up the databse...')
    print(f'Storing {len(chunks)} chunks')

    vectorstore = MongoDBAtlasVectorSearch(collection=collection, embedding=embedding_model, index_name = 'default')
    documents = [Document(page_content=chunk, metadata={"source": "pdf_file.md"}) for chunk in chunks]
    vectorstore.add_documents(documents)

pdf_path = 'docs'
md_path = 'rag/md'

if __name__ == '__main__':
    md_files = convert_to_markdown(pdf_path, md_path)
    chunks = []
    for md_file in md_files:
        with open(md_file,'r') as md:
            text = md.read()
        chunks.extend(chunk_md(text,max_tokens=300,overlap=50,min_level=1))
    print(f'Converted {len(md_files)} files to {len(chunks)} chunks')

    with open('sample.txt','w',encoding='utf-8') as f:
        for i,chunk in enumerate(chunks):
            f.write(f'Chunk {i+1}\n')
            f.write(chunk)
            f.write(f'\n\n')
    print('Wrote chunks to sample.txt')

    store(chunks, embedding_model)
    print('Stored chunks in mongodb database')