# URL Shortener Lab

사내용 단축 URL 서비스. Docker 인프라 구축 실습용입니다.

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

## 작업

강사가 제공하는 요구사항에 따라 인프라를 설계하고 배포하세요.
