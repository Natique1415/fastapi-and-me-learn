from fastapi import HTTPException, APIRouter, Depends
import app.oauth2
from app.schemas import PayloadData
from app.db_util import DB_PATH, does_id_exist, get_db
import sqlite3

router = APIRouter(prefix="/likes", tags=["Like"])


@router.post("/{post_id}", status_code=201)
def like_post(
    post_id: int,
    current_user: PayloadData = Depends(app.oauth2.get_current_user_id),
    connection: sqlite3.Connection = Depends(get_db),
):
    if does_id_exist(post_id, "posts", DB_PATH) == False:  # noqa: E712
        raise HTTPException(
            status_code=404, detail=f"Post with post_id = {post_id} does not exist"
        )
    else:
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO likes(user_id,post_id) VALUES(?,?)",
                (
                    current_user.id,
                    post_id,
                ),
            )
            connection.commit()
            return {"message": "like recorded"}

        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=409, detail="Cannot like the same post twice!"
            )


@router.delete("/{post_id}", status_code=204)
def delete_like(
    post_id: int,
    current_user: PayloadData = Depends(app.oauth2.get_current_user_id),
    connection: sqlite3.Connection = Depends(get_db),
):
    if does_id_exist(post_id, "posts", DB_PATH) == False:  # noqa: E712
        raise HTTPException(
            status_code=404, detail=f"Post with post_id = {post_id} does not exist"
        )
    else:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM likes WHERE user_id = ? AND post_id = ?",
            (
                current_user.id,
                post_id,
            ),
        )
        connection.commit()
