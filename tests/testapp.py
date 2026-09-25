import os

os.environ["ENABLE_GEMINI"] = "false"
os.environ["DATABASE_PATH"] = "data/test_pocketsmart.db"
os.environ["SECRET_KEY"] = "test-secret"


from pathlib import Path

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


def setup_function():

    database = Path(
        settings.database_path
    )

    if database.exists():
        database.unlink()


def test_health_and_full_home_flow():

    with TestClient(app) as client:

        response = client.get(
            "/health"
        )

        assert response.status_code == 200


        response = client.post(
            "/register",
            data={
                "name": "Test User",
                "email": "test@example.com",
                "password": "password123",
            },
            follow_redirects=False,
        )

        assert response.status_code == 303


        response = client.post(
            "/generate-home",
            data={
                "budget": "50000",
                "room_type": "Living room",
                "style": "Modern",
                "city": "Chennai",
                "needs":
                    "sofa and lighting",
            },
            follow_redirects=False,
        )

        assert response.status_code == 303


        details = client.get(
            response.headers["location"]
        )

        assert details.status_code == 200

        assert (
            "Your recommendations"
            in details.text
        )


def test_api_requires_auth():

    with TestClient(app) as client:

        response = client.post(
            "/api/home",
            json={
                "budget": 10000,
                "room_type": "Bedroom",
                "style": "Minimal",
                "city": "",
                "needs": "",
            },
        )

        assert response.status_code == 401