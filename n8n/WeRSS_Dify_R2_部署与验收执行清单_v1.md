# WeRSS → Dify → Supabase → R2 部署与验收执行清单 v1

更新时间：2026-07-28

## 一、需要导入 n8n 的工作流

按以下顺序导入，导入后先保持 `Inactive`：

1. `WeRSS_Dify_重复文档安全清理工作流_v1.json`
2. `WeRSS_Dify_R2_状态一致性检查与修复_v5.json`
3. `WeRSS_Dify_知识库自动化工作流_v5_生产与章节重试状态一致性完整版.json`

`WeRSS_Dify_R2_状态一致性检查与修复_v4.json` 为历史版本，不再启用。

## 二、Credentials 对应关系

| Credential 名称 | 用途 |
|---|---|
| `Supabase Secret Key` | Supabase REST/RPC、状态和资产写入 |
| `DIFY Auth account` | Dify Dataset 文档创建、更新、删除和索引状态查询 |
| `DIFY WORKFLOW AUTH` | Dify 实体事实抽取 Workflow |
| `S3 N8N0725TOKEN` | Cloudflare R2 上传 |

不得把 API Key、Secret Key、Access Key 写入 Set 或 Code 节点。

## 三、当前生产状态

Supabase 视图：`public.kb_workflow_run_gate_v1`

当前推荐动作：

```text
run_dify_cleanup
```

原因：

```text
可安全删除的 Dify 重复文档：8
Dify processing：144
Dify 待创建/更新：6
R2 missing：0
R2 error：0
待处理文章：484
```

当前 `safe_to_run_main_workflow=false`，不要直接运行 15 篇主工作流。

## 四、严格执行顺序

### 阶段 A：清理 8 个安全重复 source 文档

运行：

```text
WeRSS Dify 重复文档安全清理工作流 v1
```

要求：

- `[C03] 清理配置.cleanupEnabled=true`
- 每次最多 20 个任务
- 只读取 `kb_dify_document_cleanup_ready_view?cleanup_ready=eq.true`
- Dify DELETE 返回 `200/202/204/404` 均视为删除完成
- 删除结果必须调用 `mark_kb_dify_document_cleanup_result_v2`

完成条件：

```sql
select * from public.kb_workflow_run_gate_v1;
```

预期：

```text
dify_cleanup_ready_count 从 8 下降为 0
```

两个 `profile_document_shared_by_multiple_entities` 暂时不会删除，因为它们必须先创建新的独立 profile 文档。

### 阶段 B：同步 144 个 processing 的真实索引状态

运行：

```text
WeRSS Dify R2 状态一致性检查与修复 v5
```

需要执行多轮，每轮最多检查 100 个 Dify 任务。

完成条件：

```sql
select * from public.kb_workflow_state_snapshot_v4;
```

目标：

```text
dify_processing_count = 0
或只剩 Dify 仍真实处于 indexing 的少量任务

dify_processing_stale_count = 0
source_synced_count > 0
profile_synced_count > 0
```

### 阶段 C：处理 6 个新的唯一 Dify 文档

当前队列：

```text
profile create：4
source create：2
```

运行主工作流前，将：

```text
articleBatchSize = 1
```

保持：

```text
sectionRetryBatchSize = 6
difyQueueBatchSize = 200
Dify Workflow HTTP batching.batchSize = 3
```

运行：

```text
WeRSS Dify 知识库自动化工作流 v5 - 15篇并发3生产与章节重试状态一致性完整版
```

这次运行既会处理 1 篇文章，也会提交 `kb_dify_sync_queue_v2` 中的 6 个任务。

完成后再次运行状态一致性检查工作流，直到 6 个新文档变成 `synced`。

### 阶段 D：删除 2 个共享旧 profile 文档

新 profile 文档成功创建并保存后：

```text
profile_document_shared_by_multiple_entities
```

对应的 2 个旧文档会自动变成 `cleanup_ready=true`。

再次运行：

```text
WeRSS Dify 重复文档安全清理工作流 v1
```

完成条件：

```text
dify_cleanup_pending_count = 0
dify_cleanup_ready_count = 0
dify_cleanup_review_count = 0
```

## 五、单篇闭环验收

执行主工作流时检查以下节点：

### 文章和章节

- `[015] 读取WeRSS文章详情`：HTTP 200，正文非空
- `[016] 解析清洗文章与独立图片`：`section_count > 0`
- `[017] 写入文章详情`：RPC 返回 `ok=true`

### Dify 抽取

- `[022] 调用Dify实体抽取Workflow`：每批 3 个
- `[023] 校验并规范Dify抽取结果`：`extraction_valid=true` 或失败进入 retry
- `[024] 持久化抽取或写入章节重试`：不能静默丢失

### 图片和 R2

- `[029] 生成文章独立图片任务`：不依赖实体数量
- `[032] 计算MD5尺寸并过滤图片`：小于 30KB、GIF、装饰图被过滤
- `[034] 检查R2对象是否存在`：已存在则复用
- `[038] 上传图片到Cloudflare R2`：只上传不存在的 MD5 对象
- `[040] 写入图片资产与文章关系`：写入 `wx_image_assets` 和 `wx_article_images`

### Dify Dataset

- `[042] 读取Dify待提交队列`：从去重后的 `kb_dify_sync_queue_v2` 读取
- `[045] 创建或更新Dify文档`：返回 `document_id` 和 `batch`
- `[047] 保存Dify提交状态`：调用 `save_kb_dify_submission_v2`

### 章节重试

- 抽取失败：进入 `wx_article_section_retry`
- 抽取成功且 Dify source/profile 均提交：调用 `finalize_and_delete_wx_article_section_retry`
- 不允许在 Dify 提交未完成时删除重试记录

## 六、图片主体关联验收

```sql
select
  entity_name,
  entity_type,
  image_name,
  image_role,
  association_basis,
  relevance_score,
  article_title,
  section_title,
  r2_url
from public.kb_entity_image_catalog_view
order by entity_name, relevance_score desc, image_index
limit 100;
```

要求：

```text
image_name 非空
r2_url 非空
association_basis 优先 exact_section
article_fallback 必须保持低数量
```

## 七、最终通过标准

```sql
select * from public.kb_workflow_run_gate_v1;
```

批量扩大到 15 篇前必须满足：

```text
dify_cleanup_ready_count = 0
dify_cleanup_review_count = 0
dify_processing_stale_count = 0
r2_missing_count = 0
r2_error_count = 0
image_audit_issue_count = 0
section_retry_active = 0 或均为正常等待退避
safe_to_run_main_workflow = true
```

然后按顺序扩大：

```text
articleBatchSize 1 → 5 → 15
```

每次扩大后都要运行一次状态一致性检查工作流并检查最终快照。
