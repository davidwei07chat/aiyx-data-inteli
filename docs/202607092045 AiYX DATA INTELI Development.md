# AiYX DATA INTELI Development

| 项目 | 内容 |
| :--- | :--- |
| 文档名称 | AiYX DATA INTELI Development |
| 文档版本 | v1.1.0 |
| 创建时间 | 2026-07-09 20:45 |
| 最近更新 | 2026-07-09 |
| 项目名称 | AiYX DATA INTELI |
| 开发人 | 魏杰 |
| 项目类型 | 企业级商业情报、舆情分析与 AI 知识库系统 |
| 文档状态 | 商业化目标规格，包含 MVP、Beta、Commercial 三阶段 |

## 1. 项目定位

AiYX DATA INTELI 是一套完整独立的企业级商业情报与舆情分析系统，面向品牌、公关、市场、增长、投研、销售和管理团队，提供多源公开信息获取、授权数据导入、舆情分析、风险预警、证据管理、报告生成和 AI 知识库调用能力。

系统目标不是临时演示工具，而是可部署、可扩展、可审计、可商业化销售的企业数据产品。

## 2. 商业化目标

### 2.1 核心客户

- 品牌与公关团队：监控负面舆情、传播风险和品牌声量。
- 市场与增长团队：发现热点趋势、用户需求、潜在线索和竞品动态。
- 投研与战略团队：跟踪公司事件、行业变化、政策信号和市场反馈。
- 产品与客服团队：聚类投诉、建议、差评、功能需求和用户痛点。
- 管理层：获取日报、周报、月报和重大事件预警。

### 2.2 付费价值

- 将分散信息转为可查询、可追溯、可报告的数据资产。
- 将摘要、评论、指标和证据统一沉淀到企业知识库。
- 支持跨平台、跨时间段、跨主题的舆情监控。
- 支持企业内部 AI 对舆情数据进行问答、报告和决策辅助。
- 支持私有化部署、SaaS 多租户和 API 数据服务三种商业形态。

### 2.3 商业化版本

| 版本 | 客户类型 | 能力范围 |
| :--- | :--- | :--- |
| Starter | 小团队、试点客户 | 单租户、基础采集、基础看板、手动报告 |
| Pro | 成长期企业 | 定时任务、风险预警、知识库同步、团队权限 |
| Enterprise | 大客户、政企客户 | 私有化、多租户、审计、SLA、定制数据源、API 开放 |

## 3. 阶段范围

### 3.1 MVP 阶段

目标：验证端到端数据闭环。

必须实现：

- 数据源配置
- RSS 信息同步
- 网页公开信息同步
- 社媒数据 JSON 导入
- 标题、摘要、作者、时间、链接、互动指标入库
- 评论证据入库
- 基础情绪和风险评分
- 基础 Web 工作台
- 本地 SQLite 存储
- Docker 启动

### 3.2 Beta 阶段

目标：具备企业试用能力。

必须实现：

- PostgreSQL / Supabase 存储
- 任务队列与后台 Worker
- 定时任务
- 任务状态机
- 报告中心
- AI 查询接口
- 知识库同步状态
- API Token
- 操作日志
- 数据保留周期

### 3.3 Commercial 阶段

目标：具备商业化交付能力。

必须实现：

- 多租户
- 用户、角色、权限
- 项目空间
- 监控对象管理
- 预警规则
- 通知渠道
- 审计日志
- 订阅与配额
- 私有化部署包
- 备份与恢复
- SLA 监控

## 4. 当前实现状态

