# AYX Growth Intel Commercial Upgrade Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 AYX Growth Intel 从“可部署的品牌增长情报原型”升级为“可试用、可演示、可持续迭代的品牌增长工作台”。

**Architecture:** 先补工程治理和可信报告基础，再升级报告页、配置中心和行动闭环。核心后端继续使用 Python 包 `aiyxdata_tradar`，Web 服务继续使用 `docker/server.py`，静态前端继续从 `docs/` 构建并由容器同步到 `output/`。

**Tech Stack:** Python 3.10、FastMCP、SQLite、PyYAML、LiteLLM、Docker Compose、React、TypeScript、Vite、Tailwind CSS、ECharts、原生 HTML/CSS/JavaScript、Font Awesome、pytest、ruff。专业情报终端新增数据图表统一使用 ECharts。

> **2026-06-23 执行说明：** 本文档原计划面向“品牌增长情报工作台”升级。根据最新统一产品需求文档《AYX 营销增长评估与风险雷达 Agent 产品需求文档》，当前执行重心升级为：在已有数据采集、React 驾驶舱、事件舆情 Agent 和证据链基础上，落地“专业情报终端、品牌舆情与风险雷达、客户线索雷达、购买阻力分析、内容命中率评估、营销避雷预检、竞品转化差距、AI/GEO 风险评估、国产多模型路由、项目级对话记忆和行动复盘闭环”。旧计划作为工程历史参考，新开发以本节为准。

---

## 0A. 统一 PRD 当前执行版开发计划

### 0A.1 当前开发状态判断

当前项目已经具备以下基础：

- Python 采集与报告底座：`aiyxdata_tradar/`、`docker/server.py`、`output/`。
- React 前端工作台：`web/src/App.tsx`、`web/src/routes/`、`web/src/components/`。
- 事件舆情 Agent 雏形：`web/src/routes/EventAgentPage.tsx`、`aiyxdata_tradar/event_agent/service.py`、`output/event_agent/event_agent.db`。
- 证据链展示雏形：`web/src/components/evidence/EvidenceDrawer.tsx`、`web/src/routes/ReportPage.tsx`。
- 行动台雏形：`web/src/routes/ActionBoardPage.tsx`、`web/src/lib/useActionBoard.ts`。
- 配置中心和 AI 模型配置基础：`web/src/routes/SettingsPage.tsx`、`config/config.yaml`、`.env` 注入。

当前主要缺口：

- 缺少独立一级模块 `品牌舆情与风险雷达`，尚无 `/#/brand-risk-radar` 页面。
- 客户线索、购买阻力、内容命中率、营销避雷、竞品转化差距仍未形成独立 API、数据对象和页面闭环。
- AI/GEO 风险评估仍停留在 PRD，尚无 `/api/geo-risk/*` 和前端页面。
- 国产多模型路由、项目级对话记忆、二模型复核、自我提升闭环尚未实现。
- 主驾驶舱开发环境仍大量使用 mock 数据，需要逐步切换到真实服务返回。

### 0A.2 总体目标

在 6-8 周内，将 AYX Growth Intel 从“可演示情报驾驶舱”升级为“可销售的营销增长评估与风险雷达 Agent MVP”。

最终最小可卖闭环：

```text
创建品牌项目
→ 配置品牌、竞品、关键词、数据源
→ 数据采集与证据标准化
→ 品牌舆情与风险雷达日常监控
→ 发现风险后升级事件舆情专项报告
→ 同步输出客户线索、购买阻力、内容命中率、营销避雷和竞品转化差距
→ 报告中心生成老板版/市场版/销售版/客户外发版
→ 行动台分配建议
→ 复盘采纳结果和业务指标
→ 模型、标签和评分权重持续校准
```

### 0A.3 技术执行原则

- **不推倒重来**：沿用 React + TypeScript + Vite 前端，沿用 `docker/server.py` 轻量 API，沿用 SQLite 作为 MVP 存储。
- **先真实闭环，再高级智能**：先完成可采集、可分析、可展示、可复盘，再做模型路由和记忆。
- **证据链优先**：所有强结论必须绑定 `EvidenceItem`，无证据不进入正式报告。
- **模块独立，服务复用**：各模块前端独立页面，后端复用统一证据、项目、报告、行动、模型服务。
- **PRD 数据维度可验收**：每个模块的页面和 API 都要覆盖 PRD 中列出的关键数据维度。
- **国产模型优先，但模型可替换**：默认 Qwen，深度推理可接 DeepSeek，长期通过 Model Router 切换。

### 0A.4 目标信息架构

前端目标路由：

```text
/
├── 总览 DashboardPage
├── /intelligence-terminal   专业情报终端，正式入口，兼容 /legacy-screen
├── /brand-risk-radar        品牌舆情与风险雷达，内含事件专项分析工作区
├── /lead-radar              客户线索雷达
├── /purchase-barriers       购买阻力分析
├── /content-hit-score       内容命中率评估
├── /marketing-risk-check    营销避雷预检
├── /competitors             竞品转化差距
├── /geo-risk                AI/GEO 风险评估
├── /reports                 报告中心
├── /actions                 行动台
├── /reviews                 复盘追踪
└── /settings                配置中心
```

后端目标 API：

```text
项目与配置
GET  /api/projects
POST /api/projects
GET  /api/projects/{projectId}
POST /api/projects/{projectId}/data-sources

证据与数据源
POST /api/evidence/import
GET  /api/evidence/search
GET  /api/data-sources/health

增长分析
POST /api/growth/lead-signals
POST /api/growth/purchase-barriers
POST /api/growth/content-hit-score
POST /api/growth/marketing-risk-check

竞品与舆情
POST /api/competitors/conversion-gap
GET  /api/brand-risk-radar/dashboard
POST /api/brand-risk-radar/alerts/{alertId}/promote-event-task
POST /api/event-agent/tasks
GET  /api/event-agent/tasks/{taskId}/dashboard

AI/GEO
POST /api/geo-risk/reports
GET  /api/geo-risk/reports/{reportId}

模型与记忆
POST /api/model-router/run
GET  /api/model-router/runs/{runId}
GET  /api/memory/project/{projectId}
POST /api/memory/project/{projectId}
DELETE /api/memory/project/{projectId}

报告与行动
GET  /api/reports
GET  /api/reports/{reportId}
POST /api/reports/{reportId}/export
GET  /api/actions
POST /api/actions
POST /api/actions/{actionId}/review
```

### 0A.5 数据模型落地

MVP 阶段建议新增统一 SQLite 数据库：

```text
output/ayx_growth_intel.db
```

保留现有：

```text
output/event_agent/event_agent.db
```

过渡策略：

- 阶段 1 保留事件 Agent 现有数据库。
- 阶段 2 新增统一数据库并逐步把项目、证据、报告、行动、模型调用、记忆迁入。
- 阶段 3 将事件 Agent 数据迁移到统一库或通过视图聚合。

核心表：

```text
brand_projects
├── id
├── brand_name
├── aliases_json
├── competitors_json
├── industry
├── created_at
└── updated_at

evidence_items
├── id
├── project_id
├── source_platform
├── source_type
├── title
├── content
├── url
├── author
├── published_at
├── collected_at
├── interaction_count
├── sentiment
├── confidence
├── tags_json
└── raw_json

lead_signals
purchase_barriers
content_hit_scores
marketing_risk_checks
competitor_conversion_gaps
brand_risk_signals
brand_risk_alerts
geo_risk_reports
reports
action_items
review_records
model_runs
project_memories
data_source_health
```

### 0A.6 里程碑与任务拆解

#### 阶段 0：工程基线和真实状态锁定，2-3 天

目标：保证后续开发不会在不稳定基础上叠功能。

任务：

1. 固化当前可运行状态。
   - 检查：`web/package.json`、`docker/server.py`、`aiyxdata_tradar/event_agent/service.py`。
   - 命令：
     ```powershell
     cd web
     npm run typecheck
     cd ..
     python -m py_compile docker/server.py aiyxdata_tradar/event_agent/service.py
     ```
   - 验收：前端 typecheck 通过，关键 Python 文件编译通过。

2. 建立开发状态文档区块。
   - 修改：本文档。
   - 内容：当前已完成、进行中、未开始、风险。
   - 验收：团队能按本文档判断下一步优先级。

3. 建立模块状态矩阵。
   - 修改：本文档 `0A.11 模块状态矩阵`。
   - 验收：每个 PRD 模块都有开发状态和下一步动作。

#### 阶段 1：品牌舆情与风险雷达一级模块，5-7 天

目标：先落地最能体现“风险雷达”的一级页面，形成新 PRD 的产品门面。

新增/修改文件：

```text
web/src/routes/BrandRiskRadarPage.tsx
web/src/types/brandRisk.ts
web/src/lib/brandRiskApi.ts
web/src/App.tsx
web/src/components/layout/AppShell.tsx
aiyxdata_tradar/brand_risk/service.py
aiyxdata_tradar/brand_risk/__init__.py
docker/server.py
```

页面必须展示：

- 风险总览：风险分、风险等级、今日新增风险、待处理预警。
- 声量趋势：总声量、负面声量、声量增速、异常峰值。
- 情绪结构：正负中占比，愤怒、嘲讽、失望、焦虑等情绪。
- 平台扩散：小红书、微博、抖音、今日头条、RSS/新闻、自定义源。
- 传播路径：首发节点、扩散节点、媒体节点、KOL/KOC 节点。
- 议题热力：议题 × 平台矩阵。
- 关键节点：账号影响力、互动量、负面强度。
- 商业影响：关联产品、门店、价格、销售阻力、潜在损失等级。
- 预警记录：触发阈值、触发原因、状态、负责人、升级按钮。
- 证据链：原文、链接、时间、平台、互动量、置信度。

API：

```text
GET /api/brand-risk-radar/dashboard?projectId=demo
POST /api/brand-risk-radar/alerts/{alertId}/ack
POST /api/brand-risk-radar/alerts/{alertId}/promote-event-task
```

验收：

- 导航出现“品牌舆情与风险雷达”。
- `/#/brand-risk-radar` 可独立访问。
- 页面不依赖纯 mock，至少能读取现有 `event_agent` 或 `output` 中的真实/半真实证据生成 dashboard。
- 点击预警可以升级到事件 Agent 任务。
- 页面具备证据下钻。

#### 阶段 2：统一证据层和项目层，5-7 天

目标：把现有报告、事件 Agent、未来增长模块统一到同一套证据和项目对象，避免每个模块各写一套数据。

新增/修改文件：

```text
aiyxdata_tradar/workspace/project_service.py
aiyxdata_tradar/evidence/service.py
aiyxdata_tradar/evidence/schema.py
aiyxdata_tradar/storage/growth_schema.sql
docker/server.py
web/src/types/project.ts
web/src/types/evidence.ts
web/src/lib/projectApi.ts
web/src/lib/evidenceApi.ts
```

任务：

1. 新增 `BrandProject` 存储。
2. 新增 `EvidenceItem` 标准化对象。
3. 将事件 Agent 证据映射成统一 `EvidenceItem`。
4. 增加数据源健康状态。
5. 前端配置中心展示项目、品牌、竞品、数据源健康。

验收：

- 用户可以创建品牌项目。
- 用户可以添加品牌、竞品、关键词和数据源。
- 系统可以搜索项目证据。
- 每条证据包含来源、时间、平台、置信度、标签。
- 数据源健康页能展示最近采集时间、样本数、失败状态。

#### 阶段 3：客户线索雷达和购买阻力分析，7-10 天

目标：优先落地最直接影响销售和商业化付费的两个模块。

新增/修改文件：

```text
web/src/routes/LeadRadarPage.tsx
web/src/routes/PurchaseBarrierPage.tsx
web/src/types/growth.ts
web/src/lib/growthApi.ts
aiyxdata_tradar/growth/lead_signals.py
aiyxdata_tradar/growth/purchase_barriers.py
aiyxdata_tradar/growth/__init__.py
docker/server.py
```

客户线索雷达必须展示：

- 需求强度。
- 需求类型。
- 人群画像。
- 痛点主题。
- 平台来源。
- 用户原话证据。
- 线索价值分。
- 推荐销售话术。
- 推荐内容选题。

购买阻力分析必须展示：

- 阻力分类。
- 阻力强度。
- 情绪类型。
- 决策阶段。
- 原因归因。
- 竞品关联。
- 修复建议。
- 销售异议处理话术。

API：

```text
POST /api/growth/lead-signals
POST /api/growth/purchase-barriers
```

验收：

