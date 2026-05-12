"""
URL Shortener Lab - FastAPI 앱

이 앱이 하는 일:
  - / : 단축 URL 생성 폼 + 최근 생성된 URL 목록
  - POST /shorten : URL을 받아서 6자리 단축 코드 생성 후 DB 저장
  - GET /r/{short_code} : 원본 URL로 302 리다이렉트 + 클릭 로그 INSERT
  - GET /health : 헬스체크 (Dockerfile HEALTHCHECK가 호출)

수강생이 손댈 일은 없습니다. Dockerfile만 잘 작성하면 됩니다.
"""

import os
import secrets
import string
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg import errors as pg_errors
from psycopg_pool import ConnectionPool


# ─────────────────────────────────────────────────────────────
# 설정 (환경변수로 주입 — 컨테이너 실행 시 -e DATABASE_URL=... 형태)
# ─────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:devpass@localhost:5432/shortener",
)
SHORT_CODE_LENGTH = 6
ALPHABET = string.ascii_letters + string.digits

# 전역 연결 풀 (앱 시작 시 lifespan에서 생성)
pool: ConnectionPool | None = None


# ─────────────────────────────────────────────────────────────
# 앱 라이프사이클: 시작 시 DB 연결 풀 열고, 종료 시 닫기
# ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=5, open=True)
    yield
    pool.close()


app = FastAPI(lifespan=lifespan, title="URL Shortener Lab")
templates = Jinja2Templates(directory="app/templates")


def generate_short_code() -> str:
    """무작위 6자리 영숫자 단축 코드 생성"""
    return "".join(secrets.choice(ALPHABET) for _ in range(SHORT_CODE_LENGTH))


# ─────────────────────────────────────────────────────────────
# 헬스체크 (Dockerfile HEALTHCHECK용)
# ─────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


# ─────────────────────────────────────────────────────────────
# 홈: 단축 URL 생성 폼 + 최근 목록
# ─────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    with pool.connection() as conn:
        rows = conn.execute(
            """
            SELECT u.short_code, u.original_url, u.created_at, COUNT(c.id) AS clicks
            FROM urls u
            LEFT JOIN clicks c ON u.short_code = c.short_code
            GROUP BY u.short_code
            ORDER BY u.created_at DESC
            LIMIT 20
            """
        ).fetchall()
    urls = [
        {
            "short_code": r[0],
            "original_url": r[1],
            "created_at": r[2],
            "clicks": r[3],
        }
        for r in rows
    ]
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "urls": urls},
    )


# ─────────────────────────────────────────────────────────────
# 단축 URL 생성: POST /shorten
# ─────────────────────────────────────────────────────────────
@app.post("/shorten")
def shorten(request: Request, url: str = Form(...)):
    # http:// 또는 https:// 가 없으면 https:// 붙여줌
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # 중복 가능성 대비 5회 재시도
    for _ in range(5):
        code = generate_short_code()
        try:
            with pool.connection() as conn:
                conn.execute(
                    "INSERT INTO urls (short_code, original_url) VALUES (%s, %s)",
                    (code, url),
                )
            return RedirectResponse(url="/", status_code=303)
        except pg_errors.UniqueViolation:
            continue

    raise HTTPException(status_code=500, detail="단축 코드 생성 실패 (재시도 초과)")


# ─────────────────────────────────────────────────────────────
# 리다이렉트: GET /r/{short_code}
#   - 원본 URL 조회 후 302 응답
#   - 클릭 로그(IP, User-Agent) INSERT
# ─────────────────────────────────────────────────────────────
@app.get("/r/{short_code}")
def redirect(short_code: str, request: Request):
    with pool.connection() as conn:
        row = conn.execute(
            "SELECT original_url FROM urls WHERE short_code = %s",
            (short_code,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="단축 URL을 찾을 수 없습니다")

        # 클릭 로그 기록
        conn.execute(
            "INSERT INTO clicks (short_code, user_agent, ip) VALUES (%s, %s, %s)",
            (
                short_code,
                request.headers.get("user-agent", ""),
                request.client.host if request.client else "",
            ),
        )

    return RedirectResponse(url=row[0], status_code=302)
