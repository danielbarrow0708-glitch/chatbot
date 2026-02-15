import os
import unittest
from unittest.mock import patch

import requests

from app import app


class DummyResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._json_data


class OptimizeEndpointTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_empty_text_returns_400(self):
        response = self.client.post("/optimize", json={"text": ""})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_request_exception_returns_502(self):
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test"}):
            with patch("app.requests.post", side_effect=requests.RequestException("boom")):
                response = self.client.post("/optimize", json={"text": "hello"})
        self.assertEqual(response.status_code, 502)
        self.assertIn("error", response.get_json())

    def test_success_returns_result(self):
        payload = {
            "choices": [
                {"message": {"content": "Optimized."}}
            ]
        }
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test"}):
            with patch("app.requests.post", return_value=DummyResponse(200, payload)):
                response = self.client.post("/optimize", json={"text": "hello"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["result"], "Optimized.")


if __name__ == "__main__":
    unittest.main()
