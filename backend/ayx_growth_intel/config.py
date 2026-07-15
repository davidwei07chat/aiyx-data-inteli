from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class SourceConfig:
    id: str
    name: str
    type: str
    url: str = ""
    platform: str = ""
    tags: list[str] = field(default_factory=list)
    enabled: bool = True
    show_frontend: bool = True
    collect_comments: bool = False
    max_items: int = 30


@dataclass
class IndustryDefault:
    name: str
    keywords: list[str] = field(default_factory=list)
    core_terms: list[str] = field(default_factory=list)


@dataclass
class ReportDefaults:
    keywords: list[str] = field(default_factory=list)
    core_terms: list[str] = field(default_factory=list)
    industries: list[IndustryDefault] = field(default_factory=list)


@dataclass
class AppConfig:
    database_path: str = "data/ayx_growth_intel.db"
    web_intel_endpoint: str = "http://localhost:11235"
    social_import_dir: str = "data/social-intel"
    request_interval_seconds: float = 2.0
    ai_report_enabled: bool = False
    ai_report_api_base: str = "https://api.openai.com/v1"
    ai_report_api_key: str = ""
    ai_report_model: str = "gpt-4.1-mini"
    ai_report_timeout: int = 60
    sources: list[SourceConfig] = field(default_factory=list)
    all_sources: list[SourceConfig] = field(default_factory=list)
    report_defaults: ReportDefaults = field(default_factory=ReportDefaults)


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    env = read_env_file(config_path.parent / ".env")
    app = raw.get("app", {})
    web_intel = raw.get("web_intel", {})
    social_intel = raw.get("social_intel", {})
    ai_report = raw.get("ai_report", {})
    all_sources = [SourceConfig(**item) for item in raw.get("sources", [])]
    sources = [source for source in all_sources if source.enabled]
    report_defaults_raw = raw.get("report_defaults", {})
    report_defaults = ReportDefaults(
        keywords=list(report_defaults_raw.get("keywords", [])),
        core_terms=list(report_defaults_raw.get("core_terms", [])),
        industries=[
            IndustryDefault(
                name=item.get("name", ""),
                keywords=list(item.get("keywords", [])),
                core_terms=list(item.get("core_terms", [])),
            )
            for item in report_defaults_raw.get("industries", [])
            if item.get("name")
        ],
    )
    return AppConfig(
        database_path=app.get("database_path", "data/ayx_growth_intel.db"),
        web_intel_endpoint=os.environ.get("AYX_WEB_INTEL_ENDPOINT") or web_intel.get("endpoint", "http://localhost:11235"),
        social_import_dir=social_intel.get("import_dir", "data/social-intel"),
        request_interval_seconds=float(app.get("request_interval_seconds", 2.0)),
        ai_report_enabled=bool(ai_report.get("enabled", False)),
        ai_report_api_base=os.environ.get("AI_BACKEND_API_BASE") or env.get("AI_BACKEND_API_BASE") or os.environ.get("AI_API_BASE") or env.get("AI_API_BASE") or ai_report.get("api_base", "https://api.openai.com/v1"),
        ai_report_api_key=os.environ.get("AI_BACKEND_API_KEY") or env.get("AI_BACKEND_API_KEY") or os.environ.get("AI_API_KEY") or env.get("AI_API_KEY") or ai_report.get("api_key", ""),
        ai_report_model=os.environ.get("AI_BACKEND_MODEL") or env.get("AI_BACKEND_MODEL") or os.environ.get("AI_MODEL") or env.get("AI_MODEL") or ai_report.get("model", "gpt-4.1-mini"),
        ai_report_timeout=int(os.environ.get("AI_BACKEND_TIMEOUT") or env.get("AI_BACKEND_TIMEOUT") or os.environ.get("AI_TIMEOUT") or env.get("AI_TIMEOUT") or ai_report.get("timeout", 60)),
        sources=sources,
        all_sources=all_sources,
        report_defaults=report_defaults,
    )


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return project_root() / path


def read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result
