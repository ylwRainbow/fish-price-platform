# 源码事实映射

本文档记录当前源码中已验证的职责分布和重构关注点。后续重构前，如源码变化，应先更新本文件。

## 后端入口

| 文件 | 当前职责 | 已验证事实 | 重构关注点 |
| --- | --- | --- | --- |
| `backend/app/main.py` | FastAPI app、CORS、路由、价格录入、Excel 导入、模板下载 | `load_dotenv` 读取 `backend/.env`；目录查询和价格查询已切到 service；多数写入/导入路由仍直接写在入口文件 | 继续拆出 router 和 service；入口只注册 app |
| `backend/app/api/saved_periods.py` | 保存时间段和组合 API | API 层校验 `type` 为 `solar/lunar`；组合保存用 query 传 JSON 字符串 | POST 改 JSON body；合并返回结构 |
| `backend/app/schemas/saved_period.py` | 保存时间段 Pydantic 模型 | 只覆盖单个时间段，不覆盖组合请求模型 | 补组合模型和统一错误模型 |

## 后端数据与业务

| 文件 | 当前职责 | 已验证事实 | 重构关注点 |
| --- | --- | --- | --- |
| `backend/app/db.py` | 解析 `MYSQL_DSN` 并返回 PyMySQL 连接 | 无 DSN、无 PyMySQL 或连接失败时返回 `None`，异常被吞掉 | 明确错误处理；区分 demo 模式和数据库不可用 |
| `backend/app/repository.py` | 目录同步、价格读写、保存时间段读写 | `insert_prices` 使用 `INSERT IGNORE`；`query_prices` 按日/周/月聚合平均价 | 拆成多个 repository；处理唯一键和幂等口径 |
| `backend/app/data_loader.py` | 读取 YAML 配置、价格查询、模拟数据、预测和农历信息 | `/api/prices` 先查库，查不到会调用 connector，仍无数据时可能模拟 | 查询、采集、模拟、预测要拆开 |
| `backend/app/repositories/catalog_repository.py` | 目录数据库查询 | 查询 `fishes`、`markets`；数据库不可用时抛出 repository 异常 | 后续承接目录写入、种子同步和统一分页/过滤 |
| `backend/app/repositories/price_repository.py` | 价格数据库查询 | `query_price_points` 只查库；默认按 `markets.source_code='MZYY_WECHAT'` 过滤候选可信数据 | 后续补规格、单位标准化、数据质量状态字段 |
| `backend/app/services/catalog_service.py` | 目录服务 | 将 repository 不可用异常转换为服务层数据库不可用异常 | 后续承接缓存或 demo 模式决策 |
| `backend/app/services/price_service.py` | 价格查询服务 | `GET /api/prices` 使用该服务；默认 `include_unverified=false`；返回 `query_mode=database_only` | 后续承接查询校验、可信度策略和多鱼种/多市场结构 |
| `backend/app/lunar_utils.py` | 农历转换辅助 | 被 `data_loader.add_lunar_info` 使用 | 前后端农历口径需统一 |

## 后端采集与导入

| 文件 | 当前职责 | 已验证事实 | 重构关注点 |
| --- | --- | --- | --- |
| `backend/app/connectors.py` | 根据 source type 创建 connector | `http_html` 指向 `shuichanq_connector`，`wechat_mp` 指向 `wechat_connector` | connector 不应被查询 API 同步调用 |
| `backend/app/shuichanq_connector.py` | 水产行情页面采集 | 使用 Playwright 同步启动浏览器；从页面文本提取日期和价格 | 加任务、原始来源留存、日期最终过滤 |
| `backend/app/wechat_connector.py` | 微信/搜狗采集 | 同时存在 async 和 sync connector 逻辑 | 收敛实现，避免重复维护 |
| `backend/app/import_csv.py` | CSV 导入辅助 | 需要另行确认是否被正式 API 调用 | CSV 应由后端统一解析 |
| `backend/app/import_huangsha_excel.py` | 黄颡鱼 Excel 导入 | 独立脚本性质 | 融入 ImportService 或归档 |
| `backend/app/import_california_bass_excel.py` | 加州鲈 Excel 导入 | 独立脚本性质 | 融入 ImportService 或归档 |

