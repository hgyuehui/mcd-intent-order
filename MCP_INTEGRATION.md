# MCP 集成说明

## 使用的 MCP Server

| 项目 | 说明 |
|---|---|
| Server | 麦当劳中国 MCP Server |
| 地址 | `https://mcp.mcd.cn` |
| 协议 | Streamable HTTP |
| 鉴权 | `Authorization: Bearer <MCP_TOKEN>` |
| 限流 | 600 次/分钟/Token（超限 429） |

## 使用的 Tool 与调用流程

### 核心链路（点餐决策）

| 步骤 | Tool | 作用 |
|---|---|---|
| 1 | `now-time-info` | 取服务器时间，判定早餐/午餐/下午茶/夜宵时段 |
| 2 | `query-nearby-stores` | 获取可点餐门店（storeCode）与可预约时段 |
| 3 | `query-meals` | 拉取门店完整菜单（14 个分类、约 130 个 SKU 的名称/现价/原价/优惠类型/标签） |
| 4 | `list-nutrition-foods` | 拉取 160 条官方营养数据（热量/蛋白/脂肪/碳水/钠/钙，TOON 格式） |
| 5 | `query-meal-detail` | 展开套餐选配轮次与差价（rounds/choices/diffPrice），并读取特调参数（modification：去酱料、去冰等） |
| 6 | `calculate-price` | （实时模式下）对用户选定的组合核出真实应付价 |

### 辅助链路

| Tool | 作用 |
|---|---|
| `campaign-calendar` | 活动日历，辅助"尝新"档推荐（仅展示原文方向，不承诺精确金额） |

### 刻意不用的 Tool（网页版离线演示场景）

| Tool | 原因 |
|---|---|
| `auto-bind-coupons` | 优惠券接口缺少结构化字段（无适用商品/门槛），为避免误导用户，不自动领券 |

> `create-order` 在**网页版离线演示**中不使用（静态页无 Token、不建单）；在 **Skill 版**中，用户明确说"下单"时可用：先 `calculate-price` 核价，再 `create-order` 创建订单并返回官方 H5 支付链接，**付款仍由用户本人完成，绝不代扣款**。

## 关键实现点

- **换配餐优化**：`query-meal-detail` 的 `diffPrice` + 营养表交叉——只推荐 Δkcal<0 且 Δprice≤0 的替换（实测：中薯条→小杯玉米杯 -236 kcal 且 -¥1.5）
- **特调去酱**：`modification` 的 `selectedKey/unselectedKey` 参数机制，支持"去酱料"（如板烧鸡腿堡去烤味酱）直接参与算价/下单链路
- **报价诚实**：菜单中 `discountType=随单购麦金卡优惠` 的商品必须加购会员卡才生效，界面强制标注真实结算前提
- **离线快照**：脚本将上述接口结果固化为 `assets/snapshot.json` 内联进页面，免 Token 可演示；Token 仅存在于本地环境变量，不进仓库

## 业务价值

把"打开 App 翻菜单 → 查热量 → 比价 → 纠结"的 5-10 分钟决策过程，压缩成"说一句话 → 10 秒拿到配好的清单"；同时把每个餐品的官方热量透明标注，让控制热量的人第一次能在下单前看清自己要点什么。

## 调用流程示意

```
用户一句话/点选 → now-time-info → query-nearby-stores → query-meals
    → list-nutrition-foods（热量标注）→ query-meal-detail（换配/去酱）
    → calculate-price（实时核价）→ 点餐清单（复制去官方 App 下单）
    →（可选，Skill 版）create-order 建单 → 官方 H5 支付链接（用户自行付款）
```