| 能力 | 当前状态 | 阶段 | 说明 |
| :--- | :--- | :--- | :--- |
| 后端 API | 已部分实现 | MVP | 已有健康检查、总览、文章列表、采集触发 |
| SQLite 存储 | 已实现 | MVP | 支持文章、评论、指标、任务基础表 |
| RSS 信息同步 | 已实现 | MVP | 支持基础条目入库 |
| 网页公开信息同步 | 已接入骨架 | MVP | 需要补更多站点规则和错误处理 |
| 社媒数据导入 | 已接入骨架 | MVP | 当前为标准 JSON 导入模式 |
| 基础风险评分 | 已实现 | MVP | 规则评分，需要模型增强 |
| Web 工作台 | 已部分实现 | MVP | 当前为单页工作台 |
| 报告生成 | 未实现 | Beta | 文档中必须标为计划项 |
| AI 查询接口 | 未实现 | Beta | 需实现结构化查询与知识库查询 |
| Supabase | 未实现 | Beta | 需增加同步模块和迁移脚本 |
| Dify / AI 应用同步 | 未实现 | Beta | 需增加文档、分段和同步状态 |
| 权限系统 | 未实现 | Commercial | 需用户、角色、租户和 API Key |
| 多租户 | 未实现 | Commercial | 需租户隔离模型 |
| 监控告警 | 未实现 | Commercial | 需指标、日志和通知 |

## 5. 系统架构

### 5.1 总体架构

```text
数据源与授权数据
  ↓
采集任务调度
  ↓
采集 Worker
  ↓
数据标准化
  ↓
结构化数据库
  ↓
舆情分析引擎
  ↓
知识库处理引擎
  ↓
API 服务
  ↓
Web 工作台 / AI 应用 / 报告中心
```

### 5.2 生产架构

```text
Frontend
  ↓
API Gateway
  ↓
Backend API
  ↓
PostgreSQL / Supabase
  ↓
Task Queue + Worker
  ↓
Redis
  ↓
Object Storage
  ↓
Vector Store
  ↓
AI Workflow
```

### 5.3 模块边界

| 模块 | 责任 |
| :--- | :--- |
| Source Manager | 数据源、授权状态、采集频率、字段能力配置 |
| Task Scheduler | 定时任务、时间切片、任务状态、重试策略 |
| Collector Runtime | 公开信息同步、网页智能采集、授权数据导入 |
| Normalizer | 字段归一、去重、时间标准化、来源归一 |
| Storage Layer | 结构化数据、原始快照、指标快照、任务记录 |
| Analysis Engine | 情绪、风险、热度、主题、观点、异常增长 |
| Knowledge Engine | 摘要、正文、评论分块，向量化与同步 |
| Report Engine | 日报、周报、风险报告、竞品报告、事件复盘 |
| API Server | Web、外部 AI、企业系统调用接口 |
| Admin Console | 数据源、权限、配额、审计和系统配置 |

## 6. 数据采集设计

### 6.1 采集原则

- 只处理公开、授权或客户合法提供的数据。
- 默认先采集轻量字段，不默认全文采集。
- 对高风险、高热度、报告引用、AI 追问内容再补全文。
- 每条数据必须保存来源、链接、采集时间和原始快照。
- 每个数据源必须配置字段能力，避免假定所有平台都有完整指标。
- 采集失败必须记录错误、重试次数和下一次执行时间。

### 6.2 数据源类型

| 类型 | 说明 | 阶段 |
| :--- | :--- | :--- |
| RSS 信息流 | 新闻、行业动态、公开订阅源 | MVP |
| 网页公开信息 | 官网、新闻站、博客、行业网站 | MVP |
| 社媒数据导入 | 公开内容或授权数据导入 | MVP |
| 文件导入 | 企业内部材料、历史舆情、表格 | Beta |
| 授权 API | 合作方、客户、平台授权接口 | Beta |
| 企业内部系统 | CRM、客服系统、工单系统 | Commercial |

### 6.3 关键词任务

任务字段：

```text
query
keywords
core_terms
exclude_terms
platforms
source_ids
start_date
end_date
max_items
collect_comments
collect_metrics
fulltext_policy
schedule_policy
```

### 6.4 时间段策略

- 最近 24 小时
- 最近 7 天
- 最近 30 天
- 自定义时间段
- 按天切片
- 按周聚合
- 按月归档

