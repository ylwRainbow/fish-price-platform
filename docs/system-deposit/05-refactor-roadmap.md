# 重构路线

## 总体策略

不做一次性推倒重写。先保留当前能跑通的功能，在旁边建立清晰结构，再逐步切换调用。

优先级：

1. 数据口径。
2. 配置和数据库初始化。
3. 后端分层。
4. 前端数据来源统一。
5. 页面拆分。
6. 采集任务化。
7. 预测能力。

## 阶段 0：冻结现状

目标：明确当前系统能做什么、不能做什么。

产出：

- 本文档目录。
- 当前 API 清单。
- 当前数据库表清单。
- 当前脚本清单。
- 当前启动方式说明。

完成标准：

- 后续改动能判断是否破坏既有能力。

## 阶段 1：基础治理

目标：让项目能稳定启动、初始化、配置。

建议改动：

- 增加 `.env.example`。
- 清理脚本中的硬编码数据库凭据。
- 明确唯一后端虚拟环境。
- 补齐 `backend/requirements.txt` 中缺失的运行依赖，例如 `python-dotenv`、`python-multipart`。
- 明确后端标准端口，并同步 README、Vite proxy、OpenAPI。
- 合并主 schema 和保存时间段迁移。
- 将目录配置同步到数据库，并让前端只读 API。
- 修复 `/api/prices` 在查询链路中触发实时爬虫的问题。
- 引入数据可信度字段或临时过滤策略：默认只展示相对可信数据，非民众渔业数据先隔离。

完成标准：

- 新环境可以按文档初始化数据库。
- 查询接口不访问外部站点。
- 前端目录数据来自后端 API。
- 不配置数据库时，系统行为明确：要么进入 demo 模式，要么返回明确错误；不能静默返回空列表导致前端误判。
- 默认价格查询不会把高风险历史数据混入可信曲线。

## 阶段 2：后端分层

目标：把 API、业务、仓储、采集、导入拆开。

建议目录：

```text
backend/app/
  api/
    routes/
  core/
    config.py
  schemas/
  services/
    catalog_service.py
    price_service.py
    import_service.py
    period_service.py
  repositories/
    catalog_repository.py
    price_repository.py
    period_repository.py
  integrations/
    shuichanq.py
    wechat.py
    sohu.py
  jobs/
  utils/
```

迁移方式：

1. 先新增 service/repository，不删除旧函数。
2. 一个接口一个接口切换。
3. 切换后补轻量测试。
4. 最后删除旧入口中的重复逻辑。

完成标准：

- `main.py` 只负责注册 app 和 router。
- 价格查询、导入、保存时间段都有独立 service。

## 阶段 3：前端数据来源统一

目标：所有页面都通过 API 和 store 获取数据。

建议改动：

- 删除 `ChartView.vue` 对 `/config.yaml` 的依赖。
- 统一使用 `src/api/index.js` 或进一步拆分 API client。
- Pinia store 管理鱼种和市场目录。
- 抽离 `usePriceSeriesQuery`、`useCalendarPeriods`、`useChartOptions`。
- 明确多选市场/鱼种的真实产品含义：如果暂不支持多鱼种/多市场，应把 UI 调整为单选；如果支持，应改造查询和 series 结构。

完成标准：

- 前端没有第二份目录配置。
- 图表页可以在不改页面代码的情况下切换后端返回结构。

## 阶段 4：图表页拆分

目标：让 `ChartView.vue` 从大页面变成组合页面。

建议组件：

```text
ChartView.vue
  PriceFilterPanel.vue
  PeriodEditor.vue
  SavedPeriodDialog.vue
  PriceTrendChart.vue
  ChartLegend.vue
```

建议 composable：

```text
useCatalog.js
usePriceSeries.js
useCalendarConvert.js
useSavedPeriods.js
```

完成标准：

- 页面文件控制在 300 行以内。
- 图表配置和数据请求可单独测试。

## 阶段 5：导入和采集任务化

目标：把一次性脚本变成可追踪任务。

建议改动：

- 增加导入批次表。
- 增加采集任务表。
- Excel/CSV 都由后端解析。
- 爬虫先写原始来源，再写标准价格。
- 数据校验失败进入错误明细。

完成标准：

- 每次导入/采集都有任务 ID。
- 可以查看成功、失败、错误原因和原始来源。

## 阶段 6：预测能力正式化

目标：将模拟预测替换为离线结果。

建议改动：

- 明确预测输入数据范围。
- 预测任务写入 `forecasts`。
- API 只读取预测表。
- 前端标识模型名称、生成时间和置信区间。

完成标准：

- 预测结果可追溯，不由请求临时生成。

## 推荐近期第一刀

第一刀建议做基础治理，不建议先重构 UI。

具体顺序：

1. 清理凭据和环境文档。
2. 统一端口和依赖清单。
3. 合并 schema。
4. 目录统一为数据库 + API。
5. `/api/prices` 只查库。
6. 图表页移除 `/config.yaml` 依赖。

不建议把前端大页面拆分放在第一刀，因为数据和 API 契约还没有稳定。

这条线风险最低，也能立刻提高系统可信度。
