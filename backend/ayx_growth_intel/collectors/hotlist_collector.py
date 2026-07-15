from __future__ import annotations

import os
from pathlib import Path
import sqlite3
from typing import Any

import requests

from ayx_growth_intel.config import SourceConfig
from ayx_growth_intel.models import Article, CollectionBatch, Metric

from .base import Collector


class HotlistCollector(Collector):
    def __init__(self, api_base: str = "https://newsnow.busiyi.world/api/s", timeout: int = 15):
        self.api_base = api_base
        self.timeout = timeout
        self.archive_dir = Path(os.environ.get("AYX_HOTLIST_ARCHIVE", "/app/legacy/news"))

    def collect(self, source: SourceConfig) -> CollectionBatch:
        try:
            response = requests.get(self.api_base, params={"id": source.id, "latest": ""}, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
            return batch_from_items(source, extract_items(payload))
        except requests.RequestException as exc:
            archived = self.collect_from_archive(source)
            if archived.articles:
                return archived
            raise exc

    def collect_from_archive(self, source: SourceConfig) -> CollectionBatch:
        if not self.archive_dir.exists():
            return CollectionBatch()
        archive_files = sorted(self.archive_dir.glob("*.db"), reverse=True)
        for archive_file in archive_files:
            batch = batch_from_archive_db(source, archive_file)
            if batch.articles:
                return batch
        return CollectionBatch()


def batch_from_items(source: SourceConfig, items: list[dict[str, Any]]) -> CollectionBatch:
    batch = CollectionBatch()
    platform = source.platform or "热榜"
    for index, item in enumerate(items[: source.max_items], start=1):
        title = str(item.get("title") or item.get("name") or "").strip()
        url = str(item.get("url") or item.get("mobileUrl") or "").strip()
        if not title or not url:
            continue
        summary = str(item.get("desc") or item.get("summary") or item.get("extra") or "")
        heat = parse_heat(item.get("hot") or item.get("score") or item.get("views"))
        batch.articles.append(
            Article(
                source_id=source.id,
                platform=platform,
                title=title,
                url=url,
                summary=summary,
                content_status="summary_only",
                raw={"rank": index, **item},
            )
        )
        batch.metrics.append(
            Metric(
                article_url=url,
                platform=platform,
                read_count=heat,
                share_count=max(source.max_items - index + 1, 0),
            )
        )
    return batch


def batch_from_archive_db(source: SourceConfig, archive_file: Path) -> CollectionBatch:
    batch = CollectionBatch()
    platform = source.platform or "热榜"
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(archive_file)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, title, platform_id, rank, url, mobile_url, first_crawl_time, last_crawl_time, crawl_count
            FROM news_items
            WHERE platform_id = ?
            ORDER BY rank ASC
            LIMIT ?
            """,
            (source.id, source.max_items),
        ).fetchall()
    except sqlite3.Error:
        return batch
    finally:
        if conn is not None:
            conn.close()
    archive_date = archive_file.stem
    for row in rows:
        url = row["url"] or row["mobile_url"] or f"legacy-hotlist://{source.id}/{row['id']}"
        rank = int(row["rank"] or 0)
        batch.articles.append(
            Article(
                source_id=source.id,
                platform=platform,
                title=row["title"],
                url=url,
                summary=f"热榜排名 {rank}，归档日期 {archive_date}，最近抓取 {row['last_crawl_time']}。",
                published_at=archive_date,
                raw=dict(row),
            )
        )
        batch.metrics.append(
            Metric(
                article_url=url,
                platform=platform,
                read_count=int(row["crawl_count"] or 0),
                share_count=max(source.max_items - rank + 1, 0),
            )
        )
    return batch


def extract_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    data = payload.get("data", payload)
    if isinstance(data, dict):
        candidates = data.get("items") or data.get("list") or data.get("data") or []
    else:
        candidates = data
    return [item for item in candidates if isinstance(item, dict)] if isinstance(candidates, list) else []


def parse_heat(value: Any) -> int:
    if value is None:
        return 0
    text = str(value).replace(",", "").strip()
    multiplier = 1
    if text.endswith("万"):
        multiplier = 10000
        text = text[:-1]
    try:
        return int(float(text) * multiplier)
    except ValueError:
        return 0
