# -*- coding: utf-8 -*-
"""
搜狐网历史数据全自动采集流程
使用已知链接开始，自动扩展和采集
"""
import sys
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '.')

print("=" * 60)
print("搜狐网历史数据全自动采集系统")
print("=" * 60)

# 准备 URL 列表
print("\n【准备 URL 列表】...")

url_file = 'sohu_urls_final.txt'
urls = []

# 1. 尝试从自动收集的文件中读取
auto_files = [
    'sohu_urls_auto.txt',
    'sohu_urls_id_scan.txt',
    'sohu_historical_urls.txt',
]

for auto_file in auto_files:
    if os.path.exists(auto_file):
        with open(auto_file, 'r', encoding='utf-8') as f:
            file_urls = [line.strip() for line in f if line.strip() and line.startswith('http')]
            urls.extend(file_urls)
            print(f"从 {auto_file} 读取到 {len(file_urls)} 个 URL")

# 2. 如果没有找到 URL，使用已知的 2 个链接
if not urls:
    print("未找到自动收集的 URL，使用已知链接...")
    urls = [
        'https://www.sohu.com/a/516858961_210667',
        'https://m.sohu.com/a/660709304_210667/',
    ]
    print(f"使用 {len(urls)} 个已知链接")

# 3. 去重
urls = list(set(urls))
print(f"\n去重后共 {len(urls)} 个唯一 URL")

# 保存 URL 列表
with open(url_file, 'w', encoding='utf-8') as f:
    for url in urls:
        f.write(url + '\n')
print(f"URL 列表已保存到：{url_file}")

if len(urls) < 10:
    print("\n⚠️  警告：URL 数量较少，建议通过以下方式扩展：")
    print("  1. 访问 Google 搜索：site:sohu.com \"加州鲈\" \"湖州\"")
    print("  2. 手动复制链接到 sohu_historical_urls.txt")
    print("  3. 重新运行本脚本")
    print("\n继续执行采集流程...\n")

# 阶段 1：数据采集
print("\n【阶段 1】数据采集...")
try:
    from sohu_crawler import SohuCrawler
    
    # 执行爬取
    crawler = SohuCrawler()
    data = crawler.crawl_urls(urls)
    print(f"采集到 {len(data)} 条数据")
    
except Exception as e:
    print(f"采集失败：{e}")
    import traceback
    traceback.print_exc()
    data = []

if not data:
    print("没有采集到数据，终止流程")
    sys.exit(0)

# 阶段 2：生成 Markdown 文档
print("\n【阶段 2】生成 Markdown 文档...")
try:
    from md_generator import generate_markdown
    
    output_file = '../docs/sohu_price_data_to_verify.md'
    generate_markdown(data, output_file)
    print(f"Markdown 文档已生成：{output_file}")
except Exception as e:
    print(f"生成 Markdown 失败：{e}")
    import traceback
    traceback.print_exc()

# 阶段 3：AI 智能验证
print("\n【阶段 3】AI 智能验证...")
try:
    from ai_verifier import verify_data
    
    input_file = '../docs/sohu_price_data_to_verify.md'
    results = verify_data(input_file)
    print(f"验证完成：通过{sum(1 for r in results if r['passed'])}条，失败{sum(1 for r in results if not r['passed'])}条")
except Exception as e:
    print(f"验证失败：{e}")
    import traceback
    traceback.print_exc()

# 阶段 4：生成验证报告
print("\n【阶段 4】生成验证报告...")
try:
    from verification_report import generate_report
    
    input_file = '../docs/sohu_price_data_to_verify.md'
    output_file = '../docs/sohu_verification_report.md'
    generate_report(results, output_file)
    print(f"验证报告已生成：{output_file}")
except Exception as e:
    print(f"生成报告失败：{e}")
    import traceback
    traceback.print_exc()

# 阶段 5：导入数据库
print("\n【阶段 5】导入数据库...")
try:
    from auto_import import import_verified_data
    
    report_file = '../docs/sohu_verification_report.md'
    import_verified_data(report_file)
    print("数据库导入完成")
except Exception as e:
    print(f"导入失败：{e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("全部流程完成！")
print("=" * 60)
print("\n输出文件:")
print("  - docs/sohu_price_data_to_verify.md")
print("  - docs/sohu_verification_report.md")
print(f"\n采集统计:")
print(f"  - URL 数量：{len(urls)}")
print(f"  - 采集数据：{len(data)}条")
if data:
    print(f"  - 最早日期：{min(d['date'] for d in data if d['date'])}")
    print(f"  - 最晚日期：{max(d['date'] for d in data if d['date'])}")
