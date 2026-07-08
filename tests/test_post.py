from app.schemas import Post
from typing import List
from pydantic import TypeAdapter
import pytest


def test_get_all_posts(client, test_post):
    res = client.get("/posts/")
    assert res.status_code == 200
    adapter = TypeAdapter(List[Post])
    adapter.validate_python(res.json())


def test_latest_post_when_post_present(client, test_post):
    res = client.get("/posts/latest")
    assert res.status_code == 200
    Post.model_validate(res.json())


def test_latest_post_when_no_post_present(client):
    res = client.get("/posts/latest")
    assert res.status_code == 404


def test_get_one_not_exist_post(client):
    res = client.get(f"/posts/{1000}")
    assert res.status_code == 404
    assert res.json().get("detail") == f"Given Post Id = {1000} Does not exist"


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
    authorized_client, test_signed_in_user, title, content, is_published
):
    res = authorized_client.post(
        "/posts/",
        json={"title": title, "content": content, "is_published": is_published},
    )

    created_post = Post.model_validate(res.json())
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.user_id == test_signed_in_user["user_id"]
    assert created_post.is_published == is_published
    assert created_post.no_of_likes == 0


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


def test_get_one_valid_post(client, test_post):
    res = client.get(f"/posts/{test_post[0]['post_id']}")
    assert res.status_code == 200
    Post.model_validate(res.json())


def test_delete_existing_post(authorized_client, test_post):
    res = authorized_client.delete(f"/posts/{test_post[0]['post_id']}")
    assert res.status_code == 204


def test_delete_non_existent_post(authorized_client):
    res = authorized_client.delete(f"/posts/{1000}")
    assert res.status_code == 404
    assert res.json().get("detail") == "Post with Given Id Does not Exist"


def test_unauthorized_user_delete_Post(client):
    res = client.delete("/posts/1")
    assert res.status_code == 401
    assert res.json().get("detail") == "Not authenticated"


"""
Reason why res.status_code == 404 not found as it using get_id func with using DB_PATH and not test PATH
def test_update_existing_post(authorized_client, test_post):
    res = authorized_client.put(
        f"/posts/{test_post[0]['post_id']}",
        json={"title": "Updated Title", "content": "Updated Content"},
    )
    assert res.status_code == 200
    print(res.json().get("detail"))
    print(res.status_code)
"""
