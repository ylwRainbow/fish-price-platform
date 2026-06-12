# -*- coding: utf-8 -*-
"""
搜狐网历史数据全自动采集流程
一键执行：采集 -> Markdown -> AI 验证 -> 导入数据库
"""
import sys
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '.')

print("=" * 60)
print("搜狐网历史数据全自动采集系统")
print("=" * 60)

# 阶段 1：数据采集
print("\n【阶段 1】数据采集...")
try:
    from sohu_crawler import SohuCrawler
    
    # 读取 URL 列表
    url_file = 'sohu_historical_urls.txt'
    if os.path.exists(url_file):
        with open(url_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and line.startswith('http')]
        print(f"从 {url_file} 读取到 {len(urls)} 个 URL")
    else:
        print(f"警告：{url_file} 不存在，使用测试 URL")
        urls = [
            'https://www.sohu.com/a/516858961_210667',
            'https://m.sohu.com/a/660709304_210667/',
        ]
    
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
