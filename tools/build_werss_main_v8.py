from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("n8n/WeRSS_Dify_知识库自动化主工作流_v6_15篇批量部分成功续跑完整版.json")
OUTPUT = Path("n8n/WeRSS_Dify_知识库自动化主工作流_v8_实际执行修复版.json")
CANVAS = Path("n8n/WeRSS_Dify_知识库自动化主工作流_v8_画布粘贴版.json")
REPORT = Path("n8n/WeRSS_Dify_知识库自动化主工作流_v8_校验报告.json")


def full_response(node: dict) -> None:
    params = node.setdefault("parameters", {})
    options = params.setdefault("options", {})
    response_outer = options.setdefault("response", {})
    response = response_outer.setdefault("response", {})

    # 下载二进制文件时不要启用 fullResponse，否则会改变二进制输出结构。
    if response.get("responseFormat") == "file":
        return

    response["fullResponse"] = True
    response["neverError"] = True


def robust_status(code: str) -> str:
    old = "const status=Number(env.statusCode??env.status_code??env.error?.statusCode??0);"
    new = (
        "const hasStatus=env.statusCode!==undefined||env.status_code!==undefined||"
        "env.error?.statusCode!==undefined||env.error?.status!==undefined;"
        "const status=hasStatus?Number(env.statusCode??env.status_code??"
        "env.error?.statusCode??env.error?.status):(env.error?0:200);"
    )
    return code.replace(old, new)


def robust_rpc_status(code: str) -> str:
    old = "const status=Number(r.statusCode??r.status_code??0);"
    new = (
        "const hasStatus=r.statusCode!==undefined||r.status_code!==undefined||"
        "r.error?.statusCode!==undefined||r.error?.status!==undefined;"
        "const status=hasStatus?Number(r.statusCode??r.status_code??"
        "r.error?.statusCode??r.error?.status):(r.error?0:200);"
    )
    return code.replace(old, new)


def patch_source_updated_at(code: str) -> str:
    old = "publish_time_text:publish,publish_time_source:"
    new = (
        "publish_time_text:publish,"
        "source_updated_at_text:String(d.updated_at_text??d.updatedAtText??"
        "p.updated_at_text??p.source_updated_at_text??''),"
        "publish_time_source:"
    )
    return code.replace(old, new)


def patch_error_last_error(code: str) -> str:
    old = (
        "source_response_message:String(body.message??env.error?.message??'文章详情为空')"
        ".slice(0,1500),error_message:String(body.message??env.error?.message??"
        "`WeRSS文章详情失败 HTTP ${status||'unknown'}`).slice(0,1500)"
    )
    new = (
        "source_response_message:String(body.message??env.error?.message??'文章详情为空')"
        ".slice(0,1500),last_error:String(body.message??env.error?.message??"
        "`WeRSS文章详情失败 HTTP ${status||'unknown'}`).slice(0,1500),"
        "error_message:String(body.message??env.error?.message??"
        "`WeRSS文章详情失败 HTTP ${status||'unknown'}`).slice(0,1500)"
    )
    return code.replace(old, new)


def validate(workflow: dict) -> dict:
    nodes = workflow.get("nodes", [])
    connections = workflow.get("connections", {})
    names = [node.get("name") for node in nodes]
    name_set = set(names)

    missing_targets: list[str] = []
    for source, mapping in connections.items():
        if source not in name_set:
            missing_targets.append(f"missing source: {source}")
        for output_groups in mapping.values():
            for output_group in output_groups:
                for edge in output_group:
                    target = edge.get("node")
                    if target not in name_set:
                        missing_targets.append(f"{source} -> {target}")

    http_without_full_response: list[str] = []
    for node in nodes:
        if node.get("type") != "n8n-nodes-base.httpRequest":
            continue
        response = (
            node.get("parameters", {})
            .get("options", {})
            .get("response", {})
            .get("response", {})
        )
        if response.get("responseFormat") == "file":
            continue
        if response.get("fullResponse") is not True:
            http_without_full_response.append(node.get("name", "<unnamed>"))

    s3 = next((n for n in nodes if n.get("name") == "[038] 上传图片到Cloudflare R2"), None)
    s3_ok = bool(
        s3
        and s3.get("parameters", {}).get("binaryData") is True
        and s3.get("parameters", {}).get("binaryPropertyName") == "data"
    )

    return {
        "valid": not missing_targets and not http_without_full_response and s3_ok,
        "node_count": len(nodes),
        "connection_source_count": len(connections),
        "unique_node_names": len(name_set) == len(names),
        "missing_connection_targets": missing_targets,
        "http_nodes_without_full_response": http_without_full_response,
        "s3_binary_upload_configured": s3_ok,
    }


def main() -> None:
    workflow = json.loads(SOURCE.read_text(encoding="utf-8"))
    workflow["name"] = "WeRSS Dify 知识库自动化主工作流 v8 - 15篇批量实际执行修复版"
    workflow["active"] = False
    workflow.setdefault("settings", {})["executionOrder"] = "v1"

    nodes = {node["name"]: node for node in workflow["nodes"]}

    for node in workflow["nodes"]:
        if node.get("type") == "n8n-nodes-base.httpRequest":
            full_response(node)

    # n8n 2.26.8 的正确导出字段是 fullResponse，不是 includeResponseHeadersAndStatus。
    # 下游代码同时保留“无状态码时按成功正文处理”的兜底。
    for node_name in (
        "[016] 解析清洗正文分段与图片",
        "[023] 校验并规范实体抽取结果",
        "[046] 校验Dify提交响应",
    ):
        node = nodes[node_name]
        code = node["parameters"]["jsCode"]
        code = robust_status(code)
        if node_name == "[016] 解析清洗正文分段与图片":
            code = patch_source_updated_at(code)
            code = patch_error_last_error(code)
        node["parameters"]["jsCode"] = code

    node = nodes["[025] 检查持久化并准备补偿入队"]
    node["parameters"]["jsCode"] = robust_rpc_status(node["parameters"]["jsCode"])

    # S3 节点必须明确从 binary.data 上传。
    s3 = nodes["[038] 上传图片到Cloudflare R2"]
    s3_params = s3.setdefault("parameters", {})
    s3_params["binaryData"] = True
    s3_params["binaryPropertyName"] = "data"

    # 修复工作流说明，避免再次把它误认为状态巡检工作流。
    workflow["meta"] = {
        "workflowVersion": "2026-07-29-v8-main-runtime-fixed",
        "articleBatchSize": 15,
        "articleDetailBatchSize": 3,
        "difyExtractionBatchSize": 3,
        "imageDownloadBatchSize": 8,
        "difySubmitBatchSize": 5,
        "partialSuccessResume": True,
        "atomicArticleClaim": True,
        "sectionRetryEnabled": True,
        "imageIndependentFromEntity": True,
        "runtimeFixes": [
            "Supabase claim_wx_articles_pending_v2 ambiguity fixed in database migration",
            "HTTP Request fullResponse enabled with n8n 2.26.8 field name",
            "status-code parsing supports full response and direct body response",
            "source_updated_at_text is persisted to prevent endless re-claim",
            "Cloudflare R2 S3 node uploads binary.data",
        ],
    }

    report = validate(workflow)
    if not report["valid"]:
        raise RuntimeError(json.dumps(report, ensure_ascii=False, indent=2))

    OUTPUT.write_text(
        json.dumps(workflow, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    canvas = {
        "nodes": workflow["nodes"],
        "connections": workflow["connections"],
        "pinData": workflow.get("pinData", {}),
        "meta": workflow.get("meta", {}),
    }
    CANVAS.write_text(
        json.dumps(canvas, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
