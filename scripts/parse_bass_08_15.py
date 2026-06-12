# -*- coding: utf-8 -*-
"""
鲈鱼0.8-1.5斤价格数据解析脚本
从民众渔业微信文章中解析鲈鱼0.8-1.5斤规格的价格数据
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time

def parse_publish_date(soup):
    """
    从文章HTML中解析发布时间
    格式: 2026年1月15日 17:22
    """
    for tag in soup.find_all('em'):
        text = tag.get_text()
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            try:
                return datetime(year, month, day)
            except:
                pass
    return None

def parse_content_date(text):
    """
    从文章文本中解析日期（备用方案）
    格式: 2025-1-2更新
    """
    text_clean = text.replace('\n', '')
    match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})更新', text_clean)
    if match:
        year = match.group(1)
        month = match.group(2).zfill(2)
        day = match.group(3).zfill(2)
        date_str = "{}-{}-{}".format(year, month, day)
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return None
    return None

def parse_price(price_str):
    """
    解析价格字符串
    """
    if not price_str:
        return None
    
    price_str = price_str.strip()
    
    if price_str == '-' or price_str == '—' or price_str == '':
        return None
    
    price_str = re.sub(r'[^\d.\-]', '', price_str)
    
    if not price_str:
        return None
    
    if '-' in price_str:
        parts = price_str.split('-')
        try:
            low = float(parts[0])
            high = float(parts[1])
            return round((low + high) / 2, 2)
        except:
            try:
                return float(parts[0])
            except:
                return None
    else:
        try:
            return float(price_str)
        except:
            return None

def extract_bass_price_from_text(text):
    """
    从纯文本中提取鲈鱼0.8-1.5斤的价格
    查找格式: 加州鲈 0.8-1.5 价格
    """
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line_clean = line.strip()
        
        # 查找包含"加州鲈"或"鲈"的行
        if '加州鲈' in line_clean or ('鲈' in line_clean and '斤' not in line_clean):
            # 检查接下来的几行是否包含0.8-1.5规格
            for j in range(i+1, min(i+10, len(lines))):
                spec_line = lines[j].strip()
                
                # 查找0.8-1.5规格
                if re.search(r'0\.?8[-–—到]?1\.?5', spec_line) or '0.8-1.5' in spec_line:
                    # 在接下来的行中查找价格
                    for k in range(j+1, min(j+5, len(lines))):
                        price_line = lines[k].strip()
                        price = parse_price(price_line)
                        if price and 5 < price < 50:  # 合理价格范围
                            return {
                                'spec': '0.8-1.5斤',
                                'price': price
                            }
                
                # 也检查规格是否在同一行
                if '0.8-1.5' in spec_line or re.search(r'0\.?8.*1\.?5', spec_line):
                    # 价格可能在同一行或下一行
                    parts = spec_line.split()
                    for part in parts:
                        price = parse_price(part)
                        if price and 5 < price < 50:
                            return {
                                'spec': '0.8-1.5斤',
                                'price': price
                            }
                    
                    # 检查下一行
                    if j+1 < len(lines):
                        price_line = lines[j+1].strip()
                        price = parse_price(price_line)
                        if price and 5 < price < 50:
                            return {
                                'spec': '0.8-1.5斤',
                                'price': price
                            }
    
    return None

def fetch_article(url):
    """
    获取微信文章内容并解析鲈鱼价格
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return None, f"HTTP错误: {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content_div = soup.find('div', class_='rich_media_content')
        if not content_div:
            content_div = soup.find('div', id='js_content')
        
        if not content_div:
            return None, "无法找到文章内容"
        
        text = content_div.get_text('\n', strip=True)
        
        # 优先使用发布时间
        publish_date = parse_publish_date(soup)
        content_date = parse_content_date(text)
        
        date = publish_date or content_date
        if not date:
            return None, "无法解析日期"
        
        # 解析鲈鱼价格
        bass_price = extract_bass_price_from_text(text)
        
        if not bass_price:
            return None, "未找到鲈鱼0.8-1.5斤数据"
        
        return {
            'date': date,
            'price': bass_price['price'],
            'spec': bass_price['spec'],
            'url': url,
            'publish_date': publish_date,
            'content_date': content_date
        }, None
        
    except Exception as e:
        return None, str(e)

def main():
    """
    主函数
    """
    print("=" * 70)
    print("鲈鱼0.8-1.5斤价格数据解析")
    print("=" * 70)
    
    # 读取URL列表
    with open('/Users/zcy/IdeaProjects/fish-price-platform/数据地址', 'r') as f:
        urls = [line.strip() for line in f if line.strip().startswith('http')]
    
    print(f"\n共 {len(urls)} 个URL需要解析\n")
    
    results = []
    failed_urls = []
    
    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] 解析: {url}")
        
        data, error = fetch_article(url)
        
        if data:
            # 检查日期是否一致
            date_warning = ""
            if data['publish_date'] and data['content_date']:
                if data['publish_date'].year != data['content_date'].year:
                    date_warning = f" [注意: 发布时间{data['publish_date'].strftime('%Y-%m-%d')} != 内容日期{data['content_date'].strftime('%Y-%m-%d')}]"
            
            print(f"  ✓ 日期: {data['date'].strftime('%Y-%m-%d')}, 价格: {data['price']}元/斤{date_warning}")
            results.append(data)
        else:
            print(f"  ✗ 失败: {error}")
            failed_urls.append({'url': url, 'error': error})
        
        time.sleep(0.3)
    
    print("\n" + "=" * 70)
    print("解析结果汇总")
    print("=" * 70)
    
    print(f"\n成功解析: {len(results)} 条")
    print(f"解析失败: {len(failed_urls)} 条")
    
    if results:
        print("\n--- 成功数据 ---")
        print(f"{'日期':<12} {'价格(元/斤)':<12} {'来源'}")
        print("-" * 60)
        for r in sorted(results, key=lambda x: x['date']):
            print(f"{r['date'].strftime('%Y-%m-%d'):<12} {r['price']:<12} {r['url'][-30:]}")
    
    if failed_urls:
        print("\n--- 失败URL列表 ---")
        for f in failed_urls:
            print(f"  {f['url']}")
            print(f"    原因: {f['error']}")
    
    # 保存结果到文件供后续使用
    if results:
        import json
        with open('/Users/zcy/IdeaProjects/fish-price-platform/scripts/bass_08_15_data.json', 'w') as f:
            json.dump(results, f, default=str, indent=2, ensure_ascii=False)
        print(f"\n数据已保存到: scripts/bass_08_15_data.json")
    
    return results, failed_urls

if __name__ == '__main__':
    main()
