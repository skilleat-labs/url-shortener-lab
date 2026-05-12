# 트러블슈팅

---

**Q. `docker push`에서 "denied: requested access to the resource is denied"**

→ `docker login`을 먼저 실행하세요. 이미지 태그의 `<your-id>` 부분이 Docker Hub 계정명과 정확히 일치해야 합니다.

---

**Q. app 컨테이너가 시작 직후 종료됨**

→ `docker logs app` 으로 에러 확인. 대부분 postgres 연결 실패입니다.
- postgres가 먼저 띄워졌는지 확인
- `DATABASE_URL`의 호스트명이 `postgres`(컨테이너 이름)와 같은지 확인

---

**Q. 80 포트가 이미 사용 중**

→ `-p 8080:8000` 으로 바꿔서 http://localhost:8080 으로 접속.

---

**Q. postgres 컨테이너에서 init.sql이 실행 안 됨**

→ init.sql은 **볼륨이 비어있을 때만** 실행됩니다. 이미 데이터가 있으면 스킵됩니다.
재실행하려면 `docker volume rm postgres-data` 후 다시 시작.
