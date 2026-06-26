from fastapi.testclient import TestClient
import os
import sqlite3
import pytest

from app.main import app
from app.schemas import UserOut, UserSignup, Token

from app.config import settings
from app.db_util import get_db


TEST_DB_PATH = os.path.join(
    # fix this, shouldn't be a absolute path
    "C:\\Users\\ibrar\\OneDrive\\Desktop\\Api\\Post-Api\\app",
    f"test_{settings.db_name}",
)


def override_get_db():
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn

    finally:
        conn.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    yield TestClient(app)
    # find a better way as this is more a hack
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    curr = conn.cursor()
    curr.execute("DELETE FROM users")
    conn.commit()


@pytest.fixture
def test_user():
    return UserSignup(email="test_user@gmail.com", password="12345678910")


def test_create_user(client, test_user):
    res = client.post(
        "/users/", json={"email": test_user.email, "password": test_user.password}
    )
    new_user = UserOut.model_validate(res.json())
    assert res.status_code in (201, 409)
    assert new_user.email == "test_user@gmail.com"


def test_login_user(client, test_user):
    res = client.post(
        "/login/", json={"email": test_user.email, "password": test_user.password}
    )
    jwt_token = Token.model_validate(res.json())
    assert res.status_code in (403, 200)
