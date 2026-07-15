# TrendRadar Homepage Development Technical Documentation / TrendRadar 主页开发技术文档

## 1. Metadata / 元数据

### 1.1 Creation Record / 创建记录
- **Date / 日期**: 2026-05-12
- **Time / 时间**: 13:30 (UTC+8)
- **Author / 创建人**: Antigravity AI
- **Document Path / 文档路径**: `/TrendRadar/docs/202605121330 Homepage_Development_Documentation.md`

### 1.2 Update History / 更新历史
| Date / 日期 | Author / 更新人 | Description / 更新内容简述 |
| :--- | :--- | :--- |
| 2026-06-19 | Codex | Documented AI model query API Base auto-detection/writeback and updated AI API response fields. / 记录 AI 模型查询 API Base 自动探测与自动写回，并更新 AI 接口响应字段。 |
| 2026-06-09 | Codex | Documented fixed five-file config center defaults, runtime/default config separation, and AI analysis empty-config guidance card. / 记录五文件默认配置固定、运行配置与默认模板隔离、AI 分析空配置引导卡片。 |
| 2026-05-15 | Codex | Added AI analysis prompt-display incident retrospective and prevention checklist. / 新增 AI 分析误展示提示词问题复盘与预防清单。 |
| 2026-05-12 | Antigravity AI | Initial creation of bilingual technical documentation. / 初始创建中英双语技术文档。 |

### 1.3 Tech Stack / 技术栈
- **Frontend / 前端**:
  - **Core / 核心**: HTML5, Vanilla JavaScript (ES6+)
  - **Styling / 样式**: CSS3 (Vanilla CSS, Variables, Grid, Flexbox)
  - **Icons / 图标**: Font Awesome 6.4.0
  - **Typography / 字体**: Google Fonts (Inter, Noto Sans SC)
  - **Libraries / 第三方库**: 
    - `html2canvas 1.4.1` (Screenshot/Image Export / 截图与图片导出)
    - `marked.js` (Markdown Parsing / Markdown 解析)
- **Backend / 后端**:
  - **Framework / 框架**: Python 3.11 (SimpleHTTPRequestHandler)
  - **Database / 数据库**: SQLite3
- **Dev Tools / 开发工具**:
  - **Containerization / 容器化**: Docker, Docker Compose
  - **Reverse Proxy / 反向代理**: Nginx

### 1.4 Platform Info / 平台信息
- **Dev Platform / 开发平台**: Linux (Ubuntu), VSCode
- **Deployment / 部署平台**: Docker Container on Linux
- **Cloud Services / 云服务**: Cloudflare (SSL/Proxy)
- **Build Tools / 构建工具**: Docker Build

### 1.5 System Requirements / 系统要求
- **Operating System / 操作系统**: Linux (Recommended), Windows, or macOS
- **Python**: 3.11 or higher
- **Docker**: 20.10+ & Docker Compose 2.0+
- **Network / 网络**: External internet access for CDN assets and AI API calls.

---

## 2. Project Overview / 项目概览
TrendRadar is an AI-driven trend analysis and news aggregation platform. The homepage serves as the central dashboard for viewing real-time hot topics, searching historical data, and managing configurations.
TrendRadar 是一个 AI 驱动的趋势分析与资讯聚合平台。主页作为核心仪表盘，用于查看实时热点、搜索历史数据以及管理配置。

---

## 3. Design Philosophy & Aesthetics / 设计理念与美学

### 3.1 Visual Style / 视觉风格
- **Modern & Premium / 现代与高级感**: Uses a glassmorphism effect, subtle gradients, and a clean grid layout.
- **Dynamic Themes / 动态主题**: Supports 8 predefined color schemes using CSS Variables.

