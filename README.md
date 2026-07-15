# AiYX DATA INTELI

面向行业情报、舆情风险和市场动态的多源采集与分析平台。

## 生产部署

部署服务器需要：Docker Engine、Docker Compose、已解析到服务器公网 IP 的域名，以及可用的 AI API Key。

```bash
git clone https://github.com/davidwei07chat/aiyx-data-inteli.git
cd aiyx-data-inteli
cp .env.example .env
```

生成管理入口密码哈希；粘贴到 `.env` 前，将输出中的每个 `$` 替换为 `$$`：

```bash
docker run --rm caddy:2.10.2-alpine caddy hash-password --plaintext '替换为强密码'
```

在 `.env` 中填写：

- `APP_DOMAIN`：服务器域名，例如 `intel.example.com`
- `ACME_EMAIL`：用于 HTTPS 证书通知的邮箱
- `APP_ADMIN_USER` 和 `APP_ADMIN_PASSWORD_HASH`：管理入口凭据
- `AI_API_KEY`、`AI_API_BASE`、`AI_MODEL`：你的 AI 服务配置

启动完整生产服务：

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

访问 `https://你的域名`。部署包会自动启动 Web 页面、API、内置浏览器爬虫和定时采集任务；对外仅开放 `80` 和 `443`。

详细步骤、备份和故障排查见 `docs/production-deployment.md`。

## 本地开发

原有本地启动方式保持不变：

```bash
docker compose up --build -d
```

本地开发使用 `docker-compose.yml`，生产服务器使用 `docker-compose.prod.yml`。

## 安全

不要提交 `.env` 或 `config/.env`。如果曾在任何位置暴露 API Key，请立即在对应服务商后台撤销并重新生成。

