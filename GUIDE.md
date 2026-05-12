# 단계별 작업 가이드

강사용 / 막힌 수강생 참고용입니다.

---

## 사전 준비

- Docker Desktop 또는 Docker Engine이 설치되어 있어야 합니다.
- Docker Hub 계정이 필요합니다 (`docker login`).
- 본 가이드에서는 Docker Hub 계정명을 `<your-id>`로 표기합니다. 본인 계정명으로 바꿔서 실행하세요.

---

## 아키텍처

```
[사용자]
    ↓ :80
┌─ frontend-net ────────────┐
│         [app]              │  FastAPI 단일 컨테이너
└────────────┬──────────────┘
             ↓
┌─ backend-net (--internal) ┐
│       [postgres]           │  외부 노출 없음
└────────────────────────────┘
             │
       [postgres-data]       볼륨
```

---

## 1단계: Dockerfile 작성

프로젝트 루트(`url-shortener-lab/`)에 `Dockerfile` 파일을 직접 만들어보세요.

힌트:
- 베이스 이미지는 `python:3.12-slim` 추천
- `requirements.txt` 먼저 복사 → 설치 (캐시 최적화)
- 앱 코드는 그 다음 복사
- 비-root 사용자로 실행
- 포트 8000 노출
- 실행 명령: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

작성 후 막히면 `Dockerfile.solution`과 비교해보세요.

## 2단계: 이미지 빌드

```bash
docker build -t <your-id>/shortener-app:v1 .
```

빌드 성공 확인:
```bash
docker images | grep shortener-app
```

## 3단계: Docker Hub에 push

```bash
docker login
docker push <your-id>/shortener-app:v1
```

## 4단계: 이미지 검증 (선택)

push가 잘 됐는지 확인하려면 로컬 이미지를 삭제한 뒤 다시 pull 해봅니다.

```bash
docker rmi <your-id>/shortener-app:v1
docker pull <your-id>/shortener-app:v1
```

## 5단계: 네트워크와 볼륨 생성

```bash
# 외부 통신용 네트워크 (app이 사용자 요청 받음)
docker network create frontend-net

# 내부 전용 네트워크 (--internal 핵심: 인터넷 게이트웨이 없음)
docker network create --internal backend-net

# postgres 데이터 영속화용 볼륨
docker volume create postgres-data
```

확인:
```bash
docker network ls
docker volume ls
```

## 6단계: postgres 컨테이너 띄우기 (backend-net에만)

```bash
docker run -d \
  --name postgres \
  --network backend-net \
  -v postgres-data:/var/lib/postgresql/data \
  -v "$(pwd)/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro" \
  -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_DB=shortener \
  postgres:16-alpine
```

확인 - 테이블이 생성됐는지:
```bash
docker exec -it postgres psql -U postgres -d shortener -c '\dt'
```

`urls`와 `clicks` 테이블이 보이면 성공입니다.

## 7단계: app 컨테이너 띄우기 (두 네트워크에 attach)

`docker run`은 `--network`를 하나만 받기 때문에, 일단 backend-net으로 띄우고 그 다음 frontend-net을 추가로 붙입니다.

```bash
# backend-net으로 띄우기
docker run -d \
  --name app \
  --network backend-net \
  -e DATABASE_URL=postgresql://postgres:devpass@postgres:5432/shortener \
  -p 80:8000 \
  <your-id>/shortener-app:v1

# frontend-net 추가 attach
docker network connect frontend-net app
```

app이 attach된 네트워크 확인:
```bash
docker inspect app -f '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{"\n"}}{{end}}'
```

`backend-net`과 `frontend-net` 두 줄이 나오면 성공.

## 8단계: 동작 확인

브라우저에서 [http://localhost](http://localhost) 접속.
- URL 입력 → "단축하기" 버튼 → 단축 URL 생성
- 생성된 단축 URL 클릭 → 원본으로 리다이렉트 + 클릭 수 증가

## 9단계: 격리 검증 (핵심 학습 포인트)

postgres가 외부에서 접근 안 되는지 확인합니다.

호스트에서 직접 postgres에 접속 시도:
```bash
# Mac/Linux에 psql이 설치되어 있다면
psql -h localhost -p 5432 -U postgres
# → 연결 실패 (postgres에 -p 옵션을 안 줬으므로)
```

app 컨테이너 안에서는 접속 성공:
```bash
docker exec -it app sh -c "apt-get install -y postgresql-client 2>/dev/null; psql -h postgres -U postgres -d shortener -c '\dt'"
```

→ app은 backend-net에 attach되어 있으므로 postgres에 접근 가능합니다.

이것이 **네트워크 분리의 효과**입니다.

---

## 정리 (실습 종료 후)

```bash
docker stop app postgres
docker rm app postgres
docker network rm frontend-net backend-net
docker volume rm postgres-data         # 데이터 영구 삭제 (주의)
```

볼륨을 남겨두면 다음 실습에서 데이터가 그대로 살아있는 것을 확인할 수 있습니다.
