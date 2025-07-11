from datetime import datetime, timedelta

import pytest
from database import get_db, SessionLocal, engine
from models import Base, Users
from main import app, create_user, create_jwt_token
from fastapi.testclient import TestClient

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

def test_create_user_with_no_valid_password(client):
    create_user_response = client.post(
        "/users/",
        json={
            "login": "test_user",
            "password": "bad_psw",
            "salary": "150.24",
            "upgrade_date": "2025-12-12T00:00:00"
        }
    )
    assert create_user_response.status_code == 400
    assert create_user_response.json()['detail'] == "Password must be at least 8 characters long and contain at least one number"
    get_users_response = client.get("/users/")
    assert get_users_response.status_code == 200
    assert get_users_response.json() == []

def test_create_user_with_valid_password(client):
    create_user_response = client.post(
        "/users/",
        json={
            "login": "test_user",
            "password": "alksjdfnl123fl",
            "salary": "150.24",
            "upgrade_date": "2025-12-12T00:00:00"
        }
    )
    assert create_user_response.status_code == 200
    response_created_user_dict = create_user_response.json()
    response_login = response_created_user_dict.get("login")
    response_salary = response_created_user_dict.get("salary")
    response_upgrade_date = response_created_user_dict.get("upgrade_date")
    assert response_login == "test_user"
    assert response_salary == 150.24
    assert response_upgrade_date == "2025-12-12T00:00:00+03:00"
    get_users_response = client.get("/users/")
    print(get_users_response.json())
    assert get_users_response.status_code == 200
    response_users_dict = get_users_response.json()[0]
    user_id = response_users_dict.get("id")
    assert user_id == 1

def test_create_same_users(client):
    create_user_response = client.post(
        "/users/",
        json={
            "login": "test_user",
            "password": "alksjdfnl123fl",
            "salary": "150.24",
            "upgrade_date": "2025-12-12T00:00:00"
        }
    )
    success_respones = client.post(
        "/users/",
        json={
            "login": "test_user",
            "password": "good_password123",
            "salary": "430958.239",
            "upgrade_date": "2025-13-31T00:00:00"
    })
    invalid_response = client.post(
        "/users/",
        json={
            "login": "test_user",
            "password": "good_password123",
            "salary": "430958.239",
            "upgrade_date": "2025-13-31T00:00:00"
    })
    assert success_respones.status_code == 200
    assert invalid_response.status_code == 400

def test_request(client):
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []