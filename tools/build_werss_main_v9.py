from __future__ import annotations

import json
import uuid
import zipfile
from pathlib import Path

SOURCE = Path("n8n/WeRSS_Dify_知识库自动化主工作流_v8_实际执行修复版.json")
OUTPUT = Path("n8n/WeRSS_Dify_知识库自动化主工作流_v9_图片二进制与MD5修复完整版.json")
CANVAS = Path("n8n/WeRSS_Dify_知识库自动化主工作流_v9_画布直接粘贴版.json")
REPORT = Path("n8n/WeRSS_Dify_知识库自动化主工作流_v9_校验报告.json")
ZIP_OUTPUT = Path("n8n/WeRSS_Dify_知识库自动化主工作流_v9_完整修复包.zip")


def uid(value: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, value))


def full_response(node: dict) -> None:
    params = node.setdefault("parameters", {})
    response = (
        params.setdefault("options", {})
        .setdefault("response", {})
        .setdefault("response", {})
    )
    if response.get("responseFormat") != "file":
        response["fullResponse"] = True
        response.setdefault("neverError", True)


def validate(workflow: dict) -> dict:
    nodes = workflow.get("nodes", [])
    connections = workflow.get("connections", {})
    names = [node.get("name") for node in nodes]
    name_set = set(names)

    missing = []
    for source, mapping in connections.items():
        if source not in name_set:
            missing.append(f"missing source: {source}")
        for output_groups in mapping.values():
            for output_group in output_groups:
                for edge in output_group:
                    target = edge.get("node")
                    if target not in name_set:
                        missing.append(f"{source} -> {target}")

    http_without_full_response = []
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

    by_name = {node.get("name"): node for node in nodes}
    crypto_node = by_name.get("[031A] 计算图片MD5", {})
    merge_node = by_name.get("[031B] 合并MD5与图片二进制", {})
    image_node = by_name.get("[032] 计算MD5尺寸并过滤图片", {})
    s3_node = by_name.get("[038] 上传图片到Cloudflare R2", {})

    s3_params = s3_node.get("parameters", {})
    image_code = image_node.get("parameters", {}).get("jsCode", "")

    report = {
        "valid": True,
        "workflow_name": workflow.get("name"),
        "node_count": len(nodes),
        "connection_source_count": len(connections),
        "unique_node_names": len(names) == len(name_set),
        "missing_connection_targets": missing,
        "http_nodes_without_full_response": http_without_full_response,
        "crypto_node_type": crypto_node.get("type"),
        "crypto_output_property": crypto_node.get("parameters", {}).get("dataPropertyName"),
        "binary_restore_node_present": bool(merge_node),
        "code32_uses_require_crypto": "require('crypto')" in image_code,
        "code32_returns_empty_sentinel": "no_valid_images: true" in image_code,
        "s3_binary_upload_configured": (
            s3_params.get("binaryData") is True
            and s3_params.get("binaryPropertyName") == "data"
        ),
    }

    report["valid"] = all(
        [
            report["unique_node_names"],
            not report["missing_connection_targets"],
            not report["http_nodes_without_full_response"],
            report["crypto_node_type"] == "n8n-nodes-base.crypto",
            report["crypto_output_property"] == "image_md5",
            report["binary_restore_node_present"],
            not report["code32_uses_require_crypto"],
            report["code32_returns_empty_sentinel"],
            report["s3_binary_upload_configured"],
        ]
    )
    return report


