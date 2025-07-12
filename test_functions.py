from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import sessionmaker

from database import get_db, create_engine
from models import Base, Users
from main import app, create_user, create_jwt_token
from fastapi.testclient import TestClient
from token_func import hash_password

engine = create_engine("postgresql:///tests", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    assert get_users_response.status_code == 200
    response_users_dict = get_users_response.json()[0]
    user_id = response_users_dict.get("id")
    assert user_id == 1

def test_create_same_users(client):
    success_respones = client.post(
        "/users/",
        json={
            "login": "test_user",
            "password": "alksjdfnl123fl",
            "salary": "150.24",
            "upgrade_date": "2025-12-12T00:00:00"
        }
    )
    invalid_response = client.post(
        "/users/",
        json={
            "login": "test_user",
            "password": "good_password123",
            "salary": "430958.239",
            "upgrade_date": "2025-03-31T00:00:00"
    })
    assert success_respones.status_code == 200
    assert invalid_response.status_code == 400

def test_create_user_with_uncorrect_salary(client):
    create_user_response = client.post(
        "/users/",
        json={
            "login": "user",
            "password": "slkdjn2hbkjshbkj4",
            "salary": "-52.10",
            "upgrade_date": "2025-12-12T00:00:00"
        }
    )
    assert create_user_response.status_code == 400
    assert create_user_response.json()['detail'] == "Salary must be greater than zero"

def test_update_salary(client):
    create_user_response = client.post(
        "/users/",
        json={
            "login": "test_user",
            "password": "passwordgoodone1",
            "salary": "45.24",
            "upgrade_date": "2025-03-25T00:00:00"
        }
    )
    assert create_user_response.status_code == 200
    assert create_user_response.json().get("salary") == 45.24
    update_salary_response = client.patch(
        "/update_salary/",
        data={
            "id": "4",
            "salary": "123456.126",
            "upgrade_date": "2025-12-12T00:00:00"
        }
    )
    assert update_salary_response.status_code == 200
    assert update_salary_response.json()['salary'] == 123456.13
    assert update_salary_response.json()['upgrade_date'] == '2025-12-12T00:00:00+03:00'

def test_not_success_update_salary(client):
    update_salary_response = client.patch(
        "/update_salary/",
        data={
            "id": "4",
            "salary": "123456.126",
            "upgrade_date": "2025-12-12T00:00:00"
        }
    )
    assert update_salary_response.status_code == 404
    assert update_salary_response.json()['detail'] == "Wrong id"

def test_hashed_password(client):
    create_user_response = client.post(
        "/users/",
        json={
            "login": "test_user",
            "password": "lkjnwejkl18jskbhd4",
            "salary": "239000",
            "upgrade_date": "2026-01-01T00:00:00"
        }
    )
    assert create_user_response.status_code == 200
    correct_hashed_password = hash_password("lkjnwejkl18jskbhd4")
    get_user_response = client.get(
        "/user/",
        params = {
            "id": 5
        }
    )
    assert get_user_response.status_code == 200
    assert get_user_response.json()['password'] == correct_hashed_password

def test_success_generate_token(client):
    create_user_response = client.post(
        "/users/",
        json={
            "login": "test_user",
            "password": "ak234kljncs4k",
            "salary": "20_000",
            "upgrade_date": "2026-01-01T00:00:00"
        }
    )
    create_token_response = client.get(
        "/get_token/",
        params={
            "login": "test_user",
            "password": "ak234kljncs4k"
        }
    )
    assert create_token_response.status_code == 200
    correct_token = create_jwt_token({"id": 6}, timedelta(minutes=15))
    assert create_token_response.json() == correct_token

def test_no_token(client):
    create_token_response = client.get(
        "/get_token/",
        params={
            "login": "test_user",
            "password": "ak234kljncs4k"
        }
    )
    assert create_token_response.status_code == 404
    assert create_token_response.json()['detail'] == "Сheck the data you entered"

def test_get_user_with_valid_id(client):
    create_user_response = client.get("/user/", params={"id": 1})
    assert create_user_response.status_code == 404
    assert create_user_response.json()['detail'] == "No such user"

def test_get_salary_from_user(client):
    create_user_response = client.post(
        "/users/",
        json={
            "login": "user8",
            "password": "slkdjn20sldkjn5",
            "salary": "116_000",
            "upgrade_date": "2025-07-30T00:00:00"
        }
    )
    assert create_user_response.status_code == 200
    get_token_response = client.get(
        "/get_token/",
        params={
            "login": "user8",
            "password": "slkdjn20sldkjn5"
        }
    )
    assert get_token_response.status_code == 200
    valid_token = get_token_response.json()
    get_salary_from_token_response = client.get(
        "/get_salary/",
        params={
            "token": valid_token
        }
    )
    assert get_salary_from_token_response.status_code == 200
    assert get_salary_from_token_response.json()['salary'] == 116000
    assert get_salary_from_token_response.json()['upgrade_date'] == "2025-07-30T00:00:00+03:00"

def test_expired_token(client):
    get_salary_from_token_response = client.get(
        "/get_salary/",
        params={
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NiwiZXhwIjoxNzUyMDg4MjEyfQ.cDqkL71m_qDX4Ic_8UbfyL1C-J7Ixk1MshFEO8oa70s"
        }
    )
    assert get_salary_from_token_response.status_code == 400
    assert get_salary_from_token_response.json()['detail'] == "Token is expired"

def test_invalid_token(client):
    get_salary_from_token_response = client.get(
        "/get_salary/",
        params={
            "token": "eyJ6IkpXVCJ9.eyJpZCI6NiwiZXhwIjoxNzUyMDg4MjEyfQ.cDqkL71m_qDX4Ic_8UbfyL1C-J7Ixk1MshFEO8oa70s"
        }
    )
    assert get_salary_from_token_response.status_code == 400
    assert get_salary_from_token_response.json()['detail'] == "Invalid token"
