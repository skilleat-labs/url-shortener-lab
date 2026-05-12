-- ─────────────────────────────────────────────────────────────
-- URL Shortener Lab - DB 초기화 스크립트
--
-- postgres 컨테이너 시작 시 /docker-entrypoint-initdb.d/ 에
-- 마운트되면 컨테이너가 자동으로 이 SQL을 실행합니다.
-- ─────────────────────────────────────────────────────────────

-- 단축 URL 매핑 테이블
CREATE TABLE IF NOT EXISTS urls (
    short_code   VARCHAR(10) PRIMARY KEY,
    original_url TEXT NOT NULL,
    created_at   TIMESTAMP DEFAULT NOW()
);

-- 클릭 로그 테이블
CREATE TABLE IF NOT EXISTS clicks (
    id          SERIAL PRIMARY KEY,
    short_code  VARCHAR(10) REFERENCES urls(short_code) ON DELETE CASCADE,
    clicked_at  TIMESTAMP DEFAULT NOW(),
    user_agent  TEXT,
    ip          VARCHAR(45)
);

-- 클릭 조회 성능을 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_clicks_short_code ON clicks(short_code);
