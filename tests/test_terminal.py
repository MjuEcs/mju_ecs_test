from flask import Flask
import unittest

class TerminalTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_terminal_connection(self):
        response = self.client.get('/terminal')
        self.assertEqual(response.status_code, 200)

    def test_execute_command(self):
        response = self.client.post('/execute_command', json={'command': 'echo test'})
        self.assertEqual(response.status_code, 200)

    def test_resize_screen(self):
        response = self.client.post('/resize_screen', json={'rows': 24, 'cols': 80})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()