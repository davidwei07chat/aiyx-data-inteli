from __future__ import annotations

from typing import Any

import requests

from ayx_growth_intel.config import SourceConfig
from ayx_growth_intel.models import Article, CollectionBatch, Metric

from .base import Collector


class WebIntelCollector(Collector):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint.rstrip("/")

    def collect(self, source: SourceConfig) -> CollectionBatch:
        payload = {
            "urls": [source.url],
            "crawler_config": {
                "word_count_threshold": 20,
                "excluded_tags": ["nav", "footer", "aside"],
                "only_text": False,
            },
        }
        response = requests.post(f"{self.endpoint}/crawl", json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        items = data if isinstance(data, list) else data.get("results", [data])

        batch = CollectionBatch()
        for item in items[: source.max_items]:
            article = self._to_article(source, item)
            if article:
                batch.articles.append(article)
                batch.metrics.append(Metric(article_url=article.url, platform=article.platform))
        return batch

    def _to_article(self, source: SourceConfig, item: dict[str, Any]) -> Article | None:
        metadata = item.get("metadata") or {}
        url = item.get("url") or metadata.get("url") or source.url
        markdown = item.get("markdown") or item.get("fit_markdown") or ""
        title = metadata.get("title") or item.get("title") or _first_heading(markdown)
        summary = metadata.get("description") or _summary_from_markdown(markdown)
        if not title:
            return None
        return Article(
            source_id=source.id,
            platform=source.platform or "web",
            title=title,
            url=url,
            summary=summary,
            author=metadata.get("author", ""),
            published_at=metadata.get("published_time", "") or metadata.get("date", ""),
            raw={"metadata": metadata, "markdown_preview": markdown[:1200]},
        )


def _first_heading(markdown: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip("# ").strip()
        if stripped:
            return stripped[:160]
    return ""


def _summary_from_markdown(markdown: str) -> str:
    text = " ".join(line.strip("# ").strip() for line in markdown.splitlines() if line.strip())
    return text[:360]
