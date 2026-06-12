# 当前系统现状

## 技术栈

后端：

- 语言：Python。
- Web 框架：FastAPI。
- 数据库访问：PyMySQL。
- 配置：`backend/app/config.yaml`、`backend/.env`。
- 采集依赖：requests、BeautifulSoup、Playwright、Selenium。
- 导入依赖：openpyxl。
- 当前实际可用后端虚拟环境：`backend/.venv`。
- 当前 `backend/requirements.txt` 未列出但代码或运行需要的依赖包括：`python-dotenv`、`python-multipart`；测试如果使用 FastAPI TestClient 还需要 `httpx`。

前端：

- 框架：Vue 3。
- 构建：Vite。
- UI：Element Plus。
- 图表：ECharts。
- 状态管理：Pinia。
- 农历转换：lunar-javascript。

数据库：

- 当前主 schema：`data/schema.mysql.sql`。
- 保存时间段迁移：`backend/migrate_saved_periods.py`。
- 保存时间段组合迁移：`backend/create_combinations_tables.sql`。

## 启动端口现状

已验证：

- `frontend/vite.config.js` 将 `/api` 代理到 `http://127.0.0.1:8000`。
- `README.md` 中示例后端启动端口曾写为 `8001`。
- `backend/openapi.yaml` 的 server 写为 `http://localhost:8080`。

结论：端口文档不一致，重构前必须统一。建议第一阶段统一为后端 `8000`、前端 `5173`，除非有明确部署约束。

## 当前目录职责

```text
backend/app/main.py                 FastAPI 入口和大部分路由
backend/app/data_loader.py          目录配置读取、价格查询、预测和农历信息拼装
backend/app/repository.py           MySQL 读写和保存时间段读写
backend/app/connectors.py           数据源 connector 工厂
backend/app/shuichanq_connector.py  水产行情页面采集
backend/app/wechat_connector.py     微信公众号/搜狗采集
backend/app/api/saved_periods.py    保存时间段相关路由
frontend/src/views/ChartView.vue    价格走势主页面
frontend/src/views/EntryView.vue    单条价格录入
frontend/src/views/ImportView.vue   批量导入
frontend/src/components/SavedPeriods.vue  保存时间段弹窗和事件桥接
```

## 当前后端主链路

### 目录查询

- `/api/fishes` 读取 `backend/app/config.yaml`。
- `/api/markets` 读取 `backend/app/config.yaml`。
- `/api/fishes/list` 读取数据库 `fishes` 表。
- `/api/markets/list` 读取数据库 `markets` 表。

问题：同类接口有两套来源，前端不同页面使用不同接口。

已验证差异：

- `backend/app/config.yaml` 有 5 个鱼种，包含黄颡鱼。
- `frontend/public/config.yaml` 有 4 个鱼种，不包含黄颡鱼。
- `backend/app/config.yaml` 中 market `103` 是江苏省综合市场。
- `frontend/public/config.yaml` 中 market `103` 是浙江湖州。

### 价格查询

当前 `/api/prices` 逻辑：

1. 根据 `fish_id`、`market_id` 从配置中寻找鱼种、市场和 source。
2. 优先查询 MySQL `prices` 表。
3. 数据库没有数据时，尝试调用 source connector。
4. connector 失败或没有数据时，可能回退到模拟序列。
5. 可选追加农历信息。

问题：查询 API 会同步触发外部采集，且采集结果没有稳定保证按请求 `start/end` 过滤。

已验证行为：本地临时启动后，请求 `2026-01-01` 到 `2026-01-03` 的价格查询，数据库无匹配数据时触发外部采集，并返回了 `2026-06-10` 的数据点。该行为说明查询参数和 connector 结果之间缺少最终过滤。

### 价格写入

- `/api/prices` 写入单条价格。
- `/api/prices/batch` 批量写入价格。
- `/api/import/excel` 解析 Excel 后写入价格。
- CSV 导入目前主要由前端解析，再调用批量写入接口。

