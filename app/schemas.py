from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class Like(BaseModel):
    user_id: int
    post_id: int


class Token(BaseModel):
    access_token: str
    token_type: str


class PayloadData(BaseModel):
    id: int


class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Min. Length of password should be 8 characters, and max 128 length password to prevent hashing exhaustion attacks",
    )


class UserLogin(UserSignup):
    pass


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime


class PostBase(BaseModel):
    title: str = Field(min_length=3, max_length=30, description="Title of the post")
    content: str = Field(
        min_length=3, max_length=200, description="Content of the Post"
    )
    is_published: bool = Field(
        default=True, description="Whether to publish the post or keep it as a draft"
    )


class Post(PostBase):
    post_id: int = Field(..., description="Unique Identifier for each post")
    user_id: int
    created_at: datetime = Field(
        ..., description="Timestamp ( without timezone information )"
    )
    no_of_likes: int


class UpdatePost(BaseModel):
    title: Optional[str] = Field(
        default=None, min_length=3, max_length=30, description="Title of the post"
    )
    content: Optional[str] = Field(
        default=None, min_length=3, max_length=200, description="Content of the Post"
    )
    published: bool = Field(
        default=True, description="Whether to publish the post or keep it as a draft"
    )
