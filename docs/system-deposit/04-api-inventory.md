# 当前 API 清单

当前 API 入口主要在 `backend/app/main.py` 和 `backend/app/api/saved_periods.py`。

## 目录接口

| Method | Path | 当前来源 | 当前用途 | 风险 |
| --- | --- | --- | --- | --- |
| GET | `/api/fishes` | `backend/app/config.yaml` | 基础鱼种列表 | 与数据库目录可能不一致 |
| GET | `/api/markets` | `backend/app/config.yaml` | 基础市场列表 | 与数据库目录可能不一致 |
| GET | `/api/fishes/list` | MySQL `fishes` | 录入/导入页目录 | 无数据库时为空 |
| GET | `/api/markets/list` | MySQL `markets` | 录入/导入页目录 | 无数据库时为空 |

建议目标：

- 保留一组目录 API。
- 前端所有页面只调用后端目录 API。
- YAML 只作为初始化种子，不直接给前端使用。
- 收敛前要明确保留 `/api/fishes` 还是 `/api/fishes/list`，避免长期双轨。

## 价格接口

| Method | Path | 当前用途 | 风险 |
| --- | --- | --- | --- |
| GET | `/api/prices` | 查询价格时序 | 数据库无数据时会同步触发 connector/模拟数据 |
| POST | `/api/prices` | 新增单条价格 | 缺少批次、操作人、质量状态 |
| POST | `/api/prices/batch` | 批量新增价格 | 缺少行级错误持久化 |

建议目标：

- 查询接口只查库。
- 写入接口走 `PriceService` 做校验、单位标准化和幂等处理。
- 批量写入返回批次 ID，而不是只返回 added/failed。
- `/api/prices` 第一阶段返回结构可以保持兼容，但必须移除同步采集和模拟回退。

## 预测接口

| Method | Path | 当前用途 | 风险 |
| --- | --- | --- | --- |
| GET | `/api/forecast` | 返回模拟预测 | 当前不是正式预测模型 |

建议目标：

- 第一阶段可以保留，但在前端标识为试验能力。
- 预测结果应来自 `forecasts` 表或离线任务，而不是临时模拟。

## 模板和导入接口

| Method | Path | 当前用途 | 风险 |
| --- | --- | --- | --- |
| GET | `/api/templates/prices.xlsx` | 下载 Excel 模板 | 模板字段和真实模型可能不一致 |
| GET | `/api/templates/prices.csv` | 下载 CSV 模板 | CSV 后端没有统一导入接口 |
| POST | `/api/import/excel` | Excel 导入 | 解析逻辑在 `main.py`，缺少批次表 |

建议目标：

- `POST /api/imports` 创建导入批次。
- `GET /api/imports/{id}` 查询导入结果。
- Excel 和 CSV 都由后端解析。

## 保存时间段接口

| Method | Path | 当前用途 | 风险 |
| --- | --- | --- | --- |
| GET | `/api/saved-periods` | 查询保存时间段 | 使用 `type` 动态选择表 |
| POST | `/api/saved-periods` | 保存时间段 | 两张表结构重复 |
| PUT | `/api/saved-periods/{period_id}` | 更新时间段名称 | 只更新名称 |
| DELETE | `/api/saved-periods/{period_id}` | 删除时间段 | 返回模型语义不统一 |
| GET | `/api/saved-period-combinations` | 查询组合 | 使用 `type` 动态选择表 |
| POST | `/api/saved-period-combinations` | 保存组合 | 参数通过 query 传 JSON |
| DELETE | `/api/saved-period-combinations/{combination_id}` | 删除组合 | 删除时缺少 `type` 参数会失败 |

建议目标：

- 合并 solar/lunar 表，使用 `calendar_type` 字段区分。
- POST 请求体使用 JSON body，不通过 query 传复杂 JSON。
- 返回结构统一为 `{ success, data, message }` 或标准 HTTP 错误。

已验证前端问题：

- `SavedPeriods.vue` 查询组合时带了 `type=props.calendarType`。
- `SavedPeriods.vue` 删除组合时只请求 `/api/saved-period-combinations/{id}`，未带 `type`。
- 当前后端删除组合接口要求 `type` query 参数，因此该功能存在前后端契约不一致。

## OpenAPI 现状

`backend/openapi.yaml` 只记录了基础查询接口，缺少：

- 价格写入接口。
- 批量写入接口。
- 导入接口。
- 保存时间段接口。
- 真实端口和当前启动方式。

已验证端口差异：

- `backend/openapi.yaml` 写 `localhost:8080`。
- `frontend/vite.config.js` 代理到 `127.0.0.1:8000`。
- 根 README 示例使用过 `8001`。

建议目标：

- 以后以 FastAPI 自动生成的 `/openapi.json` 为准。
- 额外维护面向产品/前端的接口说明。

## 第一阶段建议保留接口

为了低风险重构，第一阶段可以先保留现有 path，但内部实现改为分层服务：

- `/api/fishes/list`
- `/api/markets/list`
- `/api/prices`
- `/api/prices/batch`
- `/api/import/excel`
- `/api/saved-periods`
- `/api/saved-period-combinations`

同时标记 `/api/fishes`、`/api/markets` 为待收敛接口。
