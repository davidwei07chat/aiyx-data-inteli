from __future__ import annotations

from html import unescape
import re

from dateutil import parser as date_parser
import feedparser
import requests

from ayx_growth_intel.config import SourceConfig
from ayx_growth_intel.models import Article, CollectionBatch, Metric

from .base import Collector


class RssCollector(Collector):
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def collect(self, source: SourceConfig) -> CollectionBatch:
        response = requests.get(source.url, timeout=self.timeout, headers={"User-Agent": "AiYX-DATA-INTELI/0.1"})
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        batch = CollectionBatch()
        for entry in feed.entries[: source.max_items]:
            url = entry.get("link", "")
            published = entry.get("published") or entry.get("updated") or ""
            try:
                published_at = date_parser.parse(published).isoformat() if published else ""
            except Exception:
                published_at = published
            summary = clean_summary(entry.get("summary", "") or entry.get("description", ""))
            author = entry.get("author", "")
            batch.articles.append(
                Article(
                    source_id=source.id,
                    platform=source.platform or "rss",
                    title=entry.get("title", ""),
                    url=url,
                    summary=summary,
                    author=author,
                    published_at=published_at,
                    raw=dict(entry),
                )
            )
            batch.metrics.append(Metric(article_url=url, platform=source.platform or "rss"))
        return batch


def clean_summary(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()
