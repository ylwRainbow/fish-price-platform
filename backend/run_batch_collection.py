#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量采集执行脚本
"""
import sys
import os
sys.path.insert(0, 'backend')

from smart_link_collector import SmartLinkCollector
from sohu_crawler import SohuCrawler
from data_validator import DataValidator
from md_generator import generate_md_file
from ai_verifier import verify_all_data
from verification_report import generate_report


def main():
    """主函数"""
    print("=" * 60)
    print("搜狐网历史数据批量采集")
    print("=" * 60)
    
    # 1. 加载链接
    print("\n【步骤 1】加载链接...")
    collector = SmartLinkCollector()
    collector.load_existing_urls()
    
    if len(collector.known_urls) < 10:
        print("⚠️ 链接数量不足，请先收集更多链接")
        print("运行：python backend/smart_link_collector.py")
        return
    
    urls = list(collector.known_urls)
    print(f"共 {len(urls)} 个链接")
    
    # 2. 批量爬取
    print("\n【步骤 2】批量爬取...")
    crawler = SohuCrawler()
    data = crawler.crawl_with_checkpoint(urls)
    print(f"采集到 {len(data)} 条数据")
    
    if not data:
        print("未采集到数据，终止流程")
        return
    
    # 3. 数据清洗
    print("\n【步骤 3】数据清洗...")
    validator = DataValidator()
    cleaned_data = validator.clean_data(data)
    print(f"清洗后：{len(cleaned_data)}条有效数据")
    
    # 4. 生成 Markdown
    print("\n【步骤 4】生成 Markdown...")
    generate_md_file(cleaned_data, 'docs/sohu_batch_data.md')
    print("✓ Markdown 已生成")
    
    # 5. AI 验证
    print("\n【步骤 5】AI 验证...")
    results = verify_all_data('docs/sohu_batch_data.md')
    passed = sum(1 for r in results if r['passed'])
    print(f"验证通过：{passed}/{len(results)}条")
    
    # 6. 生成报告
    print("\n【步骤 6】生成报告...")
    generate_report(results, 'docs/sohu_batch_report.md')
    print("✓ 报告已生成")
    
    # 7. 导入数据库
    print("\n【步骤 7】导入数据库...")
    os.environ['MYSQL_DSN'] = 'mysql://root:YOUR_PASSWORD@127.0.0.1:3306/fish_prices'
    from auto_import import import_verified_data
    import_verified_data('docs/sohu_batch_report.md')
    print("✓ 数据库导入完成")
    
    print("\n" + "=" * 60)
    print("批量采集完成！")
    print("=" * 60)
    print(f"\n统计:")
    print(f"  - 采集链接：{len(urls)}个")
    print(f"  - 获得数据：{len(data)}条")
    print(f"  - 有效数据：{len(cleaned_data)}条")
    print(f"  - 验证通过：{passed}条")


if __name__ == '__main__':
    main()
