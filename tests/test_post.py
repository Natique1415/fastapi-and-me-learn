from app.schemas import Post
from pydantic import ValidationError
import pytest


def test_get_posts(client):
    res = client.get("/posts/")
    assert res.status_code == 200
    for post in res.json():
        print(post)


def test_latest_post(client):
    res = client.get("/posts/latest")
    assert res.status_code in (404, 200)
    print(res.json())
    try:
        latest_post = Post.model_validate(res.json())
    except ValidationError as _:
        print("No Posts To Begin With")


@pytest.mark.parametrize(
    "title, content, is_published",
    [
        ("awesome new title", "awesome new content", True),
        ("favorite pizza", "i love pepperoni", False),
        ("tallest skyscrapers", "wahoo", True),
        ("min len 3", "min len 3", False),
    ],
)
def test_create_post(
    authorized_client, test_authorized_user, title, content, is_published
):
    res = authorized_client.post(
        "/posts/",
        json={"title": title, "content": content, "is_published": is_published},
    )

    created_post = Post.model_validate(res.json())
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.user_id == test_authorized_user["user_id"]
    assert created_post.is_published == is_published
    # assert created_post.published == published
    # assert created_post.owner_id == test_user["id"]
