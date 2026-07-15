import yaml
from fastapi.testclient import TestClient

from ayx_growth_intel.analysis.report_generator import compact_report_for_model
from ayx_growth_intel.api.main import create_app


def test_daily_report_falls_back_without_ai_key(tmp_path, monkeypatch):
    for key in ["AI_BACKEND_API_KEY", "AI_API_KEY"]:
        monkeypatch.delenv(key, raising=False)
    config = yaml.safe_load(open("config/sources.yaml", encoding="utf-8"))
    config["ai_report"]["api_key"] = ""
    test_config = tmp_path / "sources.yaml"
    test_config.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8")
    client = TestClient(create_app(str(test_config)))
    response = client.post(
        "/reports/daily",
        json={
            "keywords": ["品牌"],
            "core_terms": ["投诉", "故障"],
            "industries": [
                {
                    "name": "消费零售",
                    "keywords": ["消费", "品牌"],
                    "core_terms": ["投诉", "差评"],
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "大消费数据洞察分析"
    assert payload["ai_status"] == "disabled"
    assert payload["report_id"] > 0
    assert len(payload["industries"]) == 1


def test_model_report_payload_is_compact():
    report = {
        "industries": [
            {
                "summary": "长" * 300,
                "top_events": [{"title": "题" * 200, "summary": "文" * 800} for _ in range(6)],
            }
        ]
    }

    compact = compact_report_for_model(report)

    assert len(compact["industries"][0]["summary"]) <= 241
    assert len(compact["industries"][0]["top_events"]) == 4
    assert len(compact["industries"][0]["top_events"][0]["summary"]) <= 421
