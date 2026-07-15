from __future__ import annotations

import json
import sqlite3
from threading import RLock
from pathlib import Path
from typing import Any

from .models import Article, CollectionBatch, Comment, Metric, utc_now


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    platform TEXT DEFAULT '',
    url TEXT DEFAULT '',
    tags TEXT DEFAULT '[]',
    enabled INTEGER DEFAULT 1,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    summary TEXT DEFAULT '',
    author TEXT DEFAULT '',
    published_at TEXT DEFAULT '',
    content_status TEXT DEFAULT 'summary_only',
    sentiment TEXT DEFAULT 'neutral',
    risk_level TEXT DEFAULT 'low',
    heat_score REAL DEFAULT 0,
    matched_keywords TEXT DEFAULT '[]',
    matched_core_terms TEXT DEFAULT '[]',
    raw_json TEXT DEFAULT '{}',
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_url TEXT NOT NULL,
    platform TEXT NOT NULL,
    author TEXT DEFAULT '',
    content TEXT NOT NULL,
    published_at TEXT DEFAULT '',
    like_count INTEGER DEFAULT 0,
    sentiment TEXT DEFAULT 'neutral',
    raw_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_url TEXT NOT NULL,
    platform TEXT NOT NULL,
    read_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    heat_score REAL DEFAULT 0,
    collected_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS content_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_url TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_estimate INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    UNIQUE(article_url, chunk_index)
);