- 两个页面可独立访问。
- 每个线索主题至少绑定 3 条证据，不足则标低置信度。
- “价格贵”必须区分绝对贵和价值解释不足。
- 可以将线索或阻力建议转成行动台任务。

#### 阶段 4：内容命中率和营销避雷预检，7-10 天

目标：形成“发布前评估”能力，这是品牌方、代运营、营销评估公司最容易理解和付费的服务。

新增/修改文件：

```text
web/src/routes/ContentHitScorePage.tsx
web/src/routes/MarketingRiskCheckPage.tsx
aiyxdata_tradar/growth/content_hit_score.py
aiyxdata_tradar/growth/marketing_risk_check.py
docker/server.py
```

内容命中率必须展示：

- 用户痛点匹配。
- 购买意图匹配。
- 平台语境。
- 表达清晰度。
- 转化潜力。
- 风险因素。
- 发布后验证指标。

营销避雷必须展示：

- 表达风险。
- 价值观风险。
- 舆情联想。
- 平台风险。
- 人群风险。
- 传播风险。
- 替代方案。
- 发布决策：可发、修改后可发、建议延迟、建议取消。

API：

```text
POST /api/growth/content-hit-score
POST /api/growth/marketing-risk-check
```

验收：

- 用户输入标题、脚本、广告语或活动方案后能得到评分。
- 每个扣分点必须说明原因和修改建议。
- 高风险建议必须展示相似证据或规则依据。
- 可以生成客户外发版“发布前审核报告”。

#### 阶段 5：竞品转化差距升级，5-7 天

目标：把现有“竞品战情”升级为“竞品为什么赢，我们怎么反打”。

修改文件：

```text
web/src/routes/CompetitorPage.tsx
web/src/types/growth.ts
web/src/lib/growthApi.ts
aiyxdata_tradar/growth/competitor_gap.py
docker/server.py
```

必须展示：

- 竞品动作。
- 赢点识别。
- 用户选择理由。
- 竞品短板。
- 内容缺口。
- 迁移机会。
- 反打建议。
- 竞品赢点 vs 我方缺口矩阵。

API：

```text
POST /api/competitors/conversion-gap
```

验收：

- 销售团队可以拿到竞品异议反打话术。
- 内容团队可以拿到我方缺失选题。
- 竞品短板必须绑定用户差评或负面证据。

#### 阶段 6：报告中心、行动台和复盘闭环，5-7 天

目标：让系统从“分析展示”升级为“可交付、可执行、可续费”的工作台。

修改文件：

```text
web/src/routes/ReportPage.tsx
web/src/routes/ActionBoardPage.tsx
web/src/routes/ReviewPage.tsx
web/src/types/report.ts
web/src/lib/useActionBoard.ts
aiyxdata_tradar/report/report_service.py
aiyxdata_tradar/actions/service.py
docker/server.py
```

能力：

- 老板简报。
- 市场版报告。
- 销售版报告。
- 公关版报告。
- 客户外发白标报告。
- 洞察转行动。
- 建议采纳/未采纳原因。
- 复盘指标：内容表现、线索反馈、风险下降、销售反馈。

API：

```text
GET  /api/reports
GET  /api/reports/{reportId}
POST /api/reports/{reportId}/export
GET  /api/actions
POST /api/actions
POST /api/actions/{actionId}/review
```

验收：

- 每份报告包含数据源、时间范围、证据覆盖率和人工校对状态。
- 用户可以从任意模块把建议转为行动项。
- 行动项可记录采纳、未采纳、验证指标和复盘结果。
- 至少支持 3 类角色化报告。

#### 阶段 7：国产多模型路由和 AI/GEO 风险评估，7-10 天

目标：形成技术独特性和高客单价专项能力。

新增/修改文件：

```text
aiyxdata_tradar/ai/model_router.py
aiyxdata_tradar/ai/model_runs.py
aiyxdata_tradar/geo_risk/service.py
web/src/routes/GeoRiskPage.tsx
web/src/types/geoRisk.ts
web/src/lib/geoRiskApi.ts
docker/server.py
config/model_router.yaml
docs/defaults/model_router.yaml
```

模型路由：

- 主模型：Qwen 系列。
- 深度推理：DeepSeek 系列。
- 批量成本模型：Qwen Flash / DeepSeek Flash。
- 长文档/多模态备选：Kimi。
- 私有化备选：GLM。

AI/GEO 页面必须展示：

- 问题集。
- 品牌可见性。
- 答案质量。
- 竞品对比。
- 误读风险。
- 投毒风险。
- 内容补位建议。
- 答案快照和采样时间。

API：

```text
POST /api/model-router/run
GET  /api/model-router/runs/{runId}
POST /api/geo-risk/reports
GET  /api/geo-risk/reports/{reportId}
```

验收：

- 模型调用记录可查。
- 高风险报告支持二模型复核。
- AI/GEO 报告保留问题集、平台、采样时间、答案快照。
- 明确不做黑帽 GEO 或投毒，只做检测和风险评估。

#### 阶段 8：项目级对话记忆和主动顾问能力，5-7 天

目标：让 AYX 从“问答工具”变成“懂品牌历史的营销增长顾问”。

新增/修改文件：

```text
aiyxdata_tradar/memory/project_memory.py
web/src/routes/SettingsPage.tsx
web/src/components/memory/ProjectMemoryPanel.tsx
docker/server.py
```

记忆内容：

- 客户画像。
- 品牌定位。
- 竞品。
- 用户偏好的报告风格。
- 历史报告。
- 已采纳建议。
- 复盘结果。
- 禁用表达和合规边界。

API：

```text
GET    /api/memory/project/{projectId}
POST   /api/memory/project/{projectId}
DELETE /api/memory/project/{projectId}
```

验收：

- 项目级记忆默认关闭，需用户授权开启。
- 用户可以查看、删除、关闭记忆。
- 不同客户记忆隔离。
- 系统能基于历史记忆主动提出数据补充、风险复查或下一步动作建议。

### 0A.7 开发优先级

P0 必须做：

1. 专业情报终端第一阶段终端化演示版。
2. 品牌舆情与风险雷达一级页面。
3. 统一证据层和项目层。
4. 客户线索雷达。
5. 购买阻力分析。
6. 报告中心与行动台闭环。

P1 强烈建议：

1. 内容命中率评估。
2. 营销避雷预检。
3. 竞品转化差距升级。
4. 角色化报告。
5. 数据源健康监控。

P2 高价值增强：

1. AI/GEO 风险评估。
2. 国产多模型路由。
3. 项目级对话记忆。
4. 二模型审稿机制。
5. 私有化模型网关。

### 0A.8 推荐排期

| 周期 | 目标 | 核心交付 |
| --- | --- | --- |
| 第 1 周 | 品牌舆情与风险雷达 | 独立页面、dashboard API、预警、证据下钻、升级事件任务 |
| 第 2 周 | 统一项目与证据层 | BrandProject、EvidenceItem、数据源健康、证据搜索 |
| 第 3 周 | 线索和购买阻力 | 客户线索雷达、购买阻力分析、行动转化 |
| 第 4 周 | 发布前评估 | 内容命中率、营销避雷、发布决策建议 |
| 第 5 周 | 报告和行动闭环 | 角色化报告、行动台、采纳记录、复盘 |
| 第 6 周 | 竞品和商业演示 | 竞品转化差距、客户外发报告、演示样例 |
| 第 7 周 | 多模型和 AI/GEO | Model Router、AI/GEO 报告、二模型复核 |
| 第 8 周 | 记忆和试点交付 | 项目记忆、试点 SOP、案例库、验收修复 |

### 0A.9 每阶段统一验收命令

前端：

```powershell
cd web
npm run typecheck
npm run build
```

后端：

```powershell
python -m py_compile docker/server.py
python -m compileall -q aiyxdata_tradar mcp_server docker
```

安全：

```powershell
bash scripts/check_release_secrets.sh .
```

本地服务：

```powershell
docker compose up -d --build
```

人工访问：

```text
http://127.0.0.1:8094/
http://127.0.0.1:8094/#/intelligence-terminal
http://127.0.0.1:8094/#/legacy-screen
http://127.0.0.1:8094/#/brand-risk-radar
http://127.0.0.1:8094/#/reports
http://127.0.0.1:8094/#/actions
http://127.0.0.1:8094/#/settings
```

### 0A.10 商业化验收标准

最小可卖版本必须满足：

- 3 个真实品牌样例项目。
- 每个项目至少有 50 条以上有效证据。
- 品牌舆情与风险雷达可以展示风险总览、趋势、平台扩散、议题热力、传播路径、预警和证据链，并在同一页面内支持事件核心词 + 关键词专项分析、事件生命周期、平台情绪、信息链追踪和报告摘要。
- 客户线索雷达可以输出高意向主题、用户原话、销售切入点和内容选题。
- 购买阻力分析可以输出 Top 5 阻力、原因归因和修复建议。
- 报告中心可以生成老板版、市场版、销售版中至少 3 类报告。
- 行动台可以记录建议采纳和复盘结果。
- 核心结论证据覆盖率达到 90% 以上。
- 空泛建议比例低于 10%。
- 用户可以明确指出报告节省了什么时间、发现了什么机会或避免了什么风险。

### 0A.11 模块状态矩阵

| 模块 | 当前状态 | 下一步动作 | 优先级 |
| --- | --- | --- | --- |
| 原数据采集与 HTML 报告 | 已有 | 保持稳定，作为证据来源 | P0 |
| 专业情报终端 | 已有 `/#/legacy-screen` 承载完整报告，缺少正式入口和终端化视觉层 | 新增 `/#/intelligence-terminal`，在不改接口和数据字段的前提下升级为今日机会、今日风险、今日行动、热点事件评估和 AI 决策简报工作台 | P0 |
| React 总览驾驶舱 | 已有，可演示 | 逐步从 mock 切换真实 API | P0 |
| 事件舆情 Agent | 已有雏形，最成熟 | 接入品牌风险雷达升级链路 | P0 |
| 品牌舆情与风险雷达 | PRD 已定义，未开发 | 新增一级页面和 API | P0 |
| 统一项目层 | 缺失 | 新增 BrandProject 服务 | P0 |
| 统一证据层 | 部分存在 | 新增 EvidenceItem 标准化服务 | P0 |
| 客户线索雷达 | 雏形不足 | 新增页面、API、评分逻辑 | P0 |
| 购买阻力分析 | 雏形不足 | 新增页面、API、阻力分类 | P0 |
| 内容命中率评估 | 未开发 | 新增发布前评分页面 | P1 |
| 营销避雷预检 | 未开发 | 新增风险审核页面 | P1 |
| 竞品转化差距 | 有竞品页面但不完整 | 升级为转化差距矩阵 | P1 |
| 报告中心 | 有雏形 | 增加角色化报告和外发能力 | P0 |
| 行动台与复盘 | 有雏形 | 增加采纳、未采纳和复盘指标 | P0 |
| AI/GEO 风险评估 | 未开发 | 新增报告服务和页面 | P2 |
| 国产多模型路由 | 未开发 | 新增 Model Router | P2 |
| 项目级对话记忆 | 未开发 | 新增授权记忆服务 | P2 |

### 0A.12 关键风险与处理方式

| 风险 | 表现 | 处理方式 |
| --- | --- | --- |
| 功能太多导致开发分散 | 每个模块都有页面但都不深 | 先完成品牌风险雷达、线索、购买阻力、报告闭环 |
| 数据不足影响可信度 | 页面好看但结论无证据 | 先做统一证据层和证据覆盖率 |
| AI 幻觉 | 报告看起来专业但无法追溯 | 强制事实、推断、建议分层，强结论必须绑定证据 |
| 模型成本失控 | 批量评论都走高价模型 | 上 Model Router 前先做批量成本模型策略 |
| 用户不愿意试用 | 看不懂价值 | 优先做老板简报、销售话术、避雷报告和客户外发版 |
| 工程债扩大 | `docker/server.py` 继续膨胀 | 新功能服务放进 `aiyxdata_tradar/*/service.py`，server.py 只做路由 |

### 0A.13 第一批开发任务清单

第一批建议只做 10 个任务，完成后即可进入试点销售演示：

1. 新增 `BrandRiskRadarPage` 和导航入口。
2. 新增 `brand_risk/service.py`，复用事件 Agent 证据构建风险雷达数据。
3. 新增 `/api/brand-risk-radar/dashboard`。
4. 新增风险预警升级事件任务接口。
5. 新增统一 `EvidenceItem` 类型和前后端映射。
6. 新增客户线索雷达页面和 `/api/growth/lead-signals`。
7. 新增购买阻力分析页面和 `/api/growth/purchase-barriers`。
8. 升级报告中心，增加角色化报告入口。
9. 升级行动台，支持采纳、未采纳、复盘。
10. 准备 3 个真实品牌样例项目和一套演示脚本。

完成这 10 个任务后，产品可以对外表达为：

> AYX 已具备品牌舆情与风险监控、客户线索发现、购买阻力诊断、证据链报告和行动复盘的最小可卖闭环。

### 0A.14 专业情报终端技术开发计划

> **同步口径：** 本节只针对专业情报终端开发，产品需求以 `docs/202606100824_产品需求文档_AYXGrowthIntel.md` 的 `7.0 专业情报终端`、`7.10.0 专业情报终端`、`10.1 专业情报终端页` 为准；视觉与交互以 `docs/202606231542_UI设计方案_AYXGrowthIntel专业情报终端_V1.0.md` 为准。本节负责把产品和设计拆成可执行的前端任务。

#### 0A.14.1 定位与开发边界

专业情报终端是原 `/#/legacy-screen` 数据大屏的正式产品化升级形态，目标是把“完整报告工作区”升级为“今日机会 / 今日风险 / 今日行动 / 热点事件评估 / AI 决策简报”的商业化情报工作台。

本模块与“营销增长评估与风险雷达 Agent”保持分工：

| 模块 | 定位 | 功能方向 | 数据关系 |
| --- | --- | --- | --- |
| 专业情报终端 | 每日情报驾驶舱和决策工作台 | 今日机会、今日风险、今日行动、热点事件评估、完整报告阅读与导出 | 共享报告、证据、项目、事件、行动数据 |
| 营销增长评估与风险雷达 Agent | 专项分析与风险评估工具 | 品牌风险雷达、客户线索、购买阻力、内容命中率、营销避雷、竞品差距 | 共享同一数据源和数据库，但页面、任务流、分析深度独立 |

开发边界：

- 不改现有 `/api/refresh` 接口。
- 不改 `/html/latest/current.html` 的生成链路。
- 不改 `/config_editor/index.html` 配置中心入口。
- 不改数据库结构作为第一阶段前置条件。
- 保留 `/#/legacy-screen` 兼容入口。
- 新增 `/#/intelligence-terminal` 作为正式产品入口。
- 优先通过 React 页面外壳、Shadow DOM 样式适配、卡片增强和 AI 报告版式重排实现专业化升级。

分阶段实现口径：

| 阶段 | 技术策略 | 是否新增接口 | 是否改数据库 | 验收目标 |
| --- | --- | --- | --- | --- |
| 第一阶段：终端化演示版 | 新增正式路由，复用 legacy 报告加载和 `/api/refresh`，通过视觉适配层提取卡片、标签、AI 分析和证据线索 | 否 | 否 | 专业情报终端可访问、可搜索、可筛选、可导出、可展示今日机会/风险/行动 |
| 第二阶段：结构化终端版 | 增加 `/api/intelligence-terminal/*`，从统一证据层和报告中心读取结构化数据 | 是 | 视统一证据层进度而定 | 时间范围、平台、行业、风险等级、机会等级筛选稳定可用 |
| 第三阶段：Agent 协同版 | 终端信号可创建营销避雷、品牌风险雷达、事件专项报告、竞品分析和行动台任务 | 是 | 共享项目、证据、报告、行动数据 | 形成每日发现、深度分析、行动复盘闭环 |

第一阶段不做：

- 不新建强依赖后端接口。
- 不改报告生成链路。
- 不改数据库结构。
- 不把全部 Agent 深度分析塞进终端页面。
- 不为视觉效果添加无业务意义的粒子、光斑、霓虹或大面积紫蓝渐变。

#### 0A.14.0 需求-设计-任务追踪矩阵

| 产品需求 | UI 设计要求 | 开发任务 | 第一阶段验收 |
| --- | --- | --- | --- |
| 每日打开入口 | 页面第一眼识别为专业情报终端 | IT-1、IT-3、IT-13 | `/#/intelligence-terminal` 可访问，导航显示专业情报终端 |
| 今日机会 / 今日风险 / 今日行动 | 三栏决策卡、优先级、状态色和行动信息 | IT-4 | 首屏展示三栏，数据不足时显示空状态 |
| 热点事件快评 | 事件阶段时间线、跟进建议状态 | IT-7、IT-11 | 至少能展示事件阶段或数据不足说明 |
| 情报信号卡 | 风险卡、机会卡、观察卡、普通信号卡 | IT-5 | 卡片状态可识别，原内容不丢失 |
| AI 决策简报 | 章节化咨询报告版式 | IT-6 | AI 内容按结论、证据、风险、机会、建议动作组织 |
| 证据链下钻 | 证据链抽屉或右侧面板 | IT-9 | 情报卡和 AI 章节可打开证据抽屉 |
| 搜索与筛选 | 分区导航、结果数量、清除按钮、命中高亮 | IT-10 | 搜索和分区组合后结果数量准确 |
| 可视化增强 | 风险机会矩阵、事件时间线、平台雷达、数据源覆盖 | IT-7、IT-11 | 图表必须有业务含义，数据不足时显示缺口 |
| 导出交付 | 导出情报简报，不包含无关浮层 | IT-8、IT-12 | 导出图片可用于汇报或客户交付 |
| 不改接口边界 | 视觉适配层和 legacy 报告适配 | IT-2 | 继续复用 `/html/latest/current.html`、`/api/refresh`、`/config_editor/index.html` |
| 升级深度分析入口 | 从机会、风险、热点或 AI 决策章节进入升级面板 | IT-14 | 第一阶段展示可升级目标和待接入状态，不强制创建后端任务 |

#### 0A.14.2 当前技术基础

当前已具备以下基础：

```text
web/src/routes/LegacyDataScreenPage.tsx
web/src/App.tsx
web/src/components/layout/AppShell.tsx
web/src/components/ui/Button.tsx
```

当前页面能力：

- 从 `/html/latest/current.html` 拉取完整报告。
- 解析 `#main-content`、`#loading`、`.controls`。
- 注入 Shadow DOM，隔离 legacy 报告样式。
- 重新绑定主题、标签筛选、搜索、刷新和导出长图。
- 通过右下角按钮打开 `/config_editor/index.html`。

当前前端栈：

| 技术 | 用途 |
| --- | --- |
| React 19 | 页面结构、状态管理、组件化封装 |
| TypeScript | 类型约束，降低终端模块重构风险 |
| Vite 7 | 开发和构建 |
| Tailwind CSS v4 | 视觉系统、布局和状态样式 |
| React Router 7 | Hash 路由和正式入口 |
| lucide-react | 操作图标、状态图标 |
| motion | 卡片入场、筛选切换、抽屉和弹窗动效 |
| ECharts | 唯一图表引擎，用于风险机会矩阵、趋势小图、事件时间线、平台信号雷达、数据源覆盖矩阵和交互式下钻 |

#### 0A.14.3 目标页面结构

专业情报终端目标页面结构：

```text
/#/intelligence-terminal
├── 顶部状态与操作栏
│   ├── 页面标题
│   ├── 最近更新时间
│   ├── 搜索
│   ├── 筛选
│   ├── 刷新情报
│   ├── 导出情报简报
│   └── 情报配置中心
├── 首屏决策摘要
│   ├── 今日总判断
│   ├── 高优先级信号数
│   ├── 今日风险数
│   ├── 今日机会数
│   └── 待行动数
├── 今日机会
├── 今日风险
├── 今日行动
├── 情报分区导航
│   ├── 全部
│   ├── 热点事件
│   ├── 竞品动作
│   ├── 平台趋势
│   ├── 内容机会
│   └── 风险预警
├── 情报信号卡工作区
├── AI 决策简报区
└── 证据链 / 配置中心 / 操作抽屉
```

#### 0A.14.4 推荐新增和修改文件

第一阶段建议控制在前端视觉与路由层，不改后端。

```text
web/src/routes/LegacyDataScreenPage.tsx
web/src/routes/IntelligenceTerminalPage.tsx
web/src/components/intelligence/TerminalToolbar.tsx
web/src/components/intelligence/DecisionSummary.tsx
web/src/components/intelligence/TodayOpportunityRiskAction.tsx
web/src/components/intelligence/SignalCardShell.tsx
web/src/components/intelligence/AIDecisionBrief.tsx
web/src/components/intelligence/TerminalConfigButton.tsx
web/src/components/intelligence/IntelligenceSegmentNav.tsx
web/src/components/intelligence/TerminalSearchBar.tsx
web/src/components/intelligence/RiskOpportunityMatrix.tsx
web/src/components/intelligence/EventTimeline.tsx
web/src/components/intelligence/PlatformSignalRadar.tsx
web/src/components/intelligence/DataSourceCoverageMatrix.tsx
web/src/components/intelligence/EvidenceChainDrawer.tsx
web/src/components/intelligence/UpgradeAnalysisPanel.tsx
web/src/lib/legacyReportAdapter.ts
web/src/lib/intelligenceExport.ts
web/src/types/intelligenceTerminal.ts
web/src/App.tsx
web/src/components/layout/AppShell.tsx
```

说明：

- `IntelligenceTerminalPage.tsx` 可以先复用 `LegacyDataScreenPage` 的加载逻辑，再逐步抽出适配层。
- `legacyReportAdapter.ts` 负责解析 legacy HTML 中已有节点、卡片、标签、AI 分析区和控件。
- `types/intelligenceTerminal.ts` 定义视觉层使用的轻量类型，不要求后端立即返回新结构。
- `components/intelligence/*` 负责新终端的顶部栏、摘要、卡片外壳、AI 简报和配置入口。
- `EvidenceChainDrawer.tsx` 优先复用现有 `web/src/components/evidence/EvidenceDrawer.tsx` 的交互模式，避免重复做证据抽屉。
- `intelligenceExport.ts` 负责导出情报简报时的内容裁剪、导出态样式和截图目标选择。

第二阶段如需接入真实结构化数据，再新增 API：

```text
GET  /api/intelligence-terminal/summary?projectId=demo
GET  /api/intelligence-terminal/signals?projectId=demo&tag=risk
GET  /api/intelligence-terminal/events?projectId=demo
POST /api/intelligence-terminal/actions
```

但第一阶段不依赖这些新增 API。

#### 0A.14.5 数据适配策略

第一阶段采用“从 legacy 报告提取视觉线索”的方式：

| 目标字段 | 优先来源 | 降级策略 |
| --- | --- | --- |
| 标题 | `.data-card` 标题或文本首段 | 截取卡片前 40 字 |
| 标签 | `data-tags` | 从文本关键词推断风险、机会、观察 |
| 来源 | 卡片内来源字段 | 显示“报告来源” |
| 更新时间 | 报告生成时间或页面状态 | 使用当前加载时间 |
| 风险 / 机会状态 | 标签、关键词、AI 分析结论 | 默认普通信号 |
| 证据数量 | 卡片内证据列表数量 | 显示“证据待展开” |
| AI 决策简报 | 现有 AI 分析报告区 | 按标题和段落重新分节 |
| 平台分布 | 卡片来源、标签、正文平台词 | 无法提取时显示“平台覆盖待补充” |
| 数据源覆盖 | 报告元信息、卡片来源、配置中心数据源 | 无法提取时不渲染矩阵 |
| 搜索命中 | 卡片标题、摘要、标签、证据文本 | 只高亮可安全定位的文本片段 |

当统一证据层和报告中心成熟后，专业情报终端再切换为结构化 API 数据。

#### 0A.14.6 视觉与交互开发要求

视觉目标以 `docs/202606231542_UI设计方案_AYXGrowthIntel专业情报终端_V1.0.md` 为准。

关键要求：

- 明亮专业主题，默认背景 `#F6F8FB`。
- 卡片圆角控制在 8-12px。
- 主强调色优先使用深青绿 `#0F766E` 或商务蓝 `#2563EB`。
- 风险使用 `#DC2626`，机会使用 `#059669`，观察使用 `#D97706`。
- 不使用粒子、霓虹、大面积紫蓝渐变和无意义动态背景。
- 图标统一使用 `lucide-react`，不用 emoji 作为功能图标。
- 搜索、筛选、刷新、导出和配置中心必须保留。
- 搜索必须显示结果数量、清除按钮、空状态，并尽量支持命中高亮。
- 情报分区导航必须覆盖全部、热点事件、竞品动作、平台趋势、内容机会、风险预警等基础分区。
- 导出情报简报必须优先包含首屏摘要、今日机会、今日风险、今日行动、AI 决策简报和关键情报卡。
- 证据链抽屉必须能从情报卡或 AI 决策章节进入；证据不足时显示缺口，不伪造证据。
- 状态识别不能只依赖颜色，必须同时使用文本、图标或标签。
- 弹窗和抽屉需要具备键盘焦点、关闭按钮、`Escape` 关闭和可见焦点态。
- 动效只用于状态表达：卡片入场、筛选切换、风险状态、刷新骨架屏和弹窗。
- 必须支持 `prefers-reduced-motion`。

#### 0A.14.7 开发任务拆解

**Task IT-1: 路由与页面入口**

文件：

```text
web/src/App.tsx
web/src/components/layout/AppShell.tsx
web/src/routes/IntelligenceTerminalPage.tsx
web/src/routes/LegacyDataScreenPage.tsx
```

任务：

1. 新增 `/#/intelligence-terminal` 路由。
2. 保留 `/#/legacy-screen` 兼容入口。
3. 导航命名从“原数据大屏 / 完整报告工作区”升级为“专业情报终端”。
4. 初始实现可复用 `LegacyDataScreenPage` 逻辑，避免一次性重写。

验收：

- `http://127.0.0.1:8094/#/intelligence-terminal` 可访问。
- `http://127.0.0.1:8094/#/legacy-screen` 仍可访问。
- 两个入口均能加载最新报告。

**Task IT-2: 抽离 legacy 报告适配层**

文件：

```text
web/src/lib/legacyReportAdapter.ts
web/src/types/intelligenceTerminal.ts
web/src/routes/IntelligenceTerminalPage.tsx
```

任务：

1. 抽离报告加载、HTML 解析、样式适配、Shadow DOM 注入逻辑。
2. 提供 `loadLegacyReport()`、`adaptLegacyStyle()`、`extractSignalCards()`、`extractAIBriefSections()` 等方法。
3. 保留原主题、筛选、搜索、刷新、导出事件绑定。

验收：

- 页面加载行为与旧版一致。
- 搜索、筛选、刷新、导出功能不回退。
- TypeScript 类型检查通过。

**Task IT-3: 顶部操作栏和状态系统**

文件：

```text
web/src/components/intelligence/TerminalToolbar.tsx
web/src/components/intelligence/TerminalConfigButton.tsx
web/src/routes/IntelligenceTerminalPage.tsx
```

任务：

1. 增加专业情报终端顶部栏。
2. 显示最近更新时间、加载状态、刷新状态。
3. 将重新载入、刷新、导出、配置中心统一为工作台操作。
4. 配置中心继续打开 `/config_editor/index.html`。

验收：

- 刷新中、加载失败、加载成功状态清晰。
- 配置中心弹窗可打开和关闭。
- 操作按钮不遮挡报告内容。

**Task IT-4: 决策摘要与今日三栏**

文件：

```text
web/src/components/intelligence/DecisionSummary.tsx
web/src/components/intelligence/TodayOpportunityRiskAction.tsx
web/src/types/intelligenceTerminal.ts
```

任务：

1. 在报告上方增加“今日总判断”。
2. 增加“今日机会 / 今日风险 / 今日行动”三栏。
3. 第一阶段可从现有 AI 分析文本和卡片标签中提取摘要。
4. 无法提取时提供清晰空状态，不伪造数据。

验收：

- 首屏能看到机会、风险、行动。
- 没有结构化数据时不显示虚假结论。
- 移动端三栏自动变成单列。

**Task IT-5: 情报信号卡视觉升级**

文件：

```text
web/src/components/intelligence/SignalCardShell.tsx
web/src/routes/IntelligenceTerminalPage.tsx
```

任务：

1. 对 `#main-cards-grid .data-card` 增加情报信号卡视觉规范。
2. 区分风险卡、机会卡、观察卡和普通信号卡。
3. 展示来源、标签、更新时间、证据数量、状态徽标。
4. 保留原卡片内容，避免信息丢失。

验收：

- 卡片仍能按标签筛选。
- 搜索结果仍可显示匹配卡片。
- 高风险卡可以快速识别。

**Task IT-6: AI 决策简报区重排**

文件：

```text
web/src/components/intelligence/AIDecisionBrief.tsx
web/src/lib/legacyReportAdapter.ts
```

任务：

1. 将现有 AI 分析报告按章节拆分。
2. 形成“结论 / 证据 / 风险 / 机会 / 建议动作”版式。
3. 支持展开和收起。
4. 保留原文兜底。

验收：

- AI 分析区不再是大段文字堆叠。
- 每个章节能快速扫读。
- 原始 AI 内容没有丢失。

**Task IT-7: 可视化增强**

文件：

```text
web/src/components/intelligence/RiskOpportunityMatrix.tsx
web/src/components/intelligence/EventTimeline.tsx
web/src/components/intelligence/MiniTrendChart.tsx
```

任务：

1. 增加风险机会优先级矩阵。
2. 增加热点事件阶段时间线。
3. 增加趋势小倍图。
4. 所有图表统一使用 ECharts，不再新增其他图表库实现。
5. 第一阶段允许用提取数据或空状态展示，第二阶段接结构化 API。

验收：

- 图表有业务含义，不做装饰。
- 数据不足时显示空状态和数据来源说明。
- 图表不影响主报告加载和搜索性能。
- 专业情报终端新增图表不得引入 ECharts 之外的图表库。

**Task IT-8: 导出和响应式验收**

文件：

```text
web/src/routes/IntelligenceTerminalPage.tsx
web/src/components/intelligence/*
web/src/lib/intelligenceExport.ts
```

任务：

1. 增加导出情报简报专用样式。
2. 明确导出内容裁剪规则：优先导出首屏摘要、今日机会、今日风险、今日行动、AI 决策简报和关键情报卡。
3. 导出时固定背景、去除 hover 态和浮层遮挡。
4. 检查桌面 1366x768、宽屏 1920x1080、移动 390x844。
5. 支持 `prefers-reduced-motion`。

验收：

- 导出长图成功。
- 导出图片不包含配置中心浮层、悬浮按钮、调试状态和无关导航。
- 导出内容包含本次情报判断的关键结论和行动建议。
- 移动端无文字重叠和横向溢出。
- 主要按钮文案不溢出。

**Task IT-9: 证据链抽屉与 EvidenceDrawer 集成**

文件：

```text
web/src/components/intelligence/EvidenceChainDrawer.tsx
web/src/components/evidence/EvidenceDrawer.tsx
web/src/components/intelligence/SignalCardShell.tsx
web/src/components/intelligence/AIDecisionBrief.tsx
web/src/types/intelligenceTerminal.ts
```

任务：

1. 为情报信号卡增加“查看证据”入口。
2. 为 AI 决策简报章节增加证据入口。
3. 优先复用现有 `EvidenceDrawer` 的抽屉交互和证据展示模式。
4. 将终端从 legacy 报告中提取到的证据线索映射为 `report.EvidenceItem` 兼容结构。
5. 无法映射到 `EvidenceItem` 的字段必须显示证据缺口，不得伪造来源、链接、时间或置信度。
6. 证据不足时展示“证据待补充 / 无法从当前报告提取证据”，不伪造证据。
7. 抽屉支持 `Escape` 关闭、点击遮罩关闭、关闭按钮和键盘焦点。

验收：

- 用户可以从情报卡进入证据链抽屉。
- 用户可以从 AI 决策章节进入证据链抽屉。
- 证据字段至少展示标题、来源、时间、平台、链接或缺口说明。
- 无证据场景有清晰空状态。

**Task IT-10: 情报分区导航与搜索增强**

文件：

```text
web/src/components/intelligence/IntelligenceSegmentNav.tsx
web/src/components/intelligence/TerminalSearchBar.tsx
web/src/lib/legacyReportAdapter.ts
web/src/types/intelligenceTerminal.ts
web/src/routes/IntelligenceTerminalPage.tsx
```

任务：

1. 增加情报分区导航：全部、热点事件、竞品动作、平台趋势、内容机会、风险预警、待行动。
2. 每个分区显示数量。
3. 搜索支持结果数量、清除按钮、空状态。
4. 对标题、摘要、标签和安全可定位文本做命中高亮。
5. 搜索和分区筛选组合时，显示当前筛选条件和结果数量。

验收：

- 分区切换不会破坏原有标签筛选能力。
- 搜索无结果时有明确空状态和清除入口。
- 搜索结果数量与可见卡片数量一致。
- 移动端分区导航可横向滚动或折叠，不发生文字溢出。

**Task IT-11: 平台信号雷达与数据源覆盖矩阵**

文件：

```text
web/src/components/intelligence/PlatformSignalRadar.tsx
web/src/components/intelligence/DataSourceCoverageMatrix.tsx
web/src/components/intelligence/RiskOpportunityMatrix.tsx
web/src/components/intelligence/EventTimeline.tsx
web/src/lib/legacyReportAdapter.ts
web/src/types/intelligenceTerminal.ts
```

任务：

1. 在可视化增强中补齐平台信号雷达。
2. 增加数据源覆盖矩阵，展示不同来源、平台或标签的覆盖情况。
3. 风险机会矩阵、事件时间线、平台雷达均必须绑定可解释数据来源。
4. 图表必须基于 ECharts，优先使用 tooltip、legend、dataZoom、brush、emphasis 和 click 事件实现动态交互。
5. 数据不足时显示“数据覆盖不足，等待结构化接口接入”。
6. 禁止使用装饰性图表和无法解释的动态效果。

验收：

- 平台信号雷达能表达平台分布或平台热度。
- 数据源覆盖矩阵能表达来源覆盖或缺口。
- 数据不足时不渲染误导性图表。
- 图表加载不阻塞主报告和卡片交互。
- 所有新增可视化组件只依赖 ECharts。

**Task IT-12: 导出情报简报内容裁剪规则**

文件：

```text
web/src/lib/intelligenceExport.ts
web/src/routes/IntelligenceTerminalPage.tsx
web/src/components/intelligence/DecisionSummary.tsx
web/src/components/intelligence/TodayOpportunityRiskAction.tsx
web/src/components/intelligence/AIDecisionBrief.tsx
```

任务：

1. 定义导出截图目标区域，不直接导出整个页面外壳。
2. 导出内容顺序固定为：终端标题、更新时间、今日总判断、今日机会、今日风险、今日行动、AI 决策简报、关键情报卡。
3. 导出时隐藏侧边导航、配置中心悬浮按钮、遮罩、临时 Tooltip、调试状态。
4. 导出时统一背景、卡片阴影和字体，避免截图出现透明或错位。
5. 导出失败时给出明确错误信息，不影响页面状态恢复。

验收：

- 导出图片可直接用于汇报或客户交付。
- 导出内容不包含无关导航和配置浮层。
- 导出失败后页面恢复正常交互。

**Task IT-13: AppShell 专业化外壳改造**

文件：

```text
web/src/components/layout/AppShell.tsx
web/src/App.tsx
web/src/routes/IntelligenceTerminalPage.tsx
```

任务：

1. 导航中将“原数据大屏”改为“专业情报终端”，并指向 `/#/intelligence-terminal`。
2. 保留 `/#/legacy-screen` 兼容路由，但不作为主导航名称。
3. 移除或弱化外壳中的紫蓝渐变、光斑和过度玻璃拟态。
4. 外壳背景统一为专业工作台浅色背景，和设计方案中的 `#F6F8FB` 保持一致。
5. 页面标题、徽标、状态文案统一使用“专业情报终端 / 情报配置中心 / 导出情报简报”等产品化命名。

验收：

- 侧边导航显示“专业情报终端”。
- 访问 `/#/intelligence-terminal` 时页面标题正确。
- `/#/legacy-screen` 可以直接访问但不再作为商业演示主入口。
- 页面外壳不再呈现明显紫蓝 AI 模板风格。

**Task IT-14: 升级分析入口 MVP**

文件：

```text
web/src/components/intelligence/UpgradeAnalysisPanel.tsx
web/src/components/intelligence/SignalCardShell.tsx
web/src/components/intelligence/AIDecisionBrief.tsx
web/src/types/intelligenceTerminal.ts
web/src/routes/IntelligenceTerminalPage.tsx
```

任务：

