from fastapi import FastAPI
from .routers import likes, posts, users, auth

# Get(read), Post(create), Put(update), Delete
app = FastAPI()
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(likes.router)


@app.get("/", status_code=200)
def root():
    return {"mssg": "Hello World!"}
