from __future__ import annotations

from ayx_growth_intel.analysis.scorer import score_article
from ayx_growth_intel.collectors import HotlistCollector, RssCollector, SocialIntelImporter, WebIntelCollector
from ayx_growth_intel.config import AppConfig, SourceConfig, resolve_path
from ayx_growth_intel.models import CollectionBatch
from ayx_growth_intel.storage import Repository


class CollectionPipeline:
    def __init__(self, config: AppConfig, repository: Repository):
        self.config = config
        self.repository = repository
        self.collectors = {
            "hotlist": HotlistCollector(),
            "rss": RssCollector(),
            "web_intel": WebIntelCollector(config.web_intel_endpoint),
            "social_intel": SocialIntelImporter(resolve_path(config.social_import_dir)),
        }

    def run_all(self, keywords: list[str] | None = None, core_terms: list[str] | None = None) -> dict:
        total = 0
        failures: list[dict] = []
        for source in self.config.sources:
            try:
                total += self.run_source(source, keywords=keywords, core_terms=core_terms)
            except Exception as exc:
                failures.append({"source_id": source.id, "error": str(exc)})
        return {"saved": total, "failures": failures}

    def run_source(
        self,
        source: SourceConfig,
        keywords: list[str] | None = None,
        core_terms: list[str] | None = None,
    ) -> int:
        collector = self.collectors.get(source.type)
        if collector is None:
            raise ValueError(f"Unsupported source type: {source.type}")
        self.repository.upsert_source(source.id, source.name, source.type, source.platform, source.url, source.tags)
        batch: CollectionBatch = collector.collect(source)
        saved = self.repository.save_batch(batch)
        metrics_by_url = {metric.article_url: metric for metric in batch.metrics}
        for article in batch.articles:
            score = score_article(article, metrics_by_url.get(article.url), keywords, core_terms)
            self.repository.update_article_analysis(
                article.url,
                score.sentiment,
                score.risk_level,
                score.heat_score,
                score.matched_keywords,
                score.matched_core_terms,
            )
        return saved