1. 为情报卡、热点事件快评和 AI 决策章节增加“升级分析”入口。
2. 第一阶段点击后打开选择面板，不要求立即完成后端任务闭环。
3. 面板展示可升级目标：营销避雷预检、品牌风险雷达、事件专项报告、竞品分析。
4. 面板展示当前信号的标题、关键词、证据数量、置信度、建议升级目标和缺失字段。
5. 如果目标模块路由已存在，则允许跳转；如果目标模块未完成，则显示“待接入”状态。
6. 第二阶段再接入真实任务创建接口，保留当前证据、关键词、时间范围和初始判断。

验收：

- 用户能从终端信号看到“升级分析”入口。
- 用户能明确选择升级目标。
- 未实现的深度模块不会静默失败，必须显示待接入或不可用状态。
- 第一阶段不新增强制后端依赖。

**Task IT-15: 图表栈统一为 ECharts**

文件：

```text
web/src/components/charts/GrowthRadar.tsx
web/src/components/charts/OpportunityMatrix.tsx
web/src/components/charts/TrendChart.tsx
web/src/routes/EventAgentPage.tsx
web/package.json
```

任务：

1. 专业情报终端新增图表全部使用 ECharts。
2. 现有旧图表组件如果仍被其他页面使用，先不阻塞专业情报终端第一阶段，但不得在新终端中继续引用。
3. 后续统一把 `GrowthRadar`、`OpportunityMatrix`、`TrendChart` 迁移为 ECharts 实现。
4. 迁移完成并确认无引用后，从 `web/package.json` 移除旧图表库依赖。
5. 复用 `EventAgentPage.tsx` 中已有的 ECharts 初始化、resize、dispose 和主题色经验，抽出公共 `EChartsPanel` 时必须保证类型安全。

验收：

- 专业情报终端新增可视化组件只使用 ECharts。
- ECharts 图表具备 tooltip、legend 或点击下钻中的至少一种有效交互。
- 移除旧图表库依赖前必须全项目搜索确认无引用。
- `npm run typecheck` 和 `npm run build` 通过后才能删除依赖。

#### 0A.14.8 验收命令

前端验收：

```powershell
cd web
npm run typecheck
npm run build
```

人工访问：

```text
http://127.0.0.1:8094/#/intelligence-terminal
http://127.0.0.1:8094/#/legacy-screen
http://127.0.0.1:8094/config_editor/index.html
```

浏览器验收视口：

```text
1366x768
1920x1080
390x844
```

必须通过：

- 正式入口和兼容入口都可访问。
- 完整报告可以加载。
- 搜索、筛选、刷新、导出、配置中心功能可用。
- 首屏出现今日机会、今日风险、今日行动。
- 高风险、机会、观察状态可识别。
- AI 决策简报区具备章节化阅读体验。
- 情报分区导航可用，并显示当前筛选结果数量。
- 搜索支持结果数量、清除按钮、空状态和安全命中高亮。
- 情报卡和 AI 决策章节可以进入证据链抽屉，证据不足时显示缺口。
- 平台信号雷达、数据源覆盖矩阵、风险机会矩阵或事件时间线至少有一种可视化具备真实数据解释。
- 导出情报简报不包含侧边导航、悬浮配置按钮、遮罩或调试状态。
- AppShell 外壳不再使用明显紫蓝渐变、光斑和过度玻璃拟态作为主视觉。
- 不引入后端接口破坏性变更。

---

## 0. 当前工程判断

当前项目已经适合继续开发，但需要先做工程治理。已存在的基础能力包括：

- 主程序入口：`aiyxdata_tradar/__main__.py`
- AI 分析模块：`aiyxdata_tradar/ai/`
- 报告生成模块：`aiyxdata_tradar/report/`
- 存储模块：`aiyxdata_tradar/storage/`
- 配置服务：`docker/server.py`
- MCP 服务：`mcp_server/server.py`
- 首页：`docs/home.html`
- 配置中心：`docs/index.html`、`docs/assets/script.js`、`docs/assets/style.css`
- 默认配置：`docs/defaults/`
- 运行配置：`config/`
- Docker 部署：`Dockerfile`、`docker-compose.yml`

当前主要风险：

- 当前目录不是 Git 仓库，开发前应恢复或初始化版本管理。
- 工程区存在 `__pycache__` 运行缓存，且曾导致 `compileall` 权限错误。
- `aiyxdata_tradar/__main__.py` 过大，后续功能应逐步拆出服务层。
- 测试脚本偏诊断性质，需要整理为稳定的 pytest 测试。
- 报告缺少“事实/推测/建议/证据”的强结构，商业决策可信度不足。

---

## 1. 产品目标

### 1.1 第一阶段产品定位

产品先不做全行业泛 SaaS，第一阶段定位为：

**品牌增长周报与竞品战情自动化系统**

目标客户：

- 消费品牌市场部
- 内容运营团队
- 代运营公司
- 咨询研究团队
- MCN 与投放服务商

核心使用链路：

```text
配置品牌和竞品
-> 配置数据源和行业词库
-> 定时采集热榜与 RSS
-> 生成可信 AI 分析报告
-> 输出行动建议
-> 标记采纳状态
-> 下周期复盘效果
```

### 1.2 商业价值主张

产品不是资讯聚合器，而是帮助品牌团队降低三类成本：

- **信息整理成本**：减少人工看热榜、抄标题、拼周报。
- **判断成本**：把碎片信号整理为竞品、舆情、消费者、利弊和增长建议。
- **复盘成本**：沉淀每次建议、来源、执行状态和下一周期结果。

### 1.3 数据分析专业性目标

第一阶段必须把产品从“信息采集 + AI 摘要”升级为“可信增长情报分析”。每个关键洞察都应回答五个问题：

```text
这个结论是什么？
它来自哪些数据？
它是事实、推测还是建议？
它对品牌增长有什么影响？
团队下一步应该怎么验证？
```

分析结果需要具备以下专业特征：

- 多源数据融合：热榜、RSS、媒体资讯、行业信息源、品牌词和竞品词统一进入分析管道。
- 数据清洗与标准化：统一标题、来源、发布时间、标签、分类和品牌/竞品实体。
- 语义标签体系：围绕价格、功效、包装、渠道、服务、口碑、投放、风险和机会建立标签。
- 可信洞察结构：区分事实、推测、建议，并保留证据、样本量、时间范围、置信度和影响等级。
- 行动转化能力：把洞察转化为内容、产品、渠道、活动、公关和复盘任务。

### 1.4 技术壁垒建设目标

商业化版本的技术壁垒不应只依赖大模型能力，而应来自可持续沉淀的数据资产、行业知识和工作流：

- 数据壁垒：长期沉淀品牌、竞品、行业、渠道和用户反馈数据。
- 标签壁垒：形成专门服务品牌增长的语义标签体系。
- 模型壁垒：结合趋势、情绪、竞品、机会、风险和行动建议进行综合判断。
- 证据壁垒：关键洞察必须能追溯来源、时间、样本和判断依据。
- 工作流壁垒：采集、清洗、分析、报告、行动、复盘形成闭环。
- 行业模板壁垒：为美妆、食品饮料、母婴、个护、宠物、家居等行业沉淀不同分析模板。

---

## 2. 功能范围

### 2.1 P0 必须完成

1. 工程治理与测试门禁
2. 报告可信度结构
3. 最新报告 UI 重排
4. 品牌/竞品/行业配置结构
5. 行动建议台
6. 周报导出和客户演示路径

### 2.2 P1 后续增强

1. 多品牌空间
2. 多用户权限
3. 行业模板市场
4. 报告订阅推送
5. 任务分派与复盘闭环
6. 私有化部署安装向导

### 2.3 暂不做

1. 不做复杂多租户计费系统。
2. 不做全平台社交聆听替代品。
3. 不做暗色模式。
4. 不做重型前端框架迁移。
5. 不做无来源的自动决策闭环。

---

## 3. 页面与排版规划

### 3.1 首页 `docs/home.html`

定位：产品入口和经营态势看板。

布局：

```text
顶部导航
├── 品牌标识
├── 最新报告
├── 配置中心
└── 进入分析

首屏工作台
├── 左侧：产品一句话 + CTA + 关键状态
└── 右侧：市场信号动态画布

经营指标区
├── 品牌监测数
├── 风险标签数
├── 决策流程数
└── 最新报告状态

五大模块
├── 竞品战情
├── 舆情发展
├── 消费者态度
├── 利弊分析
└── 增长建议
```

风格：

- 明亮主题。
- 中后台产品质感。
- 色彩以白、浅灰、蓝、绿、琥珀、红为主。
- 卡片圆角不超过 12px，内部卡片建议 8px。
- 不使用装饰性渐变球、复杂背景和营销型大图。

### 3.2 最新报告页 `aiyxdata_tradar/report/html_v2.py`

定位：CEO/运营官可以直接用于晨会、周会和客户汇报的报告。

新版信息架构：

```text
报告顶部
├── 报告标题
├── 日期与生成时间
├── 数据源数量
├── AI 模型状态
└── 可信度提示

经营摘要
├── 今日最重要 3 件事
├── 最大机会
├── 最大风险
└── 建议动作数量

市场信号雷达
├── 热点信号
├── 竞品信号
├── 消费者信号
├── 渠道信号
└── 风险信号

增长雷达
├── 品牌热度
├── 用户情绪
├── 竞品压力
├── 内容机会
├── 渠道风险
└── 转化潜力

竞品战情
├── 竞品名称
├── 动作类型
├── 涉及平台
├── 证据数量
├── 影响判断
└── 建议应对

舆情发展
├── 热度阶段
├── 扩散方向
├── 正负面变化
├── 风险等级
└── 观察窗口

消费者态度
├── 正向反馈
├── 负向反馈
├── 购买阻力
├── 可放大卖点
└── 原始证据

利弊分析
├── 有利因素
├── 不利因素
├── 短期机会
├── 长期风险
└── 可验证假设

增长行动台
├── 建议标题
├── 优先级
├── 适用团队
├── 执行成本
├── 预期指标
├── 证据来源
└── 状态

证据链卡片
├── 洞察结论
├── 关键数据
├── 来源链接
├── AI 判断理由
├── 置信度
└── 推荐动作

机会矩阵
├── 立即执行
├── 持续观察
├── 储备验证
└── 暂不投入
```

### 3.3 配置中心 `docs/index.html`

定位：让非技术用户能配置品牌、竞品、行业包和 AI 分析框架。

新增分区：

```text
配置中心右侧可视化面板
├── 基础配置
├── 数据源配置
├── 关键词与标签
├── 行业模板
├── 品牌与竞品
├── AI 模型
├── Skills 能力包
└── 调度与推送
```

新增交互：

- 行业模板选择：美妆个护、食品饮料、母婴宠物。
- 品牌档案编辑：品牌名、别名、主品类、竞品、渠道、重点卖点。
- 竞品档案编辑：竞品名、别名、价格带、主渠道、观察重点。
- 保存前校验：每个品牌至少有一个关键词，每个竞品至少有一个别名。

---

## 4. 数据与配置设计

### 4.1 新增品牌档案配置

新增文件：

```text
config/brand_profiles.yaml
docs/defaults/brand_profiles.yaml
```

建议结构：

```yaml
brands:
  - id: sample_beauty_brand
    name: 示例美妆品牌
    aliases:
      - 示例品牌
      - Sample Beauty
    category: beauty_personal_care
    price_band: mid_high
    channels:
      - xiaohongshu
      - douyin
      - tmall
    selling_points:
      - 修护
      - 敏感肌
    competitors:
      - sample_competitor_a

competitors:
  - id: sample_competitor_a
    name: 示例竞品 A
    aliases:
      - 竞品A
      - Competitor A
    category: beauty_personal_care
    price_band: mid_high
    watch_points:
      - 新品
      - 达人投放
      - 价格促销
```

### 4.2 新增洞察结构

新增文件：

```text
aiyxdata_tradar/report/insight_schema.py
```

建议结构：

```python
from dataclasses import dataclass, field
from typing import Literal


InsightType = Literal[
    "competitor",
    "opinion",
    "consumer",
    "pros_cons",
    "growth_action",
]


@dataclass
class Evidence:
    title: str
    source: str
    url: str = ""
    published_at: str = ""
    sample_count: int = 1
    time_range: str = ""


@dataclass
class InsightItem:
    insight_type: InsightType
    title: str
    summary: str
    confidence: float
    priority: str
    evidence: list[Evidence] = field(default_factory=list)
    conclusion_kind: str = "inference"
    impact_level: str = "medium"
    action_owner: str = ""
    metric: str = ""
    status: str = "pending"
```

字段说明：

