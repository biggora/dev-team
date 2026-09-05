-- Seed data as idempotent code: re-running must not duplicate rows or fail.
CREATE TABLE IF NOT EXISTS subscribers (
  id    SERIAL PRIMARY KEY,
  email TEXT NOT NULL UNIQUE
);

INSERT INTO subscribers (email) VALUES ('dev@example.test')
ON CONFLICT (email) DO NOTHING;
