from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from app.schemas import PayloadData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "a78ce810dc9ea469c39a35042600757092267f94621a4e8ec9443b3fc0993b38"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(payload: dict):
    to_encode_payload = payload.copy()
    expire_time = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode_payload.update({"exp": expire_time})

    return jwt.encode(to_encode_payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(
    token: str, credentials_exception: HTTPException
) -> PayloadData:
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_id = payload.get(
            "user_id"
        )  # user id is int based on the pydantic model and the output of the get id in the db util

        if user_id is None:
            raise credentials_exception

        return PayloadData(id=user_id)

    except JWTError:
        raise credentials_exception


def get_current_user_id(token: str = Depends(oauth2_scheme)):
    return verify_access_token(
        token,
        HTTPException(
            401,
            detail="Could not Valid Credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )
