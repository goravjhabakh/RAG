class BookNotFoundException(Exception):
    def __init__(self, id: int):
        self.id = id
        self.msg = f'Book with ID: {self.id} not found'
        super().__init__(self.msg)

class BookAlreadyExistsException(Exception):
    def __init__(self, id: int):
        self.id = id
        self.msg = f'Book with ID: {self.id} already exists'
        super().__init__(self.msg)

class NoBooksFoundException(Exception):
    def __init__(self):
        self.id = id
        self.msg = f'No books found'
        super().__init__(self.msg)