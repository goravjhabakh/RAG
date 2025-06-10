import unittest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

class Tester(unittest.TestCase):
    def test_existing_book(self):
        response = client.get('/books/read/1')
        self.assertEqual(response.status_code, 200)

    def test_new_book(self):
        response = client.get('/books/read/4')
        self.assertEqual(response.status_code, 404)

    def test_invalid_id(self):
        response = client.get('/books/read/abc')
        self.assertEqual(response.status_code, 422)

if __name__ == '__main__':
    unittest.main()