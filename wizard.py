#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
US Stock Datasource — 美股数据源分层配置向导 (bilingual 中英双语)
============================================================

用法 / Usage:
    python wizard.py                 # 交互式完整向导 / interactive full wizard
    python wizard.py --status        # 只打印覆盖矩阵 / coverage only
    python wizard.py --config L5     # 只重配某一层 / reconfigure one layer
    python wizard.py --audit         # 数据源审计 / audit sources
    python wizard.py --lang en       # 英文界面 / English UI (中文默认 / Chinese default)

设计原则 / Principles:
    分层 + 每层多源 + 优先级首选 + 向导式 + 免费优先 + 装一层验一层
    Layered + multi-source + priority + wizard + free-first + verify-per-layer
    只取数,不下单 / data only, no order execution.
"""

import argparse
import datetime
import json
import shutil
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path

# 强制 UTF-8 输出,避免 Windows GBK 控制台无法编码 emoji/中文导致崩溃
# Force UTF-8 output to avoid GBK console crashing on emoji/CJK.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# i18n
# ---------------------------------------------------------------------------
LANG = "zh"


def pick(zh, en):
    """按当前语言返回中文或英文 / return zh or en by current language."""
    return zh if LANG == "zh" else en


T = {
    "banner_title": {"zh": "美股数据源 · 分层配置向导", "en": "US Stock Datasource · Layered Setup Wizard"},
    "banner_sub1": {"zh": "免费优先 · 券商可选 · 装一层验一层 · 只取数不下单",
                    "en": "Free-first · Broker optional · Verify-per-layer · Data only"},
    "env_check": {"zh": "【环境自检】", "en": "[Environment check]"},
    "python": {"zh": "Python", "en": "Python"},
    "libs": {"zh": "关键库", "en": "Key libs"},
    "skills": {"zh": "已装 skill", "en": "Installed skills"},
    "none": {"zh": "(无)", "en": "(none)"},
    "coverage_title": {"zh": "当前美股数据源覆盖状态", "en": "Current US stock data-source coverage"},
    "not_configured": {"zh": "(未配置)", "en": "(not configured)"},
    "choose_path": {"zh": "【选择路径】", "en": "[Choose path]"},
    "path1": {"zh": "[1] 快速开始 —— 全免费默认包,跳过券商,约3分钟",
              "en": "[1] Quick start — all-free pack, skip broker (~3 min)"},
    "path2": {"zh": "[2] 完整向导 —— 逐层定制,可接券商真实时(推荐,约10分钟)",
              "en": "[2] Full wizard — per-layer, optional broker real-time (recommended, ~10 min)"},
    "path3": {"zh": "[3] 只补缺口 —— 仅配置当前缺失的层",
              "en": "[3] Fill gaps — only configure missing layers"},
    "your_choice": {"zh": "你的选择", "en": "Your choice"},
    "quick_note": {"zh": "快速开始:按每层「首选免费源」自动配置,跳过券商。",
                   "en": "Quick start: auto-select the primary free source per layer, skip broker."},
    "fill_note": {"zh": "只补缺口:仅处理未就绪的层。", "en": "Fill gaps: only process layers not yet ready."},
    "full_note": {"zh": "完整向导:逐层确认。", "en": "Full wizard: confirm layer by layer."},
    "skip_ready": {"zh": "已就绪,跳过", "en": "already ready, skip"},
    "smoke_title": {"zh": "【冒烟验证】", "en": "[Smoke test]"},
    "complete1": {"zh": "配置完成!冒烟通过", "en": "Done! Smoke passed"},
    "complete2": {"zh": "以后直接说「查 AAPL 实时价」「特斯拉财报原文」「NVDA 散户情绪」",
                  "en": "From now on just say \"AAPL live price\", \"Tesla 10-K\", \"NVDA retail sentiment\""},
    "complete3": {"zh": "我会自动路由到正确数据源,并标注来源与延迟级别。",
                  "en": "I will route to the right source and label source + latency tier."},
    "complete4": {"zh": "维护命令", "en": "Maintenance"},
    "broker_first": {"zh": "首选是券商 feed(真实时),也可选免费替代。",
                     "en": "Primary is broker feed (real-time); free alternatives also available."},
    "use_broker": {"zh": "接券商真实时吗?", "en": "Connect a broker for real-time?"},
    "yes_broker": {"zh": "是,接券商", "en": "Yes, broker"},
    "no_broker": {"zh": "否,用免费源", "en": "No, free source"},
    "star": {"zh": "★", "en": "*"},
    "auto_choice": {"zh": "自动选择", "en": "auto-selected"},
    "choose_which": {"zh": "选哪个?", "en": "Choose which?"},
    "paste_key": {"zh": "粘贴 key(回车跳过)", "en": "Paste key (Enter to skip)"},
    "key_saved": {"zh": "key 已保存", "en": "key saved"},
    "skip_layer": {"zh": "跳过,该层标记为「待配置」", "en": "skipped, layer marked \"need key\""},
    "key_exists": {"zh": "已有 key,复用", "en": "existing key, reuse"},
    "installing": {"zh": "安装", "en": "Installing"},
    "install_failed": {"zh": "安装失败", "en": "install failed"},
    "setup_label": {"zh": "→ 步骤", "en": "→ setup"},
    "broker_title": {"zh": "【券商数据源 · 按地区推荐】", "en": "[Broker data source · by region]"},
    "region_q": {"zh": "你在哪个地区?", "en": "Which region are you in?"},
    "region_recommend": {"zh": "地区推荐", "en": "recommendations"},
    "recommended": {"zh": "(推荐)", "en": "(recommended)"},
    "choose_broker": {"zh": "选哪个券商?", "en": "Choose which broker?"},
    "selected_broker": {"zh": "已选", "en": "Selected"},
    "broker_subflow": {"zh": "子流程", "en": "sub-flow"},
    "broker_continue": {"zh": "请完成上述券商侧的安装/登录后再继续(向导不阻塞,先记录凭证)",
                        "en": "Finish the broker-side install/login above, then continue (wizard records credentials, non-blocking)"},
    "paste_api_key": {"zh": "粘贴 API key(回车跳过)", "en": "Paste API key (Enter to skip)"},
    "paste_secret": {"zh": "粘贴 secret(回车跳过)", "en": "Paste secret (Enter to skip)"},
    "paste_token": {"zh": "粘贴 token/确认登录态(回车跳过)", "en": "Paste token / confirm login (Enter to skip)"},
    "broker_recorded": {"zh": "已记录券商", "en": "broker recorded"},
    "broker_login_note": {"zh": "登录态请在券商侧自行维护。", "en": "Maintain login state on the broker side."},
    "audit_title": {"zh": "【数据源审计】—— 重新验证各层免费档可用性", "en": "[Data source audit] — re-verify each layer's free tier"},
    "audit_note": {"zh": "(审计不修改配置;若某层失效,用 python wizard.py --config <层> 重配)",
                   "en": "(audit does not modify config; if a layer fails, run python wizard.py --config <layer>)"},
    "layer_not_found": {"zh": "未找到层", "en": "layer not found"},
    "layer_options": {"zh": "可选", "en": "options"},
    "interrupted": {"zh": "已中断,进度已尽量保存。可重跑继续。", "en": "Interrupted; progress saved where possible. Re-run to continue."},
    "error": {"zh": "出错", "en": "error"},
    "recon_smoke": {"zh": "冒烟", "en": "smoke"},
}


def t(key):
    return T[key][LANG]


# ---------------------------------------------------------------------------
# 路径 / Paths
# ---------------------------------------------------------------------------
HOME = Path.home()
SKILL_DIR = Path(__file__).resolve().parent
CONF_DIR = SKILL_DIR  # self-contained: config/state live inside the skill dir (per-environment isolation)
CONFIG_PATH = CONF_DIR / "config.json"
STATE_PATH = CONF_DIR / "state.json"
AAPL_CIK = "0000320193"

# ---------------------------------------------------------------------------
# 十层数据源定义(双语)/ Ten-layer data-source definitions (bilingual)
# ---------------------------------------------------------------------------
LAYERS = [
    {
        "id": "L1", "name": "实时行情", "name_en": "Real-time quotes",
        "purpose": "报价 / 分时 / 真实时价格", "purpose_en": "quote / intraday / live price",
        "sources": [
            {"id": "broker", "name": "券商 feed(开户即用,真实时)", "name_en": "Broker feed (account-based, real-time)",
             "kind": "broker", "free": "开户即得", "free_en": "with account", "key": True,
             "setup": "进入券商分支,按地区推荐", "setup_en": "enter broker branch, region-based"},
            {"id": "finnhub", "name": "Finnhub 免费档(美股真实时,60次/分)", "name_en": "Finnhub free (US real-time, 60/min)",
             "kind": "api", "free": "免费档", "free_en": "free tier", "key": True,
             "setup": "https://finnhub.io 注册后粘贴 API key", "setup_en": "register at finnhub.io, paste API key"},
            {"id": "yfinance", "name": "yfinance(约15分钟延迟,免key)", "name_en": "yfinance (~15-min delay, no key)",
             "kind": "py_lib", "free": "完全免费", "free_en": "free", "key": False,
             "setup": "pip install yfinance(默认已装)", "setup_en": "pip install yfinance (usually pre-installed)"},
        ],
        "default": "yfinance",
    },
    {
        "id": "L2", "name": "财报原文", "name_en": "SEC filings",
        "purpose": "10-K / 10-Q / 8-K 原始文件", "purpose_en": "10-K / 10-Q / 8-K raw filings",
        "sources": [
            {"id": "sec_edgar", "name": "SEC EDGAR + XBRL(官方免费,免key)", "name_en": "SEC EDGAR + XBRL (official, no key)",
             "kind": "api", "free": "官方免费", "free_en": "official free", "key": False,
             "setup": "无需配置,官方接口直连", "setup_en": "no config, direct official API"},
            {"id": "sec_api", "name": "sec-api.io(EDGAR 搜索包装层)", "name_en": "sec-api.io (EDGAR wrapper)",
             "kind": "api", "free": "免费档", "free_en": "free tier", "key": True,
             "setup": "https://sec-api.io 注册后粘贴 key", "setup_en": "register at sec-api.io, paste key"},
            {"id": "yfinance_fs", "name": "yfinance 聚合财报(非原始口径)", "name_en": "yfinance aggregated (non-raw)",
             "kind": "py_lib", "free": "完全免费", "free_en": "free", "key": False,
             "setup": "降级兜底,核验请回 EDGAR", "setup_en": "fallback; verify against EDGAR"},
        ],
        "default": "sec_edgar",
    },
    {
        "id": "L3", "name": "基本面聚合", "name_en": "Fundamentals",
        "purpose": "财务 / 估值 / 股息 / 同比", "purpose_en": "financials / valuation / dividend / YoY",
        "sources": [
            {"id": "yfinance_fund", "name": "yfinance(覆盖最广,已随全家桶装)", "name_en": "yfinance (broadest, pre-installed)",
             "kind": "py_lib", "free": "完全免费", "free_en": "free", "key": False,
             "setup": "pip install yfinance", "setup_en": "pip install yfinance"},
            {"id": "simfin", "name": "SimFin(标准化口径,回测友好)", "name_en": "SimFin (standardized, backtest-friendly)",
             "kind": "api", "free": "免费档", "free_en": "free tier", "key": True,
             "setup": "https://simfin.com 注册后粘贴 key", "setup_en": "register at simfin.com, paste key"},
        ],
        "default": "yfinance_fund",
    },
    {
        "id": "L4", "name": "分析师观点", "name_en": "Analyst views",
        "purpose": "评级 / 目标价 / 预期修正", "purpose_en": "ratings / targets / estimate revisions",
        "sources": [
            {"id": "yfinance_est", "name": "Yahoo estimates(estimate-analysis,已装)", "name_en": "Yahoo estimates (estimate-analysis, pre-installed)",
             "kind": "py_lib", "free": "完全免费", "free_en": "free", "key": False,
             "setup": "无需配置", "setup_en": "no config"},
            {"id": "tipranks", "name": "TipRanks 免费网页(人工复核)", "name_en": "TipRanks free web (manual review)",
             "kind": "web", "free": "免费网页", "free_en": "free web", "key": False,
             "setup": "无需配置,网页查询", "setup_en": "no config, web lookup"},
        ],
        "default": "yfinance_est",
    },
    {
        "id": "L5", "name": "新闻事件", "name_en": "News",
        "purpose": "公司新闻 / 突发 / 财报日历", "purpose_en": "company news / events / earnings calendar",
        "sources": [
            {"id": "finnhub_news", "name": "Finnhub 新闻(与 L1 共用 key)", "name_en": "Finnhub news (shares L1 key)",
             "kind": "api", "free": "免费档", "free_en": "free tier", "key": True,
             "setup": "复用 Finnhub key", "setup_en": "reuse Finnhub key"},
            {"id": "marketaux", "name": "Marketaux(100条/天,自带情感分)", "name_en": "Marketaux (100/day, sentiment)",
             "kind": "api", "free": "免费档", "free_en": "free tier", "key": True,
             "setup": "https://www.marketaux.com 注册后粘贴 key", "setup_en": "register at marketaux.com, paste key"},
            {"id": "yahoo_news", "name": "Yahoo 新闻(ticker.news)", "name_en": "Yahoo news (ticker.news)",
             "kind": "py_lib", "free": "完全免费", "free_en": "free", "key": False,
             "setup": "随 yfinance,无需配置", "setup_en": "bundled with yfinance, no config"},
        ],
        "default": "yahoo_news",
    },
    {
        "id": "L6", "name": "散户情绪", "name_en": "Retail sentiment",
        "purpose": "Reddit / X / 社媒情绪(拥挤度旁证)", "purpose_en": "Reddit / X / social sentiment (crowding)",
        "sources": [
            {"id": "adanos", "name": "Adanos Sentiment(聚合5大源,有官方skill)", "name_en": "Adanos Sentiment (5 sources, official skill)",
             "kind": "api", "free": "免费档", "free_en": "free tier", "key": True,
             "setup": "https://adanos.org 注册后粘贴 key", "setup_en": "register at adanos.org, paste key"},
            {"id": "stocktwits", "name": "StockTwits API(交易者原生社区)", "name_en": "StockTwits API (trader community)",
             "kind": "api", "free": "免费档", "free_en": "free tier", "key": True,
             "setup": "https://stocktwits.com 注册后粘贴 key", "setup_en": "register at stocktwits.com, paste key"},
        ],
        "default": "adanos",
    },
    {
        "id": "L7", "name": "宏观指数", "name_en": "Macro",
        "purpose": "VIX / 利率 / 通胀背景", "purpose_en": "VIX / rates / inflation backdrop",
        "sources": [
            {"id": "fred", "name": "FRED(官方免费,免key)", "name_en": "FRED (official, no key)",
             "kind": "api", "free": "官方免费", "free_en": "official free", "key": False,
             "setup": "无需配置,官方接口直连", "setup_en": "no config, direct official API"},
            {"id": "yfinance_macro", "name": "yfinance ^VIX / ^TNX", "name_en": "yfinance ^VIX / ^TNX",
             "kind": "py_lib", "free": "完全免费", "free_en": "free", "key": False,
             "setup": "随 yfinance,无需配置", "setup_en": "bundled with yfinance, no config"},
        ],
        "default": "fred",
    },
    {
        "id": "L8", "name": "期权微观结构", "name_en": "Options microstructure",
        "purpose": "期权链 / 隐含波动率异动", "purpose_en": "options chain / IV anomaly",
        "sources": [
            {"id": "yfinance_opt", "name": "yfinance options(已装)", "name_en": "yfinance options (pre-installed)",
             "kind": "py_lib", "free": "完全免费", "free_en": "free", "key": False,
             "setup": "随 yfinance,无需配置", "setup_en": "bundled with yfinance, no config"},
            {"id": "polygon", "name": "Polygon 免费档(5次/分,历史期权)", "name_en": "Polygon free (5/min, historical options)",
             "kind": "api", "free": "免费档", "free_en": "free tier", "key": True,
             "setup": "https://polygon.io 注册后粘贴 key", "setup_en": "register at polygon.io, paste key"},
        ],
        "default": "yfinance_opt",
    },
    {
        "id": "L9", "name": "筛选与市场广度", "name_en": "Screening & breadth",
        "purpose": "异动量 / 相对量 / 涨跌广度", "purpose_en": "unusual volume / relative volume / breadth",
        "sources": [
            {"id": "finviz", "name": "Finviz 免费版(unusual volume)", "name_en": "Finviz free (unusual volume)",
             "kind": "web", "free": "免费", "free_en": "free", "key": False,
             "setup": "无需配置,网页查询;有现成 finviz-screener skill", "setup_en": "no config, web; a finviz-screener skill exists"},
            {"id": "yfinance_screen", "name": "yfinance yf.Screener(新版库自带)", "name_en": "yfinance yf.Screener (built-in)",
             "kind": "py_lib", "free": "完全免费", "free_en": "free", "key": False,
             "setup": "随 yfinance,无需配置", "setup_en": "bundled with yfinance, no config"},
        ],
        "default": "finviz",
    },
    {
        "id": "L10", "name": "历史数据回测", "name_en": "Historical / backtest",
        "purpose": "日线/分钟线 / 标准化财务", "purpose_en": "daily/minute bars / standardized financials",
        "sources": [
            {"id": "yfinance_hist", "name": "yfinance history(日线无限)", "name_en": "yfinance history (unlimited daily)",
             "kind": "py_lib", "free": "完全免费", "free_en": "free", "key": False,
             "setup": "随 yfinance,无需配置", "setup_en": "bundled with yfinance, no config"},
            {"id": "simfin_hist", "name": "SimFin 标准化历史财务", "name_en": "SimFin standardized history",
             "kind": "api", "free": "免费档", "free_en": "free tier", "key": True,
             "setup": "与 L3 共用 SimFin key", "setup_en": "shares SimFin key with L3"},
        ],
        "default": "yfinance_hist",
    },
]

# ---------------------------------------------------------------------------
# 券商分支(双语)/ Broker branch (bilingual)
# ---------------------------------------------------------------------------
BROKERS_BY_REGION = {
    "美国/北美": [
        {"id": "alpaca", "name": "Alpaca", "recommend": True,
         "note": "API 最简单,IEX 数据源免费真实时,有模拟盘", "note_en": "simplest API, free real-time IEX feed, paper account",
         "setup": "pip install alpaca-py;去 https://alpaca.markets 生成 Paper Key/Secret", "setup_en": "pip install alpaca-py; generate Paper Key/Secret at alpaca.markets"},
        {"id": "tradier", "name": "Tradier", "recommend": False,
         "note": "最轻,一个 token;美股期权数据强", "note_en": "lightest, single token; strong US options data",
         "setup": "去 https://tradier.com 生成 access token", "setup_en": "generate access token at tradier.com"},
        {"id": "ibkr", "name": "IBKR", "recommend": False,
         "note": "功能最全,需常驻 IB Gateway", "note_en": "most complete; needs resident IB Gateway",
         "setup": "pip install ib_insync;启动 IB Gateway 并登录", "setup_en": "pip install ib_insync; start IB Gateway and log in"},
    ],
    "香港": [
        {"id": "futu", "name": "富途 Futu", "recommend": True,
         "note": "港股最强,必须常驻 OpenD", "note_en": "best for HK; needs resident OpenD",
         "setup": "pip install futu-api;启动 OpenD 并登录牛牛号", "setup_en": "pip install futu-api; start OpenD and log in"},
        {"id": "longbridge", "name": "长桥 Longbridge", "recommend": False,
         "note": "与 value-investing skill 配套", "note_en": "pairs with value-investing skill",
         "setup": "安装 longbridge-terminal;运行 longbridge auth login 扫码", "setup_en": "install longbridge-terminal; run 'longbridge auth login'"},
        {"id": "ibkr", "name": "IBKR", "recommend": False,
         "note": "功能最全,需常驻 IB Gateway", "note_en": "most complete; needs resident IB Gateway",
         "setup": "pip install ib_insync;启动 IB Gateway 并登录", "setup_en": "pip install ib_insync; start IB Gateway and log in"},
    ],
    "内地": [
        {"id": "longbridge", "name": "长桥 Longbridge", "recommend": True,
         "note": "与 value-investing skill 配套", "note_en": "pairs with value-investing skill",
         "setup": "安装 longbridge-terminal;运行 longbridge auth login 扫码", "setup_en": "install longbridge-terminal; run 'longbridge auth login'"},
        {"id": "futu", "name": "富途 Futu", "recommend": False,
         "note": "港股最强,必须常驻 OpenD", "note_en": "best for HK; needs resident OpenD",
         "setup": "pip install futu-api;启动 OpenD 并登录牛牛号", "setup_en": "pip install futu-api; start OpenD and log in"},
        {"id": "ibkr", "name": "IBKR", "recommend": False,
         "note": "功能最全,需常驻 IB Gateway", "note_en": "most complete; needs resident IB Gateway",
         "setup": "pip install ib_insync;启动 IB Gateway 并登录", "setup_en": "pip install ib_insync; start IB Gateway and log in"},
    ],
    "欧洲": [
        {"id": "ibkr", "name": "IBKR", "recommend": True,
         "note": "全球账户,功能最全", "note_en": "global account, most complete",
         "setup": "pip install ib_insync;启动 IB Gateway 并登录", "setup_en": "pip install ib_insync; start IB Gateway and log in"},
    ],
    "全球/其他": [
        {"id": "ibkr", "name": "IBKR", "recommend": True,
         "note": "全球账户,功能最全", "note_en": "global account, most complete",
         "setup": "pip install ib_insync;启动 IB Gateway 并登录", "setup_en": "pip install ib_insync; start IB Gateway and log in"},
        {"id": "alpaca", "name": "Alpaca", "recommend": False,
         "note": "API 最简单,IEX 数据源免费真实时", "note_en": "simplest API, free real-time IEX feed",
         "setup": "pip install alpaca-py;去 https://alpaca.markets 生成 Paper Key/Secret", "setup_en": "pip install alpaca-py; generate Paper Key/Secret at alpaca.markets"},
    ],
}

# ---------------------------------------------------------------------------
# 工具函数 / Helpers
# ---------------------------------------------------------------------------

def load_json(path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def default_state():
    p = Path(__file__).parent / "state.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"layers": {}}


def ask_int(prompt, lo, hi, default=None):
    hint = f"[{lo}-{hi}]"
    if default is not None:
        hint = f"[{lo}-{hi},{pick('回车', 'Enter')}={default}]"
    while True:
        raw = input(f"{prompt} {hint}: ").strip()
        if raw == "" and default is not None:
            return default
        try:
            v = int(raw)
            if lo <= v <= hi:
                return v
        except (ValueError, EOFError, KeyboardInterrupt):
            raise
        print("  " + pick(f"请输入 {lo}~{hi} 之间的数字。", f"Enter a number between {lo} and {hi}."))


def has_cmd(cmd):
    return shutil.which(cmd) is not None


def py_importable(mod):
    try:
        subprocess.run([sys.executable, "-c", f"import {mod}"], check=True, capture_output=True, timeout=60)
        return True
    except Exception:
        return False


def detect():
    info = {"python": sys.executable, "libs": {}, "skills": [], "brokers": {}}
    for lib in ("yfinance", "pandas", "alpaca", "futu", "ib_insync"):
        info["libs"][lib] = py_importable(lib)
    skills_root = HOME / ".agents" / "skills"
    if skills_root.exists():
        info["skills"] = sorted(d.name for d in skills_root.iterdir() if d.is_dir())
    if has_cmd("longbridge"):
        info["brokers"]["longbridge"] = True
    return info


# ---------------------------------------------------------------------------
# 覆盖矩阵 / Coverage
# ---------------------------------------------------------------------------

def coverage(state):
    icon = {"ready": "✅", "need_key": "⚠️", "not_configured": "❌", "partial": "🟡"}
    print("\n" + "=" * 62)
    print("  " + t("coverage_title"))
    print("=" * 62)
    for layer in LAYERS:
        lid = layer["id"]
        st = state["layers"].get(lid, {})
        status = st.get("status", "not_configured")
        src = st.get("source", "")
        src_disp = st.get("source_name") or src
        name = pick(layer["name"], layer["name_en"])
        line = f"  {icon.get(status, '❌')} {lid} {name:<16} {src_disp or t('not_configured')}"
        print(line)
    print("=" * 62)


# ---------------------------------------------------------------------------
# 冒烟验证 / Smoke
# ---------------------------------------------------------------------------

def http_get_json(url, timeout=15, headers=None):
    h = {"User-Agent": "us-stock-datasource-wizard/1.0"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _smoke_yfinance(lid):
    code = {
        "L1": "import yfinance as yf; d=yf.Ticker('AAPL').fast_info; v=d['lastPrice']; assert v, 'empty'; print(v)",
        "L3": "import yfinance as yf; d=yf.Ticker('AAPL').income_stmt; assert not d.empty, 'empty'; print(d.shape)",
        "L4": "import yfinance as yf; d=yf.Ticker('AAPL').analyst_price_targets; assert d, 'empty'; print(d)",
        "L5": "import yfinance as yf; d=yf.Ticker('AAPL').news; assert len(d)>0, 'empty'; print(len(d))",
        "L7": "import yfinance as yf; d=yf.Ticker('^VIX').fast_info; v=d['lastPrice']; assert v, 'empty'; print(v)",
        "L8": "import yfinance as yf; d=yf.Ticker('AAPL').options; assert len(d)>0, 'empty'; print(len(d))",
        "L9": "import yfinance as yf; assert hasattr(yf,'Screener'), 'no screener'; print('screener ok')",
        "L10": "import yfinance as yf; d=yf.Ticker('AAPL').history(period='5d'); assert len(d)>0, 'empty'; print(len(d))",
    }.get(lid)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    if r.returncode == 0:
        return True, f"yfinance OK → {r.stdout.strip()[:60]}"
    return False, f"yfinance unavailable: {r.stderr.strip()[:80]}"


def _smoke_adanos(key):
    try:
        d = http_get_json(
            "https://api.adanos.org/reddit/stocks/v1/trending?days=7&limit=3",
            headers={"X-API-Key": key},
        )
        top = d[0] if d else {}
        return True, f"Adanos OK → top {top.get('ticker')} buzz {top.get('buzz_score')}"
    except Exception as e:
        return False, f"Adanos: {type(e).__name__}: {str(e)[:80]}"


def _smoke_broker(state, cfg):
    b = state.get("broker", {}).get("name", "")
    if b == "futu":
        try:
            with socket.create_connection(("127.0.0.1", 11111), timeout=5):
                return True, "Futu OpenD reachable on 127.0.0.1:11111"
        except OSError:
            return False, "Futu OpenD not reachable (start OpenD & log in)"
    if b == "longbridge":
        if has_cmd("longbridge"):
            r = subprocess.run(["longbridge", "quote", "AAPL.US"], capture_output=True, text=True, timeout=30)
            if r.returncode == 0:
                return True, "longbridge CLI OK"
            return False, f"longbridge: {r.stderr.strip()[:60]}"
        return False, "longbridge CLI not found"
    broker_cfg = cfg.get("broker", {})
    if broker_cfg.get("api_key") or broker_cfg.get("secret") or broker_cfg.get("token"):
        return True, f"broker ({b}) credential set — verify login broker-side"
    return False, f"broker ({b or '?'}) — no credential recorded yet"


def smoke_layer(layer, cfg, state):
    lid = layer["id"]
    src = state["layers"].get(lid, {}).get("source", "")
    try:
        if lid == "L1":
            if src == "broker":
                return _smoke_broker(state, cfg)
            if src == "finnhub" and cfg.get("finnhub_key"):
                d = http_get_json(f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={cfg['finnhub_key']}")
                return True, f"AAPL ${d.get('c')} (Finnhub, real-time)"
            return _smoke_yfinance("L1")
        if lid == "L2":
            d = http_get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{AAPL_CIK}.json")
            keys = list(d.get("facts", {}).get("us-gaap", {}).keys())[:3]
            return True, f"SEC EDGAR OK, us-gaap sample: {keys}"
        if lid == "L3":
            return _smoke_yfinance("L3")
        if lid == "L4":
            return _smoke_yfinance("L4")
        if lid == "L5":
            if src == "finnhub_news" and cfg.get("finnhub_key"):
                d = http_get_json(f"https://finnhub.io/api/v1/company-news?symbol=AAPL&from=2026-01-01&to=2026-01-02&token={cfg['finnhub_key']}")
                return True, f"Finnhub news OK, {len(d)} items"
            return _smoke_yfinance("L5")
        if lid == "L6":
            if src == "adanos" and cfg.get("adanos_key"):
                return _smoke_adanos(cfg["adanos_key"])
            return False, "needs Adanos key → mark 'need key'"
        if lid == "L7":
            if src == "fred":
                return False, "FRED needs a free API key (fred.stlouisfed.org/docs/api/api_key.html)"
            return _smoke_yfinance("L7")
        if lid == "L8":
            return _smoke_yfinance("L8")
        if lid == "L9":
            if src == "finviz":
                return True, "Finviz is web-based (finviz.com/screener.ashx), no install"
            return _smoke_yfinance("L9")
        if lid == "L10":
            return _smoke_yfinance("L10")
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
    return False, "no smoke logic matched"


# ---------------------------------------------------------------------------
# 主流程 / Main flow
# ---------------------------------------------------------------------------

def run_interactive():
    print("\n" + "#" * 62)
    print(f"#  {t('banner_title')}")
    print(f"#  {t('banner_sub1')}")
    print("#" * 62)

    info = detect()
    state = load_json(STATE_PATH, default_state())
    cfg = load_json(CONFIG_PATH, {})

    print("\n" + t("env_check"))
    print(f"  {t('python')}: {info['python']}")
    lib_ok = {k: ("✅" if v else "❌") for k, v in info["libs"].items()}
    print(f"  {t('libs')}: yfinance={lib_ok.get('yfinance')} pandas={lib_ok.get('pandas')} "
          f"alpaca={lib_ok.get('alpaca')} futu={lib_ok.get('futu')} ib_insync={lib_ok.get('ib_insync')}")
    print(f"  {t('skills')}({len(info['skills'])}): {', '.join(info['skills']) or t('none')}")

    coverage(state)

    print("\n" + t("choose_path"))
    print("  " + t("path1"))
    print("  " + t("path2"))
    print("  " + t("path3"))
    mode = ask_int("  " + t("your_choice"), 1, 3, default=2)

    if mode == 1:
        print("\n  🚀 " + t("quick_note"))
        for layer in LAYERS:
            _configure_layer(layer, auto_choice=None, cfg=cfg, state=state, skip_broker=True, use_default=True)
    elif mode == 3:
        print("\n  🔧 " + t("fill_note"))
        for layer in LAYERS:
            lid = layer["id"]
            if state["layers"].get(lid, {}).get("status") != "ready":
                _configure_layer(layer, auto_choice=None, cfg=cfg, state=state, skip_broker=False)
            else:
                print(f"  ✅ {lid} {t('skip_ready')}")
    else:
        print("\n  🧭 " + t("full_note"))
        for layer in LAYERS:
            _configure_layer(layer, auto_choice=None, cfg=cfg, state=state, skip_broker=False)

    print("\n" + t("smoke_title"))
    smoke_results = {}
    for layer in LAYERS:
        ok, msg = smoke_layer(layer, cfg, state)
        smoke_results[layer["id"]] = {"ok": ok, "msg": msg}
        mark = "✅" if ok else "⚠️"
        name = pick(layer["name"], layer["name_en"])
        print(f"  {mark} {layer['id']} {name:<16} {msg}")

    state["smoke"] = smoke_results
    state["last_run"] = datetime.datetime.now().isoformat(timespec="seconds")
    save_json(STATE_PATH, state)
    save_json(CONFIG_PATH, cfg)

    ready = sum(1 for s in smoke_results.values() if s["ok"])
    print("\n" + "=" * 62)
    print(f"  🎉 {t('complete1')} {ready}/{len(LAYERS)}")
    print("  " + t("complete2"))
    print("  " + t("complete3"))
    print(f"  {t('complete4')}: python wizard.py --status / --audit / --config L5")
    print("=" * 62)


def _configure_layer(layer, auto_choice, cfg, state, skip_broker, use_default=False):
    lid = layer["id"]
    name = pick(layer["name"], layer["name_en"])
    purpose = pick(layer["purpose"], layer["purpose_en"])
    print(f"\n【{lid} {name}】{purpose}")
    sources = layer["sources"]

    if lid == "L1" and not skip_broker:
        print("  " + t("broker_first"))
        use_broker = ask_int(f"  {t('use_broker')} [1={t('yes_broker')} 2={t('no_broker')}]", 1, 2, default=2)
        if use_broker == 1:
            _broker_branch(cfg, state)
            bname = state.get("broker", {}).get("name", "broker")
            bregion = state.get("broker", {}).get("region", "")
            state["layers"]["L1"] = {"status": "ready", "source": "broker",
                                     "source_name": f"broker ({bname}, {bregion})", "priority": "1"}
            return

    if use_default:
        # 快速模式:直接选该层的「默认(免费优先)」源,不逐个列清单
        choice = next((i for i, s in enumerate(sources) if s["id"] == layer["default"]), 0)
        print(f"  → {t('auto_choice')} [{choice+1}] {pick(sources[choice]['name'], sources[choice]['name_en'])}")
    else:
        for i, s in enumerate(sources):
            star = t("star") if i == 0 else "  "
            nm = pick(s["name"], s["name_en"])
            fr = pick(s["free"], s["free_en"])
            keytag = ", " + pick("需key", "key") if s["key"] else ", " + pick("免key", "no key")
            print(f"  {star} [{i+1}] {nm}  ({fr}{keytag})")

        if auto_choice is not None:
            choice = auto_choice
            print(f"  → {t('auto_choice')} [{choice+1}] {pick(sources[choice]['name'], sources[choice]['name_en'])}")
        else:
            default_idx = next((i for i, s in enumerate(sources) if s["id"] == layer["default"]), 0)
            choice = ask_int("  " + t("choose_which"), 1, len(sources), default=default_idx + 1) - 1

    src = sources[choice]

    if src["key"]:
        key_field = _key_field_for(src["id"])
        if key_field:
            have = cfg.get(key_field, "")
            if not have:
                val = input(f"  {t('paste_key')} ({src['name']}): ").strip()
                if val:
                    cfg[key_field] = val
                    print("  ✅ " + t("key_saved"))
                else:
                    print("  ⚠️ " + t("skip_layer"))
            else:
                print("  ✅ " + t("key_exists"))
            if not cfg.get(key_field):
                state["layers"][lid] = {"status": "need_key", "source": src["id"], "source_name": pick(src["name"], src["name_en"]), "priority": str(choice + 1)}
                return

    if src["kind"] == "py_lib":
        lib = "yfinance" if src["id"].startswith("yfinance") else None
        if lib and not py_importable(lib):
            print(f"  → {t('installing')} {lib} ...")
            r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", lib], capture_output=True, text=True)
            if r.returncode != 0:
                print(f"  ❌ {t('install_failed')}: {r.stderr.strip()[:120]}")
                state["layers"][lid] = {"status": "not_configured", "source": src["id"], "source_name": pick(src["name"], src["name_en"]), "priority": str(choice + 1)}
                return

    print(f"  {t('setup_label')}: {pick(src['setup'], src['setup_en'])}")
    state["layers"][lid] = {"status": "ready", "source": src["id"], "source_name": pick(src["name"], src["name_en"]), "priority": str(choice + 1)}


def _broker_branch(cfg, state):
    regions = list(BROKERS_BY_REGION.keys())
    print("\n" + t("broker_title"))
    for i, r in enumerate(regions):
        print(f"  [{i+1}] {r}")
    ridx = ask_int("  " + t("region_q"), 1, len(regions), default=1) - 1
    region = regions[ridx]
    brokers = BROKERS_BY_REGION[region]
    print(f"\n  {region} {t('region_recommend')}:")
    for i, b in enumerate(brokers):
        tag = f" {t('recommended')}" if b["recommend"] else ""
        note = pick(b["note"], b["note_en"])
        print(f"  [{i+1}] {b['name']}{tag} — {note}")
    bidx = ask_int("  " + t("choose_broker"), 1, len(brokers), default=1) - 1
    b = brokers[bidx]
    print(f"\n  {t('selected_broker')} {b['name']}。{t('broker_subflow')}: {pick(b['setup'], b['setup_en'])}")
    print("  → " + t("broker_continue"))

    cfg.setdefault("broker", {})
    cfg["broker"]["name"] = b["id"]
    cfg["broker"]["region"] = region
    if b["id"] in ("alpaca", "ibkr"):
        cfg["broker"]["api_key"] = input("  " + t("paste_api_key") + ": ").strip()
        cfg["broker"]["secret"] = input("  " + t("paste_secret") + ": ").strip()
    else:
        cfg["broker"]["token"] = input("  " + t("paste_token") + ": ").strip()
    state["broker"] = {"name": b["id"], "region": region}
    print(f"  ✅ {t('broker_recorded')} {b['name']}({region})。{t('broker_login_note')}")


def _key_field_for(source_id):
    return {
        "finnhub": "finnhub_key", "finnhub_news": "finnhub_key",
        "adanos": "adanos_key", "marketaux": "marketaux_key",
        "simfin": "simfin_key", "simfin_hist": "simfin_key",
        "sec_api": "sec_api_key", "polygon": "polygon_key", "stocktwits": "stocktwits_key",
    }.get(source_id)


# ---------------------------------------------------------------------------
# 子命令 / Subcommands
# ---------------------------------------------------------------------------

def cmd_status():
    state = load_json(STATE_PATH, default_state())
    info = detect()
    print("\n" + t("env_check"))
    print(f"  {t('python')}: {info['python']}")
    print(f"  {t('skills')}: {', '.join(info['skills']) or t('none')}")
    coverage(state)


def cmd_config_layer(lid):
    state = load_json(STATE_PATH, default_state())
    cfg = load_json(CONFIG_PATH, {})
    layer = next((l for l in LAYERS if l["id"].upper() == lid.upper()), None)
    if not layer:
        print(f"  {t('layer_not_found')} {lid}, {t('layer_options')}: {[l['id'] for l in LAYERS]}")
        return
    _configure_layer(layer, auto_choice=None, cfg=cfg, state=state, skip_broker=(lid.upper() != "L1"))
    ok, msg = smoke_layer(layer, cfg, state)
    print(f"  {'✅' if ok else '⚠️'} {t('recon_smoke')}: {msg}")
    state["smoke"] = state.get("smoke", {})
    state["smoke"][layer["id"]] = {"ok": ok, "msg": msg}
    state["last_run"] = datetime.datetime.now().isoformat(timespec="seconds")
    save_json(STATE_PATH, state)
    save_json(CONFIG_PATH, cfg)


def cmd_audit():
    print("\n" + t("audit_title"))
    state = load_json(STATE_PATH, default_state())
    cfg = load_json(CONFIG_PATH, {})
    for layer in LAYERS:
        ok, msg = smoke_layer(layer, cfg, state)
        mark = "✅" if ok else "⚠️"
        name = pick(layer["name"], layer["name_en"])
        print(f"  {mark} {layer['id']} {name:<16} {msg}")
    print("\n  " + t("audit_note"))


def main():
    parser = argparse.ArgumentParser(description="US Stock Datasource wizard (bilingual)")
    parser.add_argument("--status", action="store_true", help="print coverage only")
    parser.add_argument("--config", metavar="Lx", help="reconfigure one layer, e.g. L5")
    parser.add_argument("--audit", action="store_true", help="audit data sources")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help="UI language (default zh)")
    args = parser.parse_args()

    global LANG
    LANG = args.lang

    if args.status:
        cmd_status()
    elif args.config:
        cmd_config_layer(args.config)
    elif args.audit:
        cmd_audit()
    else:
        run_interactive()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n  " + t("interrupted"))
    except Exception as e:
        print(f"\n  ❌ {t('error')}: {type(e).__name__}: {e}")
        sys.exit(1)
