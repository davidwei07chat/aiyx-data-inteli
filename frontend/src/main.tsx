import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  BarChart3,
  BriefcaseBusiness,
  CheckCircle2,
  Circle,
  ExternalLink,
  Eye,
  FileText,
  Filter,
  Gauge,
  Globe2,
  Hash,
  Loader2,
  MessageSquare,
  Newspaper,
  RefreshCw,
  Search,
  Share2,
  SlidersHorizontal,
  TrendingUp
} from "lucide-react";
import "./styles/app.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:18088";

type ViewMode = "industry" | "platform" | "keyword";
type RiskFilter = "all" | "high" | "medium" | "low" | "critical";
type SentimentFilter = "all" | "positive" | "neutral" | "negative";

type Overview = {
  articles: number;
  high_risk: number;
  medium_risk: number;
  negative: number;
  platforms: Array<{ platform: string; count: number }>;
};

type Article = {
  id: number;
  source_id: string;
  platform: string;
  title: string;
  url: string;
  summary: string;
  author: string;
  published_at: string;
  sentiment: "positive" | "neutral" | "negative" | string;
  risk_level: "low" | "medium" | "high" | "critical" | string;
  heat_score: number;
  matched_keywords: string | string[];
  matched_core_terms: string | string[];
  read_count: number;
  comment_count: number;
  share_count: number;
  last_seen_at: string;
};

type ReportEvent = {
  title: string;
  source: string;
  url: string;
  summary: string;
  risk_level: string;
  sentiment: string;
  heat_score: number;
  read_count: number;
  comment_count: number;
  share_count: number;
  matched_core_terms: string[];
};

type IndustrySection = {
  industry: string;
  event_count: number;
  high_risk_count: number;
  negative_count: number;
  heat_index: number;
  summary: string;
  top_events: ReportEvent[];
  recommendations: string[];
};

type DailyReport = {
  report_id?: number;
  title: string;
  report_date: string;
  executive_summary: string;
  total_events: number;
  high_risk: number;
  negative: number;
  ai_status?: "disabled" | "generated" | "fallback" | "failed";
  model?: string;
  industries: IndustrySection[];
};

type RuntimeSettings = {
  sources: Array<{
    id: string;
    name: string;
    type: string;
    platform: string;
    url: string;
    tags: string[];
    enabled: boolean;
    show_frontend?: boolean;
    max_items: number;
  }>;
  report_defaults: {
    keywords: string[];
    core_terms: string[];
    industries: Array<{
      name: string;
      keywords: string[];
      core_terms: string[];
    }>;
  };
  ai_report: {
    enabled: boolean;
    api_base: string;
    model: string;
    has_api_key: boolean;
    timeout: number;
  };
};

type SourceSettings = RuntimeSettings["sources"][number];

type ConfigCenterPayload = {
  taxonomy: {
    manual_tags: string[];
    fixed_tags: Record<string, string>;
  };
  config: {
    sources?: SourceSettings[];
    [key: string]: unknown;
  };
};

type IndustryDraft = {
  name: string;
  keywords: string;
  coreTerms: string;
};

type ProcessStep = {
  id: string;
  label: string;
  detail: string;
};

const defaultIndustries: IndustryDraft[] = [
  { name: "消费零售", keywords: "消费,零售,品牌,价格,渠道", coreTerms: "投诉,涨价,降价,差评,推荐" },
  { name: "新能源汽车", keywords: "新能源,汽车,电池,充电,智能驾驶", coreTerms: "召回,故障,维权,续航,安全" },
  { name: "人工智能", keywords: "AI,人工智能,大模型,智能体,算力", coreTerms: "发布,融资,监管,竞品,风险" }
];

const fixedSourceTags: Record<string, string> = {
  hotlist: "热榜",
  rss: "RSS源"
};

const relationKeywordCandidates = [
  "烙色L'ADOR ECOLORS",
  "巴奴毛肚火锅",
  "巴奴火锅",
  "和府捞面",
  "兰州牛肉面",
  "兰州拉面",
  "青海拉面",
  "太二",
  "霸王茶姬",
  "Coupang Eats",
  "同创伟业",
  "硬氪",
  "人形机器人",
  "具身智能机器人",
  "机器人关节",
  "餐饮创业"
];

const processSteps: ProcessStep[] = [
  { id: "collect", label: "数据采集", detail: "同步多源内容与指标" },
  { id: "match", label: "关键词匹配", detail: "行业词、核心词、平台口径" },
  { id: "analyze", label: "舆情分析", detail: "热度、情绪、风险分层" },
  { id: "report", label: "报告生成", detail: "输出热点总结与证据流" }
];

