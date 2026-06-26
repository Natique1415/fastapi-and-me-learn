from fastapi.testclient import TestClient
import os
import sqlite3
import pytest

from app.main import app
from app.schemas import UserOut

from app.config import settings
from app.db_util import get_db


TEST_DB_PATH = os.path.join(
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


def test_create_user(client):
    res = client.post(
        "/users/", json={"email": "test_user@gmail.com", "password": "1234567Ilove"}
    )
    new_user = UserOut(**res.json())
    # print(res.json())
    assert (res.status_code == 201) or (res.status_code == 409)
    assert new_user.email == "test_user@gmail.com"
