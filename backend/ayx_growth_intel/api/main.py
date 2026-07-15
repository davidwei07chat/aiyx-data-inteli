from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
from typing import Any

import requests
import uvicorn
import yaml
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ayx_growth_intel.api.config_center_view import render_backend_config_center
from ayx_growth_intel.analysis.report_generator import AIReportGenerator
from ayx_growth_intel.config import load_config, resolve_path
from ayx_growth_intel.pipeline import CollectionPipeline
from ayx_growth_intel.storage import Repository


SOURCE_MANUAL_TAGS = ["热榜", "地区", "财经", "科技", "文旅", "教育", "军事", "国际", "消费", "其他"]
SOURCE_FIXED_TAGS = {"hotlist": "热榜", "rss": "RSS源"}
CONFIG_FILE_MAP = {
    "config": ("AYX 主配置", "config.yaml"),
    "sources": ("运行数据源", "sources.yaml"),
    "frequency": ("频率词", "frequency_words.txt"),
    "timeline": ("推送配置", "timeline.yaml"),
    "analysis_prompt": ("大模型分析提示词", "ai_analysis_prompt.txt"),
    "translation_prompt": ("大模型翻译提示词", "ai_translation_prompt.txt"),
    "ai_models": ("大模型提供商", "ai_models.yaml"),
    "industry_packs": ("行业词包", "industry_packs.yaml"),
    "skills": ("技能配置", "skills.yaml"),
}


class SearchTaskRequest(BaseModel):
    query: str = Field(min_length=1)
    platforms: list[str] = Field(default_factory=list)
    core_terms: list[str] = Field(default_factory=list)
    start_date: str = ""
    end_date: str = ""


class IndustryRequest(BaseModel):
    name: str = Field(min_length=1)
    keywords: list[str] = Field(default_factory=list)
    core_terms: list[str] = Field(default_factory=list)


class DailyReportRequest(BaseModel):
    report_date: str = ""
    industries: list[IndustryRequest] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    core_terms: list[str] = Field(default_factory=list)
    limit: int = 120


