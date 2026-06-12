# 领域模型沉淀

## 领域目标

鱼价平台的核心目标不是简单展示折线图，而是把不同来源、不同地区、不同规格、不同时间的鱼价数据沉淀成可追溯、可校验、可对比的标准价格序列。

## 当前已有对象

当前主 schema 中已有：

- `fishes`：鱼种目录。
- `markets`：市场目录。
- `prices`：价格点。
- `forecasts`：预测结果。

本地数据库已验证当前数据规模：

- `fishes`：5 条。
- `markets`：17 条。
- `prices`：517 条。
- `prices_back0319`：903 条备份数据。
- `forecasts`：0 条。

当前 `prices` 表已验证字段：

- `fish_id`
- `market_id`
- `price`
- `currency`
- `unit`
- `ts`
- `price_type`
- `source_url`
- `created_at`

当前唯一键为 `(fish_id, market_id, ts, price)`，不包含 `price_type`、`source_url`、规格或来源文档。这意味着同鱼种、同市场、同时间、同价格会被 `INSERT IGNORE` 忽略，即使来源或价格类型不同。

真实数据验证：

- 当前 `prices` 没有自然唯一键重复。
- 存在大量同日多价格点，例如鲈鱼/江苏省综合市场在 `2026-03-17` 有 37 个不同价格。
- 这些数据不应简单去重，更可能表示规格、来源或报价维度缺失。

当前扩展迁移中已有：

- `saved_solar_periods`：保存的公历时间段。
- `saved_lunar_periods`：保存的农历时间段。
- `saved_solar_combinations`：保存的公历时间段组合。
- `saved_lunar_combinations`：保存的农历时间段组合。

## 建议目标对象

### Fish

鱼种目录。

建议字段：

- `id`
- `name`
- `alias`
- `species_code`
- `enabled`

规则：

- 鱼种名称用于展示。
- `species_code` 用于内部稳定识别。
- 别名用于采集和导入匹配，不应作为唯一口径。

### Market

市场或产区目录。

建议字段：

- `id`
- `name`
- `region_code`
- `source_code`
- `market_type`
- `enabled`

规则：

- 市场和产区要区分，但可以先放在同一张表，用 `market_type` 标识。
- 前端只从后端 API 获取市场目录。

### ProductSpec

规格目录，例如“8 两上”“统货”“鱼塘价规格”。

建议字段：

- `id`
- `fish_id`
- `name`
- `alias`
- `weight_min`
- `weight_max`
- `unit`

当前状态：

- 当前主 schema 没有规格表。
- 当前 `prices` 表没有规格字段。
- 采集脚本和文档中出现“8 两上”“统货”等规格语义，但未标准化入库。
- 真实数据库里同日多价格点价格跨度较大，进一步证明规格字段是关键缺口。

目标规则：

- 当前价格表没有规格字段，这是后续数据质量的关键缺口。
- 历史数据规格不明确时可使用默认规格或 `unknown`，但不能默默丢失。

### PriceQuote

标准化价格点。

建议字段：

- `id`
- `fish_id`
- `market_id`
- `spec_id`
- `price`
- `currency`
- `unit`
- `quote_date`
- `price_type`
- `source_id`
- `source_url`
- `quality_status`
- `created_at`

当前状态：

- 当前对应表是 `prices`。
- 当前日期字段叫 `ts`，兼具价格日期和时间戳含义。
- 当前 `repository.query_prices` 对同一天价格做 `AVG(price)` 聚合。

目标规则：

- `quote_date` 表示价格所属日期，不等同于入库时间。
- `price_type` 至少包括 `pond`、`wholesale`、`retail`。
- `unit` 必须明确，例如 `jin` 或 `kg`，不要只靠页面文案推断。
- 展示时可以换算单位，但入库必须保留原始单位和标准单位口径。

### SourceDocument

来源文章、网页、Excel 文件或手动录入批次的原始来源。

建议字段：

- `id`
- `source_type`
- `title`
- `url`
- `published_at`
- `collected_at`
- `raw_hash`
- `raw_text_path`
- `status`

