# 搜狐网数据采集 - 快速启动指南

## 🚀 立即开始（3 步完成）

### 第 1 步：收集链接（5 分钟）

打开以下 Google 搜索链接（已生成 25 个）：

**文件位置**: `backend/sohu_search_urls.txt`

选择几个链接打开，例如：
```
https://www.google.com/search?q=site:sohu.com+"加州鲈+湖州+水产前沿"+after:2020-01-01+before:2020-12-31
```

### 第 2 步：复制链接（每篇文章 10 秒）

在搜索结果中：
1. 找到标题包含"湖州"、"加州鲈"的文章
2. 右键复制链接地址
3. 粘贴到 `backend/sohu_known_urls.txt`

**目标**: 收集 20-50 个链接（约 5-10 分钟）

### 第 3 步：运行采集（自动完成）

```bash
cd /Users/zcy/IdeaProjects/fish-price-platform
source venv/bin/activate

# 运行完整采集流程
python backend/run_sohu_full_import.py
```

**预计耗时**: 
- 采集 20 篇文章：约 1-2 分钟
- 采集 50 篇文章：约 3-5 分钟
- 采集 100 篇文章：约 5-10 分钟

## 📊 预期成果

| 链接数量 | 预计数据量 | 采集时间 | 覆盖年份 |
|---------|-----------|---------|---------|
| 20 篇 | 40-80 条 | 1-2 分钟 | 2020-2024 |
| 50 篇 | 100-200 条 | 3-5 分钟 | 2020-2024 |
| 100 篇 | 200-400 条 | 5-10 分钟 | 2020-2024 |
| 200 篇 | 400-800 条 | 10-20 分钟 | 2020-2024 |

## 💡 快速技巧

### 技巧 1：批量复制
1. 打开一个搜索链接
2. 按住 Ctrl/Cmd 点击多个搜索结果（在新标签页打开）
3. 逐个标签页复制链接

### 技巧 2：使用已知链接
已知的 2 个链接已经在 `backend/sohu_known_urls.txt` 中：
- https://www.sohu.com/a/516858961_210667 (2022 年)
- https://m.sohu.com/a/660709304_210667/ (2023 年)

可以先用这 2 个链接测试流程！

### 技巧 3：查看采集结果
采集完成后查看：
- `docs/sohu_price_data_to_verify.md` - 原始数据
- `docs/sohu_verification_report.md` - 验证报告

## ⚡ 现在就开始！

**最少时间方案**（只需 2 个链接）：

```bash
# 1. 打开终端
cd /Users/zcy/IdeaProjects/fish-price-platform
source venv/bin/activate

# 2. 直接运行（使用已有的 2 个链接）
python -c "
from backend.sohu_crawler import SohuCrawler
crawler = SohuCrawler()
urls = [
    'https://www.sohu.com/a/516858961_210667',
    'https://m.sohu.com/a/660709304_210667/',
]
data = crawler.crawl_urls(urls)
print(f'采集完成！共 {len(data)} 条数据')
"
```

**30 秒就能看到结果！** 🎯

## 📈 扩展计划

采集到第一批数据后：
1. 继续收集更多链接（每天 10-20 个）
2. 定期运行采集脚本
3. 数据会自动累积到数据库

**一周内可以收集到 200+ 链接，获得 400+ 条数据！**