### 3.2 Detailed Color Schemes / 详细配色方案
| Theme / 主题 | Background / 背景 (--bg-color) | Card / 卡片 (--card-bg) | Text Primary / 主文字 | Accent / 强调色 |
| :--- | :--- | :--- | :--- | :--- |
| **Default** | `#f7fafc` | `rgba(255,255,255,0.85)` | `#1e293b` | `#00f2ff` |
| **Solarized Light** | `#fdf6e3` | `#eee8d5` | `#657b83` | `#268bd2` |
| **Solarized Dark** | `#002b36` | `#073642` | `#839496` | `#268bd2` |
| **Nord** | `#2e3440` | `#3b4252` | `#d8dee9` | `#81a1c1` |
| **Dracula** | `#282a36` | `#44475a` | `#f8f8f2` | `#ff79c6` |
| **Gruvbox** | `#282828` | `#3c3836` | `#ebdbb2` | `#fe8019` |
| **Monokai** | `#272822` | `#3e3d32` | `#f8f8f2` | `#f92672` |
| **Catppuccin** | `#1e1e2e` | `#313244` | `#cdd6f4` | `#cba6f7` |

---

## 4. Layout & Structure / 排版与结构

### 4.1 Global Layout / 全局布局
- **Container / 容器**: `.container` with `max-width: 1200px` and center alignment.
- **Grid System / 网格系统**: `.cards-grid` uses `display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 30px;`.

### 4.2 Component Specification: Cards / 组件规范：卡片
Each card represents a category or date of news.
每张卡片代表一个类别或日期的新闻。

- **Design Details / 设计细节**:
  - `height: 600px`, `border-radius: 20px`, `box-shadow: var(--shadow-sm)`.
  - **Hover Effect / 悬停效果**: `transform: translateY(-8px)` with `box-shadow: var(--shadow-md)`.
  - **Header Border / 头部边框**: Dynamic top border color using neon palette (`#00f2ff`, `#ff00ff`, `#39ff14`, etc.).

- **Content Structure / 内容结构**:
  ```html
  <div class="card">
      <div class="card-header">
          <span class="card-title">🔥 Category Name</span>
          <span class="card-count">20 items</span>
      </div>
      <div class="card-body">
          <ul class="news-list">
              <li class="news-item">
                  <span class="news-rank">01</span>
                  <div class="news-content">
                      <a href="..." class="news-title-link">News Title</a>
                      <div class="news-meta">
                          <span class="source-tag">Source</span>
                          <span class="time-tag">🕒 Timestamp</span>
                      </div>
                  </div>
              </li>
          </ul>
      </div>
  </div>
  ```

### 4.3 Global Search Box / 全局搜索框
- **Layout**: Centered within the header.
- **Styling**: `border-radius: 30px`, `background: #f8fafc`, `padding: 15px 45px 15px 50px`.
- **Interactions**: Magnifying glass icon on the left, clear button (X) on the right (visible only when typing).

---

## 5. Functional Modules & Logic / 功能模块与逻辑

### 5.1 Search Logic / 搜索逻辑
- **Debounce / 防抖**: 500ms delay to prevent excessive API calls.
- **Trigger / 触发器**: `input` event for real-time search, `Enter` key for immediate search.
- **Rendering / 渲染**:
  1. Hides `main-cards-grid`.
  2. Shows `search-results-container`.
  3. Fetches data from `/api/search?kw=...`.
  4. Dynamically builds cards using `document.createElement('div')` and `innerHTML`.

### 5.2 Theme Management / 主题管理
- **Mechanism**: Sets `data-theme` attribute on `<html>` element.
- **Persistence**: Uses `localStorage.setItem('aiyxdata_tradar-theme', theme)`.

### 5.3 Screenshot Export / 截图导出
- **Library**: `html2canvas`.
- **Process**:
  1. Add `.is-exporting` class to body (hides UI controls).
  2. Capture `#main-content` with `scale: 2` and specific background color.
  3. Generate a download link for the PNG file.

### 5.4 Data Refresh / 数据刷新
- **Frontend**: Shows a loading spinner overlay (`#loading`).
- **Backend**: Python server calls `manage.py run` asynchronously.

### 5.5 Visual Config Editor / 可视化配置编辑器
- **Implementation**: A draggable modal (`.modal-window`) containing an `iframe`.
- **Drag Logic**: Custom JavaScript handling `mousedown`, `mousemove`, and `mouseup` for both the modal header and the floating toggle button.

---

## 6. API Reference / API 接口参考

