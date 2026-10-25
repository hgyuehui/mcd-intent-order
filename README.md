# 麦麦联想 · 猜你想吃什么（mcd-intent-order）

> 🍔 **在线试玩（打开即玩，无需下载）**：https://hgyuehui.github.io/mcd-intent-order/

> 麦当劳程序员创意开发大赛参赛作品 · 基于麦当劳 MCP 开发

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Powered by MCD MCP](https://img.shields.io/badge/Powered%20by-MCD%20MCP-FFC72C.svg)](https://open.mcd.cn/mcp)
[![Made with WorkBuddy](https://img.shields.io/badge/Made%20with-WorkBuddy-4C8BF5.svg)](https://www.workbuddy.cn)

## 项目简介

**随便说句话，它就能猜出你这顿想吃什么。** 一个下单前的点餐决策助手：说"练完腿了"、"今天好累"，或点选口味/目标/预算，四层联想引擎从真实菜单里推荐 3 款，每个餐品上方标注卡路里（官方数据 / 估算标注），换配餐实时算热量和钱——**省热量还省钱**，全程不替你付款。网页版最后生成一张可复制的点餐清单，回官方 App 自行下单；**Skill 版还可一键创建订单**（返回官方 H5 支付链接，付款仍由你本人完成）。

核心差异：别的助手让你填表，它允许你"随便说"；别的工具只推荐，它把每一处改动的热量和价格变化都摊开（实测：套餐内把中薯条换成小杯玉米杯，热量 -236 kcal 且价格便宜 ¥1.5）。

## 目标用户

- 想控制热量 / 增肌 / 减脂，但懒得自己算的营养敏感人群
- 点餐时纠结"吃什么"的高频麦当劳用户
- 想知道"套餐和单点哪个更划算"的价格敏感用户

## 安装方法

**方式 A · 网页版（免 Token 离线演示）**

直接双击打开 `index.html`（内置真实 MCP 数据快照），或部署到 GitHub Pages。

> 仓库内置的快照采集自上海某一家门店，仅作离线演示示例，店名已泛化处理。
> 想看到自己附近的门店和实时菜单，用方式 B 接入 MCP，或用方式 C 重新生成快照。

**方式 B · Skill 版（接入麦当劳 MCP 实时数据）**

1. 申请麦当劳 MCP Token：https://open.mcd.cn/mcp
2. 复制 `mcp-config.example.json`，将 `${MCD_TOKEN}` 替换为真实 Token
3. 在 WorkBuddy 连接器中配置并启用 `mcd-mcp`
4. 把 `SKILL.md` 作为技能加载，对话中说"帮我点麦当劳"即可
5. 选好餐点后说"下单"，Skill 会调 `calculate-price` 核价、`create-order` 创建订单，返回**官方 H5 支付链接**——付款由你本人完成，Skill 绝不代扣款

**方式 C · 重新生成快照**

```bash
set MCD_MCP_URL=https://mcp.mcd.cn
set MCD_TOKEN=<你的Token>
python scripts/build_snapshot.py
python scripts/build_page.py
```

## 使用示例

**输入**：`练完腿了，想吃点有肉的，别超 30 块`

**输出**：
- 联想结果：判断你想要「增肌」· 匹配置信度 86%
- 推荐 3 款：板烧鸡腿堡三件套 827 kcal ¥35 ｜ 麦辣鸡腿汉堡三件套 ¥34 ｜ 大堡口福三件套 ¥22.9
- 点进板烧三件套 → 自定义：中薯条 289 kcal → 小杯玉米杯 53 kcal（-236 kcal / -¥1.5）；可乐 → 无糖可乐（-147 kcal / ±¥0）；可勾选"去烤味酱"（接口支持特调）
- 生成清单 → 复制 → 去官方 App 下单（Skill 版：直接说"下单"→ 生成订单 + H5 支付链接，自行付款）

## 技术栈

- 麦当劳 MCP（Streamable HTTP，Bearer Token 鉴权）
- 单文件 Web 应用（纯原生 HTML/JS，零依赖，零后端）
- WorkBuddy Skill（对话形态，见 SKILL.md）
- Python 标准库脚本（快照构建与页面内联）

> 本作品仅供比赛学习交流，非麦当劳官方产品，不构成任何专业建议。

---

⭐ **如果这对你有用，点个 Star 让更多人看到吧！**
