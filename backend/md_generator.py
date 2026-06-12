# -*- coding: utf-8 -*-
"""
生成待验证的 Markdown 文档
"""
from datetime import datetime


def generate_md_file(data_list, output_file):
    """生成 Markdown 文档"""
    
    md_content = """# 鲈鱼价格数据 - 待验证

> 生成时间：{timestamp}
> 数据来源：微信文章
> 总数据条数：{total}

---

""".format(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total=len(data_list)
    )
    
    for idx, item in enumerate(data_list, 1):
        md_content += f"""## 第 {idx} 条

- **日期**: {item['date']}
- **价格**: {item['price']} 元/斤
- **来源文章**: {item['title']}
- **来源链接**: {item['source_url']}
- **原始记录**: "{item['original_text']}"

---

"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Markdown 文档已生成：{output_file}")
    print(f"共 {len(data_list)} 条数据")


if __name__ == '__main__':
    # 示例数据
    sample_data = [
        {
            'date': '2020-03-15',
            'price': 12.5,
            'title': '2020 年 3 月鲈鱼价格行情',
            'source_url': 'https://example.com/article1',
            'original_text': '2020 年 3 月 15 日，鲈鱼价格为 12.5 元每斤'
        },
        {
            'date': '2020-03-20',
            'price': 13.0,
            'title': '2020 年 3 月鲈鱼价格行情',
            'source_url': 'https://example.com/article2',
            'original_text': '3 月 20 日鲈鱼价格 13 元/斤'
        }
    ]
    
    generate_md_file(sample_data, '../docs/price_data_to_verify.md')
