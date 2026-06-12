# -*- coding: utf-8 -*-
"""
数据验证器 - 去重、验证、清洗
"""
import hashlib
from datetime import datetime


class DataValidator:
    """数据验证器类"""
    
    def __init__(self):
        self.seen_hashes = set()
    
    def generate_hash(self, item):
        """生成数据指纹"""
        key = f"{item['date']}|{item['specification']}|{item['price']}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def is_duplicate(self, item):
        """检查是否重复"""
        h = self.generate_hash(item)
        if h in self.seen_hashes:
            return True
        self.seen_hashes.add(h)
        return False
    
    def validate_price(self, price):
        """验证价格合理性"""
        try:
            p = float(price)
            return 5 <= p <= 30  # 合理价格范围
        except:
            return False
    
    def validate_date(self, date_str):
        """验证日期格式"""
        if not date_str:
            return False
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except:
            return False
    
    def clean_data(self, data_list):
        """清洗数据"""
        cleaned = []
        for item in data_list:
            # 检查重复
            if self.is_duplicate(item):
                print(f"跳过重复：{item['date']} {item['specification']}")
                continue
            
            # 验证价格
            if not self.validate_price(item['price']):
                print(f"跳过异常价格：{item['price']}")
                continue
            
            # 验证日期
            if not self.validate_date(item.get('date')):
                print(f"跳过异常日期：{item.get('date')}")
                continue
            
            cleaned.append(item)
        
        return cleaned


def main():
    """测试数据验证器"""
    validator = DataValidator()
    test_data = [
        {'date': '2022-01-15', 'specification': '大统货', 'price': 12.5},
        {'date': '2022-01-15', 'specification': '大统货', 'price': 12.5},  # 重复
        {'date': '2023-03-29', 'specification': '8 成统货', 'price': 8.5},
        {'date': '2022-05-10', 'specification': '8 两', 'price': 15.0},
        {'date': '2022-05-10', 'specification': '8 两', 'price': 15.0},  # 重复
    ]
    
    print(f"原始数据：{len(test_data)}条")
    cleaned = validator.clean_data(test_data)
    print(f"清洗后：{len(cleaned)}条")
    print("\n清洗后的数据:")
    for item in cleaned:
        print(f"  {item['date']} | {item['specification']} | {item['price']}元/斤")


if __name__ == '__main__':
    main()
