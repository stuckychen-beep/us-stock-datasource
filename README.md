# US Stock Datasource · 美股数据源分层配置

> 一个「元技能」:把美股投资所需的全部数据源,按**分层架构**组织,用一个**交互式向导**一键配置(免费优先、券商可选),并在运行时**自动路由 + 标注数据新鲜度**。中英双语。
> A **meta-skill**: organize every US-stock data source into a **layered architecture**, configure them with one **interactive wizard** (free-first, broker optional), and **route + label freshness** at runtime. Bilingual EN/中文.

---

## 解决什么问题 / What Problem It Solves

炒股投资需要的数据源多且杂(实时行情、财报、基本面、分析师、新闻、散户情绪…),每类又有好几种免费/付费、skill/MCP/券商 API 等形态。普通投资者经常:**不知道用哪个、把 15 分钟延迟当实时、装了一堆却不知道通没通**。

本 skill 把这些数据源分层、给优先级、做降级链,并让配置过程「装一层、验一层、可中断恢复」。
Investing needs many data sources across many layers; this skill layers them, prioritizes them, and makes setup verify-as-you-go.

## 核心能力 / Key Features

- **十层架构 / 10-layer architecture**:L1 实时 → L2 财报原文 → L3 基本面 → L4 分析师 → L5 新闻 → L6 散户情绪 → L7 宏观 → L8 期权 → L9 筛选 → L10 回测
- **每层多源 + 优先级降级 / multi-source + priority fallback**:首选失效自动降级
- **向导式配置 / wizard setup**:自检 → 选路径 → 逐层 → 券商 → 凭证 → 冒烟 → 完成报告
- **新鲜度标注纪律 / freshness labeling**:实时 / 15分钟延迟 / 日频 / 财报披露日
- **券商按地区适配 / region-based broker**:北美 Alpaca、香港富途、内地长桥、全球 IBKR
- **中英双语 / bilingual**;凭证存本地 `config.json`(gitignored),各环境独立
- **只取数、不下单 / data only, no order execution**

## 快速开始 / Quick Start

```bash
# 安装 / install
npx skills add <owner>/us-stock-datasource -g -y

# 走向导(中文)/ run wizard
python ~/.claude/skills/us-stock-datasource/wizard.py        # Claude Code
python ~/.agents/skills/us-stock-datasource/wizard.py        # DSH / other

# 英文 / English
python .../wizard.py --lang en

# 子命令 / subcommands
python .../wizard.py --status      # 覆盖矩阵 / coverage matrix
python .../wizard.py --config L5   # 只重配一层 / reconfigure one layer
python .../wizard.py --audit       # 数据源审计 / audit sources
```

## 文件结构 / Layout

```
us-stock-datasource/
├── SKILL.md                  # 主指令(脑)/ main instructions (brain)
├── wizard.py                 # 交互式向导(手)/ wizard (hand)
├── config.example.json       # 凭证模板 / credentials template
├── state.json                # 初始状态 / initial state
└── references/
    ├── layers.md             # 十层数据源清单 / layer catalog
    ├── routing.md            # 路由表 + 新鲜度 / routing + freshness
    └── broker-adapters.md    # 券商适配器 / broker adapters
```

## 范围与免责 / Scope & Disclaimer

- 只取数、不下单。/ Data retrieval only, no order execution.
- 本技能是分析工具;数据来源的免费额度与接口可能变化,用 `--audit` 定期验证。
  This is an analytical tool; free-tier limits/APIs change, re-verify with `--audit`.
- **以上内容仅供参考,不构成投资建议。** / For reference only, not investment advice.
