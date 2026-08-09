import os
import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config import settings
from .db_util import DB_PATH
import redis.asyncio as redis
from redis.asyncio.client import Redis

# as of now will be present in the same level as this file ( main.py )
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE = os.path.join(BASE_DIR, "schema.sql")


def init_db() -> None:
    if not os.path.exists(SCHEMA_FILE):
        print(f"️ Warning: Schema file '{SCHEMA_FILE}' not found!")
        return

    if not os.path.exists(DB_PATH):
        print(f"️ Warning: sqlite db with path:{DB_PATH} not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        print("Initializing database schema...")
        with open(SCHEMA_FILE, "r") as f:
            schema_script = f.read()

        cursor.executescript(schema_script)
        print("Database schema initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    app.state.redis = redis.from_url(
        settings.redis_url, encoding="utf-8", decode_responses=True
    )

    yield

    await app.state.redis.close()


# Get(read), Post(create), Put(update), Delete
app = FastAPI(lifespan=lifespan)


async def get_redis() -> Redis:
    return app.state.redis


from .routers import likes, posts, users, auth  # noqa: E402

# Security Nightmare, need to be more granular
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(likes.router)


@app.get("/", status_code=200)
def root():
    return {"mssg": "Hello World!"}