- `conclusion_kind`：用于区分 `fact`、`inference`、`recommendation`。
- `impact_level`：用于标记洞察对业务的影响等级，建议值为 `high`、`medium`、`low`。
- `confidence`：用于表达 AI 或规则判断的置信度，范围为 `0.0` 到 `1.0`。
- `evidence.sample_count`：用于记录支持该结论的样本数量。
- `evidence.time_range`：用于记录证据覆盖的时间范围，避免把旧信号误判为当前趋势。

### 4.3 数据展示结构要求

报告页与首页需要围绕“数据 -> 判断 -> 行动”组织展示，不做只有视觉效果、缺少解释路径的图表。

必备展示结构：

- 增长雷达：品牌热度、用户情绪、竞品压力、内容机会、渠道风险、转化潜力。
- 竞品战情面板：竞品动作、涉及平台、用户反应、威胁等级、建议应对动作。
- 趋势时间线：热点上升、负面集中、竞品活动节点、用户关注点变化。
- 机会矩阵：按商业价值和执行难度区分立即执行、持续观察、储备验证、暂不投入。
- 证据链卡片：展示洞察结论、关键数据、来源链接、AI 判断理由、置信度和推荐动作。
- 行动建议台：展示负责人、优先级、状态、验证指标和复盘入口。

验收标准：

- 每个关键图表必须对应一个业务问题。
- 每个关键结论必须能追溯到至少一条证据。
- 每个行动建议必须包含负责人类型和验证指标。
- 页面不依赖深色大屏、炫光或纯装饰动效来表达科技感。

### 4.4 新增行动状态文件

新增运行期文件：

```text
output/data/action_items.json
```

建议结构：

```json
{
  "items": [
    {
      "id": "act_20260613_001",
      "title": "跟进修护成分内容选题",
      "priority": "high",
      "owner": "content",
      "status": "pending",
      "source_report": "2026-06-13/current",
      "created_at": "2026-06-13T09:00:00+08:00",
      "updated_at": "2026-06-13T09:00:00+08:00"
    }
  ]
}
```

---

## 5. 技术路线

### 5.1 后端分层

目标结构：

```text
aiyxdata_tradar/
├── ai/
│   ├── analyzer.py
│   ├── client.py
│   └── formatter.py
├── core/
│   ├── loader.py
│   ├── scheduler.py
│   └── config.py
├── report/
│   ├── generator.py
│   ├── html.py
│   ├── html_v2.py
│   ├── insight_schema.py
│   └── insight_renderer.py
├── workspace/
│   ├── brand_profiles.py
│   └── action_items.py
└── storage/
```

### 5.2 前端分层

目标结构：

```text
docs/
├── home.html
├── index.html
├── assets/
│   ├── style.css
│   ├── script.js
│   ├── brand-workspace.css
│   └── brand-workspace.js
└── defaults/
```

React 工作台补充分层：

```text
web/src/
├── routes/
│   ├── IntelligenceTerminalPage.tsx
│   ├── LegacyDataScreenPage.tsx
│   ├── BrandRiskRadarPage.tsx
│   └── EventAgentPage.tsx
├── components/
│   ├── intelligence/
│   │   ├── TerminalToolbar.tsx
│   │   ├── DecisionSummary.tsx
│   │   ├── TodayOpportunityRiskAction.tsx
│   │   ├── SignalCardShell.tsx
│   │   ├── AIDecisionBrief.tsx
│   │   ├── TerminalConfigButton.tsx
│   │   ├── IntelligenceSegmentNav.tsx
│   │   ├── TerminalSearchBar.tsx
│   │   ├── RiskOpportunityMatrix.tsx
│   │   ├── EventTimeline.tsx
│   │   ├── PlatformSignalRadar.tsx
│   │   ├── DataSourceCoverageMatrix.tsx
│   │   ├── EvidenceChainDrawer.tsx
│   │   └── UpgradeAnalysisPanel.tsx
│   ├── evidence/
│   └── layout/
├── lib/
│   ├── legacyReportAdapter.ts
│   ├── intelligenceExport.ts
│   └── growthApi.ts
└── types/
    ├── intelligenceTerminal.ts
    └── evidence.ts
```

专业情报终端前端原则：

- `/#/intelligence-terminal` 是正式入口，`/#/legacy-screen` 是兼容入口。
- 第一阶段不新增后端依赖，复用 `/html/latest/current.html` 和 `/api/refresh`。
- 通过 `legacyReportAdapter.ts` 抽离 HTML 解析、Shadow DOM 注入和卡片提取逻辑。
- 通过 `components/intelligence/*` 承载今日机会、今日风险、今日行动、情报信号卡和 AI 决策简报。
- 后续再切换到 `/api/intelligence-terminal/*` 结构化接口。

### 5.3 服务接口

新增接口集中在 `docker/server.py`：

```text
GET  /api/brand_profiles/load
POST /api/brand_profiles/save
GET  /api/action_items/list
POST /api/action_items/update
GET  /api/report/latest_summary
```

专业情报终端第一阶段复用接口：

```text
GET  /html/latest/current.html
POST /api/refresh
GET  /config_editor/index.html
```

专业情报终端第二阶段可选新增接口：

```text
GET  /api/intelligence-terminal/summary
GET  /api/intelligence-terminal/signals
GET  /api/intelligence-terminal/events
POST /api/intelligence-terminal/actions
```

### 5.4 测试策略

新增测试目录：

```text
tests/
├── unit/
│   ├── test_brand_profiles.py
│   ├── test_action_items.py
│   ├── test_insight_schema.py
│   └── test_report_rendering.py
└── integration/
    ├── test_config_server_api.py
    └── test_report_generation_smoke.py
```

---

## 6. 任务清单

### Task 1: 工程基线与可测试环境

**Files:**

- Modify: `pyproject.toml`
- Create: `tests/unit/test_imports.py`
- Create: `tests/unit/test_config_load_smoke.py`
- Verify: `.gitignore`

**Step 1: 检查 Git 状态**

Run:

```powershell
git status -sb
```

Expected:

```text
fatal: not a git repository
```

如果仍然不是 Git 仓库，先和项目负责人确认是否初始化。若确认初始化：

```powershell
git init
git add .gitignore README.md pyproject.toml docker-compose.yml Dockerfile
git commit -m "chore: initialize project baseline"
```

**Step 2: 清理运行缓存**

Run:

```powershell
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

Expected:

```text
无错误输出
```

**Step 3: 增加开发依赖**

Modify `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "pytest>=8.2.0,<9.0.0",
    "ruff>=0.6.0,<1.0.0"
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.ruff]
line-length = 100
target-version = "py310"
```

**Step 4: 写导入冒烟测试**

Create `tests/unit/test_imports.py`:

```python
def test_core_modules_import():
    import aiyxdata_tradar
    import aiyxdata_tradar.core.loader
    import aiyxdata_tradar.report.html_v2
    import mcp_server.server

    assert aiyxdata_tradar.__version__
```

**Step 5: 写配置加载冒烟测试**

Create `tests/unit/test_config_load_smoke.py`:

```python
from aiyxdata_tradar.core.loader import load_config


def test_config_loads_default_runtime_file():
    config = load_config("config/config.yaml")

    assert "PLATFORMS" in config
    assert "RSS" in config
    assert "AI" in config
    assert "STORAGE" in config
```

**Step 6: 执行测试**

Run:

```powershell
python -m pytest tests/unit/test_imports.py tests/unit/test_config_load_smoke.py -v
```

Expected:

```text
2 passed
```

**Step 7: 提交**

Run:

```powershell
git add pyproject.toml tests/unit/test_imports.py tests/unit/test_config_load_smoke.py
git commit -m "test: add project smoke tests"
```

---

### Task 2: 品牌与竞品档案配置

**Files:**

- Create: `config/brand_profiles.yaml`
- Create: `docs/defaults/brand_profiles.yaml`
- Create: `aiyxdata_tradar/workspace/__init__.py`
- Create: `aiyxdata_tradar/workspace/brand_profiles.py`
- Create: `tests/unit/test_brand_profiles.py`
- Modify: `Dockerfile`
- Modify: `docker/entrypoint.sh`

**Step 1: 写失败测试**

Create `tests/unit/test_brand_profiles.py`:

```python
from pathlib import Path

from aiyxdata_tradar.workspace.brand_profiles import load_brand_profiles, validate_brand_profiles


def test_load_brand_profiles(tmp_path: Path):
    profile_file = tmp_path / "brand_profiles.yaml"
    profile_file.write_text(
        """
brands:
  - id: demo_brand
    name: 示例品牌
    aliases: [示例品牌, Demo Brand]
    category: beauty_personal_care
    competitors: [demo_competitor]
competitors:
  - id: demo_competitor
    name: 示例竞品
    aliases: [竞品A]
""",
        encoding="utf-8",
    )

    data = load_brand_profiles(profile_file)

    assert data["brands"][0]["id"] == "demo_brand"
    assert data["competitors"][0]["id"] == "demo_competitor"


def test_validate_brand_profiles_requires_aliases():
    data = {"brands": [{"id": "demo", "name": "Demo"}], "competitors": []}

    valid, error = validate_brand_profiles(data)

    assert not valid
    assert "aliases" in error
```

**Step 2: 运行测试确认失败**

Run:

```powershell
python -m pytest tests/unit/test_brand_profiles.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'aiyxdata_tradar.workspace'
```

**Step 3: 实现品牌档案加载器**

Create `aiyxdata_tradar/workspace/__init__.py`:

```python
"""品牌工作区模块。"""
```

Create `aiyxdata_tradar/workspace/brand_profiles.py`:

```python
from pathlib import Path
from typing import Any

import yaml


def load_brand_profiles(path: str | Path = "config/brand_profiles.yaml") -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {"brands": [], "competitors": []}

    with target.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    data.setdefault("brands", [])
    data.setdefault("competitors", [])
    return data


def validate_brand_profiles(data: dict[str, Any]) -> tuple[bool, str]:
    for section in ("brands", "competitors"):
        entries = data.get(section, [])
        if not isinstance(entries, list):
            return False, f"{section} must be a list"
        for index, item in enumerate(entries, 1):
            if not item.get("id"):
                return False, f"{section}[{index}] missing id"
            if not item.get("name"):
                return False, f"{section}[{index}] missing name"
            aliases = item.get("aliases", [])
            if not aliases:
                return False, f"{section}[{index}] missing aliases"
    return True, ""
```

**Step 4: 创建默认配置**

Create `config/brand_profiles.yaml` and `docs/defaults/brand_profiles.yaml`:

```yaml
brands:
  - id: sample_beauty_brand
    name: 示例美妆品牌
    aliases:
      - 示例品牌
      - Sample Beauty
    category: beauty_personal_care
    price_band: mid_high
    channels:
      - xiaohongshu
      - douyin
      - tmall
    selling_points:
      - 修护
      - 敏感肌
    competitors:
      - sample_competitor_a

competitors:
  - id: sample_competitor_a
    name: 示例竞品 A
    aliases:
      - 竞品A
      - Competitor A
    category: beauty_personal_care
    price_band: mid_high
    watch_points:
      - 新品
      - 达人投放
      - 价格促销
```

**Step 5: 同步到 Docker 默认配置**

Modify `Dockerfile`:

```dockerfile
COPY config/brand_profiles.yaml /app/default-config/brand_profiles.yaml
COPY docs/defaults/brand_profiles.yaml /app/default-output/config_editor/defaults/brand_profiles.yaml
```

Modify `docker/entrypoint.sh`:

```bash
seed_file "/app/default-config/brand_profiles.yaml" "/app/config/brand_profiles.yaml"
```

**Step 6: 运行测试**

Run:

```powershell
python -m pytest tests/unit/test_brand_profiles.py -v
```

Expected:

```text
2 passed
```

**Step 7: 提交**

Run:

```powershell
git add config/brand_profiles.yaml docs/defaults/brand_profiles.yaml aiyxdata_tradar/workspace tests/unit/test_brand_profiles.py Dockerfile docker/entrypoint.sh
git commit -m "feat: add brand and competitor profiles"
```

---

### Task 3: 可信洞察数据结构

**Files:**

- Create: `aiyxdata_tradar/report/insight_schema.py`
- Create: `tests/unit/test_insight_schema.py`

**Step 1: 写失败测试**

Create `tests/unit/test_insight_schema.py`:

```python
from aiyxdata_tradar.report.insight_schema import Evidence, InsightItem, clamp_confidence


def test_insight_item_defaults():
    item = InsightItem(
        insight_type="growth_action",
        title="跟进修护内容选题",
        summary="消费者对修护成分讨论升温",
        confidence=1.5,
        priority="high",
    )

    assert item.status == "pending"
    assert clamp_confidence(item.confidence) == 1.0