### 6.5 正文补全策略

触发条件：

- 风险等级为 `high`
- 热度评分超过阈值
- 评论数、转发数或阅读数增长异常
- 被报告引用
- 被 AI 问答命中
- 摘要不足以判断事件性质

状态：

```text
summary_only
fulltext_pending
fulltext_ready
fulltext_failed
```

## 7. 数据模型

### 7.1 核心业务表

| 表 | 阶段 | 说明 |
| :--- | :--- | :--- |
| tenants | Commercial | 租户 |
| users | Commercial | 用户 |
| roles | Commercial | 角色 |
| permissions | Commercial | 权限 |
| projects | Beta | 项目空间 |
| watchlists | Beta | 监控对象 |
| sources | MVP | 数据源 |
| crawl_jobs | MVP | 采集任务 |
| crawl_attempts | Beta | 采集尝试记录 |
| articles | MVP | 文章、帖子、页面主表 |
| comments | MVP | 评论与二级评论 |
| authors | Beta | 作者和账号 |
| metrics | MVP | 指标快照 |
| analysis_results | Beta | 分析结果 |
| alerts | Commercial | 预警事件 |
| report_runs | Beta | 报告生成记录 |
| content_chunks | MVP | 知识库分块 |
| knowledge_sync_jobs | Beta | 知识库同步任务 |
| api_keys | Commercial | API 调用密钥 |
| audit_logs | Commercial | 审计日志 |
| data_retention_policies | Commercial | 数据保留策略 |

### 7.2 articles

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| id | bigint | 是 | 主键 |
| tenant_id | uuid | Commercial | 租户 ID |
| project_id | uuid | Beta | 项目 ID |
| source_id | text | 是 | 来源 ID |
| platform | text | 是 | 平台 |
| title | text | 是 | 标题 |
| url | text | 是 | 链接，唯一去重主键之一 |
| summary | text | 否 | 摘要 |
| author_id | bigint | Beta | 作者 ID |
| author | text | 否 | 作者显示名 |
| published_at | timestamp | 否 | 发布时间 |
| content_status | text | 是 | 正文状态 |
| sentiment | text | 是 | 情绪 |
| risk_level | text | 是 | 风险等级 |
| heat_score | numeric | 是 | 热度评分 |
| matched_keywords | jsonb | 否 | 命中关键词 |
| matched_core_terms | jsonb | 否 | 命中核心词 |
| raw_json | jsonb | 否 | 原始数据 |
| first_seen_at | timestamp | 是 | 首次发现 |
| last_seen_at | timestamp | 是 | 最近发现 |

### 7.3 crawl_jobs

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| id | bigint | 主键 |
| tenant_id | uuid | 租户 |
| project_id | uuid | 项目 |
| query | text | 主查询词 |
| keywords | jsonb | 关键词 |
| core_terms | jsonb | 核心词 |
| exclude_terms | jsonb | 排除词 |
| platforms | jsonb | 平台 |
| start_date | date | 开始日期 |
| end_date | date | 结束日期 |
| status | text | pending / queued / running / succeeded / failed / retrying / canceled |
| attempts | integer | 已尝试次数 |
| max_attempts | integer | 最大尝试次数 |
| last_error | text | 最近错误 |
| next_run_at | timestamp | 下次执行 |
| result_count | integer | 结果数量 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 7.4 content_chunks

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| id | bigint | 主键 |
| tenant_id | uuid | 租户 |
| article_id | bigint | 内容 ID |
| chunk_index | integer | 分块序号 |
| content | text | 分块内容 |
| metadata | jsonb | 元数据 |
| embedding | vector | 向量 |
| embedding_model | text | 模型名称 |
| embedding_status | text | pending / ready / failed |
| sync_status | text | pending / synced / failed |
| created_at | timestamp | 创建时间 |

## 8. Supabase 与 AI 应用集成

