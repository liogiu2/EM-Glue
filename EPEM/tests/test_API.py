import unittest
from fastapi.testclient import TestClient
from API_communication import app
from sql_app import crud
from sql_app.database import SessionLocal
import os

class TestAPI(unittest.TestCase):

    def setUp(self):
        try:
            os.remove("db/sql_app.db")
        except FileNotFoundError:
            pass
    
    def tearDown(self):
        try:
            os.remove("db/sql_app.db")
        except FileNotFoundError:
            pass

    def test_platform_online(self):
        with TestClient(app) as client:
            response = client.head("/")
        assert response.status_code == 200
    
    def test_user_creation_platform(self):
        with TestClient(app) as client:
            with SessionLocal() as db:
                platform = crud.get_user_with_role(db, "PLATFORM")
            self.assertEqual(platform.role, "PLATFORM")