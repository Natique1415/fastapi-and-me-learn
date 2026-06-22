from fastapi.testclient import TestClient
from app.main import app
from app.schemas import UserOut


client = TestClient(app)


def test_create_user():
    res = client.post(
        "/users/", json={"email": "test_user@gmail.com", "password": "1234567Ilove"}
    )
    new_user = UserOut(**res.json())
    assert (res.status_code == 201) or (res.status_code == 409)
    assert new_user.email == "test_user@gmail.com"
