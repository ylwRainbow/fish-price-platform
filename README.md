鱼价波动数据平台（最小可用骨架）

概述
- 目标：统一采集各品种鱼在不同市场的历史价格，提供波动曲线与预测折线图展示。
- 能力：数据采集（爬虫/接口）、清洗入库、API 提供查询与预测结果、前端可视化。
- 初始技术栈：PostgreSQL/MySQL（任选其一）、后端可选 Java(Spring Boot) 或 Python(FastAPI)，前端静态页 + ECharts。

核心域模型
- 鱼种 Fish：id, name, alias, species_code
- 市场 Market：id, name, region_code, source_code
- 价格 Price：id, fish_id, market_id, price, currency, unit, ts, source_url
- 预测 Forecast：id, fish_id, market_id, horizon, predicted_at, model, price

数据采集
- 来源：各地批发市场官网、农业农村部价格信息平台、第三方 API。
- 方式：优先 API；无 API 时 Html 爬取（含反爬策略与增量更新）。
- 调度：每日/每小时增量；幂等（按 fish_id+market_id+ts 唯一约束）。

API 设计（OpenAPI 见 backend/openapi.yaml）
- GET /api/fishes：列出鱼种
- GET /api/markets：列出市场
- GET /api/prices：按鱼种/市场/时间范围查询价格时序
- GET /api/forecast：按鱼种/市场返回未来 N 天预测

前端展示
- 折线图：历史价格与预测两条曲线（颜色区分、图例、缩放、tooltip）。
- 交互：下拉选择鱼种与市场、时间范围；支持导出 CSV。

预测策略（可迭代）
- 基线：移动平均/指数平滑（ES）；节假日效应可在后续引入。
- 高阶：ARIMA/Prophet（Python 侧离线跑，结果入库）。

目录结构
- backend/              后端 API 契约与实现（可选择语言）
- data/schema.sql       数据库建表与索引
- frontend/             静态前端最小演示（ECharts）

运行指引
- 先创建数据库并执行 data/schema.sql
- 后端按 openapi.yaml 实现服务
- 前端可在 frontend 目录启动本地静态服务查看折线图

后端（FastAPI + MySQL）
- 依赖安装与启动：
  - cd backend && python3 -m venv .venv && . .venv/bin/activate
  - pip install -r backend/requirements.txt
  - python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
- 配置驱动：
  - app/config.yaml：维护鱼种、市场（江浙沪）与“鱼塘价格”数据源
  - 可追加 fishes/markets/sources 条目以扩展目标
- 数据库连接：
  - 通过环境变量 MYSQL_DSN 提供连接字符串（不在仓库中写入密码）
  - 示例：export MYSQL_DSN="mysql://user:pass@127.0.0.1:3306/fish_prices"
- 采集入库（鱼塘价格）：
  - python -m app.ingest --start 2025-11-01 --end 2026-02-05
  - 根据 config.yaml 的 sources 逐项抓取并写入 prices 表，price_type=pond
- API 查询优先读库：
  - /api/prices 会优先读取数据库中的 price_type=pond；若数据库为空，回退到配置的模拟鱼塘价格

MySQL 初始化
- 安装后创建数据库并导入表结构：
  - mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS fish_prices DEFAULT CHARACTER SET utf8mb4"
  - mysql -u root -p fish_prices < data/schema.mysql.sql
- 可选创建专用用户并授权：
  - mysql -u root -p -e "CREATE USER IF NOT EXISTS 'fishuser'@'127.0.0.1' IDENTIFIED BY 'YOUR_PASSWORD'; GRANT ALL PRIVILEGES ON fish_prices.* TO 'fishuser'@'127.0.0.1'; FLUSH PRIVILEGES;"
