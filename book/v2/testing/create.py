import unittest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

class Tester(unittest.TestCase):
    def test_create_book(self):
        payload = {
            'id': 1,
            'name': 'XYZ',
            'author': 'xyz'
        }
        response = client.post('/books/create', json=payload)
        self.assertIn(response.status_code, [409])
    
    def test_create_book2(self):
        payload = {
            'id': 4,
            'name': 'XYZ',
            'author': 'xyz'
        }
        response = client.post('/books/create', json=payload)
        self.assertIn(response.status_code, [200])

    def test_invalid_id_type(self):
        payload = {
            'id': 'abc',
            'name': 'Invalid ID Type',
            'author': 'Author'
        }
        response = client.post('/books/create', json=payload)
        self.assertEqual(response.status_code, 422)

    def test_empty(self):
        response = client.post('/books/create', json={})
        self.assertEqual(response.status_code, 422)

if __name__ == '__main__':
    unittest.main()