| Endpoint / 接口 | Method / 方法 | Description / 说明 |
| :--- | :--- | :--- |
| `/api/load?file={type}` | GET | Load config content (config, frequency, timeline, analysis_prompt, translation_prompt). |
| `/api/save` | POST | Save updated config content. |
| `/api/search?kw={kw}` | GET | Search SQLite databases for historical news matching keywords. |
| `/api/search_history` | GET/POST | Retrieve or record search history. |
| `/api/refresh` | POST | Trigger backend data update process. |
| `/api/check_ai_connection` | POST | Test AI API connectivity and return the effective OpenAI-compatible API Base URL (`api_base`, `api_base_changed`). / 测试 AI 连接，并返回最终命中的兼容 API Base。 |
| `/api/get_ai_models` | POST | Fetch available AI models and return the effective OpenAI-compatible API Base URL (`api_base`, `api_base_changed`). / 获取模型列表，并返回最终命中的兼容 API Base。 |

### 6.1 AI Model Query API Base Detection / AI 模型查询 API Base 探测

- The config center first tests `{api_base}/models`. / 配置中心优先测试 `{api_base}/models`。
- If the response is 404, HTML, or non-JSON, the backend retries `{api_base}/v1/models`. / 如果返回 404、HTML 或非 JSON，后端自动重试 `{api_base}/v1/models`。
- The successful endpoint root is returned as `api_base`. / 成功命中的接口根地址通过 `api_base` 返回。
- `api_base_changed=true` means the backend corrected the user-entered Base URL, usually by appending `/v1`. / `api_base_changed=true` 表示后端修正了用户输入的 Base URL，通常是补上 `/v1`。
- The frontend displays the detected API Base and writes it back to the current `ai.api_base` field; persistence still requires `APPLY`, `SAVE & RUN`, or profile save. / 前端显示检测到的 API Base 并写回当前 `ai.api_base` 字段；持久化仍需点击 `APPLY`、`SAVE & RUN` 或保存方案。

---

## 7. Project Structure Tree / 项目结构树

```text
/TrendRadar/
├── index.html                          # Main Homepage (Frontend entry) / 主页文件 (前端入口)
├── Dockerfile                          # Container definition / 容器定义
├── docker-compose.yml                  # Service orchestration / 服务编排
├── docker/                             # Backend source / 后端源码
│   ├── server.py                       # HTTP server & API logic / HTTP 服务器与 API 逻辑
│   ├── manage.py                       # Data processing & Refresh script / 数据处理与刷新脚本
│   └── entrypoint.sh                   # Startup script / 启动脚本
├── config/                             # Configuration files / 配置文件
│   ├── config.yaml                     # Primary system config / 系统主配置
│   ├── frequency_words.txt             # Keyword weights / 关键词权重
│   ├── timeline.yaml                   # Timeline display logic / 时间线显示逻辑
│   ├── ai_analysis_prompt.txt          # AI Analysis instructions / AI 分析提示词
│   ├── ai_translation_prompt.txt       # AI Translation instructions / AI 翻译提示词
│   └── profiles/                       # Saved config backups / 已保存的配置备份
├── output/                             # Generated data & Assets / 生成数据与资源
│   ├── rss/                            # RSS SQLite databases / RSS 数据库
│   ├── news/                           # News SQLite databases / 新闻数据库
│   ├── data/                           # Search history & Reports / 搜索历史与报告
│   └── config_editor/                  # Visual editor frontend / 可视化编辑器前端
└── docs/                               # Documentation / 项目文档
    ├── defaults/                       # Read-only default templates for the five core config files / 五个核心配置文件的只读默认模板
    ├── index.html                      # Static config center template / 静态配置中心模板
    └── assets/                         # Config center assets / 配置中心资源
```

---

## 8. Core Config Defaults / 核心默认配置

The visual config center treats the following five files as fixed core files. They must not be removed, renamed, or reordered in the tab bar or Load Defaults modal. / 可视化配置中心将以下五个文件视为固定核心文件，不得从文件分页签或“加载默认”弹窗中移除、重命名或重排。

```text
config.yaml
frequency_words.txt
timeline.yaml
ai_analysis_prompt.txt
ai_translation_prompt.txt
```