### 8.0 AI 报告生成链路

每日行业热点报告采用“规则候选 + AI 结构化增强 + 安全降级”的链路。

流程：

```text
行业配置
  ↓
关键词与核心词匹配
  ↓
证据事件排序
  ↓
规则版候选报告
  ↓
AI 结构化日报生成
  ↓
Pydantic 校验
  ↓
保存 report_runs
  ↓
前端渲染
```

运行状态：

| 状态 | 说明 |
| :--- | :--- |
| disabled | 未配置模型或 API Key，使用规则版报告 |
| generated | AI 已生成并通过结构化校验 |
| failed | AI 调用失败，自动回退规则版报告 |
| fallback | AI 输出未通过校验，自动回退安全报告 |

配置项：

```yaml
ai_report:
  enabled: false
  api_base: https://api.openai.com/v1
  api_key: ""
  model: gpt-4.1-mini
  timeout: 60
```

要求：

- AI 输出必须是 JSON 结构化结果。
- AI 不允许编造证据，必须保留原始链接。
- AI 失败不能影响日报生成，必须安全降级。
- 每次生成必须写入 `report_runs`。
- 前端必须显示当前报告是 AI 生成、规则版还是降级版。

### 8.1 Supabase 定位

Supabase 作为生产级数据中台，负责：

- PostgreSQL 结构化数据
- JSONB 原始快照
- pgvector 知识库向量
- Row Level Security
- API Key 管理
- 文件存储
- 后续实时订阅能力

### 8.2 同步策略

```text
采集结果
  ↓
标准化
  ↓
本地或生产数据库
  ↓
知识分块
  ↓
向量生成
  ↓
Supabase pgvector
  ↓
AI 应用知识库同步
```

### 8.3 AI 应用同步

同步对象：

- 高风险文章摘要
- 高热度文章摘要
- 报告引用内容
- 评论观点摘要
- 高赞评论
- 正文分块

同步状态：

```text
pending
syncing
synced
failed
disabled
```

必须保存：

- 外部知识库 ID
- 外部文档 ID
- 外部分段 ID
- 同步时间
- 同步错误

## 9. 舆情分析设计

### 9.0 行业热点日报

AiYX DATA INTELI 必须支持按行业和指定关键词生成每日热点事件总结分析报告。该能力是 Consumer Market Radar 类场景的核心商业功能，但在本系统中采用全新的专业咨询报告型 UI 与交互结构。

输入项：

- 行业名称
- 行业关键词
- 行业核心词
- 全局关键词
- 全局风险词
- 报告日期
- 数据源范围

输出项：

- 每日执行摘要
- 行业分组热点事件
- 高风险事件数量
- 负面内容数量
- 行业热度指数
- 热点事件证据链接
- 评论与互动指标
- 行动建议

验收标准：

- 至少支持 3 个行业并行生成报告。
- 支持每个行业配置独立关键词和核心词。
- 报告中的每个热点事件必须保留原始链接。
- 页面风格必须是专业咨询报告型，不复用旧版 Consumer Market Radar 页面风格。
- UI 以蓝白、数据表格、报告分区、行动建议为主，避免营销化和娱乐化表达。

### 9.1 分析维度

- 情绪倾向：positive / neutral / negative
- 风险等级：low / medium / high / critical
- 热度评分：阅读、点赞、评论、转发和增长速度
- 主题标签：品牌、产品、竞品、价格、质量、服务、政策
- 观点聚类：相似评论与重复观点
- 传播趋势：时间序列变化
- 异常检测：短时间快速增长、负面集中爆发

### 9.2 风险等级

| 等级 | 条件 | 动作 |
| :--- | :--- | :--- |
| low | 普通信息或弱相关内容 | 入库观察 |
| medium | 命中核心词或轻度负面 | 加入关注列表 |
| high | 负面 + 高热度或多平台传播 | 触发预警 |
| critical | 高风险事件持续扩散 | 推送通知并生成专项报告 |

