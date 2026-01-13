import sys
import unittest
import os
# Add current dir to path
sys.path.append(os.getcwd())

from app import create_app

class TestEduRanker(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True

    def test_index_route(self):
        print("\nTesting Index Route...")
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'EduRanker', response.data)
        print("Index Route OK")

    def test_results_route(self):
        print("\nTesting Results Route (This triggers AI & Mock Data)...")
        # Use a simple topic to ensure "Fast" response (though Gemini timing is real)
        response = self.client.get('/results?topic=Basic+Math&level=1')
        
        if response.status_code != 200:
            print("ERROR: Route returned", response.status_code)
            print(response.data.decode())
            
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Analysis Results', response.data)
        # Check if ETAS score is present
        self.assertIn(b'ETAS SCORE', response.data)
        print("Results Route OK")

if __name__ == '__main__':
    unittest.main()
