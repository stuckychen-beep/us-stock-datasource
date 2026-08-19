# 券商数据源适配器 / Broker Data-Source Adapters

券商是唯一能免费拿**真实时**行情的途径,但各家安装/登录方式差异巨大。
Brokers are the only free route to **real-time** quotes, but install/login differs widely.

本文件定义统一接口 + 各券商专属子流程。
This file defines a unified interface + per-broker sub-flows.

## 统一接口(概念层)/ Unified Interface (conceptual)

所有券商适配器对外暴露同一组能力(本技能**只取数,不含下单**)。
Every adapter exposes the same capabilities (this skill **fetches data only, never places orders**).

```
BrokerAdapter
    get_quote(symbol)      # 真实时报价 / real-time quote
    get_history(symbol)    # K 线 / bars
    get_fundamentals()     # 基本面(部分券商支持)/ fundamentals (some brokers)
```

## 券商对比 / Broker Comparison

| 券商 Broker | 安装 Install | 登录/凭证 Login/Creds | 特点 Notes | 地区 Region |
|---|---|---|---|---|
| **Alpaca** | `pip install alpaca-py` | 网页生成 API key(纸面账户免费) | 最简单;IEX 免费真实时 / simplest | 美国/全球 US/global |
| **Tradier** | 纯 REST + token | 一个 token | 最轻;美股期权强 / lightest | 美国 US |
| **IBKR** | IB Gateway 常驻 + `ib_insync` | 启动 Gateway 并登录 | 功能最全;需常驻 / most complete | 全球 global |
| **富途 Futu** | OpenD 网关 + `futu-api` | 启动 OpenD 并登录牛牛号 | 港股最强 / best for HK | 香港/内地 HK/CN |
| **长桥 Longbridge** | `longbridge-terminal` CLI | `longbridge auth login` 扫码 | 与 value-investing skill 配套 | 香港/内地/美国 HK/CN/US |

## 各券商专属子流程 / Per-Broker Sub-Flows

### Alpaca(美国/北美推荐 / recommended for US)
1. `pip install alpaca-py`
2. https://alpaca.markets 注册,生成 Paper API Key + Secret
3. 向导里粘贴 key/secret,选 `IEX` 数据源(免费真实时)
4. 冒烟:`get_quote("AAPL")`

### Tradier(最轻 / lightest)
1. 无需安装,纯 HTTP / no install, pure HTTP
2. https://tradier.com 生成 access token
3. 粘贴 token
4. 冒烟:GET `/v1/markets/quotes?symbols=AAPL`

### IBKR(最重,全球可用 / heaviest, global)
1. `pip install ib_insync`
2. 下载并启动 **IB Gateway**(https://www.interactivebrokers.com),登录
3. 确认端口(纸面 4002 / 实盘 4001)与 clientId
4. 回连验证 `ib_insync.IB().connect()`
5. 注意:Gateway 是常驻进程,需一直开着 / Gateway must stay running

### 富途 Futu(香港/内地用户首选港股 / best for HK)
1. `pip install futu-api`
2. 下载并启动 **OpenD**(https://openapi.futunn.com)
3. 在 OpenD 里登录牛牛号 / log in inside OpenD
4. 回连 `OpenQuoteContext(host='127.0.0.1', port=11111)`
5. 注意:OpenD 常驻,实时行情可能需按权限开通 / real-time may need entitlement

### 长桥 Longbridge(与已有 skill 配套 / pairs with value-investing)
1. 安装 `longbridge-terminal` CLI
2. `longbridge auth login` 扫码登录 / scan to log in
3. 回连 `longbridge quote AAPL.US`
4. 注意:行情权限按账户等级开放 / quote entitlement by account tier

## 地区推荐映射 / Region → Broker Mapping(wizard 使用 / used by wizard)

| 地区 Region | 首选 Primary | 备选 Fallback |
|---|---|---|
| 美国/北美 US/NA | Alpaca | Tradier / IBKR |
| 香港 HK | 富途 Futu | 长桥 / IBKR |
| 内地 CN | 长桥 | 富途 / IBKR |
| 欧洲 EU | IBKR | — |
| 全球/其他 Global | IBKR | Alpaca |

## 设计要点 / Design Notes

- 券商是**可选增强**,跳过仍可用完整免费路径。/ Broker is optional; the free path stays complete without it.
- 券商子流程都要「启动→登录→回连验证」三段式(与纯 API「填 key 完事」不同)。/ Broker sub-flows are start→login→reconnect-verify (unlike "paste a key").
- 凭证(含登录态提示)写入 `config.json`,**不写进 SKILL.md 或 wizard.py 正文**。/ Credentials go to config.json, never into SKILL.md/wizard.py.
