import sqlite3
from typing import List
from fastapi import HTTPException, APIRouter, Depends
from redis.asyncio.client import Redis
from app.schemas import PostBase, UpdatePost, Post, PayloadData
from app.db_util import DB_PATH, does_id_exist, get_db
from app.config import settings
from app.redis_util import get_redis
import app.oauth2

# since all endpoint start from posts instead of re-writing all the time we can just do prefix
router = APIRouter(prefix="/posts", tags=["Posts"])


# return all posts
@router.get("/", status_code=200, response_model=List[Post])
def get_posts(
    limit: int = 10,
    skip: int = 0,
    search_title: str = "",
    connection: sqlite3.Connection = Depends(get_db),
):
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
    all_posts = []

    for post in posts:
        all_posts.append(
            Post(
                post_id=post["id"],
                user_id=post["user_id"],
                title=post["title"],
                content=post["content"],
                is_published=True if post["is_published"] == 1 else False,
                created_at=posts[0]["created_at"],
                no_of_likes=posts[0]["no_of_likes"],
            )
        )

    return all_posts


@router.get("/latest", status_code=200, response_model=Post)
def get_latest_post(
    connection: sqlite3.Connection = Depends(get_db),
):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")
    posts = cursor.fetchall()
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
async def get_post(
    post_id: int,
    connection: sqlite3.Connection = Depends(get_db),
    redis_client: Redis = Depends(get_redis),
):
    cache_key = f"post:{post_id}"
    cached_post = await redis_client.get(cache_key)
    if cached_post:
        return Post.model_validate_json(cached_post)

    # in the case of cache miss
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    posts = cursor.fetchall()
    if posts == []:
        raise HTTPException(
            status_code=404, detail=f"Given Post Id = {post_id} Does not exist"
        )

    post_data = Post(
        user_id=posts[0]["user_id"],
        post_id=posts[0]["id"],
        title=posts[0]["title"],
        content=posts[0]["content"],
        is_published=True if posts[0]["is_published"] == 1 else False,
        created_at=posts[0]["created_at"],
        no_of_likes=posts[0]["no_of_likes"],
    )
    serialized_post = post_data.model_dump_json()
    await redis_client.set(cache_key, serialized_post, ex=settings.cache_ttl_sec)
    return post_data


@router.post("/", status_code=201, response_model=Post)
def create_posts(
    post: PostBase,
    current_user: PayloadData = Depends(app.oauth2.get_current_user_id),
    connection: sqlite3.Connection = Depends(get_db),
):
    cursor = connection.cursor()

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


@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    current_user: PayloadData = Depends(app.oauth2.get_current_user_id),
    connection: sqlite3.Connection = Depends(get_db),
):
    cursor = connection.cursor()
    cursor.execute("SELECT user_id FROM posts WHERE id = ?", (post_id,))
    result = cursor.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Post with Given Id Does not Exist")

    if current_user.id != result["user_id"]:
        raise HTTPException(status_code=403, detail="You cannot delete others post!")
    else:
        cursor.execute("DELETE FROM posts where id=?", (post_id,))
        connection.commit()


@router.put("/{post_id}", status_code=200, response_model=Post)
def update_post(
    post_id: int,
    updated_post: UpdatePost,
    connection: sqlite3.Connection = Depends(get_db),
    current_user: PayloadData = Depends(app.oauth2.get_current_user_id),
):
    if does_id_exist(post_id, "posts", DB_PATH) == False:  # noqa: E712
        raise HTTPException(
            status_code=404, detail=f"Post with post_id = {post_id} does not exist"
        )
    else:
        curr = connection.cursor()
        curr.execute("SELECT user_id FROM posts WHERE id = ?", (post_id,))
        result = curr.fetchone()

        if current_user.id != result["user_id"]:
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
            return Post(
                user_id=result[0]["user_id"],
                post_id=result[0]["id"],
                title=result[0]["title"],
                content=result[0]["content"],
                is_published=True if result[0]["is_published"] == 1 else False,
                created_at=result[0]["created_at"],
                no_of_likes=result[0]["no_of_likes"],
            )
