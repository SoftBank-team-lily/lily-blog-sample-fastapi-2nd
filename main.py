import os
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Lily 가 DB 를 붙이면 DATABASE_URL(postgresql://...) 이 들어온다. 없으면 로컬 SQLite 파일을 쓴다
DATABASE_URL = os.getenv("DATABASE_URL", "")
USE_POSTGRES = DATABASE_URL.startswith("postgres")
INDEX = Path(__file__).parent / "static" / "index.html"

if USE_POSTGRES:
    import psycopg

    PH = "%s"
    SCHEMA = """CREATE TABLE IF NOT EXISTS posts (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now())"""

    def connect():
        return psycopg.connect(DATABASE_URL, autocommit=True)
else:
    PH = "?"
    SCHEMA = """CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"""

    def connect():
        conn = sqlite3.connect(os.getenv("SQLITE_PATH", "blog.db"))
        conn.isolation_level = None
        return conn


def query(sql, params=()):
    conn = connect()
    try:
        cur = conn.execute(sql, params)
        return cur.fetchall() if cur.description else []
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(_):
    query(SCHEMA)
    yield


app = FastAPI(title="Lily Blog", lifespan=lifespan)


class PostIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=5000)


def to_post(row):
    return {"id": row[0], "title": row[1], "body": row[2], "createdAt": str(row[3])}


@app.get("/")
def index():
    return FileResponse(INDEX)


@app.get("/health")
def health():
    return {"status": "ok", "db": "postgres" if USE_POSTGRES else "sqlite"}


@app.get("/api/posts")
def list_posts():
    rows = query("SELECT id, title, body, created_at FROM posts ORDER BY id DESC LIMIT 100")
    return [to_post(r) for r in rows]


@app.post("/api/posts", status_code=201)
def create_post(post: PostIn):
    rows = query(
        f"INSERT INTO posts (title, body) VALUES ({PH}, {PH}) RETURNING id, title, body, created_at",
        (post.title.strip(), post.body.strip()),
    )
    return to_post(rows[0])
