import pytest
from database import get_db, SessionLocal, engine
from models import Base
from main import app
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


def test_request(client):
    response = client.get("http://127.0.0.1:8000/users/")
    assert response.status_code == 200