def test_evidence_requires_title_and_source():
    evidence = Evidence(title="示例标题", source="RSS")

    assert evidence.title == "示例标题"
    assert evidence.source == "RSS"
```

**Step 2: 运行测试确认失败**

Run:

```powershell
python -m pytest tests/unit/test_insight_schema.py -v
```

Expected:

```text
ModuleNotFoundError
```

**Step 3: 实现结构**

Create `aiyxdata_tradar/report/insight_schema.py`:

```python
from dataclasses import dataclass, field
from typing import Literal


InsightType = Literal[
    "competitor",
    "opinion",
    "consumer",
    "pros_cons",
    "growth_action",
]


@dataclass
class Evidence:
    title: str
    source: str
    url: str = ""
    published_at: str = ""


@dataclass
class InsightItem:
    insight_type: InsightType
    title: str
    summary: str
    confidence: float
    priority: str
    evidence: list[Evidence] = field(default_factory=list)
    action_owner: str = ""
    metric: str = ""
    status: str = "pending"


def clamp_confidence(value: float) -> float:
    return min(1.0, max(0.0, float(value)))
```

**Step 4: 运行测试**

Run:

```powershell
python -m pytest tests/unit/test_insight_schema.py -v
```

Expected:

```text
2 passed
```

**Step 5: 提交**

Run:

```powershell
git add aiyxdata_tradar/report/insight_schema.py tests/unit/test_insight_schema.py
git commit -m "feat: add trusted insight schema"
```

---

### Task 4: AI 分析提示词升级

**Files:**

- Modify: `config/ai_analysis_prompt.txt`
- Modify: `docs/defaults/ai_analysis_prompt.txt`
- Modify: `aiyxdata_tradar/ai/analyzer.py`
- Create: `tests/unit/test_ai_prompt_contract.py`

**Step 1: 写提示词契约测试**

Create `tests/unit/test_ai_prompt_contract.py`:

```python
from pathlib import Path


def test_ai_prompt_requires_evidence_and_action_sections():
    prompt = Path("config/ai_analysis_prompt.txt").read_text(encoding="utf-8")

    required_terms = [
        "竞品战情",
        "舆情发展",
        "消费者态度",
        "利弊分析",
        "增长建议",
        "事实",
        "推测",
        "证据",
        "置信度",
    ]
    for term in required_terms:
        assert term in prompt
```

**Step 2: 运行测试确认失败或不完整**

Run:

```powershell
python -m pytest tests/unit/test_ai_prompt_contract.py -v
```

Expected:

```text
FAIL if prompt lacks required terms
```

**Step 3: 升级提示词结构**

Modify `config/ai_analysis_prompt.txt` and `docs/defaults/ai_analysis_prompt.txt`:

```text
你是品牌增长情报分析师。请基于输入数据生成结构化商业报告。

必须区分：
1. 事实：输入数据中能直接证明的信息。
2. 推测：基于多个信号的合理判断。
3. 建议：可执行动作，必须说明适用团队和验证指标。

必须输出以下模块：
1. 经营摘要
2. 竞品战情
3. 舆情发展
4. 消费者态度
5. 利弊分析
6. 增长建议
7. 证据与置信度

每条关键结论必须包含：
- 结论标题
- 类型：事实 / 推测 / 建议
- 置信度：0.0 到 1.0
- 证据标题：至少 1 条
- 来源平台或 RSS 源
- 建议负责人：content / marketing / product / commerce / pr
- 验证指标
```

**Step 4: 调整 AI 输入摘要**

Modify `aiyxdata_tradar/ai/analyzer.py`:

- 确保传入 AI 的新闻数据保留标题、来源、URL、发布时间。
- 限制每个模块最大输入条数，避免 token 爆炸。
- 禁止在 debug 关闭时打印完整 API Key 或完整提示词。

**Step 5: 运行测试**

Run:

```powershell
python -m pytest tests/unit/test_ai_prompt_contract.py -v
```

Expected:

```text
1 passed
```

**Step 6: 提交**

Run:

```powershell
git add config/ai_analysis_prompt.txt docs/defaults/ai_analysis_prompt.txt aiyxdata_tradar/ai/analyzer.py tests/unit/test_ai_prompt_contract.py
git commit -m "feat: require evidence-based ai analysis"
```

---

### Task 5: 报告页商业化重排

**Files:**

- Modify: `aiyxdata_tradar/report/html_v2.py`
- Create: `aiyxdata_tradar/report/insight_renderer.py`
- Create: `tests/unit/test_report_rendering.py`

**Step 1: 写渲染测试**

Create `tests/unit/test_report_rendering.py`:

```python
from aiyxdata_tradar.report.insight_renderer import render_executive_summary
from aiyxdata_tradar.report.insight_schema import InsightItem, Evidence


def test_render_executive_summary_contains_business_sections():
    items = [
        InsightItem(
            insight_type="growth_action",
            title="跟进达人测评内容",
            summary="达人测评讨论增加",
            confidence=0.82,
            priority="high",
            evidence=[Evidence(title="测评内容升温", source="RSS")],
        )
    ]

    html = render_executive_summary(items)

    assert "经营摘要" in html
    assert "跟进达人测评内容" in html
    assert "置信度" in html
```

**Step 2: 运行测试确认失败**

Run:

```powershell
python -m pytest tests/unit/test_report_rendering.py -v
```

Expected:

```text
ModuleNotFoundError
```

**Step 3: 实现渲染器**

Create `aiyxdata_tradar/report/insight_renderer.py`:

```python
import html

from aiyxdata_tradar.report.insight_schema import InsightItem, clamp_confidence


def render_executive_summary(items: list[InsightItem]) -> str:
    cards = []
    for item in items[:6]:
        confidence = int(clamp_confidence(item.confidence) * 100)
        cards.append(
            f"""
            <article class="intel-card">
                <div class="intel-card__meta">{html.escape(item.priority)} · 置信度 {confidence}%</div>
                <h3>{html.escape(item.title)}</h3>
                <p>{html.escape(item.summary)}</p>
            </article>
            """
        )

    return f"""
    <section class="intel-section" id="executive-summary">
        <div class="intel-section__header">
            <h2>经营摘要</h2>
            <p>面向品牌晨会与周会的关键判断。</p>
        </div>
        <div class="intel-grid">
            {''.join(cards)}
        </div>
    </section>
    """
```

**Step 4: 接入 `html_v2.py`**

Modify `aiyxdata_tradar/report/html_v2.py`:

- 在主报告网格前加入 `经营摘要`。
- 在 AI 分析卡前加入 `市场信号雷达`。
- 保留原始热榜/RSS/搜索能力。
- 新 CSS 命名使用 `intel-*` 前缀，避免污染旧样式。

**Step 5: 运行测试**

Run:

```powershell
python -m pytest tests/unit/test_report_rendering.py -v
```

Expected:

```text
1 passed
```

**Step 6: 人工验收**

Run:

```powershell
docker compose up -d --build
```

Open:

```text
http://127.0.0.1:8094/html/latest/current.html
```

Expected:

- 页面顶部有经营摘要。
- 五大模块排版清楚。
- 旧报告数据仍可见。
- 移动端不重叠。

**Step 7: 提交**

Run:

```powershell
git add aiyxdata_tradar/report/html_v2.py aiyxdata_tradar/report/insight_renderer.py tests/unit/test_report_rendering.py
git commit -m "feat: add boardroom report layout"
```

---

### Task 6: 行动建议台

**Files:**

- Create: `aiyxdata_tradar/workspace/action_items.py`
- Create: `tests/unit/test_action_items.py`
- Modify: `docker/server.py`
- Modify: `docs/assets/script.js`
- Modify: `docs/assets/style.css`

**Step 1: 写行动项测试**

Create `tests/unit/test_action_items.py`:

```python
from pathlib import Path

from aiyxdata_tradar.workspace.action_items import list_action_items, update_action_item


def test_update_action_item_creates_file(tmp_path: Path):
    target = tmp_path / "action_items.json"

    update_action_item(
        target,
        {
            "id": "act_001",
            "title": "跟进内容选题",
            "status": "pending",
        },
    )

    items = list_action_items(target)

    assert items[0]["id"] == "act_001"
    assert items[0]["status"] == "pending"
```

**Step 2: 实现行动项存储**

Create `aiyxdata_tradar/workspace/action_items.py`:

```python
import json
from pathlib import Path
from typing import Any


def list_action_items(path: str | Path = "output/data/action_items.json") -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []
    data = json.loads(target.read_text(encoding="utf-8"))
    return data.get("items", [])


