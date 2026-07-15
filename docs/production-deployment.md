# 生产部署指南

## 架构

`docker-compose.prod.yml` 启动四个内部服务：

- `gateway`：Caddy 提供 HTTPS、Basic Auth、静态前端和 `/api` 反向代理。
- `backend`：FastAPI 业务服务，仅暴露在 Docker 内网。
- `crawler`：Playwright 浏览器采集服务，仅接受内部后端调用。
- `scheduler`：按 `COLLECT_INTERVAL_SECONDS` 调用后端采集接口。

用户只访问 `https://APP_DOMAIN`；后端、数据库和爬虫端口不会暴露到公网。

## 首次部署

1. 在服务器防火墙放行 TCP `80` 和 `443`。
2. 将域名 A/AAAA 记录解析到服务器公网 IP。
3. 克隆仓库并复制 `.env.example` 为 `.env`。
4. 使用 `docker run --rm caddy:2.10.2-alpine caddy hash-password --plaintext '强密码'` 生成 `APP_ADMIN_PASSWORD_HASH`；写入 `.env` 前，将哈希中的每个 `$` 替换成 `$$`，避免 Docker Compose 将其解释为变量。
5. 填写 `.env` 中的域名、邮箱、管理账号密码哈希和 AI 配置。
6. 执行 `docker compose -f docker-compose.prod.yml up -d --build`。
7. 使用 `docker compose -f docker-compose.prod.yml ps` 确认四个服务健康。

Caddy 会自动申请和续期 HTTPS 证书；域名 DNS 必须在启动前生效。

## 数据与备份

业务数据写入 Docker 卷 `aiyx-data-inteli_aiyx_data`。定期备份：

```bash
docker run --rm -v aiyx-data-inteli_aiyx_data:/data -v "$PWD:/backup" alpine tar czf /backup/aiyx-data-$(date +%F).tgz -C /data .
```

社媒 JSON 导入目录是 `data/social-intel/`。将合规授权的 JSON 文件放入该目录后，下一次采集会自动导入。

## 日常操作

```bash
# 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 更新到最新代码
git pull
docker compose -f docker-compose.prod.yml up -d --build

# 停止服务，但保留业务数据
docker compose -f docker-compose.prod.yml down
```

## 兼容性

现有 `docker-compose.yml` 不会被替换，仍可用于本机开发。生产编排通过 `AYX_WEB_INTEL_ENDPOINT=http://crawler:11235` 将网页采集指向内置服务；未设置该变量时，程序继续使用原有 `config/sources.yaml` 中的 `web_intel.endpoint`。

