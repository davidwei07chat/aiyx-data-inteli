from __future__ import annotations

import math
from dataclasses import dataclass

from ayx_growth_intel.models import Article, Metric


NEGATIVE_TERMS = [
    "投诉",
    "维权",
    "翻车",
    "造假",
    "召回",
    "故障",
    "暴雷",
    "欺诈",
    "差评",
    "跑路",
]

POSITIVE_TERMS = ["推荐", "增长", "获奖", "突破", "领先", "好评", "升级"]


@dataclass
class ScoreResult:
    sentiment: str
    risk_level: str
    heat_score: float
    matched_keywords: list[str]
    matched_core_terms: list[str]


def score_article(
    article: Article,
    metric: Metric | None = None,
    keywords: list[str] | None = None,
    core_terms: list[str] | None = None,
) -> ScoreResult:
    keywords = keywords or []
    core_terms = core_terms or []
    text = f"{article.title} {article.summary}".lower()
    matched_keywords = [item for item in keywords if item.lower() in text]
    matched_core_terms = [item for item in core_terms if item.lower() in text]

    negative_hits = sum(1 for item in NEGATIVE_TERMS if item in text)
    positive_hits = sum(1 for item in POSITIVE_TERMS if item in text)
    if negative_hits > positive_hits:
        sentiment = "negative"
    elif positive_hits > negative_hits:
        sentiment = "positive"
    else:
        sentiment = "neutral"

    metric = metric or Metric(article_url=article.url, platform=article.platform)
    engagement = metric.read_count + metric.like_count * 3 + metric.comment_count * 8 + metric.share_count * 10
    heat_score = round(math.log10(max(engagement, 1)) * 20 + len(matched_core_terms) * 12 + negative_hits * 15, 2)

    if sentiment == "negative" and (heat_score >= 55 or len(matched_core_terms) >= 2):
        risk_level = "high"
    elif heat_score >= 35 or negative_hits > 0 or matched_core_terms:
        risk_level = "medium"
    else:
        risk_level = "low"

    return ScoreResult(
        sentiment=sentiment,
        risk_level=risk_level,
        heat_score=heat_score,
        matched_keywords=matched_keywords,
        matched_core_terms=matched_core_terms,
    )