问题：导入批次、原始文件、失败明细、数据校验结果没有统一持久化。

已验证细节：

- `PriceInput.unit` 默认是 `kg`。
- 前端录入页文案显示“价格 (元/斤)”。
- Excel/CSV 模板中的单位示例为 `kg`。

结论：单位口径当前不一致，不能直接假设库中价格就是元/斤或元/kg。

### 保存时间段

- `/api/saved-periods`
- `/api/saved-period-combinations`

问题：相关表不在主 schema 中，新环境初始化容易漏执行迁移。

已验证细节：

- 保存时间段目前拆成 `saved_solar_periods` 和 `saved_lunar_periods`。
- 保存时间段组合拆成 `saved_solar_combinations` 和 `saved_lunar_combinations`。
- API 层校验 `type` 只能为 `solar` 或 `lunar`，repository 层仍使用动态表名。

## 当前前端主链路

### 图表页

`ChartView.vue` 当前承担：

- 市场/鱼种选择。
- 公历/农历时间段选择。
- 保存/加载时间段组合。
- 请求 `/api/prices`。
- 日期与农历转换。
- ECharts 配置和渲染。
- tooltip 逻辑。
- 图例显示隐藏。

问题：页面超过 1200 行，业务、请求、日期处理、图表渲染耦合过重。

已验证细节：

- 图表页支持多选市场和多选鱼种的 UI。
- 实际请求时只取 `selectedMarkets.value[0]` 和 `selectedFishes.value[0]`。
- 图表页直接用 `axios.get('/config.yaml')` 加载前端静态目录配置。

### 录入页和导入页

录入页、导入页通过 `frontend/src/api/index.js` 调用 `/api/fishes/list`、`/api/markets/list` 和写入接口。

问题：它们依赖数据库目录表；图表页却读取 `frontend/public/config.yaml`，前端数据来源不统一。

## 已验证事实

- 前端 Vite 生产构建可通过，但有 CSS `@import` 位置警告和大 chunk 警告。
- 后端用 `backend/.venv` 可以导入并启动。
- 项目根目录 `venv` 缺少 FastAPI，不应作为后端运行环境。
- 当前机器存在 `backend/.env`，所以数据库目录接口可以返回数据。
- `TestClient` 依赖 `httpx`，当前后端环境未安装该测试依赖。
- Vite 构建可通过，但 CSS 中存在 `@import` 顺序警告，产物中存在超过 500 kB 的 chunk 警告。
- 已连接本地数据库 `fish_prices` 做只读快照，主表 `prices` 有 517 条数据，详见 `09-database-snapshot.md`。

## 主要问题清单

1. 查询、采集、模拟数据回退混在同一个 API 链路里。
2. 配置来源重复：后端 YAML、前端 YAML、数据库目录表。
3. 数据库 schema 分散，初始化不可重复。
4. 多个脚本存在硬编码数据库凭据，不适合提交或共享。
5. 文档和真实端口、真实接口不一致。
6. 前端主页面过大，难以维护和测试。
7. 爬虫脚本、一次性导入脚本、正式 API 边界不清。
8. 缺少稳定的自动化测试分层。
9. 前端保存时间段组合删除接口调用缺少后端要求的 `type` 参数。
10. `backend/requirements.txt` 与当前 `backend/.venv` 实际包集合不完全一致。
11. 真实数据库中 `prices` 同时存在 `kg` 和 `斤` 两种单位。
12. 真实数据库中同一天同鱼种市场存在多价格点，当前查询按平均价聚合可能掩盖规格差异。

## 暂不建议做的事

- 暂不切换后端语言。
- 暂不重写所有 UI。
- 暂不把所有历史脚本一次性删除。
- 暂不引入预测模型或复杂调度平台。

当前应先稳定“目录 -> 价格入库 -> 价格查询 -> 图表展示”这条最小闭环。
