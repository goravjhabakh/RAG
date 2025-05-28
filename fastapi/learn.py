from fastapi import FastAPI, Path
from typing import Optional
from pydantic import BaseModel

# Instantiate a FastAPI object
app = FastAPI()

students = {
    1: {'name': 'Beast', 'age': 17},
    2: {'name': 'Gyan', 'age': 16},
    3: {'name': 'NSG', 'age': 13},
    4: {'name': 'Acid', 'age': 19},
    5: {'name': 'Djwoz', 'age': 20}
}

class Student(BaseModel):
    name: str
    age: int

# Different types of requests
# GET - get or return information
# POST = create something new
# PUT - update stuff
# DELETE - delete stuff

# Create an endpoint
@app.get('/')
def home_page():
    return {'data': 'Hello World!'}

# GET Method using path parameters
@app.get("/get-student/{id}")
def get_student(id: int = Path(description='Enter student id', gt=0, lt=6)): # If no path parameter then id becomes none or returns empty
    return students[id]

# Query Parameters
@app.get('/get-by-name')
def getByName(name: Optional[str] = None):
    for id in students:
        if students[id]['name'] == name:
            return students[id]
    return {'Data': 'Not Found'}

# Combining query and path params
@app.get('/student/{id}')
def student(id: Optional[int], name: Optional[str] = None):
    student = students.get(id)
    if not student:
        return {'error': 'Student not found'}
    
    if name and student['name'] != name:
        return {'error': 'Name does not match'}
    
    return student

# Request Body and POST Methods
@app.post('/create-student/{id}')
def create_student(id: int, student: Student):
    if id in students: return {'Error': 'Student already exists'}
    students[id] = student
    return students[id]