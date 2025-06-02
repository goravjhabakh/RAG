from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# Base structure for book
class Book(BaseModel):
    id: int
    name: str
    author: str

# Useful for update operations
class BookUpdate(BaseModel):
    name: Optional[str]
    author: Optional[str]

books = {}

app = FastAPI(title='Book Management System')

# Making different endpoints for different operations
# 1. Create a book
@app.post('/create')
def create(book: Book):
    if book.id in books.keys(): return {'Error': 'Book already exists..'}
    books[book.id] = {'name': book.name, 'author': book.author}
    return {'Success': 'Book created..'}

# 2. Get a book
@app.get('/read/{id}')
def read(id: int):
    if id in books.keys(): return {id: books[id]}
    else: return {'Error', 'Book not Found'}

# 3. Get all books
@app.get('/read-all')
def read_all():
    return books

# 4. Update a book (FULL) using PUT
@app.put('/update/{id}')
def update(id: int, book: BookUpdate):
    if id in books.keys(): 
        books[id] = {'name': book.name, 'author': book.author}
        return {'Success': 'Book updated successfully..'}
    return {'Error': 'Book not found..'}

# 5. Update a book (PARTIAL) using PATCH
@app.patch('/update/{id}')
def patch(id: int, book:BookUpdate):
    if id not in books: return {'Error', 'Book not found'}
    for field in book:
        if book[field] != "": books[id][field] = book[field]
    return {'Success': 'Book Updatd sucessfully..'}

# 6. Delete a book
@app.delete('/delete/{id}')
def delete(id: int):
    if id not in books: return {'Error': 'Book not found..'}
    del books[id]
    return {'Success': 'Deleted book'}