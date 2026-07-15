from __future__ import annotations


def render_backend_config_center() -> str:
    return r"""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="icon" href="data:," />
  <title>AYX Growth Intel 可视化配置中心</title>
  <style>
    :root{--ink:#172033;--muted:#68707d;--line:#e3e7ee;--paper:#fff;--canvas:#f5f3f2;--brand:#1f6bff;--brandSoft:#eef5ff;--dark:#0d1c32;--action:#ff5722;--green:#16825d;--risk:#b42318;--warn:#a15c07}
    *{box-sizing:border-box} body{margin:0;background:var(--canvas);color:var(--ink);font-family:Manrope,"Microsoft YaHei",Arial,sans-serif} button,input,select,textarea{font:inherit} button{border:0;border-radius:8px;min-height:38px;padding:0 13px;font-weight:850;cursor:pointer}
    .shell{max-width:1500px;margin:0 auto;padding:18px 24px 28px;display:grid;gap:14px}
    .top{position:sticky;top:0;z-index:10;background:rgba(255,255,255,.96);border:1px solid var(--line);border-radius:8px;box-shadow:0 18px 55px rgba(13,28,50,.06);padding:13px 16px;display:flex;justify-content:space-between;gap:16px;align-items:center}
    .brand small{color:var(--brand);font-weight:950;letter-spacing:.06em}.brand h1{margin:2px 0 0;font-size:23px;line-height:1.1}.brand p{margin:4px 0 0;color:var(--muted);font-size:13px}.actions{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.ghost{background:#fff;border:1px solid #d0d5dd;color:var(--dark)}.primary{background:var(--dark);color:#fff}.orange{background:var(--action);color:#fff}.green{background:var(--green);color:#fff}.danger{background:#fff1f1;color:var(--risk);border:1px solid #ffd0d0}.locked{background:#fff7ed;color:#9a3412;border:1px solid #fed7aa}
    .metrics{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}.metric{background:#fff;border:1px solid var(--line);border-radius:8px;padding:12px}.metric span{display:block;color:var(--muted);font-size:12px;font-weight:850}.metric strong{font-size:25px;line-height:1.2}
    .layout{display:grid;grid-template-columns:270px minmax(0,1fr) 360px;gap:14px;align-items:start}.panel{background:#fff;border:1px solid var(--line);border-radius:8px;box-shadow:0 18px 50px rgba(13,28,50,.04);overflow:hidden}.head{padding:13px 14px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:10px;align-items:center}.head h2{margin:0;font-size:16px}.body{padding:14px;display:grid;gap:12px}
    .tabs{display:grid;gap:8px}.tab{width:100%;text-align:left;background:#fff;border:1px solid var(--line);display:grid;gap:3px;height:auto;padding:10px}.tab.active{border-color:var(--brand);background:var(--brandSoft);box-shadow:inset 3px 0 0 var(--brand)}.tab b{font-size:13px}.tab small{color:var(--muted);font-weight:700}.pill{display:inline-flex;align-items:center;border-radius:5px;padding:3px 7px;background:#eef4ff;color:#175cd3;font-size:12px;font-weight:850}.pill.hot{background:#fff2dc;color:#9a5b00}.pill.off{background:#f2f4f7;color:#667085}.pill.ok{background:#e9f8f1;color:#047857}.pill.warn{background:#fff7ed;color:#b45309}
    .editorTools{display:flex;gap:8px;flex-wrap:wrap}.editor{width:100%;min-height:560px;border:1px solid #d0d5dd;border-radius:8px;padding:12px;font-family:Consolas,"Microsoft YaHei",monospace;font-size:13px;line-height:1.55;resize:vertical;background:#fff;white-space:pre;overflow:auto}.editor:disabled,.field:disabled{background:#f6f7f9;color:#7a8290}.field{width:100%;border:1px solid #d0d5dd;border-radius:8px;padding:9px 10px;background:#fff;min-width:0}
    .split{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.form{display:grid;gap:10px}.form label{display:grid;gap:5px;color:var(--muted);font-size:12px;font-weight:850}.kv{display:grid;gap:8px}.kvRow{display:flex;justify-content:space-between;gap:12px;border-bottom:1px solid #edf0f4;padding-bottom:8px;font-size:13px}.kvRow span:last-child{text-align:right;color:var(--muted)}.sourceList,.previewList,.profileList{display:grid;gap:7px;max-height:350px;overflow:auto}.sourceItem{border:1px solid var(--line);border-radius:8px;padding:9px;background:#fff;display:grid;gap:5px}.sourceItem b{font-size:13px}.sourceItem small{color:var(--muted)}.chips{display:flex;gap:5px;flex-wrap:wrap}
    .keywordCloud{display:flex;gap:7px;flex-wrap:wrap;max-height:170px;overflow:auto}.keywordCloud .pill{background:#f5f8ff}.preview{border-top:1px solid #edf0f4;padding-top:9px}.preview b{font-size:13px}.preview p{margin:4px 0 0;color:#475467;font-size:13px;line-height:1.45}.status{min-height:22px;color:var(--muted);font-size:13px}.status.bad{color:var(--risk)}.status.good{color:var(--green)}
    .smartPanel{display:grid;gap:12px}.smartCard{border:1px solid var(--line);border-radius:8px;padding:14px;background:#fff;display:grid;gap:12px}.smartCard h3{margin:0;font-size:16px}.groupGrid,.presetGrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.groupCard,.presetCard{border:1px solid var(--line);border-radius:8px;padding:10px;background:#fbfcff;display:grid;gap:8px}.presetCard.active{border-color:var(--brand);background:var(--brandSoft)}.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.tagChecks{display:flex;gap:8px;flex-wrap:wrap;color:var(--muted);font-size:12px}.miniInput{border:1px solid #d0d5dd;border-radius:8px;padding:8px 10px;min-width:0;flex:1}.barWeek{display:grid;gap:6px}.barRow{display:grid;grid-template-columns:36px 1fr;gap:8px;align-items:center;font-size:12px}.barTrack{position:relative;height:24px;background:#eef2f7;border-radius:5px;overflow:hidden}.barBlock{position:absolute;top:3px;height:18px;border-radius:4px;background:#6b5df6;color:white;text-align:center;font-size:11px;white-space:nowrap;overflow:hidden}
    .sourceEditorGrid{display:grid;grid-template-columns:1fr;gap:10px}.sourceEditorItem{border:1px solid var(--line);border-radius:8px;background:#fbfcff;padding:10px;display:grid;gap:8px}.sourceEditorItem.off{opacity:.72}.sourceEditorItem .sourceTop{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:start}.sourceToggles{display:flex;gap:10px;flex-wrap:wrap;color:var(--muted);font-size:12px;font-weight:850}.sourceToggles label{display:inline-flex;gap:5px;align-items:center}.sourceFields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.sourceFields .wide{grid-column:1/-1}
    .presetButtons{display:flex;gap:7px;flex-wrap:wrap}.presetButtons button{background:#fff;border:1px solid #d0d5dd;color:var(--ink)}.presetButtons button.active{background:var(--brand);color:#fff;border-color:var(--brand)}.modulePanel{border:1px solid #dbe4f0;border-radius:8px;background:#fbfcff;padding:12px;display:grid;gap:12px}.moduleFields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.modulePreview{display:grid;gap:7px;max-height:260px;overflow:auto}.moduleLine{display:grid;grid-template-columns:28px minmax(0,1fr);gap:8px;border-bottom:1px solid #edf0f4;padding:6px 0;font-family:Consolas,"Microsoft YaHei",monospace;font-size:12px}.moduleLine span:first-child{color:var(--muted)}.inlineForm{border:1px dashed #cbd5e1;border-radius:8px;padding:10px;display:grid;gap:8px;background:#fbfcff}.hidden{display:none}.inputAction{display:grid;grid-template-columns:minmax(0,1fr) 38px;gap:6px;align-items:center}.iconBtn{min-height:38px;padding:0;border:1px solid #d0d5dd;background:#fff;color:var(--dark);font-size:18px}.latencyBadge{display:inline-flex;width:max-content;border-radius:999px;padding:4px 9px;color:#fff;font-size:12px;font-weight:900}
    @media(max-width:1200px){.layout{grid-template-columns:1fr}.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.top{display:grid}.split{grid-template-columns:1fr}.editor{min-height:420px}}
  </style>
</head>
<body>
  <main class="shell">
    <header class="top">
      <div class="brand">
        <small>AYX GROWTH INTEL · CONFIG CENTER</small>
        <h1>可视化配置中心</h1>
        <p>数据源、关键词、推送时间线、大模型提示词、方案与默认配置统一管理</p>
      </div>
      <div class="actions">
        <button class="ghost" onclick="loadAll()">读取配置</button>
        <button id="lockBtn" class="locked" onclick="toggleLock()">锁定编辑</button>
        <button class="ghost" onclick="loadDefaultFile()">加载默认</button>
        <button class="ghost" onclick="saveProfile()">保存方案</button>
        <button class="ghost" onclick="copyActive()">复制</button>
        <button class="green" onclick="saveActive()">保存配置</button>
        <button class="orange" onclick="saveAndRun()">SAVE & RUN</button>
        <button class="ghost" onclick="location.href='http://127.0.0.1:15179/'">返回前端</button>
      </div>
    </header>

    <section class="metrics">
      <div class="metric"><span>配置文件</span><strong id="mFiles">-</strong></div>
      <div class="metric"><span>数据源</span><strong id="mSources">-</strong></div>
      <div class="metric"><span>启用源</span><strong id="mEnabled">-</strong></div>
      <div class="metric"><span>入库内容</span><strong id="mArticles">-</strong></div>
      <div class="metric"><span>高风险</span><strong id="mRisk">-</strong></div>
    </section>

    <section class="layout">
      <aside class="panel">
        <div class="head"><h2>主要文件</h2><span id="fileStatus" class="status"></span></div>
        <div class="body">
          <div id="fileTabs" class="tabs"></div>
          <div>
            <h2 style="font-size:16px;margin:6px 0 10px">方案配置</h2>
            <div class="profileList" id="profileList"></div>
          </div>
        </div>
      </aside>

      <section class="panel">
        <div class="head">
          <h2 id="activeTitle">配置编辑</h2>
          <span id="activeMeta" class="status"></span>
        </div>
        <div class="body">
          <div class="editorTools">
            <button class="ghost" onclick="loadActive()">重新读取</button>
            <button class="ghost" onclick="loadDefaultFile()">加载默认到当前文件</button>
            <button class="primary" onclick="applyToRuntime()">APPLY 应用同步</button>
          </div>
          <textarea id="fileEditor" class="editor" spellcheck="false" oninput="updateActiveContent()"></textarea>
          <div id="status" class="status"></div>
          <div id="smartPanel" class="smartPanel"></div>
        </div>
      </section>

      <aside class="panel">
        <div class="head"><h2>配置功能</h2><span id="lockStatus" class="status"></span></div>
        <div class="body">
          <section class="form">
            <h2 style="font-size:16px;margin:0">大模型配置</h2>
            <label>AI 角色<select id="aiRole" class="field" onchange="renderRuntimePanels()"><option value="backend">后台采集/分析/报告 AI</option><option value="frontend">前端交互 AI</option></select></label>
            <label>SOUL 设计<input id="aiSoul" class="field" /></label>
            <label>Provider<select id="aiProvider" class="field" onchange="selectProvider()"></select></label>
            <div class="actions"><button class="ghost" onclick="toggleCustomProvider()">自定义</button></div>
            <label>API Base<div class="inputAction"><input id="aiBase" class="field" /><button class="iconBtn" onclick="checkAI()" title="检测 API Base 与 API Key 连接">⟳</button></div></label>
            <span id="latencyBadge" class="latencyBadge hidden"></span>
            <label>Model<div class="inputAction"><select id="aiModel" class="field"></select><button class="iconBtn" onclick="loadModels()" title="读取可调用模型列表">⟳</button></div></label>
            <label>API Key<input id="aiKey" class="field" type="password" placeholder="只保存到 config/.env，不写入 YAML" /></label>
            <label>Timeout<input id="aiTimeout" class="field" type="number" /></label>
            <div id="customProvider" class="inlineForm hidden">
              <input id="customProviderName" class="field" placeholder="自定义名称，不能重复">
              <input id="customProviderBase" class="field" placeholder="API Base URL">
              <input id="customProviderModels" class="field" placeholder="模型 ID，多个用逗号分隔">
              <button class="ghost" onclick="saveCustomProvider()">保存自定义 Provider</button>
            </div>
            <div class="actions"><button class="ghost" onclick="saveAISettings()">保存大模型</button></div>
            <div id="aiStatus" class="status"></div>
          </section>

          <section class="form">
            <h2 style="font-size:16px;margin:0">关键词配置</h2>
            <div id="keywordCloud" class="keywordCloud"></div>
          </section>

          <section class="form">
            <h2 style="font-size:16px;margin:0">推送配置</h2>
            <div id="timelinePreview" class="kv"></div>
          </section>

          <section class="form">
            <h2 style="font-size:16px;margin:0">数据源与标签</h2>
            <div id="sourceList" class="sourceList"></div>
          </section>

          <section class="form">
            <h2 style="font-size:16px;margin:0">最新内容</h2>
            <div id="articlePreview" class="previewList"></div>
          </section>
        </div>
      </aside>
    </section>
  </main>

  <script>
    const $ = (id) => document.getElementById(id);
    const state = {
      files: [],
      contents: {},
      active: 'config',
      runtime: null,
      overview: null,
      profiles: [],
      latest: [],
      aiProviders: [],
      configModule: 1,
      locked: true,
      dirty: false
    };
    const manualTags = ['热榜','地区','财经','科技','文旅','教育','军事','国际','消费','其他'];
    const configModules = [
      {index: 1, section: '1.', title: '基础设置', note: '应用时区、版本提示等全局基础项。', fields: [['时区','timezone','text'], ['版本提示','show_version_update','bool']]},
      {index: 2, section: '1.5', title: '调度系统', note: '控制定时采集、分析和推送使用的预设。', fields: [['启用调度','enabled','bool'], ['调度预设','preset','text']]},
      {index: 3, section: '2.', title: '热榜平台', note: '控制热榜平台抓取开关和平台清单。', fields: [['启用热榜抓取','enabled','bool']]},
      {index: 4, section: '3.', title: 'RSS订阅', note: '控制 RSS 抓取、新鲜度和订阅源列表。', fields: [['启用RSS抓取','enabled','bool'], ['默认条数','default_max_items','number'], ['最大天数','max_age_days','number']]},
      {index: 5, section: '4.', title: '报告模式', note: '控制报告生成模式、分组维度和排序阈值。', fields: [['报告模式','mode','text'], ['展示维度','display_mode','text'], ['排名阈值','rank_threshold','number'], ['单关键词数量','max_news_per_keyword','number']]},
      {index: 6, section: '5.', title: '推送内容', note: '控制推送区域、独立平台、RSS 白名单和展示数量。', fields: [['最大条数','max_items','number']]},
      {index: 7, section: '6.', title: '通知渠道', note: '控制飞书、钉钉、企微、Telegram、邮件等通知通道。', fields: [['启用通知','enabled','bool'], ['消息类型','msg_type','text']]},
      {index: 8, section: '8.', title: 'AI模型配置', note: '控制后台 AI 模型、Base URL、超时和生成参数；API Key 请在右侧写入 .env。', fields: [['模型','model','text'], ['API Base','api_base','text'], ['超时','timeout','number'], ['温度','temperature','number'], ['最大Token','max_tokens','number'], ['重试次数','num_retries','number']]},
      {index: 9, section: '9.', title: 'AI分析', note: '控制 AI 分析开关、提示词、分析范围和语言。', fields: [['启用分析','enabled','bool'], ['语言','language','text'], ['提示词文件','prompt_file','text'], ['分析模式','mode','text'], ['最大分析数','max_news_for_analysis','number'], ['包含RSS','include_rss','bool'], ['包含独立源','include_standalone','bool'], ['包含排名轨迹','include_rank_timeline','bool']]},
      {index: 10, section: '10.', title: 'AI翻译', note: '控制翻译开关、翻译语言和翻译提示词文件。', fields: [['启用翻译','enabled','bool'], ['语言','language','text'], ['提示词文件','prompt_file','text']]},
      {index: 11, section: '11.', title: '高级设置', note: '控制调试、版本检查、请求间隔、权重和批量发送参数。', fields: [['调试模式','debug','bool'], ['版本检查URL','version_check_url','text'], ['请求间隔','request_interval','number'], ['RSS超时','timeout','number'], ['排名权重','rank','number'], ['频率权重','frequency','number'], ['热度权重','hotness','number'], ['批量间隔','batch_send_interval','number']]}
    ];
    async function requestJson(url, options) {
      const response = await fetch(url, options);
      if (!response.ok) throw new Error(await response.text());
      return response.json();
    }

    async function loadAll() {
      setStatus('读取配置中...');
      const [files, runtime, overview, profiles, summary, aiProviders] = await Promise.all([
        requestJson('/config-files'),
        requestJson('/settings/runtime'),
        requestJson('/overview'),
        requestJson('/api/profiles/list'),
        requestJson('/api/report/latest_summary'),
        requestJson('/api/ai-providers')
      ]);
      state.files = files.files;
      state.runtime = runtime;
      state.overview = overview;
      state.profiles = profiles.profiles || [];
      state.latest = summary.latest || [];
      state.aiProviders = aiProviders.providers || [];
      await Promise.all(state.files.map(async (file) => {
        const loaded = await requestJson('/api/load?file=' + encodeURIComponent(file.key));
        state.contents[file.key] = loaded.content || '';
        file.updated_at = loaded.updated_at || file.updated_at || '';
      }));
      if (!state.files.some((file) => file.key === state.active)) state.active = state.files[0]?.key || 'sources';
      renderAll();
      setStatus('配置已读取');
    }

    function renderAll() {
      renderMetrics();
      renderTabs();
      renderEditor();
      renderProfiles();
      renderRuntimePanels();
      applyLockState();
    }

    function renderMetrics() {
      $('mFiles').textContent = state.files.length;
      $('mSources').textContent = state.runtime?.sources?.length || 0;
      $('mEnabled').textContent = (state.runtime?.sources || []).filter((source) => source.enabled).length;
      $('mArticles').textContent = state.overview?.articles || 0;
      $('mRisk').textContent = state.overview?.high_risk || 0;
    }

    function renderTabs() {
      $('fileTabs').innerHTML = state.files.map((file) => `
        <button class="tab ${file.key === state.active ? 'active' : ''}" onclick="activateFile('${file.key}')">
          <b>${escapeHtml(file.label)}</b>
          <small>${escapeHtml(file.filename)} · ${file.updated_at || '未保存'}</small>
          <span><span class="pill ${file.exists ? 'ok' : 'warn'}">${file.exists ? '已存在' : '缺失'}</span>${file.default_exists ? ' <span class="pill">默认</span>' : ''}</span>
        </button>
      `).join('');
      $('fileStatus').textContent = state.locked ? '默认锁定' : '可编辑';
    }

    function activateFile(key) {
      state.active = key;
      renderTabs();
      renderEditor();
    }

    function renderEditor() {
      const file = activeFileMeta();
      $('activeTitle').textContent = file ? file.label : '配置编辑';
      $('activeMeta').textContent = file ? `${file.filename} · ${file.updated_at || '未保存'}` : '';
      $('fileEditor').value = state.contents[state.active] || '';
      renderSmartPanel();
    }

    function renderProfiles() {
      $('profileList').innerHTML = state.profiles.length ? state.profiles.map((profile) => `
        <button class="tab" onclick="loadProfile('${escapeAttr(profile.name)}')">
          <b>${escapeHtml(profile.name)}</b>
          <small>${escapeHtml(profile.updated_at || '')}</small>
        </button>
      `).join('') : '<span class="status">暂无方案，保存后会显示在这里。</span>';
    }

    function renderRuntimePanels() {
      const role = $('aiRole')?.value || 'backend';
      const ai = state.runtime?.ai_roles?.[role] || state.runtime?.ai_report || {};
      $('aiRole').value = role;
      $('aiSoul').value = ai.soul || '';
      $('aiProvider').innerHTML = state.aiProviders.map((provider) => `<option value="${escapeAttr(provider.name)}">${escapeHtml(provider.name)}</option>`).join('');
      const matched = state.aiProviders.find((provider) => provider.name === ai.provider) || state.aiProviders.find((provider) => provider.api_base === ai.api_base) || state.aiProviders[0];
      if (matched) $('aiProvider').value = matched.name;
      renderModelOptions(matched, ai.model || '');
      $('aiBase').value = ai.api_base || matched?.api_base || '';
      $('aiKey').value = '';
      $('aiKey').placeholder = ai.key_hint ? `已设置：${ai.key_hint}` : '只保存到 config/.env，不写入 YAML';
      $('aiTimeout').value = ai.timeout || 30;
      $('aiStatus').textContent = ai.has_api_key ? '已配置 API Key' : '未检测到 API Key';
      $('aiStatus').className = 'status ' + (ai.has_api_key ? 'good' : 'bad');
      setLatency(null);

      const frequency = state.contents.frequency || '';
      const words = frequency.split(/\s+/).map((word) => word.trim()).filter(Boolean).slice(0, 80);
      $('keywordCloud').innerHTML = words.length ? words.map((word) => `<span class="pill">${escapeHtml(word)}</span>`).join('') : '<span class="status">频率词文件为空。</span>';

      const timeline = state.contents.timeline || '';
      const timelineLines = timeline.split(/\r?\n/).filter((line) => line.trim() && !line.trim().startsWith('#')).slice(0, 8);
      $('timelinePreview').innerHTML = timelineLines.length ? timelineLines.map((line, index) => `<div class="kvRow"><span>${index + 1}</span><span>${escapeHtml(line.slice(0, 70))}</span></div>`).join('') : '<span class="status">时间线/推送配置为空。</span>';

      $('sourceList').innerHTML = (state.runtime?.sources || []).map((source) => {
        const tags = (source.tags || []).map((tag) => `<span class="pill ${tag === '热榜' || tag === 'RSS源' ? 'hot' : ''}">${escapeHtml(tag)}</span>`).join('');
        return `<div class="sourceItem"><b>${escapeHtml(source.name)}</b><small>${escapeHtml(source.type)} · ${escapeHtml(source.id)}</small><div class="chips">${tags}${source.enabled ? '' : '<span class="pill off">停用</span>'}</div></div>`;
      }).join('');

      $('articlePreview').innerHTML = state.latest.length ? state.latest.slice(0, 8).map((article) => `
        <div class="preview"><b>${escapeHtml(article.title || '')}</b><p>${escapeHtml(article.platform || '')} · 阅读 ${article.read_count || 0} · 评论 ${article.comment_count || 0}</p></div>
      `).join('') : '<span class="status">暂无最新内容。</span>';
    }

    function renderSmartPanel() {
      const panel = $('smartPanel');
      if (!panel) return;
      if (state.active === 'frequency') {
        panel.innerHTML = renderFrequencyEditor();
      } else if (state.active === 'timeline') {
        panel.innerHTML = renderTimelineEditor();
      } else if (state.active === 'sources') {
        panel.innerHTML = renderSourcesEditor();
      } else if (state.active === 'config') {
        panel.innerHTML = renderConfigModules();
      } else {
        panel.innerHTML = '';
      }
      applyLockState();
    }

    function renderFrequencyEditor() {
      const parsed = parseFrequency(state.contents.frequency || '');
      const groups = parsed.groups.slice(0, 12).map((group, index) => `
        <div class="groupCard">
          <div class="row"><span class="pill hot">#${index + 1}</span><b>${escapeHtml(group.name)}</b><button class="danger" onclick="deleteFrequencyGroup('${escapeAttr(group.name)}')">删除</button></div>
          <div class="chips">${group.tags.map((tag) => `<span class="pill">${escapeHtml(tag)}</span>`).join('') || '<span class="status">未设置标签</span>'}</div>
          <div class="chips">${group.keywords.slice(0, 12).map((word) => `<span class="pill">${escapeHtml(word)} <button onclick="removeKeyword('${escapeAttr(group.name)}','${escapeAttr(word)}')">×</button></span>`).join('')}</div>
          <div class="row"><input class="miniInput" id="kw-${index}" placeholder="+必含词 或 /正则词/" onkeydown="if(event.key==='Enter')addKeyword('${escapeAttr(group.name)}',this.value,this)"><button class="ghost" onclick="addKeyword('${escapeAttr(group.name)}',$('kw-${index}').value,$('kw-${index}'))">添加关键词</button></div>
          <div class="tagChecks">${manualTags.map((tag) => `<label><input type="checkbox" ${group.tags.includes(tag) ? 'checked' : ''} onchange="toggleFrequencyTag('${escapeAttr(group.name)}','${tag}',this.checked)"> ${tag}</label>`).join('')}</div>
        </div>
      `).join('');
      return `
        <section class="smartCard">
          <div class="row"><h3>频率词编辑</h3><button class="ghost" onclick="normalizeFrequency()">整理格式</button><button class="ghost" onclick="addFrequencyGroup()">添加组</button></div>
          <div class="row"><input id="globalFilterInput" class="miniInput" placeholder="/过滤词|正则/，回车添加到 GLOBAL_FILTER" onkeydown="if(event.key==='Enter')addGlobalFilter(this.value,this)"><button class="ghost" onclick="addGlobalFilter($('globalFilterInput').value,$('globalFilterInput'))">添加全局过滤词</button></div>
          <div class="chips">${parsed.filters.map((item) => `<span class="pill warn">${escapeHtml(item)} <button onclick="removeGlobalFilter('${escapeAttr(item)}')">×</button></span>`).join('')}</div>
          <div class="groupGrid">${groups || '<span class="status">未识别到关键词组。</span>'}</div>
        </section>`;
    }

    function renderSourcesEditor() {
      const sources = state.runtime?.sources || [];
      const hotlists = sources.filter((source) => source.type === 'hotlist');
      const rss = sources.filter((source) => source.type === 'rss');
      return `
        <section class="smartCard">
          <div class="row">
            <h3>运行数据源配置</h3>
            <span class="status">启用控制 AI 采集/分析读取；前端展示只控制看板可见性。</span>
          </div>
          ${renderSourceGroup('热榜平台', hotlists)}
          ${renderSourceGroup('RSS 源', rss)}
        </section>`;
    }

    function renderSourceGroup(title, sources) {
      return `
        <div class="modulePanel">
          <div class="row"><h3>${escapeHtml(title)}</h3><span class="status">${sources.length} 个</span></div>
          <div class="sourceEditorGrid">${sources.map(renderSourceEditorItem).join('') || '<span class="status">暂无数据源</span>'}</div>
        </div>`;
    }

    function renderSourceEditorItem(source) {
      const fixedTag = source.type === 'hotlist' ? '热榜' : source.type === 'rss' ? 'RSS源' : '';
      const businessTags = (source.tags || []).filter((tag) => tag && tag !== fixedTag);
      return `
        <div class="sourceEditorItem ${source.enabled ? '' : 'off'}">
          <div class="sourceTop">
            <div>
              <b>${escapeHtml(source.name)}</b>
              <small>${escapeHtml(source.id)} · ${escapeHtml(source.platform || source.type)} · AI 可读取</small>
            </div>
            <div class="sourceToggles">
              <label><input type="checkbox" ${source.enabled ? 'checked' : ''} onchange="updateSourceValue('${escapeAttr(source.id)}','enabled',this.checked)">启用采集/AI</label>
              <label><input type="checkbox" ${source.show_frontend === false ? '' : 'checked'} onchange="updateSourceValue('${escapeAttr(source.id)}','show_frontend',this.checked)">前端展示</label>
            </div>
          </div>
          <div class="sourceFields">
            <input class="field" value="${escapeAttr(source.name)}" onchange="updateSourceValue('${escapeAttr(source.id)}','name',this.value)" placeholder="名称">
            <input class="field" type="number" value="${escapeAttr(source.max_items || 50)}" onchange="updateSourceValue('${escapeAttr(source.id)}','max_items',Number(this.value)||0)" placeholder="最大条数">
            ${source.type === 'rss' ? `<input class="field wide" value="${escapeAttr(source.url || '')}" onchange="updateSourceValue('${escapeAttr(source.id)}','url',this.value)" placeholder="RSS URL">` : ''}
            <input class="field wide" value="${escapeAttr(businessTags.join(','))}" onchange="updateSourceTags('${escapeAttr(source.id)}',this.value)" placeholder="业务标签，用逗号分隔">
          </div>
          <div class="tagChecks">${manualTags.map((tag) => `<label><input type="checkbox" ${businessTags.includes(tag) ? 'checked' : ''} onchange="toggleSourceTag('${escapeAttr(source.id)}','${escapeAttr(tag)}',this.checked)"> ${escapeHtml(tag)}</label>`).join('')}</div>
        </div>`;
    }

    function updateSourceValue(id, key, value) {
      ensureUnlocked();
      const source = findRuntimeSource(id);
      if (!source) return;
      source[key] = value;
      syncSourcesContent();
    }

    function updateSourceTags(id, value) {
      ensureUnlocked();
      const source = findRuntimeSource(id);
      if (!source) return;
      source.tags = sourceTagsWithFixed(source, splitTags(value));
      syncSourcesContent();
    }

    function toggleSourceTag(id, tag, checked) {
      ensureUnlocked();
      const source = findRuntimeSource(id);
      if (!source) return;
      const fixed = fixedTagForSource(source);
      let tags = (source.tags || []).filter((item) => item && item !== fixed);
      tags = checked ? [...new Set([...tags, tag])] : tags.filter((item) => item !== tag);
      source.tags = sourceTagsWithFixed(source, tags);
      syncSourcesContent();
    }

    function findRuntimeSource(id) {
      return (state.runtime?.sources || []).find((source) => source.id === id);
    }

    function fixedTagForSource(source) {
      return source.type === 'hotlist' ? '热榜' : source.type === 'rss' ? 'RSS源' : '';
    }

    function sourceTagsWithFixed(source, tags) {
      const fixed = fixedTagForSource(source);
      const next = [...new Set([fixed, ...tags].filter(Boolean))];
      return next.some((tag) => manualTags.includes(tag)) ? next : [...next, '其他'];
    }

    function splitTags(value) {
      return String(value || '').split(/[，,]/).map((tag) => tag.trim()).filter(Boolean);
    }

    function syncSourcesContent() {
      setEditorContent('sources', serializeSourcesYaml());
      renderSmartPanel();
      renderRuntimePanels();
      setStatus('数据源配置已更新到运行数据源编辑框，保存后生效');
    }

    function serializeSourcesYaml() {
      const current = state.contents.sources || '';
      const prefixMatch = current.match(/^[\s\S]*?(?=^sources:\s*$)/m);
      const prefix = prefixMatch ? prefixMatch[0].trimEnd() + '\n' : '';
      const body = (state.runtime?.sources || []).map(serializeSource).join('');
      return `${prefix}sources:\n${body}`;
    }

    function serializeSource(source) {
      const lines = [
        `- id: ${yamlValue(source.id)}`,
        `  name: ${yamlValue(source.name)}`,
        `  type: ${yamlValue(source.type)}`,
        `  platform: ${yamlValue(source.platform || '')}`,
        `  url: ${yamlValue(source.url || '')}`,
        `  tags:`,
        ...sourceTagsWithFixed(source, source.tags || []).map((tag) => `  - ${yamlValue(tag)}`),
        `  max_items: ${Number(source.max_items || 0)}`,
        `  enabled: ${source.enabled !== false}`,
        `  show_frontend: ${source.show_frontend !== false}`
      ];
      return `${lines.join('\n')}\n`;
    }

    function yamlValue(value) {
      const text = String(value ?? '');
      if (!text) return "''";
      if (/^[A-Za-z0-9_-]+$/.test(text)) return text;
      return JSON.stringify(text);
    }

    function renderTimelineEditor() {
      const timeline = state.contents.timeline || '';
      const config = state.contents.config || '';
      const current = (config.match(/preset:\s*["']?([^"'\n#]+)/) || [,'custom'])[1].trim();
      const names = [...timeline.matchAll(/^  ([a-zA-Z0-9_-]+):\s*$/gm)].map((match) => match[1]).filter((name) => !['default','periods','day_plans','week_map','overlap'].includes(name));
      const presets = [...new Set(['always_on','morning_evening','office_hours','night_owl','custom',...names])].slice(0, 10);
      return `
        <section class="smartCard">
          <div class="row"><h3>时间线调度</h3><span class="status">当前：${escapeHtml(current)}</span></div>
          <div class="presetGrid">${presets.map((name) => `<button class="presetCard ${name === current ? 'active' : ''}" onclick="setSchedulePreset('${name}')"><b>${escapeHtml(name)}</b><small>${name === 'custom' ? '自定义时间段' : '预设模板'}</small></button>`).join('')}</div>
          <div class="smartCard">
            <h3>新建自定义时段</h3>
            <div class="split">
              <input id="tlKey" class="field" placeholder="key，例如 noon_push">
              <input id="tlName" class="field" placeholder="名称，例如 午间推送">
              <input id="tlStart" class="field" placeholder="开始，例如 12:00">
              <input id="tlEnd" class="field" placeholder="结束，例如 13:00">
            </div>
            <div class="tagChecks"><label><input id="tlAnalyze" type="checkbox" checked> AI分析</label><label><input id="tlPush" type="checkbox" checked> 推送</label><label><input id="tlCollect" type="checkbox" checked> 采集</label></div>
            <button class="ghost" onclick="appendTimelinePeriod()">添加到 custom.periods</button>
          </div>
          ${renderWeekBars()}
        </section>`;
    }

    function renderConfigModules() {
      const active = configModules.find((item) => item.index === state.configModule) || configModules[0];
      return `
        <section class="smartCard">
          <div class="row"><h3>配置模块</h3><span class="status">旧版 1-11 模块入口，点击后下方动态显示可配置内容</span></div>
          <div class="presetButtons">
            ${configModules.map((item) => `<button class="${item.index === active.index ? 'active' : ''}" onclick="selectConfigModule(${item.index})">${item.index}. ${item.title}</button>`).join('')}
          </div>
          ${renderConfigModulePanel(active)}
        </section>`;
    }

    function renderConfigModulePanel(module) {
      const rows = module.fields.map(([label, key, type]) => renderConfigField(module, label, key, type)).join('');
      const preview = renderConfigModulePreview(module);
      return `
        <div class="modulePanel">
          <div class="row"><h3>${module.index}. ${escapeHtml(module.title)}</h3><span class="status">${escapeHtml(module.note)}</span></div>
          <div class="moduleFields">${rows}</div>
          <div class="row">
            <button class="ghost" onclick="jumpConfigModule(${module.index})">定位源码</button>
            <button class="primary" onclick="applyToRuntime()">APPLY 应用同步</button>
            <button class="green" onclick="saveActive()">保存配置</button>
            <button class="orange" onclick="saveAndRun()">SAVE & RUN</button>
          </div>
          <div>
            <h3>当前模块内容</h3>
            <div class="modulePreview">${preview || '<span class="status">未识别到当前模块内容，请检查 config.yaml 的章节标题。</span>'}</div>
          </div>
        </div>`;
    }

    function renderConfigField(module, label, key, type) {
      const value = readConfigScalar(module, key);
      if (type === 'bool') {
        return `<label>${escapeHtml(label)}<select class="field" onchange="updateConfigScalar(${module.index}, '${key}', this.value, '${type}')"><option value="true" ${value === 'true' ? 'selected' : ''}>true</option><option value="false" ${value === 'false' ? 'selected' : ''}>false</option></select></label>`;
      }
      return `<label>${escapeHtml(label)}<input class="field" type="${type === 'number' ? 'number' : 'text'}" value="${escapeAttr(value)}" onchange="updateConfigScalar(${module.index}, '${key}', this.value, '${type}')"></label>`;
    }

    function renderConfigModulePreview(module) {
      const lines = getConfigModuleSection(module).split(/\r?\n/)
        .map((line) => line.trim())
        .filter((line) => line && !line.startsWith('#'))
        .slice(0, 80);
      return lines.map((line, index) => `<div class="moduleLine"><span>${index + 1}</span><span>${escapeHtml(line)}</span></div>`).join('');
    }

    function updateActiveContent() {
      state.contents[state.active] = $('fileEditor').value;
      state.dirty = true;
      renderSmartPanel();
    }

    function parseFrequency(text) {
      const filters = [];
      const groups = [];
      let section = '';
      let current = null;
      for (const raw of text.split(/\r?\n/)) {
        const line = raw.trim();
        const header = line.match(/^\[([^\]]+)\]$/);
        if (header) {
          section = header[1];
          if (!['GLOBAL_FILTER','WORD_GROUPS'].includes(section)) {
            current = {name: section, keywords: [], tags: []};
            groups.push(current);
          }
          continue;
        }
        if (!line || line.startsWith('#')) continue;
        if (section === 'GLOBAL_FILTER') filters.push(line);
        if (current && line.startsWith('@tags:')) current.tags = line.slice(6).split(/[，,\s]+/).filter(Boolean);
        else if (current && !line.startsWith('!')) current.keywords.push(line);
      }
      return {filters, groups};
    }

    function setEditorContent(key, content) {
      state.contents[key] = content;
      if (state.active === key) $('fileEditor').value = content;
      state.dirty = true;
      renderSmartPanel();
      renderRuntimePanels();
    }

    function addGlobalFilter(value, input) {
      ensureUnlocked();
      const word = String(value || '').trim();
      if (!word) return;
      const content = state.contents.frequency || '';
      const next = content.replace('[GLOBAL_FILTER]', `[GLOBAL_FILTER]\n${word}`);
      setEditorContent('frequency', next === content ? `${content}\n[GLOBAL_FILTER]\n${word}\n` : next);
      if (input) input.value = '';
    }

    function removeGlobalFilter(value) {
      ensureUnlocked();
      const lines = (state.contents.frequency || '').split(/\r?\n/).filter((line) => line.trim() !== value);
      setEditorContent('frequency', lines.join('\n'));
    }

    function addFrequencyGroup() {
      ensureUnlocked();
      const name = prompt('关键词组名称');
      if (!name) return;
      const tag = prompt('分类标签，例如 食品饮料 / 美妆护肤 / 风险舆情', '其他') || '其他';
      const block = `\n[${name.trim()}]\n/关键词1|关键词2/\n@tags:${tag.trim()}\n`;
      setEditorContent('frequency', `${state.contents.frequency || ''}\n${block}`);
    }

    function deleteFrequencyGroup(name) {
      ensureUnlocked();
      const lines = (state.contents.frequency || '').split(/\r?\n/);
      const out = [];
      let dropping = false;
      for (const line of lines) {
        const header = line.trim().match(/^\[([^\]]+)\]$/);
        if (header) dropping = header[1] === name;
        if (!dropping) out.push(line);
      }
      setEditorContent('frequency', out.join('\n'));
    }

    function addKeyword(groupName, value, input) {
      ensureUnlocked();
      const word = String(value || '').trim();
      if (!word) return;
      const lines = (state.contents.frequency || '').split(/\r?\n/);
      const out = [];
      let inGroup = false;
      let added = false;
      for (const line of lines) {
        const header = line.trim().match(/^\[([^\]]+)\]$/);
        if (header && inGroup && !added) { out.push(word); added = true; }
        if (header) inGroup = header[1] === groupName;
        if (inGroup && line.trim().startsWith('@tags:') && !added) { out.push(word); added = true; }
        out.push(line);
      }
      if (inGroup && !added) out.push(word);
      setEditorContent('frequency', out.join('\n'));
      if (input) input.value = '';
    }

    function removeKeyword(groupName, keyword) {
      ensureUnlocked();
      let inGroup = false;
      const lines = (state.contents.frequency || '').split(/\r?\n/).filter((line) => {
        const header = line.trim().match(/^\[([^\]]+)\]$/);
        if (header) inGroup = header[1] === groupName;
        return !(inGroup && line.trim() === keyword);
      });
      setEditorContent('frequency', lines.join('\n'));
    }

    function toggleFrequencyTag(groupName, tag, checked) {
      ensureUnlocked();
      const lines = (state.contents.frequency || '').split(/\r?\n/);
      const out = [];
      let inGroup = false, wrote = false;
      for (const line of lines) {
        const header = line.trim().match(/^\[([^\]]+)\]$/);
        if (header && inGroup && !wrote) { out.push(`@tags:${tag}`); wrote = true; }
        if (header) { inGroup = header[1] === groupName; wrote = false; }
        if (inGroup && line.trim().startsWith('@tags:')) {
          const tags = line.trim().slice(6).split(/[，,\s]+/).filter(Boolean);
          const next = checked ? [...new Set([...tags, tag])] : tags.filter((item) => item !== tag);
          out.push(`@tags:${next.join(',')}`);
          wrote = true;
        } else {
          out.push(line);
        }
      }
      setEditorContent('frequency', out.join('\n'));
    }

    function normalizeFrequency() {
      ensureUnlocked();
      setEditorContent('frequency', (state.contents.frequency || '').replace(/\n{3,}/g, '\n\n').trim() + '\n');
    }

    function setSchedulePreset(name) {
      ensureUnlocked();
      const content = state.contents.config || '';
      const next = content.match(/preset:\s*["']?[^"'\n#]+/) ? content.replace(/preset:\s*["']?[^"'\n#]+/, `preset: "${name}"`) : `${content}\nschedule:\n  enabled: true\n  preset: "${name}"\n`;
      setEditorContent('config', next);
      setStatus(`已选择调度预设：${name}，保存后生效`);
    }

    function appendTimelinePeriod() {
      ensureUnlocked();
      const key = $('tlKey').value.trim();
      const name = $('tlName').value.trim() || key;
      const start = $('tlStart').value.trim();
      const end = $('tlEnd').value.trim();
      if (!key || !start || !end) throw new Error('请填写 key、开始和结束时间');
      const block = `\n    ${key}:\n      name: "${name}"\n      start: "${start}"\n      end: "${end}"\n      collect: ${$('tlCollect').checked}\n      analyze: ${$('tlAnalyze').checked}\n      push: ${$('tlPush').checked}\n`;
      let content = state.contents.timeline || '';
      const marker = /custom:\n[\s\S]*?periods:\n/;
      content = marker.test(content) ? content.replace(marker, (match) => match + block) : `${content}\ncustom:\n  periods:\n${block}`;
      setEditorContent('timeline', content);
      setStatus('自定义时段已添加到 timeline.yaml，保存后生效');
    }

    function renderWeekBars() {
      const days = ['周一','周二','周三','周四','周五','周六','周日'];
      return `<div class="smartCard"><h3>周视图</h3><div class="barWeek">${days.map((day) => `<div class="barRow"><span>${day}</span><div class="barTrack"><span class="barBlock" style="left:0%;width:30%">深夜静默</span><span class="barBlock" style="left:50%;width:12%;background:#4f7cff">工作日</span><span class="barBlock" style="left:78%;width:17%;background:#5765e8">晚间汇总</span></div></div>`).join('')}</div></div>`;
    }

    function selectConfigModule(index) {
      state.configModule = index;
      renderSmartPanel();
      jumpConfigModule(index);
    }

    function getConfigModuleBounds(module) {
      const text = state.contents.config || '';
      const startPattern = new RegExp(`^#\\s*${escapeRegExp(module.section)}(?:\\s|$)`, 'm');
      const startMatch = startPattern.exec(text);
      if (!startMatch) return {start: -1, end: -1};
      const headingPattern = /^#\s*(?:1\.5|[1-9]\.|10\.|11\.)(?:\s|$)/gm;
      headingPattern.lastIndex = startMatch.index + 1;
      const nextMatch = headingPattern.exec(text);
      return {start: startMatch.index, end: nextMatch ? nextMatch.index : text.length};
    }

    function getConfigModuleSection(module) {
      const bounds = getConfigModuleBounds(module);
      if (bounds.start < 0) return '';
      return (state.contents.config || '').slice(bounds.start, bounds.end);
    }

    function readConfigScalar(module, key) {
      const match = new RegExp(`(^\\s*${escapeRegExp(key)}\\s*:\\s*)([^#\\n]*)`, 'm').exec(getConfigModuleSection(module));
      return match ? String(match[2]).trim().replace(/^["']|["']$/g, '') : '';
    }

    function updateConfigScalar(moduleIndex, key, value, type) {
      ensureUnlocked();
      const module = configModules.find((item) => item.index === moduleIndex);
      if (!module) return;
      const text = state.contents.config || '';
      const bounds = getConfigModuleBounds(module);
      if (bounds.start < 0) return;
      const section = text.slice(bounds.start, bounds.end);
      const formatted = formatConfigValue(value, type);
      const fieldPattern = new RegExp(`(^\\s*${escapeRegExp(key)}\\s*:\\s*)([^#\\n]*)(.*$)`, 'm');
      const nextSection = fieldPattern.test(section)
        ? section.replace(fieldPattern, `$1${formatted}$3`)
        : `${section.trimEnd()}\n  ${key}: ${formatted}\n`;
      setEditorContent('config', text.slice(0, bounds.start) + nextSection + text.slice(bounds.end));
      state.configModule = moduleIndex;
    }

    function formatConfigValue(value, type) {
      const raw = String(value ?? '').trim();
      if (type === 'bool') return raw === 'true' ? 'true' : 'false';
      if (type === 'number') return raw || '0';
      if (raw === '' || /[:#\[\]{}]/.test(raw)) return JSON.stringify(raw);
      return JSON.stringify(raw);
    }

    function jumpConfigModule(index) {
      const module = configModules.find((item) => item.index === index);
      const marker = module?.section;
      const editor = $('fileEditor');
      const match = marker ? new RegExp(`^#\\s*${escapeRegExp(marker)}(?:\\s|$)`, 'm').exec(editor.value) : null;
      const pos = match ? match.index : -1;
      if (pos >= 0) {
        editor.focus();
        editor.setSelectionRange(pos, pos);
      }
    }

    async function loadActive() {
      const loaded = await requestJson('/api/load?file=' + encodeURIComponent(state.active));
      state.contents[state.active] = loaded.content || '';
      const file = activeFileMeta();
      if (file) file.updated_at = loaded.updated_at || '';
      renderAll();
      setStatus('当前文件已重新读取');
    }

    async function loadDefaultFile() {
      ensureUnlocked();
      const loaded = await requestJson('/api/load?default=true&file=' + encodeURIComponent(state.active));
      state.contents[state.active] = loaded.content || '';
      renderAll();
      setStatus('默认配置已加载到当前编辑区，保存后生效');
    }

    async function saveActive() {
      ensureUnlocked();
      updateActiveContent();
      const result = await requestJson('/api/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({file: state.active, content: state.contents[state.active] || ''})
      });
      const file = activeFileMeta();
      if (file) file.updated_at = result.updated_at || '';
      state.dirty = false;
      await refreshRuntimeOnly();
      renderAll();
      setStatus('当前配置已保存', 'good');
    }

    async function saveAllFiles() {
      ensureUnlocked();
      updateActiveContent();
      for (const file of state.files) {
        await requestJson('/api/save', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({file: file.key, content: state.contents[file.key] || ''})
        });
      }
      state.dirty = false;
      await loadAll();
    }

    async function applyToRuntime() {
      await saveAllFiles();
      setStatus('所有配置已保存并同步到后端运行态', 'good');
    }

    async function saveAndRun() {
      await saveAllFiles();
      setStatus('配置已保存，开始同步采集...');
      const result = await requestJson('/api/refresh', {method: 'POST'});
      await loadAll();
      setStatus(`同步完成：保存 ${result.saved || 0} 条，失败 ${result.failures?.length || 0} 个源`, 'good');
    }

    async function saveProfile() {
      ensureUnlocked();
      const name = prompt('方案名称');
      if (!name) return;
      updateActiveContent();
      await requestJson('/api/profiles/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, files: state.contents})
      });
      const profiles = await requestJson('/api/profiles/list');
      state.profiles = profiles.profiles || [];
      renderProfiles();
      setStatus('方案已保存', 'good');
    }

    async function loadProfile(name) {
      ensureUnlocked();
      const loaded = await requestJson('/api/profiles/load?name=' + encodeURIComponent(name));
      if (loaded.files) {
        Object.assign(state.contents, loaded.files);
      } else if (loaded.content) {
        state.contents[state.active] = loaded.content;
      }
      renderAll();
      setStatus('方案已加载到编辑区，保存后生效');
    }

    function copyActive() {
      navigator.clipboard?.writeText(state.contents[state.active] || '');
      setStatus('当前配置已复制');
    }

    function renderModelOptions(provider, selectedModel) {
      const models = [...new Set([selectedModel, ...(provider?.models || [])].filter(Boolean))];
      $('aiModel').innerHTML = models.map((model) => `<option value="${escapeAttr(model)}">${escapeHtml(model)}</option>`).join('');
      if (selectedModel) $('aiModel').value = selectedModel;
    }

    function selectProvider() {
      ensureUnlocked();
      const provider = state.aiProviders.find((item) => item.name === $('aiProvider').value);
      if (!provider) return;
      $('aiBase').value = provider.api_base || '';
      renderModelOptions(provider, provider.models?.[0] || '');
      setStatus(`已选择 Provider：${provider.name}`);
    }

    function toggleCustomProvider() {
      ensureUnlocked();
      $('customProvider').classList.toggle('hidden');
    }

    async function saveCustomProvider() {
      ensureUnlocked();
      const name = $('customProviderName').value.trim();
      const apiBase = $('customProviderBase').value.trim();
      const models = $('customProviderModels').value.split(/[，,]/).map((item) => item.trim()).filter(Boolean);
      if (!name || !apiBase || !models.length) throw new Error('请填写自定义名称、API Base 和至少一个模型');
      if (state.aiProviders.some((item) => item.name === name && item.api_base !== apiBase)) throw new Error('自定义名称不能重复');
      const response = await requestJson('/api/ai-providers', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, api_base: apiBase, models})
      });
      state.aiProviders = response.providers || [];
      $('customProvider').classList.add('hidden');
      renderRuntimePanels();
      $('aiProvider').value = name;
      selectProvider();
      setStatus('自定义 Provider 已保存', 'good');
    }

    async function saveAISettings() {
      ensureUnlocked();
      const result = await requestJson('/api/ai-settings', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          api_base: $('aiBase').value,
          model: $('aiModel').value,
          api_key: $('aiKey').value,
          timeout: $('aiTimeout').value,
          role: $('aiRole').value,
          provider: $('aiProvider').value,
          soul: $('aiSoul').value
        })
      });
      state.runtime = result.runtime;
      await loadActive();
      renderRuntimePanels();
      setStatus('大模型配置已保存，API KEY 已写入 config/.env', 'good');
    }

    async function checkAI() {
      const result = await requestJson('/api/check_ai_connection', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({api_base: $('aiBase').value, model: $('aiModel').value, api_key: $('aiKey').value, role: $('aiRole').value})
      });
      setLatency(result.latency_ms);
      $('aiStatus').textContent = result.message;
      $('aiStatus').className = 'status ' + (result.success ? 'good' : 'bad');
    }

    async function loadModels() {
      const result = await requestJson('/api/get_ai_models', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({api_base: $('aiBase').value, model: $('aiModel').value, api_key: $('aiKey').value})
      });
      const provider = state.aiProviders.find((item) => item.name === $('aiProvider').value);
      const models = result.models || [];
      const selected = models.includes($('aiModel').value) ? $('aiModel').value : (result.selected || models[0] || '');
      renderModelOptions(provider ? {...provider, models} : {models}, selected);
      setLatency(result.latency_ms);
      $('aiStatus').innerHTML = result.success ? '已读取与当前 API Base 和 API Key 匹配的模型列表。' : (result.message || '读取模型失败，已显示本地已配置模型。');
      $('aiStatus').className = 'status ' + (result.success ? 'good' : 'bad');
    }

    function setLatency(ms) {
      const badge = $('latencyBadge');
      if (!badge) return;
      if (ms === null || ms === undefined || Number.isNaN(Number(ms))) {
        badge.classList.add('hidden');
        badge.textContent = '';
        return;
      }
      const value = Number(ms);
      badge.classList.remove('hidden');
      badge.textContent = `延迟 ${value} ms`;
      badge.style.background = latencyColor(value);
    }

    function latencyColor(ms) {
      if (ms < 100) return '#065f46';
      if (ms < 200) return '#047857';
      if (ms < 300) return '#65a30d';
      if (ms <= 350) return '#f59e0b';
      if (ms <= 450) return '#dc2626';
      return '#991b1b';
    }

    function toggleLock() {
      state.locked = !state.locked;
      applyLockState();
      renderTabs();
    }

    function applyLockState() {
      $('fileEditor').disabled = state.locked;
      document.querySelectorAll('.field').forEach((field) => { field.disabled = state.locked; });
      $('lockBtn').textContent = state.locked ? '锁定编辑' : '解锁编辑';
      $('lockBtn').className = state.locked ? 'locked' : 'danger';
      $('lockStatus').textContent = state.locked ? '默认锁死，点击解锁后才能修改/保存' : '已解锁，可修改配置';
    }

    async function refreshRuntimeOnly() {
      const [runtime, overview, summary] = await Promise.all([
        requestJson('/settings/runtime'),
        requestJson('/overview'),
        requestJson('/api/report/latest_summary')
      ]);
      state.runtime = runtime;
      state.overview = overview;
      state.latest = summary.latest || [];
    }

    function ensureUnlocked() {
      if (state.locked) throw new Error('当前处于锁定编辑状态，请先点击“锁定编辑”解锁。');
    }

    function activeFileMeta() {
      return state.files.find((file) => file.key === state.active);
    }

    function setStatus(message, tone) {
      $('status').textContent = message || '';
      $('status').className = 'status ' + (tone || '');
    }

    function escapeHtml(value) {
      return String(value ?? '').replace(/[&<>"']/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
    }

    function escapeAttr(value) {
      return escapeHtml(value).replace(/"/g, '&quot;');
    }

    function escapeRegExp(value) {
      return String(value ?? '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    window.addEventListener('error', (event) => setStatus(event.message, 'bad'));
    window.addEventListener('unhandledrejection', (event) => setStatus(event.reason?.message || String(event.reason), 'bad'));
    loadAll().catch((error) => setStatus('读取失败：' + error.message, 'bad'));
  </script>
</body>
</html>
"""
