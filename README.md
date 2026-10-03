# lily-blog-fastapi

Lily 배포 시험용 경량 블로그. 글쓰기와 목록만 있다.

## 구성

- `main.py`: FastAPI 서버. 화면(`/`), 글 API, 헬스체크
- `static/index.html`: 화면 한 장
- DB: `DATABASE_URL`(postgresql://...)이 있으면 Postgres, 없으면 `blog.db`(SQLite)

## API

| 경로 | 설명 |
|---|---|
| `GET /` | 화면 |
| `GET /api/posts` | 글 목록 (최신 100개) |
| `POST /api/posts` | 글쓰기 `{ "title": "...", "body": "..." }` |
| `GET /health` | 상태, 쓰는 DB 종류 |

## 로컬 실행

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

http://localhost:8000

## Lily 배포

- GitHub URL만 넣으면 된다. Dockerfile 없이 builder가 `python fastapi (main)`으로 판단해 `uvicorn main:app`을 8000 포트로 띄운다
- `psycopg`가 있어 DB 자동 판단 시 PostgreSQL이 붙고, 블루·그린 슬롯이 같은 글을 본다
- DB 없이 배포하면 SQLite라 재배포 때 글이 사라진다
