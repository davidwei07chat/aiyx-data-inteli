# AiYX DATA INTELI

开发人：魏杰

独立新版多源商业情报、舆情分析与 AI 知识库系统，不依赖也不修改旧版程序。

## 功能范围

- 多源采集任务：RSS、公开网页、社媒数据导入、授权数据同步
- 轻量优先：先采集标题、摘要、作者、发布时间、互动指标和评论摘要
- 按需正文：只有高风险、高热度或报告引用内容才进入全文抓取队列
- 舆情分析：关键词命中、核心词命中、情绪倾向、风险等级、热度评分
- 知识库准备：内容分块入库，后续可接入 pgvector、Qdrant、Milvus
- Web 工作台：任务创建、风险概览、文章与评论证据浏览

## 快速启动

```bash
cd 202607092030-ayx-growth-intel-fusion
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
python -m ayx_growth_intel.api.main --config config/sources.yaml
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## Docker

```bash
docker compose up --build -d
```

本目录是 AiYX DATA INTELI 的独立 Docker 部署版，不依赖旧项目目录，也不复用旧容器。

- 前端访问：`http://127.0.0.1:15179/#industry`
- 后端 API：`http://127.0.0.1:18088`
- 后端健康检查：`http://127.0.0.1:18088/health`
- 后端镜像：`aiyx-data-inteli-backend:standalone`
- 前端镜像：`aiyx-data-inteli-frontend:standalone`
- 后端容器：`aiyx-data-inteli-backend`
- 前端容器：`aiyx-data-inteli-frontend`
- 数据卷：`aiyx_data_inteli_data`

停止：

```bash
docker compose down
```

清理独立数据卷：

```bash
docker compose down -v
```

网页智能采集服务默认作为外部服务接入，配置在 `config/sources.yaml` 的采集服务端点。

## 社媒数据接入

本项目推荐通过授权数据、公开数据或外部采集结果导入方式接入社媒内容。将标准 JSON 放入：

```text
data/social-intel/*.json
```

系统会将其标准化为统一的 `articles`、`comments`、`metrics` 数据。

## 合规边界

本系统只提供合规采集、授权数据导入、公开网页抽取和合理频率控制能力。不提供规避风控、绕过登录限制、验证码绕过或平台限制规避方案。
