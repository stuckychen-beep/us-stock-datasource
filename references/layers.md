# 十层数据源完整清单 / Ten-Layer Data Source Catalog

每层列出「首选 → 备选」的优先级顺序,尽量免费(开户即用按免费处理)。
Each layer lists sources in priority order (primary → fallback), free-first (broker account feeds count as free).

> 安装形态 / Install type:
> `skill`(npx skills add)· `py_lib`(pip)· `mcp`(cordis.yml + 重启/restart)· `api`(纯 HTTP + key)· `broker`(券商网关/gateway)· `web`(网页/manual)

---

## L1 实时行情 / Real-time Quotes

用途 / Purpose:报价、分时、真实时价格 / quotes, intraday, live price.

| 优先级 Priority | 源 Source | 免费 Free | 安装 Install | key | 备注 Notes |
|---|---|---|---|---|---|
| 1 | 券商 feed / Broker feed(Alpaca·IBKR·Futu·Longbridge·Tradier) | 开户即得 / with account | broker | 是 yes | 唯一免费真实时;见 broker-adapters.md |
| 2 | Finnhub 免费档 / free tier | 免费档 / free tier | api | 是 yes | 美股真实时,60 次/分 |
| 3 | yfinance | 完全免费 / free | py_lib | 否 no | 约 15 分钟延迟,兜底 / ~15-min delayed fallback |

## L2 财报原文 / SEC Filings

用途 / Purpose:10-K / 10-Q / 8-K 原始文件,唯一「as-reported」真相源 / raw filings, the only as-reported truth.

| 优先级 Priority | 源 Source | 免费 Free | 安装 Install | key | 备注 Notes |
|---|---|---|---|---|---|
| 1 | SEC EDGAR + XBRL `companyfacts` | 官方免费 / official free | api | 否 no | JSON 直出,AI 最友好 / JSON, AI-friendly |
| 2 | sec-api.io | 免费档 / free tier | api | 是 yes | EDGAR 搜索/全文包装层 / search wrapper |
| 3 | yfinance 聚合财报 / aggregated | 完全免费 / free | py_lib | 否 no | 非原始口径,核验回 EDGAR / non-raw, verify vs EDGAR |

## L3 基本面聚合 / Fundamentals

用途 / Purpose:财务、估值、股息、同比 / financials, valuation, dividends, YoY.

| 优先级 Priority | 源 Source | 免费 Free | 安装 Install | key | 备注 Notes |
|---|---|---|---|---|---|
| 1 | yfinance | 完全免费 / free | py_lib | 否 no | 覆盖最广 / broadest |
| 2 | SimFin | 免费档 / free tier | api | 是 yes | 标准化口径,回测友好 / standardized, backtest-friendly |

## L4 分析师观点 / Analyst Views

用途 / Purpose:评级、目标价、盈利预期修正 / ratings, targets, estimate revisions.

| 优先级 Priority | 源 Source | 免费 Free | 安装 Install | key | 备注 Notes |
|---|---|---|---|---|---|
| 1 | Yahoo estimates(estimate-analysis) | 完全免费 / free | py_lib | 否 no | 预期修正/分布 / revisions & distribution |
| 2 | TipRanks | 免费网页 / free web | web | 否 no | 按分析师历史准确率加权 / accuracy-weighted |

## L5 新闻事件 / News

用途 / Purpose:公司新闻、突发、财报日历 / company news, events, earnings calendar.

| 优先级 Priority | 源 Source | 免费 Free | 安装 Install | key | 备注 Notes |
|---|---|---|---|---|---|
| 1 | Finnhub 新闻 / news | 免费档 / free tier | api | 是 yes | 与 L1 共用 key / shares L1 key |
| 2 | Marketaux | 免费档(100条/天)/ free tier | api | 是 yes | 自带情感分 / sentiment score |
| 3 | Yahoo 新闻(`ticker.news`) | 完全免费 / free | py_lib | 否 no | 已有能力 / built-in |