def update_action_item(path: str | Path, item: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    items = list_action_items(target)
    item_id = item["id"]
    next_items = [existing for existing in items if existing.get("id") != item_id]
    next_items.insert(0, item)
    target.write_text(
        json.dumps({"items": next_items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
```

**Step 3: 增加服务接口**

Modify `docker/server.py`:

```python
elif path == "/api/action_items/list":
    from aiyxdata_tradar.workspace.action_items import list_action_items

    return self.send_json_response(200, {"success": True, "items": list_action_items()})
```

在 `do_POST` 中增加：

```python
elif path == "/api/action_items/update":
    from aiyxdata_tradar.workspace.action_items import update_action_item

    item = payload.get("item", {})
    if not item.get("id"):
        return self.send_json_response(400, {"success": False, "error": "Missing action id"})
    update_action_item("output/data/action_items.json", item)
    return self.send_json_response(200, {"success": True})
```

**Step 4: 前端增加状态控件**

Modify `docs/assets/script.js`:

- 新增 `loadActionItems()`
- 新增 `updateActionStatus(id, status)`
- 状态值：`pending`、`accepted`、`doing`、`done`、`rejected`

Modify `docs/assets/style.css`:

- 新增 `.action-board`
- 新增 `.action-status`
- 新增 `.action-priority`

**Step 5: 运行测试**

Run:

```powershell
python -m pytest tests/unit/test_action_items.py -v
```

Expected:

```text
1 passed
```

**Step 6: 手动验收**

Open:

```text
http://127.0.0.1:8094/config_editor/index.html
```

Expected:

- 能看到行动项区域。
- 能修改行动状态。
- 刷新后状态仍保留。

**Step 7: 提交**

Run:

```powershell
git add aiyxdata_tradar/workspace/action_items.py tests/unit/test_action_items.py docker/server.py docs/assets/script.js docs/assets/style.css
git commit -m "feat: add growth action board"
```

---

### Task 7: 配置中心品牌工作区

**Files:**

- Modify: `docs/index.html`
- Modify: `docs/assets/script.js`
- Modify: `docs/assets/style.css`
- Modify: `docker/server.py`
- Create: `tests/integration/test_brand_profile_api.py`

**Step 1: 增加 API 测试**

Create `tests/integration/test_brand_profile_api.py`:

```python
from aiyxdata_tradar.workspace.brand_profiles import validate_brand_profiles


def test_brand_profile_validation_accepts_default_shape():
    data = {
        "brands": [{"id": "demo", "name": "Demo", "aliases": ["Demo"]}],
        "competitors": [{"id": "other", "name": "Other", "aliases": ["Other"]}],
    }

    valid, error = validate_brand_profiles(data)

    assert valid
    assert error == ""
```

**Step 2: 增加服务端接口**

Modify `docker/server.py`:

```python
elif path == "/api/brand_profiles/load":
    from aiyxdata_tradar.workspace.brand_profiles import load_brand_profiles

    return self.send_json_response(200, {"success": True, "data": load_brand_profiles()})
```

在 `do_POST` 中增加：

```python
elif path == "/api/brand_profiles/save":
    from aiyxdata_tradar.workspace.brand_profiles import validate_brand_profiles

    data = payload.get("data", {})
    valid, error = validate_brand_profiles(data)
    if not valid:
        return self.send_json_response(400, {"success": False, "error": error})

    target_file = CONFIG_DIR / "brand_profiles.yaml"
    with target_file.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, allow_unicode=True, sort_keys=False)
    return self.send_json_response(200, {"success": True})
```

**Step 3: 配置中心新增品牌工作区**

Modify `docs/index.html`:

- 在右侧模块导航加入 `品牌工作区`。
- 在配置模块区域加入品牌列表、竞品列表、行业模板入口。

Modify `docs/assets/script.js`:

- `renderBrandWorkspace(data)`
- `addBrandProfile()`
- `addCompetitorProfile()`
- `saveBrandProfiles()`

Modify `docs/assets/style.css`:

- `.brand-workspace`
- `.brand-profile-card`
- `.competitor-profile-card`
- `.industry-template-picker`

**Step 4: 运行测试**

Run:

```powershell
python -m pytest tests/integration/test_brand_profile_api.py -v
```

Expected:

```text
1 passed
```

**Step 5: 手动验收**

Open:

```text
http://127.0.0.1:8094/config_editor/index.html
```

Expected:

- 右侧可看到品牌工作区。
- 能新增品牌与竞品。
- 缺少 aliases 时保存失败并给出错误提示。
- 保存后 `config/brand_profiles.yaml` 更新。

**Step 6: 提交**

Run:

```powershell
git add docs/index.html docs/assets/script.js docs/assets/style.css docker/server.py tests/integration/test_brand_profile_api.py
git commit -m "feat: add brand workspace in config center"
```

---

### Task 8: 行业模板包

**Files:**

- Modify: `config/industry_packs.yaml`
- Modify: `docs/defaults/config.yaml`
- Modify: `config/skills.yaml`
- Modify: `docs/defaults/skills.yaml`
- Create: `tests/unit/test_industry_packs.py`

**Step 1: 写行业包测试**

Create `tests/unit/test_industry_packs.py`:

```python
from pathlib import Path

import yaml


def test_industry_packs_have_required_sections():
    data = yaml.safe_load(Path("config/industry_packs.yaml").read_text(encoding="utf-8"))

    for key in ["beauty_personal_care", "food_beverage", "mother_baby_pet"]:
        assert key in data
        assert data[key]["keywords"]
        assert data[key]["risk_words"]
        assert data[key]["analysis_focus"]
```

**Step 2: 补充行业模板**

Modify `config/industry_packs.yaml`:

```yaml
beauty_personal_care:
  name: 美妆个护
  keywords:
    - 修护
    - 抗老
    - 敏感肌
    - 成分
    - 功效
  risk_words:
    - 过敏
    - 烂脸
    - 虚假宣传
    - 刺激
  analysis_focus:
    - 成分可信度
    - 达人测评
    - 价格带
    - 复购口碑

food_beverage:
  name: 食品饮料
  keywords:
    - 无糖
    - 低卡
    - 高蛋白
    - 即饮
  risk_words:
    - 食安
    - 添加剂
    - 口感翻车
  analysis_focus:
    - 场景消费
    - 渠道动销
    - 价格促销

mother_baby_pet:
  name: 母婴宠物
  keywords:
    - 安全
    - 营养
    - 适口性
    - 舒缓
  risk_words:
    - 过敏
    - 不适
    - 安全隐患
  analysis_focus:
    - 信任背书
    - 专业测评
    - 社群口碑
```

**Step 3: 运行测试**

Run:

```powershell
python -m pytest tests/unit/test_industry_packs.py -v
```

Expected:

```text
1 passed
```

**Step 4: 提交**

Run:

```powershell
git add config/industry_packs.yaml config/skills.yaml docs/defaults/skills.yaml tests/unit/test_industry_packs.py
git commit -m "feat: add consumer industry packs"
```

---

### Task 9: 首页产品化优化

**Files:**

- Modify: `docs/home.html`
- Create: `tests/unit/test_homepage_contract.py`

**Step 1: 写首页契约测试**

Create `tests/unit/test_homepage_contract.py`:

```python
from pathlib import Path


def test_homepage_contains_core_product_entry_points():
    html = Path("docs/home.html").read_text(encoding="utf-8")

    assert "AYX Growth Intel" in html
    assert "/html/latest/current.html" in html
    assert "/config_editor/index.html" in html
    assert "竞品战情" in html
    assert "消费者态度" in html
    assert "增长建议" in html
```

**Step 2: 优化首页文案**

Modify `docs/home.html`:

- H1 使用品牌工作台定位，不写空泛口号。
- CTA 保留最新报告和配置中心。
- 五大模块保留，但每个模块增加更明确业务问题。
- 移动端保持单列，不出现文字溢出。

建议文案：

```text
每天给品牌团队一份可执行的增长情报。
```

模块问题：

```text
竞品战情：谁在抢你的增长窗口？
舆情发展：话题处于爆发、扩散还是衰退？
消费者态度：用户为什么买，为什么犹豫？
利弊分析：这次机会值得跟吗？
增长建议：今天应该让谁做什么？
```

**Step 3: 运行测试**

Run:

```powershell
python -m pytest tests/unit/test_homepage_contract.py -v
```

Expected:

```text
1 passed
```

**Step 4: 视觉验收**

Open:

```text
http://127.0.0.1:8094/
```

Expected:

- 第一屏明确是 AYX Growth Intel。
- 用户不需要阅读说明即可找到最新报告和配置中心。
- 颜色不单调，不是纯蓝或纯紫主题。
- 1366px、390px 宽度下没有明显重叠。

**Step 5: 提交**

Run:

```powershell
git add docs/home.html tests/unit/test_homepage_contract.py
git commit -m "feat: refine product homepage"
```

---

### Task 10: 配置服务拆分与安全加固

**Files:**

- Modify: `docker/server.py`
- Create: `docker/api_handlers.py`
- Create: `tests/unit/test_config_server_validation.py`

**Step 1: 写校验测试**

Create `tests/unit/test_config_server_validation.py`:

```python
from docker.api_handlers import is_safe_profile_name


def test_profile_name_rejects_path_traversal():
    assert not is_safe_profile_name("../secret")
    assert not is_safe_profile_name("a/b")
    assert is_safe_profile_name("beauty_default")
```

**Step 2: 抽出 API 工具函数**

Create `docker/api_handlers.py`:

```python
import re


def is_safe_profile_name(value: str) -> bool:
    return bool(re.match(r"^[A-Za-z0-9_-]{1,80}$", value or ""))
```

**Step 3: 修改 `docker/server.py`**

- 复用 `is_safe_profile_name()`。
- 将 profile 名称校验从内联判断改为统一函数。
- 对所有写入 API 增加 JSON body 大小限制。
- 写入配置前统一做 UTF-8 和 YAML 校验。

**Step 4: 运行测试**

Run:

```powershell
python -m pytest tests/unit/test_config_server_validation.py -v
```

Expected:

```text
1 passed
```

**Step 5: 提交**

Run:

```powershell
git add docker/server.py docker/api_handlers.py tests/unit/test_config_server_validation.py
git commit -m "refactor: harden config server api validation"
```

---

### Task 11: Docker 与发布验收

**Files:**

- Modify: `.dockerignore`
- Modify: `DEPLOYMENT.md`
- Modify: `README.md`
- Verify: `scripts/check_release_secrets.sh`

**Step 1: 创建或更新 `.dockerignore`**

Create/Modify `.dockerignore`:

```text
.git
.env
.env.*
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
output/
data/
logs/
docs/plans/
tests/
```

**Step 2: 更新部署文档**

Modify `DEPLOYMENT.md`:

- 增加品牌档案配置说明。
- 增加行业包配置说明。
- 增加 AI Key 与 API Base 注意事项。
- 增加常见失败排查。

**Step 3: 更新 README**

Modify `README.md`:

- 当前版本定位改为“品牌增长工作台”。
- 新增开发路线。
- 新增商业化最小版本说明。
- 明确 source-only、Docker 部署、AI 配置边界。

**Step 4: 发布检查**

Run:

```powershell
bash scripts/check_release_secrets.sh .
```

Expected:

```text
Release secret scan OK: .
```

**Step 5: Docker 构建**

Run:

```powershell
docker compose up -d --build
```

Expected:

```text
容器 ayx_growth_intel 和 ayx_growth_intel_mcp 正常启动
```

**Step 6: 手动访问**

Open:

```text
http://127.0.0.1:8094/
http://127.0.0.1:8094/config_editor/index.html
http://127.0.0.1:8094/html/latest/current.html
http://127.0.0.1:3344/mcp
```

Expected:

- 首页可访问。
- 配置中心可读取配置。
- 最新报告可访问或显示等待生成。
- MCP 服务端口打开。

**Step 7: 提交**

Run:

```powershell
git add .dockerignore DEPLOYMENT.md README.md
git commit -m "docs: update deployment and product roadmap"
```

---

## 7. 验收标准

### 7.1 工程验收

必须通过：

```powershell
python -m pytest tests -v
python -m compileall -q aiyxdata_tradar mcp_server docker
bash scripts/check_release_secrets.sh .
docker compose up -d --build
```

### 7.2 产品验收

必须满足：

- 首页清楚表达“品牌增长情报工作台”。
- 最新报告包含经营摘要、五大分析模块和增长行动建议。
- 每条关键 AI 结论至少展示证据标题或来源。
- 配置中心可以维护品牌与竞品档案。
- 行动建议可标记状态。
- 默认配置不包含真实密钥。

### 7.3 UI 验收

必须检查：

- 桌面 1366x768。
- 宽屏 1920x1080。
- 移动端 390x844。
- 首页、配置中心、报告页无文字重叠。
- 主要按钮文案不溢出。
- 卡片内标题不使用过大字号。
- 不使用 emoji 作为功能图标。

---

## 8. 迭代节奏

### Week 1: 工程治理与可信报告

- Task 1
- Task 2
- Task 3
- Task 4

交付物：

- 可测试工程基线。
- 品牌档案配置。
- 可信洞察结构。
- 证据化 AI 提示词。

### Week 2: 报告页与行动闭环

- Task 5
- Task 6
- Task 8

交付物：

- 商业化报告页。
- 增长行动台。
- 行业模板包。

### Week 3: 配置中心与发布验收

- Task 7
- Task 9
- Task 10
- Task 11

交付物：

- 品牌工作区。
- 首页优化。
- 配置服务安全加固。
- Docker 可演示版本。

---

## 9. 交付目录总览

最终主要路径：

```text
D:\Docker\202606100809-ayx-growth-intel
├── README.md
├── DEPLOYMENT.md
├── pyproject.toml
├── docker-compose.yml
├── Dockerfile
├── config
│   ├── config.yaml
│   ├── brand_profiles.yaml
│   ├── industry_packs.yaml
│   ├── ai_analysis_prompt.txt
│   └── skills.yaml
├── docs
│   ├── home.html
│   ├── index.html
│   ├── plans
│   │   └── 2026-06-13-ayx-growth-intel-commercial-upgrade.md
│   ├── defaults
│   │   └── brand_profiles.yaml
│   └── assets
│       ├── style.css
│       └── script.js
├── aiyxdata_tradar
│   ├── report
│   │   ├── insight_schema.py
│   │   ├── insight_renderer.py
│   │   └── html_v2.py
│   └── workspace
│       ├── brand_profiles.py
│       └── action_items.py
├── docker
│   ├── server.py
│   └── api_handlers.py
└── tests
    ├── unit
    └── integration
```

---

## 10. 风险与回滚

### 风险 1: AI 输出不可控

缓解：

- 强制提示词契约。
- 报告里区分事实、推测、建议。
- 每条建议展示来源和置信度。

回滚：

- 保留原 AI 原文区。
- 若结构化解析失败，回退到原始 AI 分析卡片。

### 风险 2: 配置中心变复杂

缓解：

- 不一次性重写配置中心。
- 品牌工作区作为新模块接入。
- 原 YAML 编辑器保留。

回滚：

- 隐藏品牌工作区入口。
- 继续使用原始 YAML 配置。

### 风险 3: Docker 构建受网络影响

缓解：

- 保留当前 requirements 文件。
- 构建失败时先检查 supercronic 下载和 pip 源。

回滚：

- 使用已有镜像运行旧版本。

### 风险 4: 大文件继续膨胀

缓解：

- 新功能尽量新增模块，不继续扩大 `__main__.py`。
- 每个新模块必须有测试。

回滚：

- 新模块独立，删除入口调用即可恢复旧流程。

---

## 11. 最终演示脚本

演示顺序：

1. 打开首页：`http://127.0.0.1:8094/`
2. 说明产品定位：品牌增长情报工作台。
3. 打开配置中心：`http://127.0.0.1:8094/config_editor/index.html`
4. 展示品牌档案、竞品档案、行业模板、AI 配置。
5. 触发一次分析或打开最新报告。
6. 展示经营摘要、竞品战情、消费者态度和增长建议。
7. 修改一条行动建议状态。
8. 说明下一周期可以复盘执行结果。

成功标准：

- 用户能在 5 分钟内理解产品用途。
- 用户能在 10 分钟内完成一个品牌配置。
- 用户能在报告里看到可执行建议和证据来源。
- 开发团队能基于测试继续迭代。
