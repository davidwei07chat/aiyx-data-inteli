from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

import requests
from pydantic import BaseModel, Field, ValidationError

from ayx_growth_intel.config import AppConfig


class ReportEvent(BaseModel):
    title: str = Field(description="Event title")
    source: str = Field(description="Source platform or channel")
    url: str = Field(description="Original evidence URL")
    summary: str = Field(description="Concise evidence-backed event summary")
    risk_level: Literal["low", "medium", "high", "critical"] = Field(description="Event risk level")
    sentiment: Literal["positive", "neutral", "negative"] = Field(description="Event sentiment")
    heat_score: float = Field(description="Heat score computed by the system")
    read_count: int = Field(description="Latest read count")
    comment_count: int = Field(description="Latest comment count")
    share_count: int = Field(description="Latest share count")
    matched_core_terms: list[str] = Field(description="Matched risk or strategic terms")


class IndustryReportSection(BaseModel):
    industry: str = Field(description="Industry name")
    event_count: int = Field(description="Number of matched events")
    high_risk_count: int = Field(description="Number of high or critical risk events")
    negative_count: int = Field(description="Number of negative events")
    heat_index: float = Field(description="Aggregated heat index")
    summary: str = Field(description="Executive industry summary in Chinese")
    top_events: list[ReportEvent] = Field(description="Top evidence-backed events")
    recommendations: list[str] = Field(description="Actionable recommendations for business users")


class DailyReport(BaseModel):
    title: str = Field(description="Report title")
    report_date: str = Field(description="Report date")
    executive_summary: str = Field(description="Overall executive summary in Chinese")
    total_events: int = Field(description="Total matched events")
    high_risk: int = Field(description="Total high risk events")
    negative: int = Field(description="Total negative events")
    industries: list[IndustryReportSection] = Field(description="Industry sections")
    ai_status: Literal["disabled", "generated", "fallback", "failed"] = Field(description="AI generation status")
    model: str = Field(description="Model used for report generation")


class AIReportGenerator:
    def __init__(self, config: AppConfig, analysis_prompt_path: str | Path | None = None):
        self.config = config
        self.analysis_prompt_path = Path(analysis_prompt_path) if analysis_prompt_path else None

    def generate(self, base_report: dict[str, Any]) -> dict[str, Any]:
        if not self.config.ai_report_enabled or not self.config.ai_report_api_key:
            return self._with_status(base_report, "disabled")

        try:
            generated = self._call_model(base_report)
            return generated.model_dump()
        except Exception as exc:
            fallback = self._with_status(base_report, "failed")
            fallback["ai_error"] = str(exc)
            return fallback

    def _call_model(self, base_report: dict[str, Any]) -> DailyReport:
        schema = make_strict_json_schema(DailyReport.model_json_schema())
        payload = {
            "model": self.config.ai_report_model,
            "messages": [
                {
                    "role": "system",
                    "content": self._analysis_prompt(),
                },
                {"role": "user", "content": json.dumps(compact_report_for_model(base_report), ensure_ascii=False)},
            ],
            "temperature": 0.2,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "daily_industry_intelligence_report",
                    "strict": True,
                    "schema": schema,
                },
            },
        }
        response = self._post_chat(payload)
        if response.status_code in {400, 422}:
            payload.pop("response_format", None)
            payload["messages"][0]["content"] += "\n\n只输出有效 JSON，字段必须符合日报结构，不要输出 Markdown。"
            response = self._post_chat(payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(clean_json_content(content))
        parsed["ai_status"] = "generated"
        parsed["model"] = self.config.ai_report_model
        return DailyReport.model_validate(parsed)

    def _post_chat(self, payload: dict[str, Any]) -> requests.Response:
        return requests.post(
            f"{self.config.ai_report_api_base.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.config.ai_report_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=self.config.ai_report_timeout,
        )

    def _analysis_prompt(self) -> str:
        if self.analysis_prompt_path and self.analysis_prompt_path.exists():
            return self.analysis_prompt_path.read_text(encoding="utf-8").strip()
        return (
            "你是企业级商业情报和舆情分析系统。"
            "你的任务是基于输入证据生成结构化中文日报。"
            "必须保留每个事件的原始链接，不要编造未出现的事实。"
            "输出必须符合 JSON Schema。"
        )

    def _with_status(self, base_report: dict[str, Any], status: Literal["disabled", "failed"]) -> dict[str, Any]:
        enriched = dict(base_report)
        enriched["ai_status"] = status
        enriched["model"] = self.config.ai_report_model if status != "disabled" else ""
        return self._validate_or_fallback(enriched)

    def _validate_or_fallback(self, report: dict[str, Any]) -> dict[str, Any]:
        try:
            return DailyReport.model_validate(report).model_dump()
        except ValidationError:
            normalized = {
                "title": str(report.get("title") or "大消费数据洞察分析"),
                "report_date": str(report.get("report_date") or "latest"),
                "executive_summary": str(report.get("executive_summary") or "暂无摘要。"),
                "total_events": int(report.get("total_events") or 0),
                "high_risk": int(report.get("high_risk") or 0),
                "negative": int(report.get("negative") or 0),
                "industries": report.get("industries") or [],
                "ai_status": report.get("ai_status") or "fallback",
                "model": report.get("model") or "",
            }
            return DailyReport.model_validate(normalized).model_dump()


def make_strict_json_schema(schema: dict[str, Any]) -> dict[str, Any]:
    strict_schema = json.loads(json.dumps(schema))
    _mark_objects_strict(strict_schema)
    return strict_schema


def clean_json_content(content: str) -> str:
    value = content.strip()
    if value.startswith("```"):
        value = value.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return value


def compact_report_for_model(report: dict[str, Any]) -> dict[str, Any]:
    compact = dict(report)
    compact["industries"] = []
    for section in report.get("industries", []):
        next_section = dict(section)
        next_section["summary"] = truncate_text(str(next_section.get("summary", "")), 240)
        next_section["top_events"] = [
            {
                **event,
                "title": truncate_text(str(event.get("title", "")), 160),
                "summary": truncate_text(str(event.get("summary", "")), 420),
            }
            for event in next_section.get("top_events", [])[:4]
        ]
        compact["industries"].append(next_section)
    return compact


def truncate_text(value: str, limit: int) -> str:
    return value if len(value) <= limit else f"{value[:limit]}…"


def _mark_objects_strict(node: Any) -> None:
    if isinstance(node, dict):
        if node.get("type") == "object":
            node["additionalProperties"] = False
            properties = node.get("properties", {})
            if properties:
                node["required"] = list(properties.keys())
        for value in node.values():
            _mark_objects_strict(value)
    elif isinstance(node, list):
        for item in node:
            _mark_objects_strict(item)
