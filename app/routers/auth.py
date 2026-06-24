from fastapi import HTTPException, APIRouter, Depends
from app.security import verify_password
from app.schemas import UserLogin, Token
from app.oauth2 import create_access_token
from app.db_util import get_id, DB_PATH, get_db
import sqlite3

# in the docs given by fastapi we can category endpoints via tags
router = APIRouter(prefix="/login", tags=["Authentication"])


# create a new user
@router.post("/", status_code=200, response_model=Token)
def login(user_credential: UserLogin, connection: sqlite3.Connection = Depends(get_db)):
    cursor = connection.cursor()

    cursor.execute(
        "SELECT password_hash FROM users WHERE email = ?", (user_credential.email,)
    )

    result = cursor.fetchone()

    # meaning that mail doesn't exist in the db
    if result is None:
        raise HTTPException(status_code=403, detail="Given Email does not exist")

    else:
        if verify_password(user_credential.password, result[0]):
            # here is where we generate the JWT token
            access_token = create_access_token(
                payload={"user_id": get_id(user_credential.email, "users", DB_PATH)}
            )
            return Token(access_token=access_token, token_type="bearer")

        else:
            raise HTTPException(
                status_code=403, detail="Invalid Password for the given email"
            )
