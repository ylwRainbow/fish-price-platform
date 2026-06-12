# 数据流沉淀

## 当前数据流

### 目录数据流

```text
backend/app/config.yaml
  -> /api/fishes, /api/markets

MySQL fishes/markets
  -> /api/fishes/list, /api/markets/list

frontend/public/config.yaml
  -> ChartView.vue
```

现状问题：目录存在三个来源，且内容不完全一致。

目标方向：

```text
backend/app/config.yaml 或 管理端
  -> 同步到 MySQL
  -> 后端目录 API
  -> 前端所有页面
```

第一阶段建议保留 YAML 作为种子数据，但前端只读 API。

### 手工录入数据流

```text
EntryView.vue
  -> POST /api/prices
  -> repository.insert_prices
  -> MySQL prices
```

现状问题：

- 没有操作人。
- 没有录入批次。
- 没有质量状态。
- 价格单位展示为“元/斤”，接口默认单位为 `kg`。

目标方向：

```text
EntryView.vue
  -> POST /api/price-quotes
  -> PriceService 校验和单位标准化
  -> price_quotes
  -> import_batches 或 audit_logs
```

### Excel 导入数据流

```text
ImportView.vue
  -> POST /api/import/excel
  -> main.py 解析 Excel
  -> repository.insert_prices
  -> MySQL prices
```

现状问题：

- 导入解析逻辑在 `main.py` 中。
- 失败行只返回前 10 条错误。
- 没有保存原始文件和导入批次。

目标方向：

```text
Upload file
  -> ImportService 创建 ImportBatch
  -> Parser 解析原始行
  -> Validator 校验鱼种/市场/日期/价格/单位
  -> PriceService 写入标准价格
  -> 返回批次结果
```

### CSV 导入数据流

```text
ImportView.vue
  -> POST /api/import/prices
  -> 后端 csv.reader 解析和行级校验
  -> MySQL prices
```

现状问题：

- CSV 已改为后端解析，接口响应返回行级错误。
- 当前仍没有导入批次表，行级错误没有持久化。

目标方向：增加导入批次表，持久化原始文件、成功/失败数量和错误明细。

### 采集数据流

当前存在多类脚本：

- 水产行情页采集。
- 搜狐文章采集。
- 微信公众号/搜狗采集。
- 一次性导入脚本。
- 数据检查脚本。

当前 `/api/prices` 在数据库无数据时会尝试同步调用 connector。

现状问题：

- 查询链路触发外部采集，响应不稳定。
- 采集没有任务状态。
- 原始文档和标准价格点没有分层。
- 请求日期和采集文章日期之间没有强约束。

目标方向：

```text
CollectionTask
  -> Collector 拉取 SourceDocument
  -> Extractor 提取候选价格
  -> Validator 校验日期/地区/规格/价格区间
  -> PriceService 写入标准价格
  -> Query API 只查库
```

### 图表查询数据流

当前：

```text
ChartView.vue
  -> 读取 frontend/public/config.yaml
  -> GET /api/prices
  -> 前端做农历转换、月日对齐、tooltip 拼装
  -> ECharts
```

已验证限制：

- 虽然 UI 支持多市场、多鱼种选择，但当前请求只使用第一个市场和第一个鱼种。
- 多条线主要来自多个时间段，不是多个鱼种或多个市场。
- 图表横轴在公历模式下按 `MM-DD` 对齐，不直接按完整日期连续展示。

目标：

```text
ChartView.vue
  -> GET /api/catalog
  -> POST /api/price-series/query
  -> 后端返回已对齐的 series 数据
  -> 前端只负责展示和少量交互
```

第一阶段不必把全部图表计算移到后端，但至少要做到：

- 前端不读静态目录配置。
- API 不触发爬虫。
- 日期过滤在服务层统一执行。
- 查询参数和返回结构有明确契约。

## 目标数据闭环

```text
目录初始化
  -> 导入/采集/录入
  -> 原始数据留存
  -> 标准价格入库
  -> 查询聚合
  -> 图表展示
  -> 数据校验反馈
```

第一阶段最小闭环：

```text
MySQL 目录 + MySQL prices
  -> /api/fishes/list, /api/markets/list
  -> /api/prices 只查库
  -> ChartView 展示
```

第一阶段必须明确：如果数据库没有价格数据，查询 API 应返回空数据和明确状态，不应触发采集或返回模拟数据。模拟数据可以保留在 demo 模式，但不能混入正式查询模式。