def create_app(config_path: str | None = None) -> FastAPI:
    config_file = config_path or os.environ.get("AYX_CONFIG", "config/sources.yaml")
    config = load_config(config_file)
    repo = Repository(resolve_path(config.database_path))
    pipeline = CollectionPipeline(config, repo)
    report_generator = AIReportGenerator(config, config_file_path(config_file, "analysis_prompt"))

    app = FastAPI(title="AiYX DATA INTELI", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    def root() -> HTMLResponse:
        return HTMLResponse(render_backend_config_center())

    @app.get("/api")
    def api_info() -> dict[str, Any]:
        return {
            "name": "AiYX DATA INTELI",
            "developer": "魏杰",
            "service": "api",
            "status": "running",
            "docs": "/docs",
            "health": "/health",
            "runtime_settings": "/settings/runtime",
            "frontend": os.environ.get("AYX_FRONTEND_URL", "http://127.0.0.1:15179"),
        }

    @app.get("/settings/runtime")
    def runtime_settings() -> dict[str, Any]:
        env_values = read_env_values(config_root_dir(config_file) / ".env")
        return {
            "app": {
                "name": "AiYX DATA INTELI",
                "developer": "魏杰",
                "database_path": config.database_path,
            },
            "sources": [
                {
                    "id": source.id,
                    "name": source.name,
                    "type": source.type,
                    "platform": source.platform,
                    "url": source.url,
                    "tags": source.tags,
                    "enabled": source.enabled,
                    "show_frontend": source.show_frontend,
                    "max_items": source.max_items,
                }
                for source in config.all_sources
            ],
            "report_defaults": {
                "keywords": config.report_defaults.keywords,
                "core_terms": config.report_defaults.core_terms,
                "industries": [
                    {
                        "name": industry.name,
                        "keywords": industry.keywords,
                        "core_terms": industry.core_terms,
                    }
                    for industry in config.report_defaults.industries
                ],
            },
            "ai_report": {
                "enabled": config.ai_report_enabled,
                "api_base": config.ai_report_api_base,
                "model": config.ai_report_model,
                "has_api_key": bool(config.ai_report_api_key),
                "key_hint": mask_secret(config.ai_report_api_key),
                "timeout": config.ai_report_timeout,
            },
            "ai_roles": {
                "backend": ai_role_settings(env_values, "BACKEND", config.ai_report_api_base, config.ai_report_model, config.ai_report_api_key, config.ai_report_timeout, "增长情报分析师"),
                "frontend": ai_role_settings(env_values, "FRONTEND", "", "", "", 60, "交互式情报助理"),
            },
        }

    @app.get("/settings/config")
    def settings_config() -> dict[str, Any]:
        return {
            "taxonomy": source_taxonomy(),
            "config": read_config_document(config_file),
        }

    @app.post("/settings/config")
    def save_settings_config(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
        nonlocal config, pipeline, report_generator
        raw_config = payload.get("config", payload)
        if not isinstance(raw_config, dict):
            raise HTTPException(status_code=400, detail="config must be an object")
        normalized = normalize_config_document(raw_config)
        try:
            Path(config_file).write_text(yaml.safe_dump(normalized, allow_unicode=True, sort_keys=False), encoding="utf-8")
        except OSError as exc:
            raise HTTPException(status_code=500, detail=f"failed to save config: {exc}") from exc
        config = load_config(config_file)
        pipeline = CollectionPipeline(config, repo)
        report_generator = AIReportGenerator(config, config_file_path(config_file, "analysis_prompt"))
        return {"saved": True, "taxonomy": source_taxonomy(), "runtime": runtime_settings()}

    @app.get("/config-files")
    def config_files() -> dict[str, Any]:
        return {"files": config_files_index(config_file)}

    @app.get("/api/load")
    def api_load(file: str = "config", default: bool = False) -> dict[str, Any]:
        file_key = normalize_config_file_key(file)
        path = config_file_path(config_file, file_key, default=default)
        if not path.exists():
            return {
                "success": False,
                "file": file_key,
                "label": CONFIG_FILE_MAP[file_key][0],
                "content": "",
                "exists": False,
                "default": default,
                "updated_at": "",
            }
        return {
            "success": True,
            "file": file_key,
            "label": CONFIG_FILE_MAP[file_key][0],
            "content": path.read_text(encoding="utf-8"),
            "exists": True,
            "default": default,
            "updated_at": file_mtime(path),
        }

    @app.post("/api/save")
    def api_save(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
        nonlocal config, pipeline, report_generator
        file_key = normalize_config_file_key(str(payload.get("file", "config")))
        content = payload.get("content", "")
        if not isinstance(content, str):
            raise HTTPException(status_code=400, detail="content must be a string")
        path = config_file_path(config_file, file_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        if file_key == "sources":
            config = load_config(config_file)
            pipeline = CollectionPipeline(config, repo)
            report_generator = AIReportGenerator(config, config_file_path(config_file, "analysis_prompt"))
        return {"success": True, "saved": True, "file": file_key, "updated_at": file_mtime(path)}

    @app.get("/api/profiles/list")
    def api_profiles_list() -> dict[str, Any]:
        profile_dir = config_root_dir(config_file) / "profiles"
        profile_dir.mkdir(parents=True, exist_ok=True)
        profiles = [
            {"name": path.stem, "updated_at": file_mtime(path), "size": path.stat().st_size}
            for path in sorted(profile_dir.glob("*.yaml"))
        ]
        return {"success": True, "profiles": profiles}

    @app.get("/api/profiles/load")
    def api_profiles_load(name: str) -> dict[str, Any]:
        path = profile_path(config_file, name)
        if not path.exists():
            raise HTTPException(status_code=404, detail="profile not found")
        content = path.read_text(encoding="utf-8")
        files: dict[str, str] = {}
        try:
            parsed = yaml.safe_load(content) or {}
        except yaml.YAMLError:
            parsed = {}
        if isinstance(parsed, dict):
            if isinstance(parsed.get("files"), dict):
                files = {normalize_profile_file_key(key): str(value) for key, value in parsed["files"].items()}
            else:
                for key in ["config", "sources", "frequency", "timeline", "analysis_prompt", "translation_prompt", "industry_packs", "skills"]:
                    if key in parsed and isinstance(parsed[key], str):
                        files[normalize_profile_file_key(key)] = parsed[key]
        return {"success": True, "name": path.stem, "content": content, "files": files, "updated_at": file_mtime(path)}

    @app.post("/api/profiles/save")
    def api_profiles_save(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
        name = str(payload.get("name", "")).strip()
        if not name:
            raise HTTPException(status_code=400, detail="name is required")
        content = payload.get("content")
        if content is None:
            files = payload.get("files", {})
            if not isinstance(files, dict):
                raise HTTPException(status_code=400, detail="files must be an object")
            content = yaml.safe_dump({"files": files}, allow_unicode=True, sort_keys=False)
        if not isinstance(content, str):
            raise HTTPException(status_code=400, detail="content must be a string")
        path = profile_path(config_file, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return {"success": True, "saved": True, "name": path.stem, "updated_at": file_mtime(path)}

    @app.post("/api/refresh")
    def api_refresh() -> dict[str, Any]:
        return pipeline.run_all()

    @app.post("/api/check_ai_connection")
    def api_check_ai_connection(payload: dict[str, Any] | None = Body(None)) -> dict[str, Any]:
        payload = payload or {}
        api_key = str(payload.get("api_key") or config.ai_report_api_key or "").strip()
        api_base = str(payload.get("api_base") or config.ai_report_api_base or "").strip()
        model = str(payload.get("model") or config.ai_report_model or "").strip()
        probe = probe_models(api_base, api_key, timeout=8)
        return {
            "success": bool(api_key and api_base and model and probe["success"]),
            "api_base": api_base,
            "model": model,
            "latency_ms": probe["latency_ms"],
            "message": probe["message"] if api_key and api_base and model else "缺少 API Key、API Base 或模型名称。",
        }

    @app.get("/api/get_ai_models")
    def api_get_ai_models() -> dict[str, Any]:
        return ai_models_response(config.ai_report_model, config.ai_report_api_base, config.ai_report_api_key)

    @app.post("/api/get_ai_models")
    def api_get_ai_models_post(payload: dict[str, Any] | None = Body(None)) -> dict[str, Any]:
        payload = payload or {}
        return ai_models_response(
            str(payload.get("model") or config.ai_report_model or ""),
            str(payload.get("api_base") or ""),
            str(payload.get("api_key") or config.ai_report_api_key or ""),
        )

    @app.get("/api/ai-providers")
    def api_ai_providers() -> dict[str, Any]:
        return {"success": True, **read_ai_providers(config_file)}

    @app.post("/api/ai-providers")
    def api_ai_providers_save(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
        name = str(payload.get("name", "")).strip()
        api_base = str(payload.get("api_base", "")).strip()
        models = [str(model).strip() for model in payload.get("models", []) if str(model).strip()]
        if not name or not api_base or not models:
            raise HTTPException(status_code=400, detail="name, api_base and models are required")
        data = read_ai_providers(config_file)
        providers = data["providers"]
        if any(provider["name"] == name and provider.get("api_base") != api_base for provider in providers):
            raise HTTPException(status_code=400, detail="provider name already exists")
        for provider in providers:
            if provider.get("api_base") == api_base:
                provider["name"] = provider.get("name") or name
                provider["models"] = list(dict.fromkeys([*provider.get("models", []), *models]))
                break
        else:
            providers.append({"name": name, "api_base": api_base, "models": list(dict.fromkeys(models))})
        save_ai_providers(config_file, providers)
        return {"success": True, "providers": providers}

    @app.post("/api/ai-settings")
    def api_ai_settings(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
        nonlocal config, pipeline, report_generator
        role = str(payload.get("role") or "backend").strip().lower()
        if role not in {"backend", "frontend"}:
            raise HTTPException(status_code=400, detail="role must be backend or frontend")
        api_base = str(payload.get("api_base") or "").strip()
        model = str(payload.get("model") or "").strip()
        api_key = str(payload.get("api_key") or "").strip()
        provider = str(payload.get("provider") or "").strip()
        soul = str(payload.get("soul") or "").strip() or ("增长情报分析师" if role == "backend" else "交互式情报助理")
        timeout = int(payload.get("timeout") or config.ai_report_timeout or 60)
        if not api_base or not model:
            raise HTTPException(status_code=400, detail="api_base and model are required")
        env_path = config_root_dir(config_file) / ".env"
        prefix = "AI_BACKEND" if role == "backend" else "AI_FRONTEND"
        existing = read_env_values(env_path)
        write_env_values(env_path, {
            f"{prefix}_API_KEY": api_key or existing.get(f"{prefix}_API_KEY", ""),
            f"{prefix}_API_BASE": api_base,
            f"{prefix}_MODEL": model,
            f"{prefix}_TIMEOUT": str(timeout),
            f"{prefix}_PROVIDER": provider,
            f"{prefix}_SOUL": soul,
            **({
                "AI_API_KEY": api_key or config.ai_report_api_key,
                "AI_API_BASE": api_base,
                "AI_MODEL": model,
                "AI_TIMEOUT": str(timeout),
            } if role == "backend" else {}),
        })
        os.environ[f"{prefix}_API_KEY"] = api_key or existing.get(f"{prefix}_API_KEY", "")
        os.environ[f"{prefix}_API_BASE"] = api_base
        os.environ[f"{prefix}_MODEL"] = model
        os.environ[f"{prefix}_TIMEOUT"] = str(timeout)
        if role == "backend":
            os.environ["AI_API_KEY"] = api_key or config.ai_report_api_key
            os.environ["AI_API_BASE"] = api_base
            os.environ["AI_MODEL"] = model
            os.environ["AI_TIMEOUT"] = str(timeout)
            update_sources_ai_settings(config_file, api_base, model, timeout)
            config = load_config(config_file)
            pipeline = CollectionPipeline(config, repo)
            report_generator = AIReportGenerator(config, config_file_path(config_file, "analysis_prompt"))
        return {"success": True, "saved": True, "runtime": runtime_settings()}

    def ai_models_response(selected: str, api_base: str = "", api_key: str = "") -> dict[str, Any]:
        configured = config.ai_report_model or "gpt-4.1-mini"
        providers = read_ai_providers(config_file)["providers"]
        remote_checked = bool(api_base and api_key)
        probe = probe_models(api_base, api_key, timeout=12) if remote_checked else {
            "success": False,
            "models": [],
            "latency_ms": None,
            "message": "缺少 API Key，显示本地已配置模型",
        }
        if remote_checked and probe.get("success"):
            models = list(dict.fromkeys(probe.get("models", [])))
            return {
                "success": True,
                "models": models,
                "selected": selected if selected in models else (models[0] if models else ""),
                "latency_ms": probe.get("latency_ms"),
                "message": probe.get("message", ""),
                "source": "remote",
            }
        models = [
            model
            for provider in providers
            if not api_base or provider.get("api_base") == api_base
            for model in provider.get("models", [])
        ]
        if not remote_checked:
            models = list(dict.fromkeys([selected or configured, configured, *models]))
        return {
            "success": False if remote_checked else True,
            "models": list(dict.fromkeys(models)),
            "selected": selected if selected in models else (models[0] if models else ""),
            "latency_ms": probe.get("latency_ms"),
            "message": probe.get("message", ""),
            "source": "local",
        }

    @app.get("/api/report/latest_summary")
    def api_report_latest_summary() -> dict[str, Any]:
        latest = repo.latest_articles(12)
        return {"overview": repo.overview(), "latest": latest}

    @app.get("/api/web/terminal")
    def api_web_terminal() -> dict[str, Any]:
        stats = repo.overview()
        lines = [
            "AiYX DATA INTELI backend running",
            f"config: {config_file}",
            f"sources: {len(config.all_sources)}",
            f"articles: {stats.get('articles', 0)}",
            f"high_risk: {stats.get('high_risk', 0)}",
        ]
        return {"output": "\n".join(lines)}

    @app.get("/overview")
    def overview() -> dict[str, Any]:
        return repo.overview()

    @app.get("/articles")
    def articles(limit: int = 100) -> list[dict[str, Any]]:
        return repo.latest_articles(limit)

    @app.post("/collect/run")
    def run_collection(payload: SearchTaskRequest) -> dict[str, Any]:
        job_id = repo.create_job(payload.model_dump())
        result = pipeline.run_all(keywords=[payload.query], core_terms=payload.core_terms)
        return {"job_id": job_id, **result}

    @app.post("/collect/run-all")
    def run_all() -> dict[str, Any]:
        return pipeline.run_all()

    @app.post("/reports/daily")
    def daily_report(payload: DailyReportRequest) -> dict[str, Any]:
        articles = repo.latest_articles(payload.limit)
        industries = payload.industries or [
            IndustryRequest(name=industry.name, keywords=industry.keywords, core_terms=industry.core_terms)
            for industry in config.report_defaults.industries
        ] or [IndustryRequest(name="综合市场", keywords=payload.keywords, core_terms=payload.core_terms)]
        sections = [
            build_industry_section(
                article_rows=articles,
                industry=industry,
                global_keywords=payload.keywords,
                global_core_terms=payload.core_terms,
            )
            for industry in industries
        ]
        matched_urls = {
            url
            for section in sections
            for url in section.pop("matched_urls", [])
            if url
        }
        matched_rows = [
            row
            for row in articles
            if row.get("url") in matched_urls
        ] if matched_urls else []
        total_events = len(matched_rows)
        high_risk = sum(1 for row in matched_rows if row.get("risk_level") == "high")
        negative = sum(1 for row in matched_rows if row.get("sentiment") == "negative")
        base_report = {
            "title": "大消费数据洞察分析",
            "report_date": payload.report_date or "latest",
            "executive_summary": build_executive_summary(total_events, high_risk, negative),
            "total_events": total_events,
            "high_risk": high_risk,
            "negative": negative,
            "industries": sections,
        }
        report = report_generator.generate(base_report)
        report_id = repo.save_report_run(
            report_type="daily_industry_hotspot",
            report_date=report["report_date"],
            title=report["title"],
            payload=report,
            ai_status=report["ai_status"],
            model=report.get("model", ""),
        )
        report["report_id"] = report_id
        return report

    return app


def build_industry_section(
    article_rows: list[dict[str, Any]],
    industry: IndustryRequest,
    global_keywords: list[str],
    global_core_terms: list[str],
) -> dict[str, Any]:
    industry_terms = list(dict.fromkeys(industry.keywords + [industry.name]))
    core_terms = list(dict.fromkeys(industry.core_terms + global_core_terms))
    keywords = industry_terms or global_keywords
    matched = [row for row in article_rows if row_matches(row, keywords)]
    if not matched and not industry.keywords:
        matched = article_rows
    ranked = sorted(
        matched,
        key=lambda row: (
            risk_rank(str(row.get("risk_level", ""))),
            float(row.get("heat_score") or 0),
            int(row.get("comment_count") or 0),
        ),
        reverse=True,
    )
    top_events = [event_from_row(row, core_terms) for row in ranked[:6]]
    high_risk_count = sum(1 for row in matched if row.get("risk_level") == "high")
    negative_count = sum(1 for row in matched if row.get("sentiment") == "negative")
    event_count = len(matched)
    return {
        "industry": industry.name,
        "event_count": event_count,
        "high_risk_count": high_risk_count,
        "negative_count": negative_count,
        "heat_index": round(sum(float(row.get("heat_score") or 0) for row in matched), 2),
        "summary": build_section_summary(industry.name, event_count, high_risk_count, negative_count),
        "top_events": top_events,
        "recommendations": build_recommendations(industry.name, high_risk_count, negative_count, top_events),
        "matched_urls": [row.get("url", "") for row in matched],
    }


def row_matches(row: dict[str, Any], keywords: list[str]) -> bool:
    if not keywords:
        return True
    text = f"{row.get('title', '')} {row.get('summary', '')} {row.get('platform', '')}".lower()
    return any(keyword.lower() in text for keyword in keywords if keyword.strip())


def risk_rank(risk_level: str) -> int:
    return {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(risk_level, 0)


def event_from_row(row: dict[str, Any], core_terms: list[str]) -> dict[str, Any]:
    text = f"{row.get('title', '')} {row.get('summary', '')}".lower()
    matched_terms = [term for term in core_terms if term.lower() in text]
    return {
        "title": row.get("title", ""),
        "source": row.get("platform", ""),
        "url": row.get("url", ""),
        "summary": row.get("summary", ""),
        "risk_level": normalize_risk_level(str(row.get("risk_level", "low"))),
        "sentiment": normalize_sentiment(str(row.get("sentiment", "neutral"))),
        "heat_score": float(row.get("heat_score") or 0),
        "read_count": int(row.get("read_count") or 0),
        "comment_count": int(row.get("comment_count") or 0),
        "share_count": int(row.get("share_count") or 0),
        "matched_core_terms": matched_terms,
    }


def normalize_risk_level(value: str) -> str:
    return value if value in {"low", "medium", "high", "critical"} else "low"


def normalize_sentiment(value: str) -> str:
    return value if value in {"positive", "neutral", "negative"} else "neutral"


def build_executive_summary(total_events: int, high_risk: int, negative: int) -> str:
    if total_events == 0:
        return "今日未发现符合条件的热点事件，建议扩大关键词或检查数据源。"
    if high_risk > 0:
        return f"今日共识别 {total_events} 条行业相关事件，其中 {high_risk} 条高风险、{negative} 条负面内容，需要优先复核证据与传播路径。"
    return f"今日共识别 {total_events} 条行业相关事件，整体风险可控，建议关注热度变化和用户评论中的需求信号。"


def build_section_summary(industry: str, event_count: int, high_risk: int, negative: int) -> str:
    if event_count == 0:
        return f"{industry} 暂无明显热点事件。"
    if high_risk:
        return f"{industry} 出现 {event_count} 条相关事件，其中高风险 {high_risk} 条，需纳入当日重点监控。"
    return f"{industry} 发现 {event_count} 条相关事件，负面内容 {negative} 条，可作为市场观察和内容选题依据。"


def build_recommendations(
    industry: str,
    high_risk_count: int,
    negative_count: int,
    top_events: list[dict[str, Any]],
) -> list[str]:
    if high_risk_count:
        return [
            f"对 {industry} 高风险事件建立证据包，确认原始链接、评论证据和传播指标。",
            "优先输出内部快报，明确负责人、响应口径和下一次复核时间。",
            "跟踪同类关键词在未来 24 小时内的热度变化。",
        ]
    if negative_count:
        return [
            f"复核 {industry} 负面内容的真实影响范围，区分个案反馈和趋势性问题。",
            "沉淀高频评论观点，提供给产品、客服或市场团队跟进。",
        ]
    if top_events:
        return [
            f"将 {industry} 热点事件转为内容选题、竞品观察或销售线索。",
            "保留今日高热内容进入周报候选池。",
        ]
    return ["暂不需要专项动作，保持日常监控。"]


def source_taxonomy() -> dict[str, Any]:
    return {
        "manual_tags": SOURCE_MANUAL_TAGS,
        "fixed_tags": SOURCE_FIXED_TAGS,
    }


def config_center_html() -> str:
    return """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="icon" href="data:," />
  <title>AYX Growth Intel 可视化配置中心</title>
  <style>
    :root{--ink:#172033;--muted:#68707d;--line:#e4e5e8;--paper:#fff;--canvas:#f5f3f2;--brand:#1f6bff;--dark:#0d1c32;--action:#ff5722;--green:#16825d;--risk:#b42318}
    *{box-sizing:border-box} body{margin:0;background:var(--canvas);color:var(--ink);font-family:Manrope,"Microsoft YaHei",sans-serif} button,input,select,textarea{font:inherit}
    .shell{max-width:1440px;margin:0 auto;padding:22px 28px;display:grid;gap:16px}
    .top{position:sticky;top:0;z-index:5;background:rgba(255,255,255,.94);border:1px solid var(--line);border-radius:8px;box-shadow:0 18px 50px rgba(13,28,50,.05);padding:14px 18px;display:flex;justify-content:space-between;gap:18px;align-items:center}
    .brand small{color:var(--brand);font-weight:900;letter-spacing:.06em}.brand h1{margin:2px 0 0;font-size:24px;line-height:1.15}.actions{display:flex;gap:10px;flex-wrap:wrap}
    button{border:0;border-radius:8px;min-height:40px;padding:0 14px;font-weight:850;cursor:pointer}.ghost{background:#fff;border:1px solid #d0d5dd;color:var(--dark)}.primary{background:var(--dark);color:#fff}.orange{background:var(--action);color:#fff}.green{background:var(--green);color:#fff}
    .metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.metric{background:#fff;border:1px solid var(--line);border-radius:8px;padding:14px}.metric span{display:block;color:var(--muted);font-size:12px;font-weight:800}.metric strong{font-size:28px}
    .grid{display:grid;grid-template-columns:300px minmax(0,1fr) 430px;gap:16px;align-items:start}.panel{background:#fff;border:1px solid var(--line);border-radius:8px;box-shadow:0 18px 50px rgba(13,28,50,.04);overflow:hidden}.panelHead{padding:14px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:10px;align-items:center}.panelHead h2{font-size:16px;margin:0}.panelBody{padding:14px;display:grid;gap:12px}
    .search{display:grid;gap:8px}.search input,.search select,.sourceEdit input,.sourceEdit select,.jsonBox{border:1px solid #d0d5dd;border-radius:8px;padding:10px;background:#fff;min-width:0}.sourceList{display:grid;gap:8px;max-height:62vh;overflow:auto}.sourceItem{border:1px solid var(--line);border-radius:8px;padding:10px;text-align:left;background:#fff;display:grid;gap:5px}.sourceItem.active{border-color:var(--brand);box-shadow:inset 3px 0 0 var(--brand);background:#f5f9ff}.sourceItem b{font-size:13px}.sourceItem small{color:var(--muted)}
    .chips{display:flex;gap:6px;flex-wrap:wrap}.chip{background:#eef4ff;color:#175cd3;border-radius:5px;padding:3px 7px;font-size:12px;font-weight:850}.chip.fixed{background:#fff2dc;color:#9a5b00}.chip.off{background:#f2f4f7;color:#667085}
    .sourceEdit{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.sourceEdit label{display:grid;gap:6px;color:var(--muted);font-size:12px;font-weight:850}.sourceEdit .wide{grid-column:1/-1}.tagGrid{display:flex;gap:8px;flex-wrap:wrap}.tagGrid label{display:inline-flex;gap:6px;align-items:center;border:1px solid var(--line);border-radius:999px;padding:7px 10px;color:var(--ink);font-size:12px;background:#fff}
    .jsonBox{width:100%;height:360px;font-family:Consolas,monospace;font-size:12px;line-height:1.55;resize:vertical}.status{min-height:22px;color:var(--muted);font-size:13px}.articles{display:grid;gap:8px;max-height:280px;overflow:auto}.article{border-top:1px solid var(--line);padding-top:8px}.article b{font-size:13px}.article small{display:block;color:var(--muted);margin-top:4px}
    @media(max-width:1100px){.grid{grid-template-columns:1fr}.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.top{display:grid}.sourceEdit{grid-template-columns:1fr}}
  </style>
</head>
<body>
  <main class="shell">
    <header class="top">
      <div class="brand"><small>AYX GROWTH INTEL · BACKEND CONFIG CENTER</small><h1>可视化配置中心</h1></div>
      <div class="actions">
        <button class="ghost" onclick="loadAll()">读取配置</button>
        <button class="green" onclick="saveConfig()">保存配置</button>
        <button class="orange" onclick="collectAll()">同步采集</button>
        <button class="ghost" onclick="location.href='http://127.0.0.1:15179/'">返回前端</button>
        <button class="ghost" onclick="location.href='/docs'">API Docs</button>
      </div>
    </header>
    <section class="metrics">
      <div class="metric"><span>数据源</span><strong id="mSources">-</strong></div>
      <div class="metric"><span>启用源</span><strong id="mEnabled">-</strong></div>
      <div class="metric"><span>入库内容</span><strong id="mArticles">-</strong></div>
      <div class="metric"><span>高风险</span><strong id="mRisk">-</strong></div>
    </section>
    <section class="grid">
      <aside class="panel">
        <div class="panelHead"><h2>数据源列表</h2><span id="sourceCount" class="status"></span></div>
        <div class="panelBody">
          <div class="search">
            <input id="q" placeholder="搜索源名称、ID、标签" oninput="renderSources()" />
            <select id="typeFilter" onchange="renderSources()"><option value="">全部类型</option><option value="hotlist">热榜</option><option value="rss">RSS源</option><option value="social_intel">社媒导入</option></select>
          </div>
          <div id="sourceList" class="sourceList"></div>
        </div>
      </aside>
      <section class="panel">
        <div class="panelHead"><h2>源配置与标签</h2><span id="selectedTitle" class="status">选择一个数据源</span></div>
        <div class="panelBody">
          <div id="sourceEditor" class="sourceEdit"></div>
          <div>
            <b>业务标签</b>
            <div id="tagGrid" class="tagGrid"></div>
          </div>
          <div>
            <b>最新内容预览</b>
            <div id="articlePreview" class="articles"></div>
          </div>
        </div>
      </section>
      <aside class="panel">
        <div class="panelHead"><h2>完整配置</h2><span class="status">JSON 直接编辑</span></div>
        <div class="panelBody">
          <textarea id="jsonEditor" class="jsonBox" spellcheck="false"></textarea>
          <div class="actions"><button class="ghost" onclick="applyJson()">应用到表单</button><button class="green" onclick="saveConfig()">保存配置</button></div>
          <div id="status" class="status"></div>
        </div>
      </aside>
    </section>
  </main>
  <script>
    let payload=null, config=null, runtime=null, overview=null, selectedId=null, articles=[];
    const $=id=>document.getElementById(id);
    const fixed={hotlist:'热榜',rss:'RSS源'};
    async function loadAll(){
      [payload,runtime,overview,articles]=await Promise.all([
        fetch('/settings/config').then(r=>r.json()),
        fetch('/settings/runtime').then(r=>r.json()),
        fetch('/overview').then(r=>r.json()),
        fetch('/articles?limit=80').then(r=>r.json())
      ]);
      config=payload.config; selectedId=selectedId || config.sources?.[0]?.id;
      $('jsonEditor').value=JSON.stringify(config,null,2);
      renderMetrics(); renderSources(); renderEditor(); setStatus('配置已读取');
    }
    function renderMetrics(){
      $('mSources').textContent=config.sources.length;
      $('mEnabled').textContent=config.sources.filter(s=>s.enabled).length;
      $('mArticles').textContent=overview.articles||0;
      $('mRisk').textContent=overview.high_risk||0;
    }
    function sourceTags(s){return s.tags?.length?s.tags:[s.platform].filter(Boolean)}
    function renderSources(){
      const q=$('q').value.toLowerCase(), type=$('typeFilter').value;
      const list=config.sources.filter(s=>(!type||s.type===type)&&(`${s.id} ${s.name} ${sourceTags(s).join(' ')}`.toLowerCase().includes(q)));
      $('sourceCount').textContent=list.length+' 个';
      $('sourceList').innerHTML=list.map(s=>`<button class="sourceItem ${s.id===selectedId?'active':''}" onclick="selectSource('${s.id.replaceAll(\"'\",\"\\\\'\")}')"><b>${esc(s.name)}</b><small>${esc(s.type)} · ${esc(s.id)}</small><div class="chips">${sourceTags(s).map(t=>`<span class="chip ${t===fixed[s.type]?'fixed':''}">${esc(t)}</span>`).join('')}${s.enabled?'':'<span class="chip off">停用</span>'}</div></button>`).join('');
    }
    function selectSource(id){selectedId=id;renderSources();renderEditor()}
    function renderEditor(){
      const s=config.sources.find(x=>x.id===selectedId); if(!s)return;
      $('selectedTitle').textContent=s.name;
      $('sourceEditor').innerHTML=`
        <label>名称<input value="${escAttr(s.name)}" oninput="patch('name',this.value)"></label>
        <label>ID<input value="${escAttr(s.id)}" disabled></label>
        <label>类型<select onchange="patch('type',this.value)"><option ${s.type==='hotlist'?'selected':''}>hotlist</option><option ${s.type==='rss'?'selected':''}>rss</option><option ${s.type==='social_intel'?'selected':''}>social_intel</option></select></label>
        <label>启用<select onchange="patch('enabled',this.value==='true')"><option value="true" ${s.enabled?'selected':''}>启用</option><option value="false" ${!s.enabled?'selected':''}>停用</option></select></label>
        <label>最大条数<input type="number" value="${s.max_items||50}" oninput="patch('max_items',Number(this.value)||0)"></label>
        <label>平台<input value="${escAttr(s.platform||'')}" oninput="patch('platform',this.value)"></label>
        <label class="wide">URL<input value="${escAttr(s.url||'')}" oninput="patch('url',this.value)"></label>`;
      $('tagGrid').innerHTML=payload.taxonomy.manual_tags.map(t=>`<label><input type="checkbox" ${sourceTags(s).includes(t)?'checked':''} onchange="toggleTag('${t}',this.checked)">${t}</label>`).join('');
      renderArticlePreview(s.id);
    }
    function renderArticlePreview(id){
      const rows=articles.filter(a=>a.source_id===id).slice(0,8);
      $('articlePreview').innerHTML=rows.length?rows.map(a=>`<div class="article"><b>${esc(a.title)}</b><small>${esc(a.platform||'')} · ${esc(a.published_at||a.last_seen_at||'')}</small></div>`).join(''):'<span class="status">暂无内容，保存后可同步采集。</span>';
    }
    function patch(key,value){const s=config.sources.find(x=>x.id===selectedId);s[key]=value;syncJson();renderSources()}
    function toggleTag(tag,on){const s=config.sources.find(x=>x.id===selectedId);const f=fixed[s.type];let tags=sourceTags(s).filter(t=>t!==f);tags=on?[...new Set([...tags,tag])]:tags.filter(t=>t!==tag);s.tags=f?[f,...tags]:tags;syncJson();renderSources();renderEditor()}
    function syncJson(){$('jsonEditor').value=JSON.stringify(config,null,2)}
    function applyJson(){try{config=JSON.parse($('jsonEditor').value);selectedId=config.sources?.[0]?.id;renderMetrics();renderSources();renderEditor();setStatus('JSON 已应用到表单')}catch(e){setStatus('JSON 格式错误：'+e.message,true)}}
    async function saveConfig(){try{applyJson();const r=await fetch('/settings/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({config})});if(!r.ok)throw new Error(await r.text());setStatus('已保存');await loadAll()}catch(e){setStatus('保存失败：'+e.message,true)}}
    async function collectAll(){setStatus('采集中，请稍候...');const r=await fetch('/collect/run-all',{method:'POST'});const data=await r.json();setStatus(`采集完成：${data.saved||0} 条，失败 ${data.failures?.length||0} 个`);await loadAll()}
    function setStatus(t,bad=false){$('status').textContent=t;$('status').style.color=bad?'#b42318':'#68707d'}
    function esc(v){return String(v??'').replace(/[&<>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]))}
    function escAttr(v){return esc(v).replace(/"/g,'&quot;')}
    loadAll();
  </script>
</body>
</html>
"""


def read_config_document(config_file: str) -> dict[str, Any]:
    path = Path(config_file)
    if not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return normalize_config_document(raw)


def normalize_config_document(raw: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(raw)
    sources = []
    for item in normalized.get("sources", []) or []:
        if not isinstance(item, dict):
            continue
        source = dict(item)
        source["tags"] = normalize_source_tags(source)
        sources.append(source)
    normalized["sources"] = sources
    return normalized


def normalize_source_tags(source: dict[str, Any]) -> list[str]:
    raw_tags = source.get("tags", [])
    if isinstance(raw_tags, str):
        tags = [tag.strip() for tag in raw_tags.replace("，", ",").split(",")]
    else:
        tags = [str(tag).strip() for tag in raw_tags or []]
    fixed_tag = SOURCE_FIXED_TAGS.get(str(source.get("type", "")))
    if fixed_tag:
        tags.insert(0, fixed_tag)
    manual_tags = [tag for tag in tags if tag in SOURCE_MANUAL_TAGS]
    if not manual_tags:
        tags.append("其他")
    return list(dict.fromkeys(tag for tag in tags if tag))


def config_root_dir(config_file: str) -> Path:
    return Path(config_file).resolve().parent


def normalize_config_file_key(file_key: str) -> str:
    key = file_key.strip().lower()
    aliases = {
        "config.yaml": "config",
        "sources.yaml": "sources",
        "frequency_words.txt": "frequency",
        "timeline.yaml": "timeline",
        "ai_analysis_prompt.txt": "analysis_prompt",
        "ai_translation_prompt.txt": "translation_prompt",
        "ai_models.yaml": "ai_models",
        "industry_packs.yaml": "industry_packs",
        "skills.yaml": "skills",
    }
    key = aliases.get(key, key)
    if key not in CONFIG_FILE_MAP:
        raise HTTPException(status_code=404, detail=f"unknown config file: {file_key}")
    return key


def normalize_profile_file_key(file_key: str) -> str:
    try:
        return normalize_config_file_key(file_key)
    except HTTPException:
        return file_key


def config_file_path(config_file: str, file_key: str, default: bool = False) -> Path:
    normalized = normalize_config_file_key(file_key)
    filename = CONFIG_FILE_MAP[normalized][1]
    root = config_root_dir(config_file)
    if default:
        default_path = root / "defaults" / filename
        if default_path.exists():
            return default_path
        if normalized in {"config", "sources"}:
            legacy_default = root / "defaults" / "config.yaml"
            if legacy_default.exists():
                return legacy_default
    return root / filename


def config_files_index(config_file: str) -> list[dict[str, Any]]:
    return [
        {
            "key": key,
            "label": label,
            "filename": filename,
            "exists": config_file_path(config_file, key).exists(),
            "updated_at": file_mtime(config_file_path(config_file, key)),
            "default_exists": config_file_path(config_file, key, default=True).exists(),
        }
        for key, (label, filename) in CONFIG_FILE_MAP.items()
    ]


def profile_path(config_file: str, name: str) -> Path:
    safe_name = "".join(char for char in name.strip() if char.isalnum() or char in {"-", "_", "."})
    if not safe_name:
        raise HTTPException(status_code=400, detail="invalid profile name")
    if not safe_name.endswith((".yaml", ".yml")):
        safe_name = f"{safe_name}.yaml"
    path = config_root_dir(config_file) / "profiles" / safe_name
    profile_dir = (config_root_dir(config_file) / "profiles").resolve()
    resolved = path.resolve()
    if profile_dir not in resolved.parents and resolved != profile_dir:
        raise HTTPException(status_code=400, detail="invalid profile path")
    return resolved


def file_mtime(path: Path) -> str:
    if not path.exists():
        return ""
    return __import__("datetime").datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "已设置"
    return f"{value[:4]}...{value[-4:]}"


def ai_role_settings(
    env_values: dict[str, str],
    role: str,
    default_base: str,
    default_model: str,
    default_key: str,
    default_timeout: int,
    default_soul: str,
) -> dict[str, Any]:
    api_key = env_values.get(f"AI_{role}_API_KEY") or default_key
    return {
        "provider": env_values.get(f"AI_{role}_PROVIDER") or "",
        "api_base": env_values.get(f"AI_{role}_API_BASE") or default_base,
        "model": env_values.get(f"AI_{role}_MODEL") or default_model,
        "timeout": int(env_values.get(f"AI_{role}_TIMEOUT") or default_timeout),
        "soul": env_values.get(f"AI_{role}_SOUL") or default_soul,
        "has_api_key": bool(api_key),
        "key_hint": mask_secret(api_key),
    }


def read_ai_providers(config_file: str) -> dict[str, Any]:
    path = config_file_path(config_file, "ai_models")
    if not path.exists():
        return {"providers": []}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    providers = []
    for item in raw.get("providers", []):
        if not isinstance(item, dict):
            continue
        models = list(dict.fromkeys(str(model).strip() for model in item.get("models", []) if str(model).strip()))
        if item.get("name") and item.get("api_base"):
            providers.append({"name": str(item["name"]), "api_base": str(item["api_base"]), "models": models})
    return {"providers": providers}


def save_ai_providers(config_file: str, providers: list[dict[str, Any]]) -> None:
    path = config_file_path(config_file, "ai_models")
    path.write_text(yaml.safe_dump({"providers": providers}, allow_unicode=True, sort_keys=False), encoding="utf-8")


def probe_models(api_base: str, api_key: str, timeout: int = 10) -> dict[str, Any]:
    if not api_base or not api_key:
        return {"success": False, "models": [], "latency_ms": None, "message": "缺少 API Base 或 API Key"}
    start = time.perf_counter()
    url = f"{api_base.rstrip('/')}/models"
    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=timeout)
        latency_ms = int((time.perf_counter() - start) * 1000)
        if response.status_code >= 400:
            return {"success": False, "models": [], "latency_ms": latency_ms, "message": f"连接失败：HTTP {response.status_code}"}
        data = response.json()
        rows = data.get("data") or data.get("models") or data.get("result") or data.get("items") or []
        models = []
        for item in rows if isinstance(rows, list) else []:
            if isinstance(item, str):
                models.append(item)
            elif isinstance(item, dict):
                model_id = item.get("id") or item.get("model") or item.get("name") or item.get("model_id")
                if model_id:
                    models.append(str(model_id))
        return {"success": True, "models": list(dict.fromkeys(models)), "latency_ms": latency_ms, "message": "连接成功，模型列表已读取"}
    except Exception as exc:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return {"success": False, "models": [], "latency_ms": latency_ms, "message": f"连接失败：{exc}"}


def read_env_values(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def write_env_values(path: Path, updates: dict[str, str]) -> None:
    values = read_env_values(path)
    values.update({key: value for key, value in updates.items() if value is not None})
    path.write_text("\n".join(f"{key}={value}" for key, value in values.items()) + "\n", encoding="utf-8")


def update_sources_ai_settings(config_file: str, api_base: str, model: str, timeout: int) -> None:
    path = config_file_path(config_file, "sources")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    ai_report = dict(raw.get("ai_report", {}))
    ai_report.update({
        "enabled": True,
        "api_base": api_base,
        "api_key": "",
        "model": model,
        "timeout": timeout,
    })
    raw["ai_report"] = ai_report
    path.write_text(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False), encoding="utf-8")


app = create_app(os.environ.get("AYX_CONFIG"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/sources.yaml")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8088)
    args = parser.parse_args()
    os.environ["AYX_CONFIG"] = str(Path(args.config))
    uvicorn.run(create_app(args.config), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
