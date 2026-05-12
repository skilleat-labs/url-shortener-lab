# URL Shortener Lab (Solutions Branch)

수강생용 `main` 브랜치와 동일한 코드 + 정답 자료가 있는 브랜치입니다.

## 추가 파일

| 파일 | 내용 |
|------|------|
| `Dockerfile.solution` | 정답 Dockerfile |
| `GUIDE.md` | 단계별 작업 가이드 (9단계) |
| `TROUBLESHOOTING.md` | 자주 발생하는 에러와 해결법 |

---

## 디렉터리 구조

```
url-shortener-lab/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱
│   └── templates/
│       └── index.html
├── postgres/
│   └── init.sql             # DB 초기 스키마 (컨테이너 최초 기동 시 자동 실행)
├── requirements.txt
├── Dockerfile.solution      # 정답 Dockerfile
├── GUIDE.md                 # 단계별 작업 가이드
├── TROUBLESHOOTING.md       # 트러블슈팅
├── .dockerignore
└── README.md
```

## 기술 정보

| 항목 | 내용 |
|------|------|
| 언어 | Python 3.12 |
| 웹 프레임워크 | FastAPI |
| 실행 명령 | `uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| 데이터베이스 | PostgreSQL 16 |
| 환경변수 | `DATABASE_URL` — DB 연결 문자열 |
