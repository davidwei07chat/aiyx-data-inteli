from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Article:
    source_id: str
    platform: str
    title: str
    url: str
    summary: str = ""
    author: str = ""
    published_at: str = ""
    content_status: str = "summary_only"
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Comment:
    article_url: str
    platform: str
    author: str = ""
    content: str = ""
    published_at: str = ""
    like_count: int = 0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Metric:
    article_url: str
    platform: str
    read_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    collected_at: str = field(default_factory=utc_now)


@dataclass
class CollectionBatch:
    articles: list[Article] = field(default_factory=list)
    comments: list[Comment] = field(default_factory=list)
    metrics: list[Metric] = field(default_factory=list)