## 10. Web 页面设计

### 10.1 页面地图

```text
AiYX DATA INTELI
├── Dashboard
├── Collection Tasks
├── Intelligence Feed
├── Risk Radar
├── Evidence Center
├── Reports
├── Knowledge Base
├── Sources
├── Alerts
├── Team & Roles
├── API Keys
└── Settings
```

### 10.2 Dashboard

必须包含：

- 今日新增
- 高风险数量
- 负面内容数量
- 平台分布
- 风险趋势
- 情绪趋势
- 热度增长榜
- 最新预警

### 10.3 Collection Tasks

必须包含：

- 任务创建
- 关键词、核心词、排除词
- 平台选择
- 时间范围
- 采集频率
- 评论开关
- 正文策略
- 任务状态
- 失败原因
- 手动重试

### 10.4 Intelligence Feed

必须包含：

- 内容列表
- 平台过滤
- 风险过滤
- 情绪过滤
- 时间过滤
- 热度排序
- 关键词命中
- 评论证据
- 原文链接

### 10.5 Risk Radar

必须包含：

- 风险事件聚合
- 风险等级变化
- 负面关键词
- 传播趋势
- 高风险评论
- 处置建议

### 10.6 Evidence Center

必须包含：

- 原始链接
- 采集快照
- 摘要
- 评论证据
- 指标快照
- AI 分析依据
- 报告引用状态
- 证据导出

### 10.7 Reports

必须包含：

- 日报
- 周报
- 月报
- 品牌风险报告
- 竞品动态报告
- 产品反馈报告
- 事件复盘报告
- PDF / HTML / Markdown 导出

### 10.8 Knowledge Base

必须包含：

- 入库内容
- 分块预览
- 元数据过滤
- 同步状态
- 启用 / 禁用
- 重试同步
- 外部 AI 应用映射

## 11. API 契约

### 11.1 已实现 API

```text
GET /health
GET /overview
GET /articles?limit=100
POST /collect/run
POST /collect/run-all
```

### 11.2 Beta 必须补充 API

```text
GET /sources
POST /sources
PATCH /sources/{id}

GET /jobs
POST /jobs
GET /jobs/{id}
POST /jobs/{id}/retry
POST /jobs/{id}/cancel

GET /articles/{id}
POST /articles/{id}/fetch-fulltext

GET /comments?article_id={id}
GET /metrics?article_id={id}

POST /reports/generate
POST /reports/daily
GET /reports
GET /reports/{id}

POST /knowledge/sync
GET /knowledge/chunks
POST /knowledge/chunks/{id}/disable

POST /ai/query
```

### 11.3 错误格式

```json
{
  "error": {
    "code": "JOB_FAILED",
    "message": "采集任务执行失败",
    "details": {
      "source_id": "source id",
      "reason": "具体错误"
    }
  }
}
```

## 12. 权限与多租户

### 12.1 租户隔离

所有生产数据表必须包含 `tenant_id`，所有 API 查询必须按租户隔离。Supabase 部署时必须启用 Row Level Security。

### 12.2 角色

| 角色 | 权限 |
| :--- | :--- |
| Owner | 全部权限、计费、删除租户 |
| Admin | 数据源、任务、用户、报告、知识库 |
| Analyst | 查看数据、生成报告、管理分析结果 |
| Viewer | 查看看板和报告 |
| API Client | 调用指定接口 |

### 12.3 审计事件

必须记录：

- 登录
- 创建数据源
- 创建任务
- 修改权限
- 生成报告
- 导出证据
- 删除数据
- 同步知识库
- API Key 创建和撤销

## 13. 安全与合规

### 13.1 合规原则

- 只处理公开、授权或客户合法提供的数据。
- 不提供规避访问限制的能力。
- 评论和用户信息默认做最小化保存。
- 支持脱敏、删除、保留周期和审计。
- 对外报告保留证据链接和来源。

