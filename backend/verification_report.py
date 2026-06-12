# -*- coding: utf-8 -*-
"""
生成验证报告
"""
from datetime import datetime


def generate_report(results, output_file):
    """生成验证报告"""
    
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    
    if total == 0:
        print("没有数据需要验证")
        return
    
    report = f"""# 鲈鱼价格数据验证报告

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 总体统计

- 总数据条数：{total}
- 验证通过：{passed} ({passed/total*100:.1f}%)
- 验证未通过：{failed} ({failed/total*100:.1f}%)

## 验证详情

### ✅ 通过的数据 ({passed}条)

"""
    
    for r in results:
        if r['passed']:
            report += f"""
#### 第 {r['id']} 条：{r['date']} | {r['price']}元/斤
- 可信度：{r['confidence']}
- 验证理由：{r['reason']}
- 决策：**导入**
"""
    
    report += f"""
### ❌ 未通过的数据 ({failed}条)

"""
    
    for r in results:
        if not r['passed']:
            report += f"""
#### 第 {r['id']} 条：{r['date']} | {r['price']}元/斤
- 可信度：{r['confidence']}
- 验证理由：{r['reason']}
- 决策：**跳过**
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"验证报告已生成：{output_file}")


if __name__ == '__main__':
    from ai_verifier import verify_all_data
    results = verify_all_data('../docs/price_data_to_verify.md')
    generate_report(results, '../docs/verification_report.md')