### 8.1 Default vs Runtime Config / 默认模板与运行配置隔离
- `docs/defaults/` stores built-in read-only templates used by the Load Defaults modal. / `docs/defaults/` 存放“加载默认”读取的内置只读模板。
- `config/` stores deployer/runtime configuration. APPLY, SAVE & RUN, and profile save write to this runtime config, not to `docs/defaults/`. / `config/` 存放部署者运行配置；APPLY、SAVE & RUN、保存方案写入这里，不写回 `docs/defaults/`。
- Docker builds copy `docs/defaults/` into `/app/default-output/config_editor/defaults/`. The entrypoint syncs config center static files on startup so stale three-tab editors are refreshed. / Docker 构建会把 `docs/defaults/` 复制到 `/app/default-output/config_editor/defaults/`；启动脚本会同步配置中心静态文件，避免旧三文件配置中心残留。
- `scripts/export_clean_repo.sh` validates that all five default files exist before exporting a migration repo. / `scripts/export_clean_repo.sh` 会在导出迁移仓库前校验五个默认文件是否完整。

### 8.2 AI Analysis Empty-State Card / AI 分析空配置卡片
- The generated HTML report must always show the `✨ AI 深度分析研判` card. / 生成的 HTML 报告必须始终显示 `✨ AI 深度分析研判` 卡片。
- If model/API key is missing, the card shows guidance to open the visual config center and configure model, API Base, and API Key. / 如果未配置模型或 API Key，卡片显示前往可视化配置中心配置模型、API Base 和 API Key 的提示。
- This empty-state card must not trigger an extra model request. / 该空状态卡片不得触发额外模型请求。

---

## 9. Deployment & Ports / 部署与端口

### 9.1 Network Mapping / 网络映射
- **Internal Port (Docker)**: `8080` (Python `server.py`)
- **Host Port (Local)**: `8084` (Mapped via `docker-compose.yml`)
- **Public Port**: `443` (HTTPS via Nginx reverse proxy)

### 9.2 Nginx Configuration / Nginx 配置
Files: `/etc/nginx/sites-available/trendradar.aiyxtech.us.kg.conf`
```nginx
server {
    listen 80;
    server_name trendradar.aiyxtech.us.kg;
    return 301 https://$host$request_uri;
}
server {
    listen 443 ssl;
    server_name trendradar.aiyxtech.us.kg;
    location / {
        proxy_pass http://127.0.0.1:8084;
        proxy_set_header Host $host;
        # ... standard proxy headers
    }
}
```

---

## 10. Development Guide / 开发指南

1. **Local Setup**: Install Python 3.11+, run `pip install -r requirements.txt`.
2. **Start Backend**: `cd docker && python3 server.py`.
3. **Modify UI**: Edit `index.html`. Styles are in the `<style>` block, Logic in the `<script>` block (end of body).
4. **API Extensions**: Add new routes in `server.py` within the `do_GET` or `do_POST` methods.
5. **Theme Addition**: Add a new `[data-theme="..."]` block in `index.html` CSS and update the `#theme-select` options.

---

## 11. Incident Retrospective: AI Analysis Prompt Display / 问题复盘：AI 分析区域误展示提示词

### 11.1 Incident Summary / 问题概述
- **Date / 日期**: 2026-05-15
- **Affected Area / 影响区域**: `✨ AI 深度分析研判` section in generated HTML reports / HTML 报告中的 `✨ AI 深度分析研判` 区域。
- **Symptom / 现象**: The report displayed prompt/config explanation text such as `这是一份 TrendRadar AI 分析系统的提示词配置文件`, instead of a real AI analysis report. / 页面展示了提示词配置说明，而不是基于热榜数据生成的 AI 研判报告。
- **Impact / 影响**: Users could mistake prompt text for analysis output, and the AI analysis card lost its decision-support value. / 用户可能误把提示词说明当作分析结论，AI 分析卡片失去研判价值。

### 11.2 Root Causes / 根因
- **Prompt template validation gap / 提示词模板校验缺失**: If the prompt file contained a `[system]` block without a valid `[user]` block or data placeholders, the analyzer could send prompt instructions in the wrong context. / 当提示词文件缺少有效 `[user]` 段或新闻数据占位符时，分析器可能把提示词配置当成待处理内容发送。
- **Unsafe parser fallback / 解析兜底过宽**: `_parse_response()` previously treated non-JSON AI output as a successful result by putting the raw response into `core_trends`. / 旧解析逻辑会把非 JSON 原文兜底塞入 `core_trends` 并标记成功。
- **Provider configuration failure / 模型配置不可用**: The configured Claude proxy endpoint returned 404, so the normal AI generation path could not be trusted. / 当前 Claude 代理端点请求返回 404，正常 AI 生成链路不可用。
- **Quote normalization bug / 引号处理缺陷**: Replacing Chinese quotes with English quotes globally could break otherwise valid JSON strings and truncate fields. / 全局替换中文引号会破坏合法 JSON 字符串，导致字段被截断。