function App() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [report, setReport] = useState<DailyReport | null>(null);
  const [runtime, setRuntime] = useState<RuntimeSettings | null>(null);
  const [articles, setArticles] = useState<Article[]>([]);
  const [industries, setIndustries] = useState<IndustryDraft[]>(defaultIndustries);
  const [globalKeywords, setGlobalKeywords] = useState("品牌,产品,竞品,用户反馈");
  const [globalCoreTerms, setGlobalCoreTerms] = useState("投诉,维权,故障,召回,涨价,差评");
  const [viewMode, setViewMode] = useState<ViewMode>("industry");
  const [query, setQuery] = useState("");
  const [viewFilter, setViewFilter] = useState("all");
  const [platformFilter, setPlatformFilter] = useState("all");
  const [riskFilter, setRiskFilter] = useState<RiskFilter>("all");
  const [sentimentFilter, setSentimentFilter] = useState<SentimentFilter>("all");
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [activeStep, setActiveStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const [configCenterOpen, setConfigCenterOpen] = useState(false);
  const [configCenter, setConfigCenter] = useState<ConfigCenterPayload | null>(null);
  const [configSaving, setConfigSaving] = useState(false);

  async function refreshOverview() {
    const [overviewResponse, articleResponse] = await Promise.all([
      fetch(`${API_BASE}/overview`),
      fetch(`${API_BASE}/articles?limit=240`)
    ]);
    setOverview(await overviewResponse.json());
    const nextArticles = await articleResponse.json();
    setArticles(Array.isArray(nextArticles) ? nextArticles : nextArticles.value ?? []);
  }

  async function loadRuntimeSettings() {
    const response = await fetch(`${API_BASE}/settings/runtime`);
    const settings: RuntimeSettings = await response.json();
    const nextKeywords = settings.report_defaults.keywords.length
      ? settings.report_defaults.keywords.join(",")
      : globalKeywords;
    const nextCoreTerms = settings.report_defaults.core_terms.length
      ? settings.report_defaults.core_terms.join(",")
      : globalCoreTerms;
    const nextIndustries = settings.report_defaults.industries.length
      ? settings.report_defaults.industries.map((industry) => ({
          name: industry.name,
          keywords: industry.keywords.join(","),
          coreTerms: industry.core_terms.join(",")
        }))
      : industries;
    setRuntime(settings);
    setGlobalKeywords(nextKeywords);
    setGlobalCoreTerms(nextCoreTerms);
    setIndustries(nextIndustries);
    return { nextIndustries, nextKeywords, nextCoreTerms };
  }

  async function openConfigCenter() {
    window.location.href = `${API_BASE}/`;
  }

  function updateConfigSource(sourceId: string, patch: Partial<SourceSettings>) {
    setConfigCenter((current) => {
      if (!current?.config.sources) {
        return current;
      }
      return {
        ...current,
        config: {
          ...current.config,
          sources: current.config.sources.map((source) =>
            source.id === sourceId ? { ...source, ...patch } : source
          )
        }
      };
    });
  }

  async function saveConfigCenter() {
    if (!configCenter) {
      return;
    }
    setConfigSaving(true);
    try {
      const response = await fetch(`${API_BASE}/settings/config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ config: configCenter.config })
      });
      if (!response.ok) {
        throw new Error("save failed");
      }
      await loadRuntimeSettings();
      await refreshOverview();
      setMessage("配置中心已保存，新的数据源和标签将在下一次同步时生效。");
      setConfigCenterOpen(false);
    } catch {
      setMessage("配置保存失败，请检查后端配置目录是否可写。");
    } finally {
      setConfigSaving(false);
    }
  }

  async function generateReport(
    collectFirst = false,
    reportIndustries = industries,
    reportKeywords = globalKeywords,
    reportCoreTerms = globalCoreTerms
  ) {
    setLoading(true);
    setMessage("");
    setActiveStep(0);
    setCompletedSteps([]);
    const timer = window.setInterval(() => {
      setActiveStep((current) => Math.min(current + 1, processSteps.length - 1));
      setCompletedSteps((current) => {
        const nextStep = processSteps[Math.min(current.length, processSteps.length - 1)]?.id;
        return nextStep && !current.includes(nextStep) ? [...current, nextStep] : current;
      });
    }, 620);
    try {
      if (collectFirst) {
        const collectResponse = await fetch(`${API_BASE}/collect/run-all`, { method: "POST" });
        const collectResult = await collectResponse.json();
        if (collectResult.failures?.length) {
          setMessage(`部分数据源同步失败：${collectResult.failures.length} 个，请查看后端日志。`);
        } else {
          setMessage(`数据源同步完成，新增或更新 ${collectResult.saved ?? 0} 条内容。`);
        }
        await refreshOverview();
      }
      const response = await fetch(`${API_BASE}/reports/daily`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          report_date: new Date().toISOString().slice(0, 10),
          keywords: splitTerms(reportKeywords),
          core_terms: splitTerms(reportCoreTerms),
          industries: reportIndustries.map((industry) => ({
            name: industry.name,
            keywords: splitTerms(industry.keywords),
            core_terms: splitTerms(industry.coreTerms)
          })),
          limit: 160
        })
      });
      setReport(await response.json());
      setMessage("");
      setActiveStep(processSteps.length - 1);
      setCompletedSteps(processSteps.map((step) => step.id));
      await refreshOverview();
    } catch {
      setMessage("无法生成报告，请确认 API 服务已启动。");
    } finally {
      window.clearInterval(timer);
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRuntimeSettings()
      .then(({ nextIndustries, nextKeywords, nextCoreTerms }) =>
        refreshOverview().then(() => generateReport(false, nextIndustries, nextKeywords, nextCoreTerms))
      )
      .catch(() => setMessage("无法连接后端，请确认 API 服务已启动。"));
  }, []);

  const enabledSources = runtime?.sources.filter((source) => source.enabled) ?? [];
  const frontendSources = enabledSources.filter((source) => source.show_frontend !== false);
  const frontendSourceIds = useMemo(() => new Set(frontendSources.map((source) => source.id)), [frontendSources]);
  const sourceNameById = useMemo(() => {
    const values = new Map<string, string>();
    runtime?.sources.forEach((source) => values.set(source.id, source.name));
    return values;
  }, [runtime]);
  const sourceTagsById = useMemo(() => {
    const values = new Map<string, string[]>();
    runtime?.sources.forEach((source) => values.set(source.id, source.tags?.length ? source.tags : [source.platform].filter(Boolean)));
    return values;
  }, [runtime]);
  const platformOptions = useMemo(() => {
    return unique(frontendSources.map((source) => source.name));
  }, [frontendSources]);

  const industryOptions = useMemo(() => {
    const tagOptions = unique(frontendSources.flatMap((source) => businessTagsForSource(source)));
    return tagOptions.length ? tagOptions : industries.map((industry) => industry.name);
  }, [frontendSources, industries]);

  const keywordOptions = useMemo(() => {
    return unique([...splitTerms(globalKeywords), ...splitTerms(globalCoreTerms)]);
  }, [globalCoreTerms, globalKeywords]);

  const keywordStats = useMemo(() => {
    return keywordOptions
      .map((term) => {
        const matched = articles.filter((article) =>
          articleSearchText(article, sourceNameById, sourceTagsById).includes(term.toLowerCase())
        );
        return {
          term,
          count: matched.length,
          negative: matched.filter((item) => item.sentiment === "negative").length,
          heat: Math.round(matched.reduce((sum, item) => sum + Number(item.heat_score ?? 0), 0))
        };
      })
      .filter((item) => item.count > 0)
      .sort((a, b) => b.count - a.count)
      .slice(0, 18);
  }, [articles, keywordOptions, sourceNameById, sourceTagsById]);

  const lensOptions = viewMode === "industry" ? industryOptions : viewMode === "platform" ? platformOptions : keywordOptions;
  const lensLabel = viewMode === "industry" ? "行业标签" : viewMode === "platform" ? "平台标签" : "关键词标签";
  const activeLensFilter = viewMode === "platform" ? platformFilter : viewFilter;
  const activeLensSummary = activeLensFilter === "all" ? `展示全部${lensLabel}` : `已筛选：${activeLensFilter}`;

  const filteredArticles = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    return articles
      .filter((article) => frontendSourceIds.has(article.source_id))
      .filter((article) => {
        const text = articleSearchText(article, sourceNameById, sourceTagsById);
        return keyword ? text.includes(keyword) : true;
      })
      .filter((article) => {
        if (viewFilter === "all" || viewMode === "platform") {
          return true;
        }
        if (viewMode === "keyword") {
          const text = articleSearchText(article, sourceNameById, sourceTagsById);
          return text.includes(viewFilter.toLowerCase());
        }
        return articleSourceTags(article, sourceTagsById).includes(viewFilter);
      })
      .filter((article) => (platformFilter === "all" ? true : articleSourceName(article, sourceNameById) === platformFilter))
      .filter((article) => (riskFilter === "all" ? true : article.risk_level === riskFilter))
      .filter((article) => (sentimentFilter === "all" ? true : article.sentiment === sentimentFilter))
      .sort((a, b) => Number(b.heat_score ?? 0) - Number(a.heat_score ?? 0));
  }, [articles, frontendSourceIds, platformFilter, query, riskFilter, sentimentFilter, sourceNameById, sourceTagsById, viewFilter, viewMode]);

  function switchViewMode(nextMode: ViewMode) {
    setViewMode(nextMode);
    setViewFilter("all");
    setPlatformFilter("all");
  }

  const selected = selectedArticle ?? filteredArticles[0] ?? null;
  return (
    <main className="radarShell">
      <header className="topCommand">
        <div className="brandCluster">
          <div className="brandCopy">
            <p className="brandLine">AYX GROWTH INTEL · CONSUMER MARKET RADAR</p>
            <h1 className="brandLine">大消费经济情报舱</h1>
          </div>
        </div>
        <div className="commandActions">
          <button className="ghostButton" onClick={() => refreshOverview()} title="刷新数据">
            <RefreshCw size={17} />
            刷新
          </button>
          <button className="ghostButton" onClick={openConfigCenter} title="数据源与标签配置中心">
            <SlidersHorizontal size={17} />
            配置中心
          </button>
          <button className="primaryButton" onClick={() => generateReport(true)} disabled={loading}>
            {loading ? <Loader2 size={17} className="spin" /> : <Activity size={17} />}
            {loading ? "运行中" : "同步并生成"}
          </button>
        </div>
      </header>

      <section className="radarHero">
        <div className="heroCopy">
          <div className="heroMeta">
            <span>{formatHeroDateTime(new Date())}</span>
            <span>{enabledSources.length} 个数据源在线</span>
            <span>{formatModelStatus(runtime)}</span>
          </div>
          <h2>大数据AI追踪消费市场热点、风险与产品增长信号</h2>
          <p>{report?.executive_summary ?? "正在读取行业舆情与热点事件，生成可执行的市场情报摘要。"}</p>
        </div>
        <div className="heroMetrics">
          <MetricCard icon={<Newspaper size={18} />} label="入库内容" value={overview?.articles ?? 0} />
          <MetricCard icon={<TrendingUp size={18} />} label="今日事件" value={report?.total_events ?? 0} />
          <MetricCard icon={<AlertTriangle size={18} />} label="高风险" value={report?.high_risk ?? 0} tone="risk" />
          <MetricCard icon={<MessageSquare size={18} />} label="负面内容" value={report?.negative ?? 0} tone="warn" />
        </div>
      </section>

      <section className="queryConsole">
        <label className="searchField">
          <Search size={18} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="搜索标题、摘要、平台或关键词"
          />
        </label>
        <label>
          <span>平台</span>
          <select value={platformFilter} onChange={(event) => setPlatformFilter(event.target.value)}>
            <option value="all">全部平台</option>
            {platformOptions.map((platform) => (
              <option value={platform} key={platform}>{platform}</option>
            ))}
          </select>
        </label>
        <label>
          <span>风险</span>
          <select value={riskFilter} onChange={(event) => setRiskFilter(event.target.value as RiskFilter)}>
            <option value="all">全部风险</option>
            <option value="critical">critical</option>
            <option value="high">high</option>
            <option value="medium">medium</option>
            <option value="low">low</option>
          </select>
        </label>
        <label>
          <span>情绪</span>
          <select value={sentimentFilter} onChange={(event) => setSentimentFilter(event.target.value as SentimentFilter)}>
            <option value="all">全部情绪</option>
            <option value="negative">negative</option>
            <option value="neutral">neutral</option>
            <option value="positive">positive</option>
          </select>
        </label>
        <button className="ghostButton" onClick={() => generateReport(false)} disabled={loading}>
          <Gauge size={17} />
          生成报告
        </button>
      </section>

      {message && <p className="statusLine">{message}</p>}

      <section className="processTracker">
        <div className="processHeader">
          <div>
            <p className="eyebrow">RUNNING PIPELINE</p>
            <h2>搜索、匹配、分析与报告生成流程</h2>
          </div>
          <div className="runState">
            {loading ? <Loader2 size={16} className="spin" /> : <CheckCircle2 size={16} />}
            <span>{loading ? "任务运行中" : completedSteps.length ? "报告已生成" : "等待执行"}</span>
          </div>
        </div>
        <div className="progressTrack">
          <span style={{ width: `${progressValue(loading, activeStep, completedSteps)}%` }} />
        </div>
        <div className="stepGrid">
          {processSteps.map((step, index) => {
            const done = completedSteps.includes(step.id);
            const active = loading && index === activeStep;
            return (
              <div className={`processStep ${done ? "done" : ""} ${active ? "active" : ""}`} key={step.id}>
                {done ? <CheckCircle2 size={18} /> : active ? <Loader2 size={18} className="spin" /> : <Circle size={18} />}
                <div>
                  <strong>{step.label}</strong>
                  <span>{step.detail}</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <GrowthReportPanel report={report} loading={loading} />

      <section className="analysisTabs" id="industry">
        <div className="tabHeader">
          <div>
            <p className="eyebrow">INTELLIGENCE LENS</p>
            <h2>舆情信息展示与分析报告</h2>
          </div>
          <div className="segmentedControl" aria-label="切换分析视角">
            <button className={viewMode === "industry" ? "active" : ""} onClick={() => switchViewMode("industry")}>
              <BriefcaseBusiness size={16} />
              按行业
            </button>
            <button className={viewMode === "platform" ? "active" : ""} onClick={() => switchViewMode("platform")}>
              <Globe2 size={16} />
              按平台
            </button>
            <button className={viewMode === "keyword" ? "active" : ""} onClick={() => switchViewMode("keyword")}>
              <Hash size={16} />
              按关键词
            </button>
          </div>
        </div>
        <div className="lensFilterBar">
          <label>
            <span>{lensLabel}</span>
            <select
              value={activeLensFilter}
              onChange={(event) => {
                if (viewMode === "platform") {
                  setPlatformFilter(event.target.value);
                } else {
                  setViewFilter(event.target.value);
                }
              }}
            >
              <option value="all">全部</option>
              {lensOptions.map((option) => (
                <option value={option} key={option}>{option}</option>
              ))}
            </select>
          </label>
          <small><Filter size={14} />{activeLensSummary}</small>
        </div>
      </section>

      <section className="workspaceGrid">
        <section className="contentStream">
          <div className="sectionBar">
            <div>
              <p className="eyebrow">EVIDENCE STREAM</p>
              <h2>相关内容搜索与筛选结果</h2>
            </div>
            <span>{filteredArticles.length} / {articles.length} 条</span>
          </div>
          <div className="articleList">
            {filteredArticles.slice(0, 36).map((article) => (
              <article
                className={`articleItem ${selected?.url === article.url ? "selected" : ""}`}
                key={article.url}
                onClick={() => setSelectedArticle(article)}
              >
                <div className="articleMeta">
                  <span>{articleSourceName(article, sourceNameById)}</span>
                  <TagChips tags={articleSourceTags(article, sourceTagsById)} />
                  <Badge label={article.risk_level || "low"} tone={article.risk_level || "low"} />
                  <Badge label={article.sentiment || "neutral"} tone={article.sentiment || "neutral"} />
                </div>
                <h3>{cleanText(article.title)}</h3>
                <div className="readonlyMetrics" aria-label="文章指标">
                  <span>发布 {formatDateTime(article.published_at || article.last_seen_at)}</span>
                  <span>采集 {formatDateTime(article.last_seen_at)}</span>
                  <span>阅读 {displayReadCount(article)}</span>
                  <span>评论 {displayCommentCount(article)}</span>
                  <span>转发 {displayShareCount(article)}</span>
                  <span>热度 {Math.round(Number(article.heat_score ?? 0))}</span>
                </div>
                <p>{truncate(cleanText(article.summary), 168)}</p>
                <div className="signalRow">
                  {parseList(article.matched_core_terms).slice(0, 4).map((term) => (
                    <em key={term}>{term}</em>
                  ))}
                </div>
              </article>
            ))}
            {filteredArticles.length === 0 && (
              <div className="emptyState">
                <SlidersHorizontal size={24} />
                <strong>没有符合筛选条件的内容</strong>
                <span>尝试放宽平台、风险、情绪或关键词条件。</span>
              </div>
            )}
          </div>
        </section>

        <aside className="insightPanel">
          <div className="sectionBar compact">
            <div>
              <p className="eyebrow">SELECTED SIGNAL</p>
              <h2>内容详情</h2>
            </div>
          </div>
          {selected ? (
            <div className="selectedCard">
              <div className="selectedFixedHead">
                <div className="articleMeta">
                  <span>{articleSourceName(selected, sourceNameById)}</span>
                  <TagChips tags={articleSourceTags(selected, sourceTagsById)} />
                  <Badge label={selected.risk_level || "low"} tone={selected.risk_level || "low"} />
                  <Badge label={selected.sentiment || "neutral"} tone={selected.sentiment || "neutral"} />
                </div>
                <h3>{cleanText(selected.title)}</h3>
                <div className="publishLine">
                  发布 {formatDateTime(selected.published_at || selected.last_seen_at)} · 采集 {formatDateTime(selected.last_seen_at)}
                </div>
                <div className="detailMetricRow" aria-label="文章指标">
                  <span>阅读 {displayReadCount(selected)}</span>
                  <span>评论 {displayCommentCount(selected)}</span>
                  <span>转发 {displayShareCount(selected)}</span>
                  <span>热度 {Math.round(Number(selected.heat_score ?? 0))}</span>
                </div>
                <a className="sourceLinkButton" href={selected.url} target="_blank" rel="noreferrer">
                  打开原文 <ExternalLink size={15} />
                </a>
              </div>
              <div className="selectedScrollBody">
                <HighlightedArticleText article={selected} />
              </div>
            </div>
          ) : (
            <div className="emptyState">选择一条内容查看详情。</div>
          )}

          <div className="relationPanel">
            <div className="recommendationTitle">
              <Hash size={16} />
              <strong>内容关键词</strong>
            </div>
            {selected ? <RelationSummary article={selected} /> : <small>选择内容后显示关系信息。</small>}
          </div>
        </aside>
      </section>
      {configCenterOpen && (
        <section className="configOverlay" role="dialog" aria-modal="true" aria-label="配置中心">
          <div className="configDrawer">
            <div className="configHeader">
              <div>
                <p className="eyebrow">CONFIG CENTER</p>
                <h2>数据源与标签</h2>
              </div>
              <div className="commandActions">
                <button className="ghostButton" onClick={() => setConfigCenterOpen(false)}>关闭</button>
                <button className="primaryButton" onClick={saveConfigCenter} disabled={configSaving || !configCenter}>
                  {configSaving ? <Loader2 size={17} className="spin" /> : <CheckCircle2 size={17} />}
                  保存配置
                </button>
              </div>
            </div>
            <div className="tagLibrary">
              {(configCenter?.taxonomy.manual_tags ?? []).map((tag) => (
                <span key={tag}>{tag}</span>
              ))}
            </div>
            <div className="configSourceList">
              {(configCenter?.config.sources ?? []).map((source) => (
                <article className="configSourceItem" key={source.id}>
                  <label className="sourceToggle">
                    <input
                      type="checkbox"
                      checked={source.enabled}
                      onChange={(event) => updateConfigSource(source.id, { enabled: event.target.checked })}
                    />
                    <span>{source.enabled ? "启用" : "停用"}</span>
                  </label>
                  <div className="configSourceMain">
                    <strong>{source.name}</strong>
                    <small>{source.type} · {source.id}{fixedTagForSource(source) ? ` · 自动标签：${fixedTagForSource(source)}` : ""}</small>
                    <input
                      value={businessTagsForSource(source).join(",")}
                      onChange={(event) => updateConfigSource(source.id, { tags: splitTerms(event.target.value) })}
                      placeholder="业务标签，用逗号分隔"
                    />
                    {source.type === "rss" && (
                      <input
                        value={source.url}
                        onChange={(event) => updateConfigSource(source.id, { url: event.target.value })}
                        placeholder="RSS URL"
                      />
                    )}
                  </div>
                </article>
              ))}
              {!configCenter && <div className="emptyState">正在加载配置中心...</div>}
            </div>
          </div>
        </section>
      )}
      <footer className="deployFooter">
        <div className="footerMain">
          <div className="footerBrand">
            <strong translate="no">AiYX DATA TECH</strong>
            <span>© 2024 Ai Data Technology Co., Ltd. All rights reserved.</span>
            <span>上海爱元飨数据科技有限公司保留所有权利。</span>
          </div>
          <nav className="footerLinks" aria-label="Footer navigation">
            <a href="https://www.aiyxtech.top/privacy-policy" target="_blank" rel="noreferrer">
              Privacy Policy&nbsp; 隐私政策
            </a>
            <a href="https://www.aiyxtech.top/methodology" target="_blank" rel="noreferrer">
              Methodology&nbsp; 方法论
            </a>
            <a href="https://www.aiyxtech.top/agent-api" target="_blank" rel="noreferrer">
              Agent API&nbsp; 接口
            </a>
            <a href="https://www.aiyxtech.top/contact" target="_blank" rel="noreferrer">
              Contact&nbsp; 联系我们
            </a>
          </nav>
        </div>
        <div className="footerIcp">
          ICP备案主体信息/许可证号：沪ICP备2026018988号&nbsp;&nbsp;&nbsp; ICP备案服务信息许可证号：沪ICP备2026018988号-1
        </div>
      </footer>
    </main>
  );
}

function MetricCard({ icon, label, value, tone = "normal" }: { icon: React.ReactNode; label: string; value: number; tone?: string }) {
  return (
    <div className={`metricCard metric-${tone}`}>
      {icon}
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function MetricMini({ label, value }: { label: string; value: number }) {
  return (
    <div className="metricMini">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Badge({ label, tone }: { label: string; tone: string }) {
  return <span className={`badge badge-${tone}`}>{label}</span>;
}

function TagChips({ tags }: { tags: string[] }) {
  return (
    <>
      {tags.map((tag) => (
        <em className="sourceTag" key={tag}>{tag}</em>
      ))}
    </>
  );
}

function GrowthReportPanel({ report, loading }: { report: DailyReport | null; loading: boolean }) {
  const sections = report?.industries ?? [];
  return (
    <section className="growthReport">
      <div className="growthReportHead">
        <div>
          <p className="eyebrow">AI GROWTH INTELLIGENCE</p>
          <h2>大消费数据洞察分析</h2>
        </div>
        <div className="growthMeta">
          <span>{report?.report_date ?? "latest"}</span>
          <span>{report?.model || "规则报告"}</span>
          <Badge label={report?.ai_status ?? (loading ? "generating" : "pending")} tone={report?.ai_status ?? "neutral"} />
        </div>
      </div>
      <div className="growthSummary">
        <FileText size={18} />
        <p>{report?.executive_summary || "报告生成后将在这里展示 AI 对商业增长机会、风险信号和行动建议的研判。"}</p>
      </div>
      <div className="growthMetrics">
        <MetricMini label="匹配事件" value={report?.total_events ?? 0} />
        <MetricMini label="高风险" value={report?.high_risk ?? 0} />
        <MetricMini label="负面" value={report?.negative ?? 0} />
      </div>
      <div className="growthSections">
        {sections.length ? sections.map((section) => (
          <article className="growthSection" key={section.industry}>
            <div className="growthSectionTitle">
              <div>
                <h3>{section.industry}</h3>
                <p>{section.summary}</p>
              </div>
              <strong>{Math.round(section.heat_index)}</strong>
            </div>
            <div className="growthSectionMetrics">
              <span>事件 {section.event_count}</span>
              <span>高风险 {section.high_risk_count}</span>
              <span>负面 {section.negative_count}</span>
            </div>
            <div className="growthSubgrid">
              <div>
                <h4>舆情发展与风险信号</h4>
                {section.top_events.slice(0, 3).map((event) => (
                  <a className="growthEvent" href={event.url} target="_blank" rel="noreferrer" key={event.url || event.title}>
                    <span>{event.title}</span>
                    <small>{event.source} · 热度 {Math.round(event.heat_score)} · {event.risk_level}</small>
                  </a>
                ))}
              </div>
              <div>
                <h4>商业行动建议</h4>
                <ol>
                  {section.recommendations.slice(0, 4).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ol>
              </div>
            </div>
          </article>
        )) : (
          <div className="emptyState">
            <BarChart3 size={24} />
            <strong>{loading ? "大消费数据洞察分析生成中" : "暂无大消费数据洞察分析"}</strong>
            <span>点击“生成报告”或“同步并生成”后展示完整研判内容。</span>
          </div>
        )}
      </div>
    </section>
  );
}

function RelationSummary({ article }: { article: Article }) {
  const relations = extractRelations(article);
  return (
    <div className="relationStack">
      <RelationGroup label="地点" values={relations.locations} tone="location" />
      <RelationGroup label="品牌/关键词" values={relations.brands} tone="brand" />
      <RelationGroup label="人物" values={relations.people} tone="person" />
      <SignalMeter label="文章热度" value={articleHeatValue(article)} min={0} max={100} />
      <SignalMeter label="正负情绪值" value={sentimentValue(article)} min={-10} max={10} signed />
    </div>
  );
}

function RelationGroup({ label, values, tone }: { label: string; values: string[]; tone: "location" | "brand" | "person" }) {
  return (
    <div className="relationGroup">
      <span>{label}</span>
      <div>
        {values.length ? values.map((value) => <em className={`relationChip chip-${tone}`} key={value}>{value}</em>) : <small>未识别</small>}
      </div>
    </div>
  );
}

function HighlightedArticleText({ article }: { article: Article }) {
  const text = cleanText(article.summary) || "暂无摘要";
  const relations = extractRelations(article);
  const terms = [
    ...relations.locations.map((value) => ({ value, tone: "location" as const })),
    ...relations.brands.map((value) => ({ value, tone: "brand" as const })),
    ...relations.people.map((value) => ({ value, tone: "person" as const }))
  ];
  return (
    <div className="highlightedContent">
      {paragraphs(text).map((paragraph, index) => (
        <p key={`${paragraph.slice(0, 18)}-${index}`}>{highlightTerms(paragraph, terms)}</p>
      ))}
    </div>
  );
}

function SignalMeter({ label, value, min, max, signed = false }: { label: string; value: number; min: number; max: number; signed?: boolean }) {
  const percent = ((value - min) / (max - min)) * 100;
  return (
    <div className="signalMeter">
      <div>
        <span>{label}</span>
        <strong>{signed && value > 0 ? `+${value}` : value}</strong>
      </div>
      <i style={{ "--meter-value": `${Math.max(0, Math.min(100, percent))}%` } as React.CSSProperties} />
    </div>
  );
}

function splitTerms(value: string) {
  return value.split(/[,\n，]/).map((item) => item.trim()).filter(Boolean);
}

function unique(values: string[]) {
  return Array.from(new Set(values.filter(Boolean)));
}

function parseList(value: string | string[] | undefined) {
  if (!value) {
    return [];
  }
  if (Array.isArray(value)) {
    return value;
  }
  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return value.split(",").map((item) => item.trim()).filter(Boolean);
  }
}

function cleanText(value = "") {
  const withoutTags = value.replace(/<[^>]+>/g, " ");
  const decoded = document.createElement("textarea");
  decoded.innerHTML = withoutTags;
  return decoded.value.replace(/\s+/g, " ").trim();
}

function truncate(value: string, limit: number) {
  return value.length > limit ? `${value.slice(0, limit)}…` : value;
}

function formatHeroDateTime(date: Date) {
  return formatBeijingDateTime(date);
}

function formatDate(value: string) {
  return formatDateTime(value);
}

function formatDateTime(value: string) {
  if (!value) {
    return "未标注时间";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value.slice(0, 16).replace(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}).*/, "$1年$2月$3日 $4:$5");
  }
  return formatBeijingDateTime(date);
}

function formatBeijingDateTime(value: Date) {
  const parts = new Intl.DateTimeFormat("zh-CN", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(value);
  const byType = Object.fromEntries(parts.map((part) => [part.type, part.value]));

  return `${byType.year}年${byType.month}月${byType.day}日 ${byType.hour}:${byType.minute}`;
}

function articleSourceName(article: Article, sourceNameById: Map<string, string>) {
  return sourceNameById.get(article.source_id) ?? article.source_id;
}

function articleSourceTags(article: Article, sourceTagsById: Map<string, string[]>) {
  return sourceTagsById.get(article.source_id) ?? [article.platform].filter(Boolean);
}

function articleSearchText(article: Article, sourceNameById: Map<string, string>, sourceTagsById: Map<string, string[]>) {
  return `${article.title} ${cleanText(article.summary)} ${articleSourceName(article, sourceNameById)} ${articleSourceTags(article, sourceTagsById).join(" ")} ${parseList(article.matched_keywords).join(" ")} ${parseList(article.matched_core_terms).join(" ")}`
    .toLowerCase();
}

function fixedTagForSource(source: SourceSettings) {
  return fixedSourceTags[source.type] ?? "";
}

function businessTagsForSource(source: SourceSettings) {
  const fixedTag = fixedTagForSource(source);
  return (source.tags ?? []).filter((tag) => tag && tag !== fixedTag);
}

function extractRelations(article: Article) {
  const text = `${article.title} ${cleanText(article.summary)}`;
  const brands = extractBrands(text);
  return {
    locations: pickMatches(text, ["北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "武汉", "南京", "苏州", "兰州", "青海", "香港", "中国", "美国", "韩国", "日本"]),
    brands,
    people: extractPeople(text)
  };
}

function extractBrands(text: string) {
  const values: string[] = [];
  const known = text.match(/烙色\s*L\s*['’]\s*ADOR ECOLORS|烙色L\s*['’]\s*ADOR ECOLORS|烙色L'?ADOR ECOLORS/i);
  if (known) {
    values.push("烙色L'ADOR ECOLORS");
  }
  values.push(...pickMatches(text, relationKeywordCandidates));
  values.push(...Array.from(text.matchAll(/#([^#\s，。；、]{2,18})/g), (match) => match[1]));
  return unique(values.filter(isUsefulRelationKeyword)).slice(0, 8);
}

function isUsefulRelationKeyword(value: string) {
  return value.length > 1 && !/^(GMV|IP|AI|TOP\d+|独家|最近|未来|原文链接)$/i.test(value);
}

function extractPeople(text: string) {
  const values: string[] = [];
  for (const segment of text.matchAll(/(?:博主|达人)[^。；;，,]{0,40}/g)) {
    for (const name of segment[0].matchAll(/[“"『「]([^”"』」]{2,12})[”"』」]/g)) {
      values.push(name[1]);
    }
  }
  return unique(values.filter((value) => value !== "饼干" && !["互撕", "贴标", "撕逼战"].includes(value))).slice(0, 6);
}

function pickMatches(text: string, candidates: string[]) {
  return candidates.filter((candidate) => text.includes(candidate)).slice(0, 5);
}

function articleHeatValue(article: Article) {
  return Math.max(0, Math.min(100, Math.round(Number(article.heat_score ?? 0))));
}

function sentimentValue(article: Article) {
  if (article.sentiment === "positive") return 7;
  if (article.sentiment === "negative") return -7;
  return 0;
}

function displayReadCount(article: Article) {
  return Number(article.read_count || parseMetricFromText(article, /阅读数[:：]\s*([0-9,]+)/));
}

function displayCommentCount(article: Article) {
  return Number(article.comment_count || parseMetricFromText(article, /评论数[:：]\s*([0-9,]+)/));
}

function displayShareCount(article: Article) {
  return Number(article.share_count || parseMetricFromText(article, /转发数[:：]\s*([0-9,]+)/));
}

function parseMetricFromText(article: Article, pattern: RegExp) {
  const match = `${article.title} ${cleanText(article.summary)}`.match(pattern);
  return match ? Number(match[1].replace(/,/g, "")) : 0;
}

function paragraphs(text: string) {
  const normalized = text.replace(/\s+/g, " ").trim();
  const chunks = normalized.match(/[^。！？!?]+[。！？!?]?/g) ?? [normalized];
  return chunks.map((item) => item.trim()).filter(Boolean);
}

function highlightTerms(text: string, terms: Array<{ value: string; tone: "location" | "brand" | "person" }>) {
  const values = terms
    .filter((term) => term.value && text.includes(term.value))
    .sort((a, b) => b.value.length - a.value.length);
  if (!values.length) {
    return text;
  }
  const nodes: React.ReactNode[] = [];
  let cursor = 0;
  while (cursor < text.length) {
    const next = values
      .map((term) => ({ ...term, index: text.indexOf(term.value, cursor) }))
      .filter((term) => term.index >= 0)
      .sort((a, b) => a.index - b.index || b.value.length - a.value.length)[0];
    if (!next) {
      nodes.push(text.slice(cursor));
      break;
    }
    if (next.index > cursor) {
      nodes.push(text.slice(cursor, next.index));
    }
    nodes.push(<mark className={`keywordMark mark-${next.tone}`} key={`${next.value}-${next.index}`}>{next.value}</mark>);
    cursor = next.index + next.value.length;
  }
  return nodes;
}

function articleTime(article: Article) {
  const value = article.published_at || article.last_seen_at;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 0 : date.getTime();
}

function formatModelStatus(runtime: RuntimeSettings | null) {
  if (!runtime) {
    return "模型状态读取中";
  }
  return `${runtime.ai_report.enabled ? "模型已启用" : "规则报告"} · ${runtime.ai_report.model}`;
}

function progressValue(loading: boolean, activeStep: number, completedSteps: string[]) {
  if (loading) {
    return Math.max(12, ((activeStep + 1) / processSteps.length) * 100);
  }
  return completedSteps.length === processSteps.length ? 100 : 0;
}

createRoot(document.getElementById("root")!).render(<App />);
