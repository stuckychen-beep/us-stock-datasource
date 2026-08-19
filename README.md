# US Stock Datasource · 美股数据源分层配置

> 一站式美股数据源管家:配置 + 取数 + 路由,一个入口全搞定。
> One-stop US-stock data-source manager: setup + retrieval + routing, all in one place.

## 安装 / Install

**方法一 · 命令行 / Method 1 · CLI**

打开终端(Windows 用 PowerShell,macOS/Linux 用 Terminal),粘贴这一行回车:

Open a terminal (PowerShell on Windows, Terminal on macOS/Linux) and paste:

```bash
npx skills add stuckychen-beep/us-stock-datasource@us-stock-datasource -g -y
```

**方法二 · 交给你的 AI 助手 / Method 2 · Let your agent do it**

把这个链接复制给你的 AI 助手(支持 skills 的,如 Claude Code、Cursor、DSH、Codex、OpenClaw 等),对它说:

Copy this link to your AI assistant (one that supports skills — Claude Code, Cursor, DSH, Codex, OpenClaw …) and say:

> 帮我安装这个 skill:https://github.com/stuckychen-beep/us-stock-datasource
> Install this skill for me: https://github.com/stuckychen-beep/us-stock-datasource

---

## 简介 / Introduction

### 痛点 / The Problem

投资美股,数据源又多又乱:实时行情、SEC 财报、基本面、分析师评级、新闻、散户情绪……每一类又有免费/付费、skill / MCP / 券商 API 好几种形态,**而且真正实时、好用的那一档,大多要收费**。结果就是:不知道该用哪个、把 15 分钟延迟当实时、装了一堆却不知道通没通、换个券商数据源又要从头折腾一遍。

Investing in US stocks means juggling many messy data sources — real-time quotes, SEC filings, fundamentals, analyst ratings, news, retail sentiment — each with multiple free/paid forms (skills, MCP servers, broker APIs), **and the genuinely real-time, good-quality tier usually costs money**. The result: you don't know which to use, you mistake a 15-minute-delayed feed for real-time, you install a pile of tools without knowing what works, and switching brokers means redoing everything.

### 怎么解决 / The Solution

这个 skill 把数据源拆成**十层**,每层排好**优先级 + 降级链**;用一个**交互式向导**「装一层、验一层、可中断恢复」地配好;之后你随口说一句「查 AAPL 实时价」,它**自动路由**到正确的层和源,并**强制标注数据新鲜度**。**而且做到【真免费】:免费源优先、券商开户即有(按免费处理),不用为数据本身掏一分钱。**

This skill splits data sources into **ten layers**, each with **priority + fallback**; an **interactive wizard** configures them verify-as-you-go and resumable; afterward "AAPL live price" is **auto-routed** to the right layer and source with **mandatory freshness labeling**. **And it's genuinely free: free sources first, broker account feeds treated as free — no money required for the data itself.**

### 一站式 / One-Stop ✨

**一个 skill,管全部。** 从「配置」到「日常取数」一站式搞定:不用再逐个找 skill、逐个配 key、逐个记命令。实时行情、财报原文、散户情绪……所有数据需求,一个入口,**真免费,券商真实时可选。**

**One skill, everything.** A single entry point for both setup and daily retrieval: no more hunting for individual skills, configuring keys one by one, or memorizing per-tool commands. Quotes, filings, sentiment — every data need in one place, **genuinely free, with optional broker real-time.**

---

## 核心能力 / Key Features

- **十层架构 / 10-layer architecture**:L1 实时 → L2 财报原文 → L3 基本面 → L4 分析师 → L5 新闻 → L6 散户情绪 → L7 宏观 → L8 期权 → L9 筛选 → L10 回测。
  Real-time → filings → fundamentals → analysts → news → sentiment → macro → options → screening → backtest.
- **每层多源 + 优先级降级 / multi-source + priority fallback**:首选失效自动降级到备选,不中断。
  Falls back automatically when the primary source fails, without interruption.
- **向导式配置 / wizard setup**:自检 → 选路径 → 逐层 → 券商 → 凭证 → 冒烟 → 完成报告;装一层验一层、可中断恢复。
  Self-check → path → per-layer → broker → credentials → smoke → report; verify-as-you-go and resumable.
- **新鲜度标注纪律 / freshness labeling**:实时 / 15 分钟延迟 / 日频 / 财报披露日,杜绝「把延迟当实时」。
  Real-time / 15-min delayed / daily / filing-date — never mistake delayed data for real-time.
- **券商按地区适配 / region-based broker**:北美 Alpaca、香港富途、内地长桥、全球 IBKR,开户即有真实时。
  US→Alpaca, HK→Futu, CN→Longbridge, global→IBKR; real-time with just an account.
- **中英双语 / bilingual**:界面与文档均双语;凭证存本地 `config.json`(gitignored),各环境独立。
  UI and docs in both languages; credentials stored locally in `config.json` (gitignored), each environment isolated.
- **只取数、不下单 / data retrieval only, no order execution.**

## 运行向导 / Run the Wizard

```bash
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