## L6 散户情绪 / Retail Sentiment

用途 / Purpose:Reddit / X / 社媒情绪,拥挤度旁证 / social sentiment as crowding signal.

| 优先级 Priority | 源 Source | 免费 Free | 安装 Install | key | 备注 Notes |
|---|---|---|---|---|---|
| 1 | Adanos Market Sentiment | 免费档 / free tier | api | 是 yes | 聚合 5 大源 / aggregates 5 sources |
| 2 | StockTwits | 免费档 / free tier | api | 是 yes | 交易者原生社区 / trader community |
| 3 | 机构 13F / WhaleWisdom | 免费网页 / free web | web | 否 no | 机构动向(季度滞后)/ lagged quarterly |

## L7 宏观指数 / Macro

用途 / Purpose:VIX、利率、通胀背景 / VIX, rates, inflation backdrop.

| 优先级 Priority | 源 Source | 免费 Free | 安装 Install | key | 备注 Notes |
|---|---|---|---|---|---|
| 1 | FRED | 官方免费 / official free | api | 是* | 需免费 API key;宏观最权威 / needs free key |
| 2 | yfinance `^VIX` / `^TNX` | 完全免费 / free | py_lib | 否 no | 零成本 / zero cost |

> *FRED 的 key 免费但需注册;若不想注册,用 yfinance `^VIX` 兜底。
> *FRED key is free but requires signup; use yfinance ^VIX to avoid it.

## L8 期权微观结构 / Options Microstructure

用途 / Purpose:期权链、隐含波动率异动 / options chain, IV anomaly.

| 优先级 Priority | 源 Source | 免费 Free | 安装 Install | key | 备注 Notes |
|---|---|---|---|---|---|
| 1 | yfinance options | 完全免费 / free | py_lib | 否 no | 期权链/到期日 / chain & expiry |
| 2 | Polygon 免费档 / free tier | 免费档(5次/分)/ free tier | api | 是 yes | 历史期权 / historical options |

## L9 筛选与市场广度 / Screening & Breadth

用途 / Purpose:异动量、相对量、做空比例、涨跌广度 / unusual volume, relative volume, breadth.

| 优先级 Priority | 源 Source | 免费 Free | 安装 Install | key | 备注 Notes |
|---|---|---|---|---|---|
| 1 | Finviz 免费版 / free | 免费 / free | web | 否 no | unusual/relative volume;有现成 skill |
| 2 | yfinance `yf.Screener` | 完全免费 / free | py_lib | 否 no | 新版库自带 / built-in |

## L10 历史数据回测 / Historical & Backtest

用途 / Purpose:日线/分钟线历史、标准化财务 / daily/minute bars, standardized financials.

| 优先级 Priority | 源 Source | 免费 Free | 安装 Install | key | 备注 Notes |
|---|---|---|---|---|---|
| 1 | yfinance history | 完全免费 / free | py_lib | 否 no | 日线无限,1m≈7天 / unlimited daily |
| 2 | SimFin | 免费档 / free tier | api | 是 yes | 标准化历史财务 / standardized history |

---

## 免费 key 汇总 / Free API Key Summary(仅这些需要注册 / only these need signup)

| key | 用途 / Use | 注册 / Sign up |
|---|---|---|
| Finnhub | L1 真实时 + L5 新闻 / L1 real-time + L5 news | https://finnhub.io |
| Adanos | L6 情绪 / L6 sentiment | https://adanos.org |
| Marketaux | L5 新闻(备选)/ L5 news (fallback) | https://www.marketaux.com |
| SimFin | L3/L10 标准化财务(可选)/ standardized financials (optional) | https://simfin.com |
| sec-api.io | L2 包装层(可选)/ L2 wrapper (optional) | https://sec-api.io |
| FRED | L7 宏观 / L7 macro | https://fred.stlouisfed.org/docs/api/api_key.html |
| 券商凭证 / Broker creds | L1 真实时 / L1 real-time | 各券商官网 / broker site |
