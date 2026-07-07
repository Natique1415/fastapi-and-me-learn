from app.schemas import Post
from pydantic import ValidationError
import pytest


def test_get_posts(client):
    res = client.get("/posts/")
    assert res.status_code == 200
    """
    Find a way to model validate each of elements 
    for post in res.json():
        print(post)
    """


def test_latest_post(client):
    res = client.get("/posts/latest")
    assert res.status_code in (404, 200)
    try:
        latest_post = Post.model_validate(res.json())
    except ValidationError as _:
        ...


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


def test_unauthorized_create_post(client):
    res = client.post(
        "/posts/",
        json={
            "title": "Some Random title",
            "content": "Some Random Content",
        },
    )

    assert res.status_code == 401
    assert res.json().get("detail") == "Not authenticated"


def test_unauthorized_user_delete_Post(client):
    res = client.delete("/posts/1")
    assert res.status_code == 401
    assert res.json().get("detail") == "Not authenticated"
