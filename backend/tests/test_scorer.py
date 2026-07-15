from ayx_growth_intel.analysis.scorer import score_article
from ayx_growth_intel.models import Article, Metric


def test_negative_core_term_raises_risk():
    article = Article(
        source_id="demo",
        platform="weibo",
        title="某品牌售后投诉引发维权",
        url="https://example.com/a",
        summary="用户集中反馈故障和差评",
    )
    metric = Metric(
        article_url=article.url,
        platform=article.platform,
        read_count=10000,
        comment_count=220,
        share_count=80,
    )
    score = score_article(article, metric, keywords=["某品牌"], core_terms=["投诉", "维权"])
    assert score.sentiment == "negative"
    assert score.risk_level == "high"
    assert "投诉" in score.matched_core_terms