## 前端入口

| 文件 | 当前职责 | 已验证事实 | 重构关注点 |
| --- | --- | --- | --- |
| `frontend/src/main.js` | Vue app 初始化 | 注册 Pinia、Router、Element Plus、图标 | 保持即可 |
| `frontend/src/router/index.js` | 页面路由 | `/` 图表页，`/entry` 录入页，`/import` 导入页 | 预览页是否保留需确认 |
| `frontend/src/App.vue` | 顶层布局和导航 | 导航菜单写死，含内联 SVG | 后续可组件化 |
| `frontend/src/api/index.js` | 部分 API client | 录入/导入页使用；图表页没有统一使用 | 统一所有请求 |
| `frontend/src/stores/catalog.js` | 目录 store | 读取 `/api/fishes/list` 和 `/api/markets/list` | 图表页也应使用 |

## 前端页面

| 文件 | 当前职责 | 已验证事实 | 重构关注点 |
| --- | --- | --- | --- |
| `frontend/src/views/ChartView.vue` | 图表主页面 | 超过 1200 行；目录已改为通过后端 API 获取；多选 UI 只取第一个鱼种/市场请求 | 优先拆请求、时间段、图表配置；收敛多选 UI 和实际查询能力 |
| `frontend/src/views/EntryView.vue` | 单条和快速录入 | 文案为“元/斤”，提交默认可使用后端 `unit=kg` | 单位口径需统一 |
| `frontend/src/views/ImportView.vue` | Excel/CSV/手工批量导入 | Excel 走后端，CSV 在前端 `split(',')` 后批量提交 | CSV 移到后端解析 |
| `frontend/src/components/SavedPeriods.vue` | 保存时间段弹窗 | 使用 window event 和 fetch；删除组合缺少 `type` query | 改为 props/emits 或 store；修复契约 |
| `frontend/src/components/LunarDatePicker.vue` | 农历日期选择 | 图表页农历模式使用 | 与后端农历口径同步 |

## 配置与 schema

| 文件 | 当前职责 | 已验证事实 | 重构关注点 |
| --- | --- | --- | --- |
| `backend/app/config.yaml` | 后端鱼种、市场、source 配置 | 5 个鱼种、11 个市场、6 个 source | 作为种子数据或后台管理来源 |
| `frontend/public/config.yaml` | 图表页静态目录配置 | 4 个鱼种；market 103 与后端含义不同 | 删除或仅保留 demo 用途 |
| `data/schema.mysql.sql` | 主 MySQL schema | 包含 fishes、markets、prices、forecasts | 补保存时间段、导入批次、来源表 |
| `backend/migrate_saved_periods.py` | 保存时间段表迁移 | 创建 solar/lunar 两张时间段表 | 纳入统一迁移 |
| `backend/create_combinations_tables.sql` | 保存组合表迁移 | 创建 solar/lunar 两张组合表 | 纳入统一迁移 |

## 依赖与运行

| 文件 | 当前事实 | 重构关注点 |
| --- | --- | --- |
| `backend/requirements.txt` | 已补 `python-dotenv`、`python-multipart`；未包含 `httpx` | 补 API 自动化测试时确认是否加入测试依赖 |
| `frontend/package.json` | Vue 3、Vite 7、Element Plus、ECharts、Pinia；已移除未使用的 `js-yaml` | 构建可通过但 chunk 偏大 |
| `frontend/vite.config.js` | `/api` 代理到 `127.0.0.1:8000` | 与 README/OpenAPI 端口统一 |
| `backend/openapi.yaml` | 只覆盖基础查询，server 为 `localhost:8080` | 改为自动生成或同步维护 |
