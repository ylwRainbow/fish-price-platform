# -*- coding: utf-8 -*-
"""
AI 智能验证 - 逐条搜索验证数据准确性
"""
import requests
from urllib.parse import quote
import re


def search_web(query):
    """执行 Web 搜索（简化版）"""
    # 注意：实际使用中可能需要更复杂的搜索策略
    # 这里只是演示框架
    return ""


def verify_price_data(item, idx):
    """
    验证单条数据
    返回：(是否通过，验证理由，可信度)
    """
    date = item['date']
    price = item['price']
    
    # 简化验证：检查价格范围
    if price < 1 or price > 100:
        return False, f"价格异常 ({price}元)", "低"
    
    # 检查日期是否合理
    from datetime import datetime
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        if date_obj > datetime.now():
            return False, "未来日期", "低"
    except:
        return False, "日期格式错误", "低"
    
    # 简化版：暂时假设都通过
    # TODO: 实现真实的 Web 搜索验证
    return True, "数据格式合理", "中"


def verify_all_data(md_file):
    """验证 Markdown 文件中的所有数据"""
    # 解析 Markdown 文件
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取数据块
    pattern = r'## 第 (\d+) 条.*?- \*\*日期\*\*: (.*?)\n.*?- \*\*价格\*\*: (\d+\.?\d*)'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    results = []
    for idx, match in enumerate(matches, 1):
        item_id = match.group(1)
        date = match.group(2)
        price = float(match.group(3))
        
        print(f"[{idx}] 验证：{date} | {price}元")
        
        passed, reason, confidence = verify_price_data(
            {'date': date, 'price': price}, 
            item_id
        )
        
        results.append({
            'id': item_id,
            'date': date,
            'price': price,
            'passed': passed,
            'reason': reason,
            'confidence': confidence
        })
        
        print(f"  -> {'✅ 通过' if passed else '❌ 跳过'}: {reason}")
    
    return results


if __name__ == '__main__':
    results = verify_all_data('../docs/price_data_to_verify.md')
    print(f"\n验证完成：通过{sum(1 for r in results if r['passed'])}/{len(results)}条")
