---
name: us-stock-datasource
description: >
  美股数据源分层配置与运行时路由 / US stock data-source layered setup and runtime routing.
  提供 10 层数据源架构(实时行情 / SEC财报原文 / 基本面 / 分析师观点 / 新闻 / 散户情绪 /
  宏观 / 期权微观结构 / 筛选与市场广度 / 历史回测),向导式一键配置免费数据源(含券商开户即用),
  运行时按请求自动路由并标注延迟级别与来源。
  Provides a 10-layer data-source architecture (real-time quotes / SEC filings / fundamentals /
  analyst views / news / retail sentiment / macro / options microstructure / screening and breadth /
  historical backtesting), a wizard to configure free sources (including broker account feeds),
  and runtime routing that labels latency tier and source.
  Triggers / 触发词: "配置美股数据源", "数据源", "美股数据", "实时行情", "券商数据",
  "数据源审计", "查看我的数据源", "重新配置数据源", "配置 L5", "数据源覆盖", "行情延迟",
  "财报原文", "散户情绪", "configure us stock data source", "us stock data", "market data",
  "data source audit", "real-time quotes", "SEC filings", "retail sentiment".
---

# US Stock Datasource(美股数据源)/ US Stock Datasource

一个**元技能** / A **meta-skill**:它不直接提供行情,而是负责「**分层架构 → 向导配置 → 运行时路由**」,
让 Agent 在任何美股数据需求下自动选对数据源、并如实标注数据新鲜度。
It does not serve quotes directly; it owns **layered architecture → wizard setup → runtime routing**,
so the agent always picks the right source and honestly labels data freshness.

> 范围约定 / Scope:本技能**只做取数,不做交易下单**。/ This skill **only fetches data, never places orders**.

---

## 一、十层数据源架构 / 1. Ten-Layer Architecture

数据源必须分层,因为每一层解决不同问题、时延和成本不同,**上层不能替代下层**。
Data sources must be layered: each layer solves a different problem with different latency/cost,
and **a higher layer can never substitute a lower one**.
完整清单见 / Full source list:[references/layers.md](references/layers.md)。

```
L1  实时行情 Real-time quotes   券商 feed → Finnhub → yfinance(15min delay)
L2  财报原文 SEC filings         SEC EDGAR → sec-api.io → yfinance(aggregated)
L3  基本面聚合 Fundamentals      yfinance → SimFin
L4  分析师观点 Analyst views     yfinance estimates → TipRanks
L5  新闻事件 News                Finnhub news → Marketaux → Yahoo news
L6  散户情绪 Retail sentiment    Adanos → StockTwits
L7  宏观指数 Macro               FRED → yfinance ^VIX
L8  期权微观结构 Options         yfinance options → Polygon
L9  筛选与广度 Screening/breadth Finviz free → yfinance Screener
L10 历史回测 Historical/backtest yfinance history → SimFin
```

## 二、两种工作模式 / 2. Two Modes

### 模式 A:向导安装模式 / Mode A — Setup Wizard(首次配置 / 重配)

```bash
python wizard.py                  # 交互式完整向导 / interactive full wizard
python wizard.py --status         # 只看覆盖矩阵 / print coverage only
python wizard.py --config L5      # 只重配某一层 / reconfigure one layer
python wizard.py --audit          # 数据源审计 / audit sources
python wizard.py --lang en        # 英文界面 / English UI(中文默认 / Chinese default)
```

### 模式 B:运行时路由模式 / Mode B — Runtime Routing(日常)

用户用自然语言提需求时,按 [references/routing.md](references/routing.md) 的路由表映射到正确的层与工具。
每次取数**必须**标注来源与延迟级别。
Map natural-language requests to the right layer/tool via the routing table; **always** label source + latency tier.

## 三、新鲜度标注(强制)/ 3. Freshness Labeling (mandatory)

每次返回数据,末尾必须带一行 / every result must end with:

```
[来源 source: {source} | 延迟 latency: {实时 | 15min delayed | daily | filing-date} | 获取时间 fetched: {iso}]
```

| 级别 Tier | 含义 Meaning | 典型来源 Typical |
|---|---|---|
| 实时 Real-time | 秒级 seconds | 券商 feed、Finnhub(美股) |
| 15 分钟延迟 15-min delayed | 免费行情 free quotes | yfinance 快照 |
| 日频 Daily | 日线/收盘 daily close | yfinance history、FRED |
| 财报披露日 Filing-date | SEC 提交时点 | SEC EDGAR |

**禁止**/ Never:把 15 分钟延迟当实时;把不同层数字混用不标注。
Treat 15-min delayed as real-time; mix numbers across layers without labels.

## 四、向导流程(9 步)/ 4. Wizard Journey (9 steps)

1. **发现/安装 Discover/install** `npx skills add <owner>/us-stock-datasource -g -y`
2. **启动自检 Self-check** → 覆盖矩阵 coverage matrix(每层 ✅/⚠️/❌)
3. **选路径 Choose path** `[1] 快速 Quick [2] 完整 Full [3] 只补缺口 Fill gaps`
4. **逐层向导 Per-layer wizard** 每层一个数字选择带默认值 / one number per layer with default
5. **券商分支(可选)Broker branch (optional)** 先问地区 → 推荐券商 → 专属子流程
6. **凭证录入 Credentials** 填 key(可跳过)→ 写入 `config.json`(gitignored)
7. **冒烟验证 Smoke test** 每层跑一条标准调用,逐行打勾
8. **完成报告 Completion** 最终覆盖矩阵 + 用法说明
9. **日常+维护 Daily + maintenance** `--status` / `--audit` / `--config Lx`

## 五、关键设计规则 / 5. Design Rules

1. **每层多源 + 优先级 / multi-source + priority**:首选一个,失效自动降级到备选。
2. **凭证与状态分离 / credentials & state separated**:key 存 `~/.agents/us-stock-datasource/config.json`(gitignored);状态存 `state.json`。
3. **装一层验一层 / verify per layer**:每层配置完立刻冒烟。
4. **可中断恢复 / resumable**:重跑读 `state.json`,已完成层不重装。
5. **券商不强制 / broker optional**:跳过券商,免费路径仍完整可用。
6. **会自我更新 / self-auditing**:`--audit` 定期验证免费档"当下可用"。

## 六、券商适配(可选)/ 6. Broker Adapters (optional)

券商数据源安装方式各不相同(Alpaca 填 key、IBKR 常驻 Gateway、富途 OpenD、长桥 CLI、Tradier token)。
统一接口与专属子流程见 [references/broker-adapters.md](references/broker-adapters.md)。

## 七、参考文件 / 7. Reference Files

| 文件 File | 内容 Contents |
|---|---|
| [references/layers.md](references/layers.md) | 10 层完整数据源清单 / full 10-layer source list |
| [references/routing.md](references/routing.md) | 运行时路由表 + 新鲜度标注 / routing + freshness |
| [references/broker-adapters.md](references/broker-adapters.md) | 券商统一接口 + 差异化安装 / broker adapters |
| [wizard.py](wizard.py) | 交互式向导安装器(中英双语)/ interactive wizard (bilingual) |
| [config.example.json](config.example.json) | 凭证配置模板 / credentials template |
| [state.json](state.json) | 安装状态清单模板 / state manifest template |
