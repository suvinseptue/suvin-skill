# 数据结构定义（Data Schema）

> 本文件定义 Gift Adjustment Skill 所需的所有数据结构。
> 数据来源可以是 API 注入、CSV 导入或用户手动提供。
> 字段标注 `*` 为必填，未标注为可选。

---

## 数据集一览

| 数据集标识 | 说明 | 更新频率建议 |
|------------|------|-------------|
| `venues` | 场地基础信息 | 有变更时更新 |
| `venue_sales` | 场地销售数据 | 每次换品前拉取最新90天数据 |
| `venue_gifts` | 场地当前在售礼品 | 每次换品前拉取 |
| `adjustment_log` | 历史换品记录 | 每次换品后更新 |
| `problem_venues` | 问题场地名单 | 有变更时更新 |
| `gift_catalog` | 全国礼品目录 | 有新品上架或下架时更新 |
| `national_ranking` | 全国礼品销售排名 | 每次换品前拉取最新90天数据 |

---

## venues — 场地基础信息

```json
{
  "venue_id": "string *",           // 场地唯一ID
  "venue_name": "string *",         // 场地名称
  "location": "string",             // 城市/地区
  "project_type": "string *",       // "全国项目" | "非全国项目"
  "slot_count": "integer *",        // 仓位总数
  "layout_type": "string *",        // "普通" | "背靠背" | "L型" | "分开两组"
  "price_level": "string *",        // "正常" | "高价"
  "withdrawal_risk": "boolean *",   // 是否有撤场风险
  "semi_annual_profit_per_machine": "number"  // 半年台均盈利（元）
}
```

---

## venue_sales — 场地销售数据

```json
{
  "venue_id": "string *",
  "gift_id": "string *",
  "slot_layer": "string *",         // "上层" | "下层"
  "period_days": 90,                // 统计周期（固定90天）
  "coin_count": "integer *",        // 投币数（90天）
  "coin_count_30d": "integer",      // 投币数（近30天，用于库存预估）
  "coin_count_60d": "integer",      // 投币数（近60天，用于例外3判断）
  "rank_in_venue": "integer *",     // 在该场地内的排名
  "rank_percentile": "number *"     // 排名百分位（0-1，越小越靠前）
}
```

> **说明**：`rank_percentile > 0.7` 即为后30%候选礼品。

---

## venue_gifts — 场地当前在售礼品

```json
{
  "venue_id": "string *",
  "gift_id": "string *",
  "gift_name": "string *",
  "slot_layer": "string *",         // "上层" | "下层"
  "slot_index": "integer",          // 仓位编号（同层多仓位时区分）
  "price_coins": "integer *",       // 当前定价（币数）
  "inventory": "integer *",         // 当前库存数量
  "is_tail_stock": "boolean *",     // 是否为尾货款
  "audience_type": "string *"       // "儿童" | "年轻人" | "全人群"
}
```

---

## adjustment_log — 历史换品记录

```json
{
  "venue_id": "string *",
  "adjustment_date": "string *",    // 最近一次调整日期，格式：YYYY-MM-DD
  "days_since_last": "integer"      // 距今天数（可由系统计算）
}
```

---

## problem_venues — 问题场地名单

```json
{
  "venue_id": "string *",
  "added_date": "string",           // 加入名单日期
  "reason": "string"                // 原因描述（可选）
}
```

---

## gift_catalog — 全国礼品目录

```json
{
  "gift_id": "string *",
  "gift_name": "string *",
  "price_standard": "integer *",    // 标准定价（币数）
  "price_min": "integer",           // 最低可调价格（币数）
  "profit_tier": "string *",        // 利润率档位："S" | "A" | "B" | "C"（S最高）
  "audience_type": "string *",      // "儿童" | "年轻人" | "全人群"
  "is_tail_stock": "boolean *",     // 是否为尾货款
  "is_available": "boolean *",      // 当前是否可供货
  "category": "string"              // 礼品品类（如：毛绒、手办、食品等）
}
```

> **利润率档位说明**：S > A > B > C，A档以下指B档和C档。

---

## national_ranking — 全国礼品销售排名

```json
{
  "gift_id": "string *",
  "period_days": 90,
  "national_rank": "integer *",     // 全国排名
  "top2_ratio": "number *",         // 前二占比（0-1）
                                    // 即：在所有投放该礼品的场地中，
                                    // 排名第1或第2的场地占比
  "total_venues": "integer"         // 投放该礼品的场地总数
}
```

---

## API 注入格式（完整示例）

```json
{
  "skill": "gift-adjustment",
  "triggered_at": "2024-01-15T09:00:00Z",
  "operator": "张三",

  "data": {
    "venues": [ /* venues 数组 */ ],
    "venue_sales": [ /* venue_sales 数组 */ ],
    "venue_gifts": [ /* venue_gifts 数组 */ ],
    "adjustment_log": [ /* adjustment_log 数组 */ ],
    "problem_venues": [ /* problem_venues 数组 */ ],
    "gift_catalog": [ /* gift_catalog 数组 */ ],
    "national_ranking": [ /* national_ranking 数组 */ ]
  },

  "market_context": "（可选）本次换品的市场背景，如：五一节前，儿童礼品需求预期上升",

  "rule_overrides": "（可选）本次临时调整的规则，如：本次跳过例外3的销售数据判断，因为数据有异常",

  "focus_venues": ["venue_001", "venue_002"]
  // （可选）只处理指定场地，不填则处理所有场地
}
```

---

## 数据校验规则

接收数据后，在执行决策前需检查：

1. `venues` 中的每个 `venue_id`，在 `adjustment_log` 中必须有对应记录
2. `venue_gifts` 中的每个 `gift_id`，必须在 `gift_catalog` 中存在
3. `venue_sales` 的 `rank_percentile` 应在 0-1 之间
4. `profit_tier` 只接受 `S / A / B / C` 四个值

发现数据异常时，列出异常条目，询问用户确认后再继续。