### 13.2 脱敏字段

建议处理：

- 手机号
- 邮箱
- 身份证号
- 详细地址
- 账号唯一标识
- 个人头像链接

### 13.3 数据保留

| 数据 | 默认保留 |
| :--- | :--- |
| 原始快照 | 90 天 |
| 摘要和指标 | 365 天 |
| 评论证据 | 180 天 |
| 审计日志 | 730 天 |
| 报告 | 永久或按客户配置 |

## 14. 部署与运维

### 14.1 Docker 单机

适合 MVP、试点、演示。

组件：

- frontend
- backend
- database
- worker
- redis

### 14.2 云部署

适合 Pro 版本。

组件：

- 托管 PostgreSQL / Supabase
- 对象存储
- Redis
- 后端服务
- 前端静态托管
- 日志与监控

### 14.3 私有化部署

适合 Enterprise。

必须提供：

- 离线部署文档
- 环境变量模板
- 数据库迁移脚本
- 备份恢复脚本
- 健康检查
- 版本升级说明

## 15. 报告生成

### 15.1 报告类型

- 每日舆情简报
- 每周趋势报告
- 每月品牌报告
- 竞品动态报告
- 产品反馈报告
- 重大事件复盘

### 15.2 报告结构

```text
1. 本期摘要
2. 核心发现
3. 关键风险
4. 热点事件
5. 平台分布
6. 情绪变化
7. 重点评论
8. 竞品动态
9. 建议动作
10. 证据链接
```

### 15.3 报告验收

- 每个结论必须有证据链接。
- 每个风险必须有风险等级。
- 每个建议必须对应具体内容或指标。
- 导出格式至少支持 HTML 和 Markdown，PDF 作为 Beta 后能力。

## 16. 开发约束

- 产品名称统一使用 `AiYX DATA INTELI`。
- 开发人统一写 `魏杰`。
- 产品文案和代码命名使用商业化中性表达。
- 不在文档、页面、配置和代码中暴露底层采集工具名称。
- 所有新增页面必须按完整商业化系统设计，不做临时演示页。
- 所有新增后端能力必须考虑权限、日志、错误、测试和部署。
- 不影响旧系统任何文件、功能和运行状态。

## 17. 验收标准

### 17.1 MVP 验收

- `python -m pytest` 通过。
- `npm run build` 通过。
- `GET /health` 返回正常。
- 可创建关键词采集任务。
- 可入库文章、摘要、指标、评论。
- 可在 Web 工作台查看总览和内容列表。

### 17.2 Beta 验收

- PostgreSQL / Supabase 迁移通过。
- 任务队列和 Worker 可运行。
- 任务状态可追踪。
- 报告可生成。
- 知识库同步可追踪。
- API Token 可鉴权。

### 17.3 Commercial 验收

- 多租户隔离通过。
- 权限控制通过。
- 审计日志完整。
- 备份恢复验证通过。
- 私有化部署文档完整。
- 监控告警可用。
- 数据合规策略可配置。

## 18. 访问路径

| 服务 | 地址 |
| :--- | :--- |
| Web 工作台 | http://127.0.0.1:5179 |
| API 服务 | http://127.0.0.1:8088 |
| 健康检查 | http://127.0.0.1:8088/health |
| 内容接口 | http://127.0.0.1:8088/articles |
| 总览接口 | http://127.0.0.1:8088/overview |

## 19. 迭代历史

| 版本 | 日期 | 开发人 | 内容 |
| :--- | :--- | :--- | :--- |
| v1.1.0 | 2026-07-09 | 魏杰 | 按完整商业化系统目标补充当前状态、阶段范围、数据模型、Supabase、AI 应用同步、多租户、权限、安全合规、API 契约和验收标准。 |
| v1.0.0 | 2026-07-09 | 魏杰 | 创建 AiYX DATA INTELI 独立新版系统开发文档。 |