规则：

- 爬虫应先保留来源，再生成标准价格点。
- 同一来源重复采集应幂等。

当前状态：

- 当前标准价格表只保留 `source_url`，没有来源文档表。
- `source_text` 在部分 connector 返回值中存在，但 `repository.insert_prices` 不入库。

### ImportBatch

批量导入任务。

建议字段：

- `id`
- `file_name`
- `import_type`
- `operator`
- `total_count`
- `success_count`
- `failed_count`
- `status`
- `error_summary`
- `created_at`

规则：

- Excel/CSV 导入需要记录批次。
- 失败行要可追溯，不能只在接口响应中短暂返回。

当前状态：

- 当前没有导入批次表。
- Excel/CSV 文件导入统一走 `/api/import/prices`，返回 `added`、`failed` 和最多 10 条错误。
- CSV 已由后端解析，但错误明细仍未持久化。

### CollectionTask

采集任务。

建议字段：

- `id`
- `source_type`
- `target_fish_id`
- `target_market_id`
- `params`
- `status`
- `started_at`
- `finished_at`
- `error_message`

规则：

- 采集任务不应由查询接口同步触发。
- 采集任务完成后写入 `SourceDocument` 和 `PriceQuote`。

当前状态：

- 当前没有采集任务表。
- `/api/prices` 在数据库无数据时可能同步调用 connector。
- `backend/` 下存在多份手动采集脚本和 URL 列表。

### SavedPeriod

保存时间段。

建议字段：

- `id`
- `calendar_type`
- `name`
- `start_date`
- `end_date`
- `created_at`
- `updated_at`

规则：

- 当前拆成 `saved_solar_periods` 和 `saved_lunar_periods` 两张表，后续可收敛为一张表。
- `calendar_type` 标识 `solar` 或 `lunar`。

### Forecast

预测结果。

建议字段：

- `id`
- `fish_id`
- `market_id`
- `spec_id`
- `horizon`
- `predicted_at`
- `target_date`
- `model`
- `price`
- `lower`
- `upper`

规则：

- 当前预测是模拟逻辑，后续应明确模型来源和生成时间。

## 关键数据口径

### 可信度口径

当前业务判断：除“民众渔业”来源数据外，其他历史数据可能都有问题。

目标模型必须引入数据可信度字段，例如：

- `trusted`：可用于默认展示和分析。
- `unverified`：已入库但未校验，默认不进入正式曲线。
- `suspect`：已发现明显口径或质量风险。
- `rejected`：确认无效，仅保留审计或原始记录。

第一阶段建议：

- 民众渔业数据先标记为 `unverified` 或 `trusted_candidate`，经过单位和来源校验后再转 `trusted`。
- 非民众渔业数据默认标记为 `suspect` 或 `unverified`。
- 图表查询默认只查可信数据，除非用户显式开启“显示待校验数据”。

### 日期口径

- `quote_date`：价格所属日期。
- `published_at`：来源文章发布时间。
- `collected_at`：系统采集时间。
- `created_at`：入库时间。

这些时间不能互相替代。

### 价格单位口径

当前代码和页面文案多处使用“元/斤”，但数据库默认 `unit='kg'`。后续必须统一：

- 原始单位：保留来源中的单位。
- 标准单位：用于查询和图表展示。
- 换算规则：在服务层显式执行。

### 数据质量口径

建议引入：

- `raw`：原始导入或采集数据。
- `normalized`：已标准化。
- `verified`：已人工或规则校验。
- `rejected`：确认无效。

## 待确认问题

1. 平台主要展示“元/斤”还是“元/kg”？
2. 是否必须区分塘口价、批发价、零售价？
3. 规格是否是第一阶段必须字段？
4. 历史数据中的不确定规格如何处理？
5. 是否需要多用户和操作人审计？
6. 同一天、同鱼种、同市场多条价格是否取平均、保留区间，还是保留多个来源点？
7. `fish_id + market_id + quote_date + spec + price_type` 是否足够作为业务唯一口径？
