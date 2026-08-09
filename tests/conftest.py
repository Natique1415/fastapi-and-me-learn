from fastapi.testclient import TestClient
import sqlite3
import pytest
from pathlib import Path

from app.main import app
from app.schemas import UserSignup

from app.config import settings
from app.db_util import get_db
from app.security import hash_password
from app.oauth2 import create_access_token


BASE_DIR = Path(__file__).resolve().parent  # directory containing this file
TEST_DB_PATH = BASE_DIR.parent / "app" / f"test_{settings.db_name}"


@pytest.fixture
def client():
    def override_get_db():
        conn = sqlite3.connect(TEST_DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn

        finally:
            conn.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    conn = sqlite3.connect(TEST_DB_PATH)
    curr = conn.cursor()
    curr.execute("DELETE FROM users")
    curr.execute("DELETE FROM posts")
    curr.execute("DELETE FROM likes")
    conn.commit()
    conn.close()


@pytest.fixture
def test_new_user():
    return UserSignup(email="test_user@gmail.com", password="12345678910")


@pytest.fixture
def test_signed_in_user():
    authorized_user = {"email": "test_user@gmail.com", "password": "12345678"}
    conn = sqlite3.connect(TEST_DB_PATH)
    curr = conn.cursor()
    try:
        curr.execute(
            "INSERT INTO users(email,password_hash) VALUES(?,?) RETURNING id",
            (authorized_user["email"], hash_password(authorized_user["password"])),
        )
        user_info = curr.fetchone()
        authorized_user["user_id"] = user_info[0]
        conn.commit()
    finally:
        conn.close()
        return authorized_user


@pytest.fixture
def test_post(test_signed_in_user):
    conn = sqlite3.connect(TEST_DB_PATH)
    curr = conn.cursor()
    posts_data = [
        {
            "title": "1st title",
            "content": "first content",
            "user_id": test_signed_in_user["user_id"],
        },
        {
            "title": "2nd title",
            "content": "2nd content",
            "user_id": test_signed_in_user["user_id"],
        },
        {
            "title": "3rd title",
            "content": "3rd content",
            "user_id": test_signed_in_user["user_id"],
        },
        {
            "title": "3rd title",
            "content": "3rd content",
            "user_id": test_signed_in_user["user_id"],
        },
    ]

    try:
        for post in posts_data:
            curr.execute(
                "INSERT INTO posts(title,content,user_id) VALUES(?,?,?) RETURNING id",
                (
                    post["title"],
                    post["content"],
                    post["user_id"],
                ),
            )
            post_id = curr.fetchone()
            post["post_id"] = post_id[0]
        conn.commit()

    finally:
        conn.close()
        return posts_data


@pytest.fixture
def token(test_signed_in_user):
    return create_access_token(payload={"user_id": test_signed_in_user["user_id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client
