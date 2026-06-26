from typing import List
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import Post
from pydantic import TypeAdapter, ValidationError

client = TestClient(app)


def test_get_posts():
    res = client.get("/posts/")
    post_list_adapter = TypeAdapter(List[Post])
    validate_posts_list = post_list_adapter.validate_python(res.json())
    assert res.status_code == 200


def test_latest_post():
    res = client.get("/posts/latest")
    assert res.status_code in (200, 404)
    try:
        latest_post = Post.model_validate(res.json())
    except ValidationError as _:
        print("No Posts To Begin With")
