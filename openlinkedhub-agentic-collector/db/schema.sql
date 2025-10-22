CREATE TABLE IF NOT EXISTS records (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    dataset TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    tags JSON NOT NULL,
    indicator TEXT NOT NULL,
    province TEXT,
    province_code TEXT,
    year TEXT,
    date TEXT,
    value REAL,
    raw JSON NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
