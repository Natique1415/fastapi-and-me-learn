from fastapi import HTTPException, APIRouter, Depends
from app.schemas import PostBase, UpdatePost, Post
from app.db_util import does_id_exist
from app.db_util import DB_PATH
from app.schemas import PayloadData
import app.oauth2
import sqlite3

# since all endpoint start from posts instead of re-writing all the time we can just do prefix
router = APIRouter(prefix="/posts", tags=["Posts"])


# return all posts
@router.get("/")  # response_model=List[Post])
def get_posts(limit: int = 10, skip: int = 0, search_title: str = ""):
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = (
        sqlite3.Row
    )  # returns the key ( being the column name ) and value being the value
    cursor = connection.cursor()
    if search_title != "":
        cursor.execute(
            "SELECT * FROM posts WHERE title LIKE ? LIMIT ? OFFSET ?",
            (
                f"%{search_title}%",
                limit,
                skip,
            ),
        )
    else:
        cursor.execute(
            "SELECT * FROM posts LIMIT ? OFFSET ?",
            (
                limit,
                skip,
            ),
        )
    posts = cursor.fetchall()
    # todo create a list and loop through and create the post ( pydantic model ) and return it
    connection.close()
    return posts


@router.get("/latest", status_code=200, response_model=Post)
def get_latest_post():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")
    posts = cursor.fetchall()
    connection.close()
    if posts == []:
        raise HTTPException(status_code=404, detail="No Posts to Begin with")

    return Post(
        user_id=posts[0]["user_id"],
        post_id=posts[0]["id"],
        title=posts[0]["title"],
        content=posts[0]["content"],
        is_published=True if posts[0]["is_published"] == 1 else False,
        created_at=posts[0]["created_at"],
        no_of_likes=posts[0]["no_of_likes"],
    )


@router.get("/{post_id}", status_code=200, response_model=Post)
def get_post(post_id: int):

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    posts = cursor.fetchall()
    connection.close()
    if posts == []:
        raise HTTPException(
            status_code=404, detail=f"Given Post Id = {post_id} Does not exist"
        )

    return Post(
        user_id=posts[0]["user_id"],
        post_id=posts[0]["id"],
        title=posts[0]["title"],
        content=posts[0]["content"],
        is_published=True if posts[0]["is_published"] == 1 else False,
        created_at=posts[0]["created_at"],
        no_of_likes=posts[0]["no_of_likes"],
    )


@router.post("/", status_code=201, response_model=Post)
def create_posts(
    post: PostBase,
    current_user: PayloadData = Depends(app.oauth2.get_current_user_id),
):
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = (
        sqlite3.Row
    )  # returns the key ( being the column name ) and value being the value
    cursor = connection.cursor()

    # so sqlite3 by default has no protection on fk, this is how we turn it out, lasts as long as the connection does
    cursor.execute("PRAGMA foreign_keys = ON;")
    # so if the user added a non-existent user_id post we will get error which we have to handle ( todo )
    try:
        cursor.execute(
            "INSERT INTO posts(user_id,title,content,is_published) VALUES(?,?,?,?) RETURNING *",
            (current_user.id, post.title, post.content, post.is_published),
        )
        added_post = cursor.fetchall()
        connection.commit()
        # print(current_user.id)
        return Post(
            user_id=added_post[0]["user_id"],
            post_id=added_post[0]["id"],
            title=added_post[0]["title"],
            content=added_post[0]["content"],
            is_published=True if added_post[0]["is_published"] == 1 else False,
            created_at=added_post[0]["created_at"],
            no_of_likes=added_post[0]["no_of_likes"],
        )

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Given user_id does not exist!")
    finally:
        connection.close()


@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int, current_user: PayloadData = Depends(app.oauth2.get_current_user_id)
):
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT user_id FROM posts WHERE id = ?", (post_id,))
    result = cursor.fetchone()
    if result is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Post with Given Id Does not Exist")

    if current_user.id != result["user_id"]:
        connection.close()
        raise HTTPException(status_code=403, detail="You cannot delete others post!")
    else:
        cursor.execute("DELETE FROM posts where id=?", (post_id,))
        connection.commit()
        connection.close()


@router.put("/{post_id}", status_code=200, response_model=Post)
def update_post(
    post_id: int,
    updated_post: UpdatePost,
    current_user: PayloadData = Depends(app.oauth2.get_current_user_id),
):
    if does_id_exist(post_id, "posts", DB_PATH) == False:  # noqa: E712
        raise HTTPException(
            status_code=404, detail=f"Post with post_id = {post_id} does not exist"
        )
    else:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        curr = connection.cursor()
        curr.execute("SELECT user_id FROM posts WHERE id = ?", (post_id,))
        result = curr.fetchone()

        if current_user.id != result["user_id"]:
            connection.close()
            raise HTTPException(
                status_code=403, detail="You cannot update others post!"
            )
        else:
            if updated_post.title is not None:
                curr.execute(
                    "UPDATE posts SET title = ? WHERE id = ?",
                    (updated_post.title, post_id),
                )

            if updated_post.content is not None:
                curr.execute(
                    "UPDATE posts SET content = ? WHERE id = ?",
                    (updated_post.content, post_id),
                )

            connection.commit()

            curr.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
            result = curr.fetchall()
            connection.close()
            return Post(
                user_id=result[0]["user_id"],
                post_id=result[0]["id"],
                title=result[0]["title"],
                content=result[0]["content"],
                is_published=True if result[0]["is_published"] == 1 else False,
                created_at=result[0]["created_at"],
                no_of_likes=result[0]["no_of_likes"],
            )