CREATE TABLE IF NOT EXISTS crawl_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    platforms TEXT DEFAULT '[]',
    core_terms TEXT DEFAULT '[]',
    start_date TEXT DEFAULT '',
    end_date TEXT DEFAULT '',
    status TEXT DEFAULT 'pending',
    result_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS report_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,
    report_date TEXT DEFAULT '',
    title TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    ai_status TEXT DEFAULT 'not_used',
    model TEXT DEFAULT '',
    created_at TEXT NOT NULL
);
"""


class Repository:
    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = RLock()
        self.conn = sqlite3.connect(self.database_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self._ensure_migrations()
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def _ensure_migrations(self) -> None:
        source_columns = {
            row["name"]
            for row in self.conn.execute("PRAGMA table_info(sources)").fetchall()
        }
        if "tags" not in source_columns:
            self.conn.execute("ALTER TABLE sources ADD COLUMN tags TEXT DEFAULT '[]'")

    def upsert_source(self, source_id: str, name: str, type_: str, platform: str, url: str, tags: list[str] | None = None) -> None:
        with self.lock:
            self.conn.execute(
                """
                INSERT INTO sources (id, name, type, platform, url, tags, enabled, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    type=excluded.type,
                    platform=excluded.platform,
                    url=excluded.url,
                    tags=excluded.tags,
                    updated_at=excluded.updated_at
                """,
                (source_id, name, type_, platform, url, json.dumps(tags or [], ensure_ascii=False), utc_now()),
            )
            self.conn.commit()

    def save_batch(self, batch: CollectionBatch) -> int:
        saved = 0
        now = utc_now()
        with self.lock:
            for article in batch.articles:
                if not article.title.strip() or not article.url.strip():
                    continue
                self.conn.execute(
                    """
                    INSERT INTO articles (
                        source_id, platform, title, url, summary, author, published_at,
                        content_status, raw_json, first_seen_at, last_seen_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(url) DO UPDATE SET
                        title=excluded.title,
                        summary=excluded.summary,
                        author=excluded.author,
                        published_at=excluded.published_at,
                        last_seen_at=excluded.last_seen_at,
                        raw_json=excluded.raw_json
                    """,
                    (
                        article.source_id,
                        article.platform,
                        article.title,
                        article.url,
                        article.summary,
                        article.author,
                        article.published_at,
                        article.content_status,
                        json.dumps(article.raw, ensure_ascii=False),
                        now,
                        now,
                    ),
                )
                saved += 1
            for comment in batch.comments:
                if comment.content.strip():
                    self.conn.execute(
                        """
                        INSERT INTO comments (
                            article_url, platform, author, content, published_at,
                            like_count, raw_json, created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            comment.article_url,
                            comment.platform,
                            comment.author,
                            comment.content,
                            comment.published_at,
                            comment.like_count,
                            json.dumps(comment.raw, ensure_ascii=False),
                            now,
                        ),
                    )
            for metric in batch.metrics:
                self.conn.execute(
                    """
                    INSERT INTO metrics (
                        article_url, platform, read_count, like_count,
                        comment_count, share_count, collected_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        metric.article_url,
                        metric.platform,
                        metric.read_count,
                        metric.like_count,
                        metric.comment_count,
                        metric.share_count,
                        metric.collected_at,
                    ),
                )
            self.conn.commit()
        return saved

    def update_article_analysis(
        self,
        url: str,
        sentiment: str,
        risk_level: str,
        heat_score: float,
        matched_keywords: list[str],
        matched_core_terms: list[str],
    ) -> None:
        with self.lock:
            self.conn.execute(
                """
                UPDATE articles
                SET sentiment=?, risk_level=?, heat_score=?,
                    matched_keywords=?, matched_core_terms=?
                WHERE url=?
                """,
                (
                    sentiment,
                    risk_level,
                    heat_score,
                    json.dumps(matched_keywords, ensure_ascii=False),
                    json.dumps(matched_core_terms, ensure_ascii=False),
                    url,
                ),
            )
            self.conn.commit()

    def latest_articles(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT a.*,
                COALESCE((SELECT read_count FROM metrics m WHERE m.article_url=a.url ORDER BY m.collected_at DESC LIMIT 1), 0) AS read_count,
                COALESCE((SELECT like_count FROM metrics m WHERE m.article_url=a.url ORDER BY m.collected_at DESC LIMIT 1), 0) AS like_count,
                COALESCE((SELECT comment_count FROM metrics m WHERE m.article_url=a.url ORDER BY m.collected_at DESC LIMIT 1), 0) AS comment_count,
                COALESCE((SELECT share_count FROM metrics m WHERE m.article_url=a.url ORDER BY m.collected_at DESC LIMIT 1), 0) AS share_count
            FROM articles a
            ORDER BY a.last_seen_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    def overview(self) -> dict[str, Any]:
        row = self.conn.execute(
            """
            SELECT
                COUNT(*) AS articles,
                SUM(CASE WHEN risk_level='high' THEN 1 ELSE 0 END) AS high_risk,
                SUM(CASE WHEN risk_level='medium' THEN 1 ELSE 0 END) AS medium_risk,
                SUM(CASE WHEN sentiment='negative' THEN 1 ELSE 0 END) AS negative
            FROM articles
            """
        ).fetchone()
        platforms = self.conn.execute(
            "SELECT platform, COUNT(*) AS count FROM articles GROUP BY platform ORDER BY count DESC"
        ).fetchall()
        return {
            "articles": row["articles"] or 0,
            "high_risk": row["high_risk"] or 0,
            "medium_risk": row["medium_risk"] or 0,
            "negative": row["negative"] or 0,
            "platforms": [dict(item) for item in platforms],
        }

    def create_job(self, payload: dict[str, Any]) -> int:
        now = utc_now()
        with self.lock:
            cur = self.conn.execute(
                """
                INSERT INTO crawl_jobs (query, platforms, core_terms, start_date, end_date, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
                """,
                (
                    payload.get("query", ""),
                    json.dumps(payload.get("platforms", []), ensure_ascii=False),
                    json.dumps(payload.get("core_terms", []), ensure_ascii=False),
                    payload.get("start_date", ""),
                    payload.get("end_date", ""),
                    now,
                    now,
                ),
            )
            self.conn.commit()
            return int(cur.lastrowid)

    def save_report_run(
        self,
        report_type: str,
        report_date: str,
        title: str,
        payload: dict[str, Any],
        ai_status: str,
        model: str = "",
    ) -> int:
        with self.lock:
            cur = self.conn.execute(
                """
                INSERT INTO report_runs (
                    report_type, report_date, title, payload_json, ai_status, model, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report_type,
                    report_date,
                    title,
                    json.dumps(payload, ensure_ascii=False),
                    ai_status,
                    model,
                    utc_now(),
                ),
            )
            self.conn.commit()
            return int(cur.lastrowid)
