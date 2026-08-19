# US Stock Datasource · 美股数据源分层配置

## 简介 / Introduction

**中文**

一个「元技能」:把美股投资所需的全部数据源——实时行情、SEC 财报原文、基本面、分析师观点、新闻、散户情绪、宏观、期权微观结构、筛选、历史回测——按**十层架构**组织,用一个**交互式向导**一键配置(免费优先、券商按地区可选、中英双语),并在运行时**自动路由 + 标注数据新鲜度**,从机制上杜绝「把 15 分钟延迟当成实时」。

**English**

A meta-skill that organizes every US-stock data source — real-time quotes, SEC filings, fundamentals, analyst views, news, retail sentiment, macro, options microstructure, screening, and backtesting — into a **10-layer architecture**, configures them through an **interactive wizard** (free-first, region-based brokers, bilingual), and **routes + labels freshness** at runtime, so a 15-minute-delayed feed is never mistaken for real-time.

---

## 核心能力 / Key Features

- **十层架构 / 10-layer architecture**:L1 实时 → L2 财报原文 → L3 基本面 → L4 分析师 → L5 新闻 → L6 散户情绪 → L7 宏观 → L8 期权 → L9 筛选 → L10 回测
- **每层多源 + 优先级降级 / multi-source + priority fallback**:首选失效自动降级到备选
- **向导式配置 / wizard setup**:自检 → 选路径 → 逐层 → 券商 → 凭证 → 冒烟 → 完成报告,装一层验一层、可中断恢复
- **新鲜度标注纪律 / freshness labeling**:实时 / 15 分钟延迟 / 日频 / 财报披露日
- **券商按地区适配 / region-based broker**:北美 Alpaca、香港富途、内地长桥、全球 IBKR
- **中英双语 / bilingual**;凭证存本地 `config.json`(gitignored),各环境独立
- **只取数、不下单 / data retrieval only, no order execution**

## 快速开始 / Quick Start

```bash
# 安装 / install
npx skills add <owner>/us-stock-datasource -g -y

# 走向导 / run wizard
python ~/.claude/skills/us-stock-datasource/wizard.py        # Claude Code
python ~/.agents/skills/us-stock-datasource/wizard.py        # DSH / other

# 英文界面 / English UI
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
  This is an analytical tool; free-tier limits and APIs change — re-verify with `--audit`.
- **以上内容仅供参考,不构成投资建议。** / For reference only, not investment advice.
