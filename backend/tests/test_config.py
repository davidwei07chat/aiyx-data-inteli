from ayx_growth_intel.config import load_config


def test_web_intel_endpoint_can_be_overridden_by_environment(monkeypatch) -> None:
    monkeypatch.setenv("AYX_WEB_INTEL_ENDPOINT", "http://crawler:11235")

    config = load_config("config/sources.yaml")

    assert config.web_intel_endpoint == "http://crawler:11235"
