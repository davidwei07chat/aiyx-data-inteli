from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ayx_growth_intel.config import SourceConfig
from ayx_growth_intel.models import Article, CollectionBatch, Comment, Metric

from .base import Collector


class SocialIntelImporter(Collector):
    def __init__(self, import_dir: str | Path):
        self.import_dir = Path(import_dir)

    def collect(self, source: SourceConfig) -> CollectionBatch:
        batch = CollectionBatch()
        if not self.import_dir.exists():
            return batch

        for path in sorted(self.import_dir.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            records = payload if isinstance(payload, list) else payload.get("items", [])
            for record in records[: source.max_items]:
                article = self._article_from_record(source, record)
                if article is None:
                    continue
                batch.articles.append(article)
                batch.metrics.append(self._metric_from_record(article, record))
                for comment in record.get("comments", []) or []:
                    batch.comments.append(self._comment_from_record(article, comment))
        return batch

    def _article_from_record(self, source: SourceConfig, record: dict[str, Any]) -> Article | None:
        title = first(record, "title", "note_title", "desc", "content", "text")
        url = first(record, "url", "note_url", "share_url", "web_url")
        if not title or not url:
            return None
        summary = first(record, "summary", "desc", "content", "text")[:360]
        author = first(record, "nickname", "author", "user_name", "user")
        published_at = first(record, "publish_time", "published_at", "time", "created_at")
        platform = source.platform or first(record, "platform", "source") or "social"
        return Article(
            source_id=source.id,
            platform=platform,
            title=title[:180],
            url=url,
            summary=summary,
            author=author,
            published_at=str(published_at),
            raw=record,
        )

    def _metric_from_record(self, article: Article, record: dict[str, Any]) -> Metric:
        return Metric(
            article_url=article.url,
            platform=article.platform,
            read_count=to_int(first(record, "read_count", "view_count", "play_count")),
            like_count=to_int(first(record, "like_count", "liked_count", "digg_count")),
            comment_count=to_int(first(record, "comment_count", "comments_count")),
            share_count=to_int(first(record, "share_count", "forward_count", "repost_count")),
        )

    def _comment_from_record(self, article: Article, record: dict[str, Any]) -> Comment:
        return Comment(
            article_url=article.url,
            platform=article.platform,
            author=first(record, "nickname", "author", "user_name", "user"),
            content=first(record, "content", "text", "comment_content"),
            published_at=str(first(record, "publish_time", "published_at", "time", "created_at")),
            like_count=to_int(first(record, "like_count", "liked_count")),
            raw=record,
        )


def first(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return value
    return ""


def to_int(value: Any) -> int:
    try:
        return int(float(value or 0))
    except Exception:
        return 0
