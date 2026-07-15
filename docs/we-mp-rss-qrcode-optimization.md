# We-MP-RSS 二维码获取优化复盘文档

**文档版本**: 1.0
**创建日期**: 2026-03-06
**作者**: Claude Code
**状态**: 已完成

---

## 目录

1. [背景与问题](#1-背景与问题)
2. [问题诊断](#2-问题诊断)
3. [实施过程](#3-实施过程)
4. [遇到的问题与解决方案](#4-遇到的问题与解决方案)
5. [最终修改内容](#5-最终修改内容)
6. [优化效果](#6-优化效果)
7. [部署配置](#7-部署配置)
8. [后续建议](#8-后续建议)

---

## 1. 背景与问题

### 1.1 项目概述

**WeRSS (微信公众号订阅助手)** 是一个微信公众号 RSS 订阅服务，部署在服务器上通过 Docker 容器运行。

**服务架构**:
```
用户浏览器
    ↓
https://werss.aiyxtech.us.kg (Cloudflare CDN)
    ↓
服务器 45.78.226.155:443 (NGINX)
    ↓
http://127.0.0.1:8001 (Docker 容器)
    ↓
WeRSS 应用 (FastAPI + Playwright)
```

### 1.2 问题描述

用户在 Web 界面点击"扫码微信授权"按钮时，**获取二维码一直在转圈没有反应**。

**现象**:
- 前端显示加载动画，但二维码不显示
- 偶尔出现 404 错误（二维码图片不存在）
- 需要手动刷新页面多次才能看到二维码

---

## 2. 问题诊断

### 2.1 诊断过程

通过以下步骤进行诊断：

1. **检查容器状态**: 容器正常运行
2. **检查 NGINX 日志**: 显示请求正常到达
3. **检查应用日志**: 发现关键信息

**关键日志发现**:
```
INFO: GET /api/v1/wx/auth/qr/code HTTP/1.1" 200 OK
资源清理完成
正在启动浏览器...
启动浏览器: webkit, 无头模式: True
浏览器特征设置完成: 桌面端
正在加载登录页面...
正在生成二维码图片...
二维码已保存为 wx_qrcode.png，请扫码登录...
```

**问题发现**:
- API 请求立即返回 200（约 1 秒）
- 但二维码生成需要 5-8 秒
- 前端请求图片时文件还不存在，导致 404

### 2.2 根本原因

**二维码生成是异步的**：

```python
# 原始代码逻辑
def GetCode(self, CallBack=None, Notice=None):
    # ...
    self.thread = ThreadManager(target=self.wxLogin, args=(CallBack, True))
    self.thread.start()  # 启动线程后立即返回
    return WX_API.QRcode()  # 此时二维码可能还没生成完成
```

API 启动线程后立即返回，不等待二维码生成完成，导致：
1. `is_exists` 返回 `false`
2. 前端请求图片时返回 404
3. 用户看到一直转圈

---

## 3. 实施过程

### 3.1 初步尝试（失败）

首先尝试修改 `/app/driver/wx_api.py` 文件：

```python
# 添加等待逻辑
max_wait = 15
wait_time = 0
while wait_time < max_wait:
    if os.path.exists(self.qr_code_path):
        break
    time.sleep(0.5)
    wait_time += 0.5
```

**结果**: 修改后测试无效，API 仍然在 1 秒后返回。

### 3.2 深入排查

通过直接在容器内运行 Python 代码测试：

```bash
docker exec we-mp-rss /app/x86_64/bin/python3 -c "
from driver.wx_api import WeChat_api
result = WeChat_api.GetCode()
print(f'结果: {result}')
"
```

**发现**: 代码修改正确，直接运行时等待逻辑生效（耗时 3.5 秒，`is_exists=True`）

### 3.3 找到真正原因

检查 `driver/base.py` 发现：

```python
if bool(cfg.get("server.auth_web", False)) == True:
    from driver.wx import WX_API      # 实际使用的是这个！
else:
    from driver.wx_api import WeChat_api as WX_API
```

**关键发现**: 因为配置了 `Web认证=True`，API 实际使用的是 `driver/wx.py`，而不是我修改的 `driver/wx_api.py`！

### 3.4 正确修改

修改 `driver/wx.py` 文件后，问题解决。

---

## 4. 遇到的问题与解决方案

### 问题 1: 修改文件不生效

**现象**: 修改代码后 API 响应时间不变

**原因**: Python 模块缓存（`.pyc` 文件）导致旧代码仍在运行

**解决方案**:
```bash
# 清除 Python 缓存
docker exec we-mp-rss find /app -name "__pycache__" -type d -exec rm -rf {} +
docker exec we-mp-rss find /app -name "*.pyc" -delete
docker restart we-mp-rss
```

### 问题 2: Volume Mount 不生效

**现象**: docker-compose 配置了 volume mount，但容器内代码未更新

**原因**: 需要重新创建容器（`docker rm` + `docker-compose up`），而不是简单重启

**解决方案**:
```bash
docker stop we-mp-rss
docker rm we-mp-rss
docker-compose -f docker-compose-sqlite-local.yaml up -d
```

### 问题 3: 修改了错误的文件

**现象**: 代码修改正确但 API 行为不变

**原因**: 应用根据配置选择不同的驱动模块：
- `Web认证=True` → 使用 `driver/wx.py`
- `Web认证=False` → 使用 `driver/wx_api.py`

**解决方案**: 检查 `driver/base.py` 确认实际使用的模块，修改正确的文件

---

## 5. 最终修改内容

### 5.1 修改的文件

| 文件 | 路径 | 说明 |
|------|------|------|
| wx.py | `/app/we-mp-rss/patches/wx.py` | 主要修改文件 |
| docker-compose | `/app/we-mp-rss/compose/docker-compose-sqlite-local.yaml` | 添加 volume mount |

### 5.2 代码修改详情

**文件**: `driver/wx.py`
**类**: `Wx`
**方法**: `GetCode`

**修改前**:
```python
def GetCode(self, CallBack=None, Notice=None):
    self.Notice = Notice
    if self.check_lock():
        print_warning("微信公众平台登录脚本正在运行，请勿重复运行")
        return {
            "code": f"{self.wx_login_url}?t={(time.time())}",
            "msg": "微信公众平台登录脚本正在运行，请勿重复运行！"
        }

    self.Clean()
    print("子线程执行中")
    from core.thread import ThreadManager
    self.thread = ThreadManager(target=self.wxLogin, args=(CallBack, True))
    self.thread.start()
    from core.ver import VERSION
    print(f"微信公众平台登录 v{VERSION}")
    return WX_API.QRcode()  # 立即返回，不等待
```

**修改后**:
```python
def GetCode(self, CallBack=None, Notice=None):
    self.Notice = Notice
    if self.check_lock():
        print_warning("微信公众平台登录脚本正在运行，请勿重复运行")
        return {
            "code": f"{self.wx_login_url}?t={(time.time())}",
            "msg": "微信公众平台登录脚本正在运行，请勿重复运行！"
        }

    self.Clean()
    print("子线程执行中")
    from core.thread import ThreadManager
    self.thread = ThreadManager(target=self.wxLogin, args=(CallBack, True))
    self.thread.start()
    from core.ver import VERSION
    print(f"微信公众平台登录 v{VERSION}")

    # ===== 新增：等待二维码文件生成完成 =====
    abs_qr_path = os.path.abspath(self.wx_login_url)
    max_wait = 15
    wait_time = 0
    while wait_time < max_wait:
        if os.path.exists(abs_qr_path):
            print_success(f"二维码生成完成，耗时 {wait_time:.1f} 秒")
            break
        time.sleep(0.5)
        wait_time += 0.5

    if wait_time >= max_wait:
        print_warning("二维码生成超时，请稍后重试")

    return {
        "code": f"/{self.wx_login_url}?t={(time.time())}",
        "is_exists": os.path.exists(abs_qr_path),
    }
    # ===== 新增代码结束 =====
```

### 5.3 Docker Compose 配置

**文件**: `/app/we-mp-rss/compose/docker-compose-sqlite-local.yaml`

```yaml
version: '3.9'
services:
  we-mp-rss:
    image: docker.1ms.run/rachelos/we-mp-rss:latest
    container_name: we-mp-rss
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - DB=sqlite:///data/we_mp_rss.db
      - USERNAME=admin
      - PASSWORD=admin@123
    volumes:
      - ./data:/app/data
      # 优化补丁：等待二维码生成完成后再返回
      - ../patches/wx.py:/app/driver/wx.py:ro

volumes:
  db_data:

networks:
  we-mp-rss:
```

---

## 6. 优化效果

### 6.1 对比数据

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| API 响应时间 | ~1 秒 | ~8 秒（等待二维码生成） |
| `is_exists` 返回值 | `false` | `true` |
| 二维码显示 | 需要手动刷新等待 | 直接显示 |
| 用户体验 | 一直转圈，无反馈 | 正常显示二维码 |

### 6.2 日志验证

**优化后的日志输出**:
```
子线程执行中
微信公众平台登录 v1.4.9
INFO: GET /api/v1/wx/auth/qr/code HTTP/1.1" 200 OK
资源清理完成
正在启动浏览器...
二维码生成完成，耗时 7.0 秒
```

### 6.3 API 响应示例

**优化后**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "code": "/static/wx_qrcode.png?t=1772773955.8438277",
    "is_exists": true
  }
}
```

---

## 7. 部署配置

### 7.1 文件结构

```
/app/we-mp-rss/
├── compose/
│   ├── docker-compose-sqlite-local.yaml
│   └── data/
│       ├── we_mp_rss.db
│       └── ...
└── patches/
    ├── wx.py              # 优化补丁文件
    └── wx_api.py          # 备用补丁（非 Web 认证模式使用）
```

### 7.2 部署步骤

```bash
# 1. 停止并删除现有容器
docker stop we-mp-rss
docker rm we-mp-rss

# 2. 清除锁文件（如果存在）
rm -f /app/we-mp-rss/compose/data/lock.lock

# 3. 使用 docker-compose 重新创建容器
cd /app/we-mp-rss/compose
docker-compose -f docker-compose-sqlite-local.yaml up -d

# 4. 等待容器启动
sleep 20

# 5. 验证服务状态
curl -s http://127.0.0.1:8001/api/v1/wx/sys/info | jq .
```

### 7.3 回滚方案

如果需要回滚优化：

```bash
# 1. 修改 docker-compose 文件，移除补丁挂载
# 删除这一行: - ../patches/wx.py:/app/driver/wx.py:ro

# 2. 重新创建容器
docker stop we-mp-rss && docker rm we-mp-rss
docker-compose -f docker-compose-sqlite-local.yaml up -d
```

---

## 8. 后续建议

### 8.1 可能的进一步优化

1. **前端优化**: 添加加载进度提示，让用户知道正在生成二维码
2. **WebSocket 推送**: 使用 WebSocket 实时推送二维码生成状态
3. **二维码缓存**: 预生成二维码，减少等待时间
4. **健康检查**: 添加 `/health` 端点监控二维码生成服务状态

### 8.2 监控建议

```bash
# 监控二维码生成耗时
docker logs -f we-mp-rss 2>&1 | grep "二维码生成完成"

# 监控超时情况
docker logs -f we-mp-rss 2>&1 | grep "二维码生成超时"
```

### 8.3 注意事项

1. **容器重建**: 修改补丁文件后需要重新创建容器才能生效
2. **缓存清理**: 如遇修改不生效，清除 Python 缓存后重启
3. **锁文件**: 如果二维码一直不显示，检查 `data/lock.lock` 是否存在

---

## 附录

### A. 相关文件路径

| 类型 | 路径 |
|------|------|
| 应用目录 | `/app/we-mp-rss/` |
| Docker Compose | `/app/we-mp-rss/compose/docker-compose-sqlite-local.yaml` |
| 补丁目录 | `/app/we-mp-rss/patches/` |
| 数据目录 | `/app/we-mp-rss/compose/data/` |
| NGINX 配置 | `/etc/nginx/sites-available/werss` |
| SSL 证书 | `/etc/nginx/ssl/werss.crt`, `/etc/nginx/ssl/werss.key` |

### B. 服务访问信息

| 项目 | 值 |
|------|------|
| 外部访问 | `https://werss.aiyxtech.us.kg` |
| 内部访问 | `http://127.0.0.1:8001` |
| 默认用户名 | `admin` |
| 默认密码 | `admin@123` |

### C. 参考链接

- WeRSS GitHub: https://github.com/rachelos/we-mp-rss
- FastAPI 文档: https://fastapi.tiangolo.com/
- Playwright 文档: https://playwright.dev/python/

---

**文档结束**
