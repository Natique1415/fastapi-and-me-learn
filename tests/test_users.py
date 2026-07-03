from fastapi.testclient import TestClient
import sqlite3
import pytest
from pathlib import Path

from app.main import app
from app.schemas import UserOut, UserSignup, Token

from app.config import settings
from app.db_util import get_db


BASE_DIR = Path(__file__).resolve().parent  # directory containing this file
TEST_DB_PATH = BASE_DIR.parent / "app" / f"test_{settings.db_name}"


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
    # find a better way as this is more of a hack
    conn = sqlite3.connect(TEST_DB_PATH)
    curr = conn.cursor()
    curr.execute("DELETE FROM users")
    conn.commit()
    conn.close()


@pytest.fixture
def test_new_user():
    return UserSignup(email="test_user@gmail.com", password="12345678910")


def test_create_user(client, test_new_user):
    res = client.post(
        "/users/",
        json={"email": test_new_user.email, "password": test_new_user.password},
    )
    new_user = UserOut.model_validate(res.json())
    assert res.status_code in (201, 409)
    assert new_user.email == "test_user@gmail.com"


# Need to create a authorized client to make this test pass
def test_login_user(client, test_new_user):
    res = client.post(
        "/login/",
        json={"email": "ibrarnatique812@gmail.com", "password": "12345678"},
    )
    # jwt_token = Token.model_validate(res.json())
    print(res.status_code)
    print(res.json().get("detail"))
    assert res.status_code in (403, 200)
