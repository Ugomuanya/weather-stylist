import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from main import get_weather  # assuming function is in main.py

class TestWeatherAPI(unittest.TestCase):
    def test_valid_city(self):
        result = get_weather("Lagos")
        self.assertIsInstance(result, dict)
        self.assertIn("temperature", result)  # adjust this to match your return keys

    def test_invalid_city(self):
        result = get_weather("InvalidCityXYZ")
        self.assertIn("error", result)  # adjust if you return an error differently

if __name__ == "__main__":
    unittest.main()