def main() -> None:
    workflow = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    workflow["name"] = "WeRSS Dify 知识库自动化主工作流 v9 - 图片二进制与MD5修复完整版"
    workflow["active"] = False
    workflow.setdefault("settings", {})["executionOrder"] = "v1"
    workflow.setdefault("pinData", {})

    # 清除旧修复节点，确保脚本重复执行时不会生成重复节点。
    workflow["nodes"] = [
        node
        for node in workflow["nodes"]
        if node.get("name")
        not in {"[031A] 计算图片MD5", "[031B] 合并MD5与图片二进制"}
    ]

    nodes = workflow["nodes"]
    by_name = {node["name"]: node for node in nodes}

    for node in nodes:
        if node.get("type") == "n8n-nodes-base.httpRequest":
            full_response(node)

    download = by_name["[031] 批量下载图片为二进制"]
    download["parameters"]["options"] = {
        "batching": {"batch": {"batchSize": 8, "batchInterval": 1200}},
        "redirect": {"redirect": {"maxRedirects": 5}},
        "response": {"response": {"responseFormat": "file"}},
        "timeout": 120000,
    }
    download["retryOnFail"] = True
    download["maxTries"] = 5
    download["waitBetweenTries"] = 5000
    download["onError"] = "continueRegularOutput"
    download["notes"] = "必须输出 binary.data；每批8张，批次间隔1200ms。"

    crypto_node = {
        "parameters": {
            "action": "hash",
            "binaryData": True,
            "binaryPropertyName": "data",
            "type": "MD5",
            "dataPropertyName": "image_md5",
            "encoding": "hex",
        },
        "type": "n8n-nodes-base.crypto",
        "typeVersion": 2,
        "position": [480, 40],
        "id": uid("werss-main-v9-031a-image-md5"),
        "name": "[031A] 计算图片MD5",
        "notes": "内置 Crypto 读取 binary.data 计算 MD5，写入 json.image_md5。Crypto V2 不保留二进制，必须经过 [031B]。",
    }

    merge_code = r'''/**
 * [031B] 合并MD5与图片二进制
 * 模式：Run Once for All Items
 *
 * Crypto V2 对二进制执行 Hash 后不会继续输出 binary。
 * 根据 pairedItem/位置，从 [031] 恢复原始 binary.data。
 */
const hashItems = $input.all();
const downloadedItems = $('[031] 批量下载图片为二进制').all();

function pairedIndex(item, fallback) {
  const paired = item?.pairedItem;
  if (Array.isArray(paired) && paired.length) {
    const value = Number(paired[0]?.item);
    if (Number.isInteger(value)) return value;
  }
  if (paired && typeof paired === 'object') {
    const value = Number(paired.item);
    if (Number.isInteger(value)) return value;
  }
  return fallback;
}

return hashItems.map((hashItem, index) => {
  const sourceIndex = pairedIndex(hashItem, index);
  const source = downloadedItems[sourceIndex] ?? { json: {}, binary: {} };
  const imageMd5 = String(
    hashItem.json?.image_md5 ??
    hashItem.json?.data ??
    ''
  ).trim().toLowerCase();
  const binary = source.binary ?? {};

  return {
    json: {
      ...(source.json ?? {}),
      ...(hashItem.json ?? {}),
      image_md5: imageMd5,
      binary_available: Boolean(binary?.data),
      binary_property: binary?.data ? 'data' : null,
      source_item_index: sourceIndex,
    },
    binary,
    pairedItem: { item: sourceIndex },
  };
});'''

    merge_node = {
        "parameters": {
            "mode": "runOnceForAllItems",
            "jsCode": merge_code,
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [720, 40],
        "id": uid("werss-main-v9-031b-restore-binary"),
        "name": "[031B] 合并MD5与图片二进制",
        "notes": "恢复 [031] 的 binary.data，并与 [031A] 的 image_md5 合并。",
    }

    download_index = next(
        index
        for index, node in enumerate(nodes)
        if node.get("name") == "[031] 批量下载图片为二进制"
    )
    nodes[download_index + 1 : download_index + 1] = [crypto_node, merge_node]
    by_name = {node["name"]: node for node in nodes}

    image_code = r'''/**
 * [032] 计算MD5尺寸并过滤图片
 * 模式：Run Once for All Items
 *
 * 输入：json.image_md5 + binary.data。
 * 不调用 require('crypto')，兼容禁止外部模块的 n8n 2.26.8。
 */
const items = $input.all();
const cfg = $('[006] 解析目标知识库').first().json ?? {};

const MIN_FILE_BYTES = Math.max(30720, Number(cfg.minImageFileSize ?? 30720));
const MIN_WIDTH = Math.max(1, Number(cfg.minImageWidth ?? 400));
const MIN_HEIGHT = Math.max(1, Number(cfg.minImageHeight ?? 250));
const MIN_RATIO = 0.18;
const MAX_RATIO = 5.5;

const stats = {
  input: items.length,
  missing_binary: 0,
  missing_md5: 0,
  too_small_bytes: 0,
  unknown_type: 0,
  gif_filtered: 0,
  too_small_dimensions: 0,
  extreme_ratio: 0,
  duplicate_in_article: 0,
  accepted: 0,
};

function detectType(buffer, binaryMeta = {}) {
  const declared = String(binaryMeta.mimeType ?? '').toLowerCase();
  if (buffer.length >= 8 && buffer[0] === 0x89 && buffer[1] === 0x50 && buffer[2] === 0x4e && buffer[3] === 0x47) {
    return { mime: 'image/png', ext: 'png' };
  }
  if (buffer.length >= 3 && buffer[0] === 0xff && buffer[1] === 0xd8 && buffer[2] === 0xff) {
    return { mime: 'image/jpeg', ext: 'jpg' };
  }
  if (buffer.length >= 12 && buffer.subarray(0, 4).toString('ascii') === 'RIFF' && buffer.subarray(8, 12).toString('ascii') === 'WEBP') {
    return { mime: 'image/webp', ext: 'webp' };
  }
  if (buffer.length >= 6 && (buffer.subarray(0, 6).toString('ascii') === 'GIF87a' || buffer.subarray(0, 6).toString('ascii') === 'GIF89a')) {
    return { mime: 'image/gif', ext: 'gif' };
  }
  if (declared.startsWith('image/jpeg')) return { mime: 'image/jpeg', ext: 'jpg' };
  if (declared.startsWith('image/png')) return { mime: 'image/png', ext: 'png' };
  if (declared.startsWith('image/webp')) return { mime: 'image/webp', ext: 'webp' };
  if (declared.startsWith('image/gif')) return { mime: 'image/gif', ext: 'gif' };
  return { mime: declared || 'application/octet-stream', ext: 'bin' };
}

function jpegSize(buffer) {
  let offset = 2;
  while (offset + 9 < buffer.length) {
    if (buffer[offset] !== 0xff) {
      offset += 1;
      continue;
    }
    const marker = buffer[offset + 1];
    offset += 2;
    if (marker === 0xd8 || marker === 0xd9) continue;
    if (marker === 0xda) break;
    if (offset + 2 > buffer.length) break;
    const length = buffer.readUInt16BE(offset);
    if (length < 2 || offset + length > buffer.length) break;
    const isSof = (
      (marker >= 0xc0 && marker <= 0xc3) ||
      (marker >= 0xc5 && marker <= 0xc7) ||
      (marker >= 0xc9 && marker <= 0xcb) ||
      (marker >= 0xcd && marker <= 0xcf)
    );
    if (isSof && offset + 7 < buffer.length) {
      return {
        width: buffer.readUInt16BE(offset + 5),
        height: buffer.readUInt16BE(offset + 3),
      };
    }
    offset += length;
  }
  return { width: 0, height: 0 };
}

function webpSize(buffer) {
  const kind = buffer.subarray(12, 16).toString('ascii');
  try {
    if (kind === 'VP8X' && buffer.length >= 30) {
      return {
        width: 1 + buffer.readUIntLE(24, 3),
        height: 1 + buffer.readUIntLE(27, 3),
      };
    }
    if (kind === 'VP8L' && buffer.length >= 25) {
      const bits = buffer.readUInt32LE(21);
      return {
        width: (bits & 0x3fff) + 1,
        height: ((bits >> 14) & 0x3fff) + 1,
      };
    }
    if (kind === 'VP8 ' && buffer.length >= 30) {
      return {
        width: buffer.readUInt16LE(26) & 0x3fff,
        height: buffer.readUInt16LE(28) & 0x3fff,
      };
    }
  } catch {}
  return { width: 0, height: 0 };
}

function readSize(buffer, type) {
  try {
    if (type.ext === 'png' && buffer.length >= 24) {
      return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
    }
    if (type.ext === 'jpg') return jpegSize(buffer);
    if (type.ext === 'gif' && buffer.length >= 10) {
      return { width: buffer.readUInt16LE(6), height: buffer.readUInt16LE(8) };
    }
    if (type.ext === 'webp') return webpSize(buffer);
  } catch {}
  return { width: 0, height: 0 };
}

const output = [];
const seenArticleMd5 = new Set();

for (let index = 0; index < items.length; index++) {
  const item = items[index];
  const json = item.json ?? {};
  const imageMd5 = String(json.image_md5 ?? json.data ?? '').trim().toLowerCase();

  if (!/^[a-f0-9]{32}$/.test(imageMd5)) {
    stats.missing_md5 += 1;
    continue;
  }

  let buffer;
  try {
    buffer = await this.helpers.getBinaryDataBuffer(index, 'data');
  } catch {
    stats.missing_binary += 1;
    continue;
  }

  if (!Buffer.isBuffer(buffer) || buffer.length === 0) {
    stats.missing_binary += 1;
    continue;
  }

  if (buffer.length < MIN_FILE_BYTES) {
    stats.too_small_bytes += 1;
    continue;
  }

  const imageType = detectType(buffer, item.binary?.data ?? {});
  if (imageType.ext === 'gif') {
    stats.gif_filtered += 1;
    continue;
  }
  if (imageType.ext === 'bin' || !imageType.mime.startsWith('image/')) {
    stats.unknown_type += 1;
    continue;
  }

  const size = readSize(buffer, imageType);
  const width = Number(size.width || 0);
  const height = Number(size.height || 0);
  const ratio = width > 0 && height > 0 ? width / height : 0;

  if (width > 0 && height > 0 && (width < MIN_WIDTH || height < MIN_HEIGHT)) {
    stats.too_small_dimensions += 1;
    continue;
  }
  if (ratio > 0 && (ratio < MIN_RATIO || ratio > MAX_RATIO)) {
    stats.extreme_ratio += 1;
    continue;
  }

  const articleId = String(json.article_id ?? '').trim() || `unknown_${index}`;
  const dedupeKey = `${articleId}::${imageMd5}`;
  if (seenArticleMd5.has(dedupeKey)) {
    stats.duplicate_in_article += 1;
    continue;
  }
  seenArticleMd5.add(dedupeKey);

  const prefix = String(cfg.r2Md5Prefix ?? 'wx-images-md5').replace(/^\/+|\/+$/g, '');
  const publicBase = String(cfg.r2PublicBaseUrl ?? '').replace(/\/+$/, '');
  const r2Key = `${prefix}/${imageMd5.slice(0, 2)}/${imageMd5}.${imageType.ext}`;

  stats.accepted += 1;
  const outputJson = {
    ...json,
    image_md5: imageMd5,
    content_hash: imageMd5,
    file_size: buffer.length,
    mime_type: imageType.mime,
    file_extension: imageType.ext,
    width: width || null,
    height: height || null,
    aspect_ratio: ratio ? Number(ratio.toFixed(4)) : null,
    quality_score: width && height ? 0.9 : 0.7,
    image_status: 'active',
    upload_status: 'pending',
    storage: 'cloudflare_r2',
    r2_key: r2Key,
    r2_url: `${publicBase}/${r2Key}`,
    binary_available: true,
    filter_stats: stats,
  };
  delete outputJson.data;

  output.push({
    json: outputJson,
    binary: item.binary,
    pairedItem: item.pairedItem ?? { item: index },
  });
}

if (!output.length) {
  return [{
    json: {
      __empty: true,
      no_valid_images: true,
      image_status: 'filtered',
      filter_reason: 'all_images_filtered_or_binary_missing',
      filter_stats: stats,
    },
  }];
}

return output;'''

    image_node = by_name["[032] 计算MD5尺寸并过滤图片"]
    image_node["parameters"] = {
        "mode": "runOnceForAllItems",
        "jsCode": image_code,
    }
    image_node["notes"] = (
        "从 [031B] 同时读取 json.image_md5 与 binary.data；"
        "全部图片被过滤时输出 __empty 占位项，不再让工作流因零输出停止。"
    )

    s3 = by_name["[038] 上传图片到Cloudflare R2"]
    s3_params = s3.setdefault("parameters", {})
    s3_params["operation"] = "upload"
    s3_params["bucketName"] = "={{ $('[006] 解析目标知识库').first().json.r2BucketName }}"
    s3_params["binaryData"] = True
    s3_params["binaryPropertyName"] = "data"
    s3_params["fileName"] = "={{ $json.r2_key }}"
    s3_params["additionalFields"] = {}
    s3["notes"] = "必须从 binary.data 上传；不设置ACL。"

    head = by_name["[034] 检查R2对象是否存在"]
    head_response = (
        head.setdefault("parameters", {})
        .setdefault("options", {})
        .setdefault("response", {})
        .setdefault("response", {})
    )
    head_response["fullResponse"] = True
    head_response["neverError"] = True
    head_response["responseFormat"] = "text"

    positions = {
        "[031] 批量下载图片为二进制": [240, 40],
        "[031A] 计算图片MD5": [480, 40],
        "[031B] 合并MD5与图片二进制": [720, 40],
        "[032] 计算MD5尺寸并过滤图片": [960, 40],
        "[033] 是否有有效图片": [1200, 40],
        "[034] 检查R2对象是否存在": [1440, -40],
        "[035] 合并R2检查上下文": [1680, -40],
        "[036] R2对象已存在": [1920, -40],
        "[037] 准备复用R2图片": [2160, -120],
        "[038] 上传图片到Cloudflare R2": [2160, 40],
        "[039] 准备新上传R2图片": [2400, 40],
        "[040] 写入图片资产与文章关系": [2640, -40],
        "[041] 图片分支完成": [2880, -40],
    }
    by_name = {node["name"]: node for node in nodes}
    for name, position in positions.items():
        if name in by_name:
            by_name[name]["position"] = position

    connections = workflow["connections"]
    connections["[031] 批量下载图片为二进制"] = {
        "main": [[{"node": "[031A] 计算图片MD5", "type": "main", "index": 0}]]
    }
    connections["[031A] 计算图片MD5"] = {
        "main": [[{"node": "[031B] 合并MD5与图片二进制", "type": "main", "index": 0}]]
    }
    connections["[031B] 合并MD5与图片二进制"] = {
        "main": [[{"node": "[032] 计算MD5尺寸并过滤图片", "type": "main", "index": 0}]]
    }

    workflow["meta"] = {
        **workflow.get("meta", {}),
        "workflowVersion": "2026-07-30-v9-image-binary-fixed",
        "imageBinaryFix": True,
        "imageMd5Node": "n8n-nodes-base.crypto v2",
        "imageMd5OutputProperty": "image_md5",
        "imageBinaryRestoreNode": "[031B] 合并MD5与图片二进制",
        "imageEmptySentinel": True,
        "runtimeFixes": [
            "Crypto V2 hashes binary.data into json.image_md5",
            "binary.data is restored after Crypto because Crypto V2 removes processed binary",
            "image dimension and filtering node no longer uses require('crypto')",
            "JPEG, PNG and WEBP dimensions are parsed from real binary",
            "all-filtered batches return an __empty sentinel instead of zero output",
            "Cloudflare R2 upload explicitly reads binary.data",
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

    # 从磁盘重新解析，验证输出文件不是仅内存中有效。
    json.loads(OUTPUT.read_text(encoding="utf-8"))
    json.loads(CANVAS.read_text(encoding="utf-8"))

    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(OUTPUT, OUTPUT.name)
        archive.write(CANVAS, CANVAS.name)
        archive.write(REPORT, REPORT.name)

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
