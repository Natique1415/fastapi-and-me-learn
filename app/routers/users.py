from fastapi import HTTPException, APIRouter, Depends
from app.schemas import UserSignup, UserOut
from app.security import hash_password
from app.db_util import DB_PATH, get_db
import sqlite3


# in the docs given by fastapi we can category endpoints via tags
router = APIRouter(prefix="/users", tags=["Users"])


# create a new user
@router.post("/", status_code=201, response_model=UserOut)
def create_user(
    user: UserSignup,
    connection: sqlite3.Connection = Depends(get_db),
):
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO users(email,password_hash) VALUES(?,?) RETURNING id,email,created_at",
            (user.email, hash_password(user.password)),
        )
        user_info = cursor.fetchone()
        connection.commit()
        return UserOut(id=user_info[0], email=user_info[1], created_at=user_info[2])
    # the only integrity error would be the email uniqueness
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Given Email is already in use")
