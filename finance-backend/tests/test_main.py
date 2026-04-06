import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.database import Base, get_db

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def setup_module():
    Base.metadata.create_all(bind=engine)

def teardown_module():
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        os.remove("./test.db")

def test_create_user():
    response = client.post("/users/", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "role": "admin"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

def test_create_transaction_admin():
    # User ID 1 is the testuser created above (auto-increment)
    response = client.post(
        "/transactions/", 
        json={
            "amount": 100.5,
            "type": "income",
            "category": "Bonus",
            "notes": "Good job"
        },
        headers={"X-User-ID": "1"}
    )
    assert response.status_code == 201
    assert response.json()["amount"] == 100.5

def test_summary_viewer():
    # Create a viewer
    client.post("/users/", json={
        "username": "viewer_user",
        "email": "viewer@example.com",
        "password": "password",
        "role": "viewer"
    })
    
    # Viewer should be able to get summary (will be empty for them)
    response = client.get("/analytics/summary", headers={"X-User-ID": "2"})
    assert response.status_code == 200
    assert response.json()["current_balance"] == 0

def test_detailed_insights_viewer_denied():
    # Viewer should be denied detailed insights
    response = client.get("/analytics/detailed-insights", headers={"X-User-ID": "2"})
    assert response.status_code == 403

def test_detailed_insights_admin_allowed():
    response = client.get("/analytics/detailed-insights", headers={"X-User-ID": "1"})
    assert response.status_code == 200
    assert "analyst_notes" in response.json()

def test_transaction_search():
    # Admin creates a transaction with specific notes
    client.post(
        "/transactions/", 
        json={
            "amount": 50.0,
            "type": "expense",
            "category": "Food",
            "notes": "Starbucks Coffee"
        },
        headers={"X-User-ID": "1"}
    )
    
    # Search for "Coffee"
    response = client.get("/transactions/?search=Coffee", headers={"X-User-ID": "1"})
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert "Coffee" in response.json()[0]["notes"]

def test_csv_export():
    response = client.get("/transactions/export/csv", headers={"X-User-ID": "1"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "Amount,Type,Category" in response.text
