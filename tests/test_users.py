import jwt
from app.schemas import UserOut, Token
from app.config import settings


def test_create_user(client, test_new_user):
    res = client.post(
        "/users/",
        json={"email": test_new_user.email, "password": test_new_user.password},
    )
    new_user = UserOut.model_validate(res.json())
    assert res.status_code in (201, 409)
    assert new_user.email == "test_user@gmail.com"


# Need to create a authorized client to make this test pass
def test_login_user(client, test_authorized_user):
    res = client.post(
        "/login/",
        json={
            "email": test_authorized_user["email"],
            "password": test_authorized_user["password"],
        },
    )
    jwt_token = Token.model_validate(res.json())
    payload = jwt.decode(
        jwt_token.access_token, settings.secret_key, [settings.algorithm]
    )
    assert payload.get("user_id") == test_authorized_user["user_id"]
    assert res.status_code == 200
    assert jwt_token.token_type == "bearer"


def test_incorrect_password_login(client, test_authorized_user):
    res = client.post(
        "/login/",
        json={
            "email": test_authorized_user["email"],
            "password": "wrong_password",
        },
    )
    assert res.status_code == 403
    assert res.json().get("detail") == "Invalid Password for the given email"
