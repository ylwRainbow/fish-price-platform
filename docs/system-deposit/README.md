# Fish Price Platform System Deposit

生成日期：2026-06-11

本文档目录用于沉淀 `fish-price-platform` 的当前系统事实、领域模型、数据流、接口清单和后续重构路线。这里先记录“已验证现状”和“建议目标态”，不直接等同于最终实现。

## 文档索引

- [01-current-state.md](./01-current-state.md)：当前系统结构、技术栈、运行方式和主要问题。
- [02-domain-model.md](./02-domain-model.md)：鱼价平台核心领域对象、数据口径和建议目标模型。
- [03-data-flow.md](./03-data-flow.md)：录入、导入、采集、查询、图表展示的数据流。
- [04-api-inventory.md](./04-api-inventory.md)：当前 API 清单、调用来源和接口风险。
- [05-refactor-roadmap.md](./05-refactor-roadmap.md)：分阶段重构路线。
- [06-migration-checklist.md](./06-migration-checklist.md)：重构迁移检查表。
- [07-source-map.md](./07-source-map.md)：源码文件职责映射和已验证代码事实。
- [08-refactor-decisions.md](./08-refactor-decisions.md)：重构前置决策记录。
- [09-database-snapshot.md](./09-database-snapshot.md)：本地数据库真实数据快照和数据质量观察。
- [10-data-trust.md](./10-data-trust.md)：数据可信度分级、隔离和校验策略。

## 当前结论

后端当前使用 Python + FastAPI，前端使用 Vue 3 + Vite + Element Plus + ECharts。当前不建议切换后端语言，优先级应放在系统边界、数据模型、配置、迁移、接口和前端页面拆分上。

## 事实等级

为保证后续重构正确性，文档中的内容按以下等级理解：

- `已验证`：来自当前源码、配置、schema 或本地运行验证。
- `推断`：基于源码行为的工程判断，重构前仍需用数据或测试确认。
- `目标态`：建议重构方向，不代表当前系统已经实现。

后续开发必须优先信任 `已验证` 内容；如果发现源码与文档不一致，应先修正文档再改代码。

## 数据库快照

已连接本地 MySQL `127.0.0.1:3306/fish_prices` 做只读查询，结果见 [09-database-snapshot.md](./09-database-snapshot.md)。文档只记录 host、端口、库名、表结构、数量和样例，不记录密码或完整 DSN。

## 数据可信度

用户已补充业务判断：除“民众渔业”来源数据外，其他历史数据可能都有问题。重构时必须默认将非民众渔业数据标为待校验或高风险，不能直接当作可信历史价格使用。详见 [10-data-trust.md](./10-data-trust.md)。

## 重构原则

1. 先沉淀领域口径，再拆代码。
2. 保留能跑通的能力，逐步替换混乱边界。
3. 查询 API 不触发实时爬虫。
4. 目录数据只保留一个权威来源。
5. 数据库初始化、迁移和测试必须可重复。
6. 凭据只能来自环境变量或本地未提交配置。

## 建议第一阶段产出

- 一套可重复执行的数据库初始化脚本。
- 一个统一的后端目录配置来源。
- 一份真实 API 文档。
- 一条稳定的“查库 -> 返回图表数据”链路。
- 一个不依赖前端静态配置的图表页面。
