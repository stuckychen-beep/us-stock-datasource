# 运行时路由表 / Runtime Routing Table

日常使用中,把用户的自然语言请求映射到正确的层与工具。每次取数必须标注来源与延迟级别。
Map natural-language requests to the right layer/tool; always label source + latency tier.

## 路由规则 / Routing

| 用户说 / User says | 层 Layer | 首选 / Primary | 降级链 / Fallback | 延迟标注 / Latency |
|---|---|---|---|---|
| "AAPL 现在多少钱" / "live price" | L1 | 券商 feed / Finnhub | yfinance | 实时 / 15min |
| "谷歌 10-K 原文" / "10-K filing" | L2 | SEC EDGAR | sec-api.io → yfinance | 财报披露日 / filing-date |
| "微软利润表" / "income statement" | L3 | yfinance | SimFin | 日频 / daily |
| "分析师怎么看" / "analyst view" | L4 | yfinance estimates | TipRanks | 日频 / daily |
| "今天有什么新闻" / "news today" | L5 | Finnhub news | Marketaux → Yahoo | 实时(事件流)/ real-time |
| "散户情绪" / "retail sentiment" | L6 | Adanos | StockTwits | 日频 / daily |
| "VIX 多少" / "VIX" | L7 | FRED | yfinance ^VIX | 日频 / daily |
| "期权链" / "options chain" | L8 | yfinance options | Polygon | 日频 / daily |
| "扫异动量" / "unusual volume scan" | L9 | Finviz | yfinance Screener | 日频 / daily |
| "拉 5 年日线" / "5y daily history" | L10 | yfinance history | SimFin | 日频 / daily |

## 新鲜度标注(强制)/ Freshness Labeling (mandatory)

每次返回数据,末尾必须有一行 / every result must end with:

```
[来源 source: {source} | 延迟 latency: {实时 | 15分钟延迟 | 日频 | 财报披露日} | 获取时间 fetched: {iso}]
```

| 级别 Tier | 含义 / Meaning | 典型 / Typical |
|---|---|---|
| 实时 Real-time | 秒级 / seconds | 券商 feed、Finnhub(美股) |
| 15 分钟延迟 15-min delayed | 免费行情 / free quotes | yfinance 快照 |
| 日频 Daily | 日线/收盘 / daily close | yfinance history、FRED |
| 财报披露日 Filing-date | SEC 提交时点 / SEC filing time | SEC EDGAR |

**禁止 / Never**:把 15 分钟延迟当实时;把不同层数字混用不标注。
Treat 15-min delayed as real-time; mix cross-layer numbers without labels.

## 降级与失败处理 / Fallback & Failure Handling

1. 首选源不可用(无 key / 限流 / 报错)→ 自动降级到备选,并在标注里如实写降级后的来源。
   Primary unavailable (no key / rate-limited / error) → fall back and label the actual source.
2. 整层都不可用 → 明确告知「Lx 未配置,可 `python wizard.py --config Lx` 配置」,**不要**静默用别的层顶替。
   Whole layer unavailable → say "Lx not configured, run `python wizard.py --config Lx`"; never silently substitute another layer.
3. 情绪层(L6)只做「拥挤度/旁证」,**不得单独作为买卖依据**,输出时附带提醒。
   L6 is crowding/context only — never a standalone buy/sell signal; add a reminder.

## 常见组合场景 / Common Multi-Source Recipes

| 场景 / Scenario | 拼装 / Compose |
|---|---|
| 财报季个股全景 / Earnings season | L2 财报原文 + L4 预期 + L5 新闻 |
| "大盘回调+资金流入"策略 / pullback+inflow | L7 宏观 + L9 筛选 + L8 期权旁证 |
| 估值分析 / Valuation | L3 基本面 + L4 分析师 + L10 历史区间 |
| 情绪确认 / Sentiment check | L6 情绪 + L5 新闻 + L1 行情 |