### 11.3 Fixes Applied / 已完成修复
- Added strict prompt template validation in `aiyxdata_tradar/ai/analyzer.py`: missing prompt file, empty `[user]`, missing `[user]`, or missing `{news_content}` / `{rss_content}` / `{standalone_content}` placeholders now fail fast. / 在 `analyzer.py` 增加提示词模板校验，缺文件、缺 `[user]`、`[user]` 为空或缺新闻数据占位符时直接失败。
- Removed the raw-response success fallback. Invalid JSON is now rejected instead of being displayed as a report. / 移除“非 JSON 原文也算成功”的兜底逻辑，非法 JSON 不再展示为报告。
- Added prompt-marker rejection for responses containing prompt/config explanation phrases. / 增加提示词说明文本识别，疑似提示词内容会被拒绝展示。
- Preserved Chinese quotes during JSON parsing and improved fallback field extraction. / 保留中文引号并增强异常 JSON 字段提取，避免正文被截断。
- Added `extra_params` support in `aiyxdata_tradar/ai/client.py`, enabling provider-level options such as `response_format`. / 在 AI client 增加 `extra_params` 支持，可启用 `response_format` 等模型参数。
- Updated `config/config.yaml` to use a verified OpenAI-compatible SiliconFlow Kimi endpoint with JSON response format. API keys must remain private and should be masked in documentation or logs. / 将主配置切换到已验证可用的 SiliconFlow Kimi 兼容端点并启用 JSON 输出格式；API Key 必须私密保存，文档和日志中只应脱敏展示。
- Tightened `config/ai_analysis_prompt.txt` to require complete, data-grounded, non-template analysis fields. / 收紧 AI 分析提示词，要求输出完整、基于数据、非模板化的研判字段。

### 11.4 Verification / 验证结果
- Forced AI analysis with existing 2026-05-15 collected data and generated `output/html/2026-05-15/08-41.html`. / 使用 2026-05-15 已采集数据强制执行 AI 分析，生成 `output/html/2026-05-15/08-41.html`。
- Synced latest report files: `output/html/latest/current.html`, `output/index.html`, and root `index.html`. / 已同步最新报告文件。
- Confirmed the report no longer contains prompt markers: `我已理解你的需求`, `提示词配置文件`, `用于指导AI分析`. / 已确认最新页面不再包含旧提示词说明文本。
- Confirmed AI fields returned normal paragraph-level content: `core_trends`, `sentiment_controversy`, `signals`, and `outlook_strategy` all contain substantive analysis. / 已确认主要 AI 字段恢复为正常段落级分析内容。
- Ran Python syntax checks for the changed AI modules. / 已对改动的 AI 模块执行 Python 语法检查。

### 11.5 Prevention Checklist / 预防清单
- Keep `[system]` and `[user]` sections explicit in `config/ai_analysis_prompt.txt`. / 保持提示词文件中的 `[system]` 与 `[user]` 段清晰分离。
- Ensure the `[user]` section contains at least one data placeholder: `{news_content}`, `{rss_content}`, or `{standalone_content}`. / 确保 `[user]` 段至少包含一个新闻数据占位符。
- Do not display raw AI responses when JSON parsing fails. Show an error state instead. / JSON 解析失败时不要展示原始 AI 回复，应显示错误状态。
- Probe model endpoints after provider/model changes before enabling scheduled runs. / 更换模型或供应商后，先探测端点可用性，再启用定时运行。
- Prefer provider-enforced JSON mode when available, for example `response_format: {"type": "json_object"}`. / 模型支持时优先启用供应商侧 JSON 模式。
- Search the generated report for prompt markers after prompt changes. / 修改提示词后，检查生成报告是否残留提示词说明文本。
- Never paste full API keys into documentation, screenshots, or issue reports. / 不要在文档、截图或问题报告中粘贴完整 API Key。

---
**Documentation End / 文档结束**
