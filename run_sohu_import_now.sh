#!/bin/bash
# 搜狐网数据一键采集脚本

cd /Users/zcy/IdeaProjects/fish-price-platform
source venv/bin/activate

echo "============================================================"
echo "搜狐网历史数据一键采集系统"
echo "============================================================"

# 阶段 1: 数据采集
echo ""
echo "【阶段 1】数据采集..."
python3 << 'PYTHON'
import sys
sys.path.insert(0, 'backend')
from sohu_crawler import SohuCrawler

urls = [
    'https://www.sohu.com/a/516858961_210667',
    'https://m.sohu.com/a/660709304_210667/',
]

crawler = SohuCrawler()
data = crawler.crawl_urls(urls)

if data:
    from md_generator import generate_md_file
    generate_md_file(data, 'docs/sohu_price_data_to_verify.md')
    print(f'\n✓ 采集完成：{len(data)}条数据')
    print('✓ Markdown 已生成')
else:
    print('采集失败！')
    sys.exit(1)
PYTHON

if [ $? -ne 0 ]; then
    echo "采集失败，终止流程"
    exit 1
fi

# 阶段 2: AI 验证
echo ""
echo "【阶段 2】AI 验证..."
python3 << 'PYTHON'
import sys
sys.path.insert(0, 'backend')
from ai_verifier import verify_all_data

results = verify_all_data('docs/sohu_price_data_to_verify.md')
passed = sum(1 for r in results if r['passed'])
print(f'\n✓ 验证完成：通过{passed}/{len(results)}条')
PYTHON

# 阶段 3: 生成报告
echo ""
echo "【阶段 3】生成验证报告..."
python3 << 'PYTHON'
import sys
sys.path.insert(0, 'backend')
from verification_report import generate_report
from ai_verifier import verify_all_data

results = verify_all_data('docs/sohu_price_data_to_verify.md')
generate_report(results, 'docs/sohu_verification_report.md')
print('✓ 报告已生成')
PYTHON

# 阶段 4: 导入数据库
echo ""
echo "【阶段 4】导入数据库..."
export MYSQL_DSN="mysql://root:YOUR_PASSWORD@127.0.0.1:3306/fish_prices"
python3 backend/auto_import.py docs/sohu_verification_report.md

echo ""
echo "============================================================"
echo "全部完成！"
echo "============================================================"
echo ""
echo "输出文件:"
echo "  - docs/sohu_price_data_to_verify.md"
echo "  - docs/sohu_verification_report.md"
echo ""
