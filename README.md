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
| `GET /api/slow?ms=500` | 부하 시험용. ms(최대 3000) 만큼 붙잡은 뒤 처리 거점(`local`·`cloud`)을 돌려준다 |

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

## 부하 시험

- 화면의 `부하 시험`에서 동시 요청 수·시간·지연을 정하고 `부하 주기`를 누른다 (동시 30개, 30초 상한)
- 내 PC 처리 한도(에이전트 `BURST_LOCAL_LIMIT`, 기본 8)를 넘긴 요청이 클라우드로 넘어가면 `클라우드` 줄에 쌓인다
- 처리 거점은 `KUBERNETES_SERVICE_HOST` 유무로 판단한다 (클라우드 Pod 에만 있다)
- 공개 주소로 접속해야 에이전트 프록시를 거친다. localhost 로 열면 모두 `내 PC`로 처리된다
