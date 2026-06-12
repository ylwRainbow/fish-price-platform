#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库鲈鱼价格数据质量检查脚本
检查数据库中鲈鱼价格数据的质量和准确性，识别问题数据并提供修复建议。
"""

import pymysql
from datetime import datetime, timedelta
from tabulate import tabulate
import statistics


def connect_to_database():
    """连接数据库并返回连接对象"""
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='YOUR_PASSWORD',
        database='fish_prices',
        autocommit=True,
        charset='utf8mb4'
    )
    return conn


def get_basic_statistics(cursor):
    """执行基础数据统计"""
    print("\n" + "="*80)
    print("第二步：基础数据统计")
    print("="*80)
    
    # 1. 统计鲈鱼数据总量（market_id=103, fish_id=1）
    cursor.execute("""
        SELECT COUNT(*) as total_count 
        FROM prices 
        WHERE market_id = 103 AND fish_id = 1
    """)
    total_count = cursor.fetchone()[0]
    
    # 2. 按年份分组统计
    cursor.execute("""
        SELECT YEAR(ts) as year, COUNT(*) as count 
        FROM prices 
        WHERE market_id = 103 AND fish_id = 1
        GROUP BY YEAR(ts)
        ORDER BY year
    """)
    year_stats = cursor.fetchall()
    
    # 3. 按月份分组统计（最近 3 年）
    cursor.execute("""
        SELECT DATE_FORMAT(ts, '%Y-%m') as month, COUNT(*) as count 
        FROM prices 
        WHERE market_id = 103 AND fish_id = 1
        AND ts >= DATE_SUB(CURDATE(), INTERVAL 3 YEAR)
        GROUP BY DATE_FORMAT(ts, '%Y-%m')
        ORDER BY month
    """)
    month_stats = cursor.fetchall()
    
    # 4. 找出价格的最大值、最小值、平均值
    cursor.execute("""
        SELECT 
            MAX(price) as max_price,
            MIN(price) as min_price,
            AVG(price) as avg_price
        FROM prices 
        WHERE market_id = 103 AND fish_id = 1
    """)
    price_stats_result = cursor.fetchone()
    
    # 单独计算中位数 - 使用简化方法
    cursor.execute("""
        SELECT price
        FROM prices
        WHERE market_id = 103 AND fish_id = 1
        ORDER BY price
    """)
    all_prices = [row[0] for row in cursor.fetchall()]
    n = len(all_prices)
    if n > 0:
        if n % 2 == 1:
            median = all_prices[n // 2]
        else:
            median = (all_prices[n // 2 - 1] + all_prices[n // 2]) / 2
    else:
        median = 0
    
    price_stats = (price_stats_result[0], price_stats_result[1], price_stats_result[2], median)
    
    # 打印统计结果
    print(f"\n1. 鲈鱼数据总量：{total_count} 条")
    
    print("\n2. 按年份分组统计:")
    year_table = tabulate(year_stats, headers=['年份', '记录数'], tablefmt='grid')
    print(year_table)
    
    print("\n3. 最近 3 年按月份分组统计:")
    month_table = tabulate(month_stats, headers=['月份', '记录数'], tablefmt='grid')
    print(month_table)
    
    print("\n4. 价格统计:")
    price_table = tabulate([[price_stats[0], price_stats[1], price_stats[2], price_stats[3]]], 
                          headers=['最大值', '最小值', '平均值', '中位数'], tablefmt='grid')
    print(price_table)
    
    return {
        'total_count': total_count,
        'year_stats': year_stats,
        'month_stats': month_stats,
        'price_stats': {
            'max': price_stats[0],
            'min': price_stats[1],
            'avg': price_stats[2],
            'median': price_stats[3]
        }
    }


def check_price_anomalies(cursor):
    """检查价格异常值"""
    print("\n" + "="*80)
    print("第三步：数据质量检查")
    print("="*80)
    print("\n1. 价格异常值检查（价格 < 3 或价格 > 30）:")
    
    cursor.execute("""
        SELECT id, ts, price, market_id, fish_id 
        FROM prices 
        WHERE market_id = 103 AND fish_id = 1
        AND (price < 3 OR price > 30)
        ORDER BY ts
    """)
    price_anomalies = cursor.fetchall()
    
    if price_anomalies:
        print(f"发现 {len(price_anomalies)} 条价格异常记录:")
        anomaly_table = tabulate(price_anomalies, 
                                headers=['ID', '日期', '价格', '市场 ID', '鱼 ID'], 
                                tablefmt='grid')
        print(anomaly_table)
    else:
        print("未发现价格异常记录")
    
    return price_anomalies


def check_date_anomalies(cursor):
    """检查日期异常"""
    print("\n2. 日期异常检查（未来时间或不合理日期）:")
    
    cursor.execute("""
        SELECT id, ts, price 
        FROM prices 
        WHERE market_id = 103 AND fish_id = 1
        AND (ts > CURDATE() OR ts < '2000-01-01')
        ORDER BY ts
    """)
    date_anomalies = cursor.fetchall()
    
    if date_anomalies:
        print(f"发现 {len(date_anomalies)} 条日期异常记录:")
        anomaly_table = tabulate(date_anomalies, 
                                headers=['ID', '日期', '价格'], 
                                tablefmt='grid')
        print(anomaly_table)
    else:
        print("未发现日期异常记录")
    
    return date_anomalies


def check_duplicate_data(cursor):
    """检查重复数据"""
    print("\n3. 重复数据检查（同一天有多条价格记录）:")
    
    cursor.execute("""
        SELECT DATE(ts) as date, COUNT(*) as count, GROUP_CONCAT(id ORDER BY id) as ids
        FROM prices 
        WHERE market_id = 103 AND fish_id = 1
        GROUP BY DATE(ts)
        HAVING COUNT(*) > 1
        ORDER BY date
    """)
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"发现 {len(duplicates)} 天存在重复记录:")
        duplicate_table = tabulate(duplicates, 
                                  headers=['日期', '记录数', '记录 ID'], 
                                  tablefmt='grid')
        print(duplicate_table)
    else:
        print("未发现重复数据")
    
    return duplicates


def check_data_gaps(cursor):
    """检查数据断档"""
    print("\n4. 数据断档检查（超过 1 个月没有数据）:")
    
    cursor.execute("""
        SELECT ts 
        FROM prices 
        WHERE market_id = 103 AND fish_id = 1
        ORDER BY ts
    """)
    dates = [row[0] for row in cursor.fetchall()]
    
    gaps = []
    for i in range(1, len(dates)):
        gap = dates[i] - dates[i-1]
        if gap.days > 30:
            gaps.append((dates[i-1], dates[i], gap.days))
    
    if gaps:
        print(f"发现 {len(gaps)} 处数据断档（超过 30 天）:")
        gap_table = tabulate(gaps, 
                            headers=['开始日期', '结束日期', '间隔天数'], 
                            tablefmt='grid')
        print(gap_table)
    else:
        print("未发现明显数据断档")
    
    return gaps


def check_price_volatility(cursor):
    """检查价格波动异常"""
    print("\n5. 价格波动异常检查（相邻日期间价格波动超过 50%）:")
    
    cursor.execute("""
        SELECT ts, price 
        FROM prices 
        WHERE market_id = 103 AND fish_id = 1
        ORDER BY ts
    """)
    prices = cursor.fetchall()
    
    volatility_anomalies = []
    for i in range(1, len(prices)):
        prev_date, prev_price = prices[i-1]
        curr_date, curr_price = prices[i]
        
        if prev_price > 0:
            volatility = abs(curr_price - prev_price) / prev_price * 100
            if volatility > 50:
                volatility_anomalies.append((
                    prev_date, prev_price, curr_date, curr_price, volatility
                ))
    
    if volatility_anomalies:
        print(f"发现 {len(volatility_anomalies)} 次价格波动异常（超过 50%）:")
        volatility_table = tabulate(volatility_anomalies, 
                                   headers=['前日期', '前价格', '现日期', '现价格', '波动率 (%)'], 
                                   tablefmt='grid')
        print(volatility_table)
    else:
        print("未发现价格波动异常")
    
    return volatility_anomalies


def sample_verification(cursor):
    """抽样验证 20 条数据"""
    print("\n" + "="*80)
    print("第四步：抽样验证")
    print("="*80)
    print("\n随机抽取 20 条数据:")
    
    cursor.execute("""
        SELECT id, ts, price, market_id, fish_id, created_at
        FROM prices 
        WHERE market_id = 103 AND fish_id = 1
        ORDER BY RAND()
        LIMIT 20
    """)
    samples = cursor.fetchall()
    
    print(tabulate(samples, 
                  headers=['ID', '时间戳', '价格', '市场 ID', '鱼 ID', '创建时间'], 
                  tablefmt='grid'))
    
    # 验证检查
    issues = []
    for sample in samples:
        id, ts, price, market_id, fish_id, created_at = sample
        
        # 检查日期格式
        if not isinstance(ts, str) or len(str(ts)) < 10:
            issues.append(f"ID {id}: 日期格式异常")
        
        # 检查价格合理性
        if price < 0 or price > 100:
            issues.append(f"ID {id}: 价格异常 ({price})")
        
        # 检查市场规律
        if price < 5 or price > 25:
            issues.append(f"ID {id}: 价格可能不符合市场规律 ({price})")
    
    if issues:
        print("\n抽样验证发现的问题:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n抽样验证未发现明显问题")
    
    return samples, issues


def calculate_quality_score(total_count, price_anomalies, date_anomalies, 
                           duplicates, gaps, volatility_anomalies, sample_issues):
    """计算数据质量评分"""
    print("\n" + "="*80)
    print("第五步：数据质量报告")
    print("="*80)
    
    # 基础分 100 分
    score = 100
    
    # 价格异常扣分（每条扣 2 分）
    score -= len(price_anomalies) * 2
    
    # 日期异常扣分（每条扣 3 分）
    score -= len(date_anomalies) * 3
    
    # 重复数据扣分（每组扣 1 分）
    score -= len(duplicates) * 1
    
    # 数据断档扣分（每处扣 2 分）
    score -= len(gaps) * 2
    
    # 价格波动异常扣分（每次扣 1 分）
    score -= len(volatility_anomalies) * 1
    
    # 抽样问题扣分（每个扣 1 分）
    score -= len(sample_issues) * 1
    
    # 确保分数在 0-100 之间
    score = max(0, min(100, score))
    
    return score


def generate_report(cursor, stats, price_anomalies, date_anomalies, 
                   duplicates, gaps, volatility_anomalies, samples, sample_issues):
    """生成数据质量报告"""
    score = calculate_quality_score(
        stats['total_count'], price_anomalies, date_anomalies, 
        duplicates, gaps, volatility_anomalies, sample_issues
    )
    
    print("\n1. 数据总体统计表:")
    summary_table = tabulate([
        ['数据总量', stats['total_count']],
        ['价格最大值', f"{stats['price_stats']['max']:.2f}"],
        ['价格最小值', f"{stats['price_stats']['min']:.2f}"],
        ['价格平均值', f"{stats['price_stats']['avg']:.2f}"],
        ['价格中位数', f"{stats['price_stats']['median']:.2f}"],
        ['价格异常数', len(price_anomalies)],
        ['日期异常数', len(date_anomalies)],
        ['重复数据组数', len(duplicates)],
        ['数据断档数', len(gaps)],
        ['价格波动异常数', len(volatility_anomalies)],
        ['抽样问题数', len(sample_issues)]
    ], headers=['指标', '数值'], tablefmt='grid')
    print(summary_table)
    
    print("\n2. 问题数据汇总:")
    issues_summary = []
    if price_anomalies:
        issues_summary.append(['价格异常', len(price_anomalies), '价格 < 3 或 > 30'])
    if date_anomalies:
        issues_summary.append(['日期异常', len(date_anomalies), '未来时间或 < 2000 年'])
    if duplicates:
        issues_summary.append(['重复数据', len(duplicates), '同一天多条记录'])
    if gaps:
        issues_summary.append(['数据断档', len(gaps), '间隔超过 30 天'])
    if volatility_anomalies:
        issues_summary.append(['价格波动异常', len(volatility_anomalies), '波动超过 50%'])
    if sample_issues:
        issues_summary.append(['抽样问题', len(sample_issues), '抽样验证发现'])
    
    if issues_summary:
        print(tabulate(issues_summary, 
                      headers=['问题类型', '数量', '说明'], 
                      tablefmt='grid'))
    else:
        print("未发现明显问题数据")
    
    print(f"\n3. 数据质量评分：{score}/100")
    
    # 评级
    if score >= 90:
        rating = "优秀"
    elif score >= 80:
        rating = "良好"
    elif score >= 70:
        rating = "中等"
    elif score >= 60:
        rating = "合格"
    else:
        rating = "需要改进"
    
    print(f"   评级：{rating}")
    
    print("\n4. 修复建议和处理方案:")
    recommendations = []
    
    if price_anomalies:
        recommendations.append("  - 价格异常：建议核实数据来源，修正明显错误值或标记为异常数据")
    if date_anomalies:
        recommendations.append("  - 日期异常：建议检查数据采集系统，修正未来时间记录")
    if duplicates:
        recommendations.append("  - 重复数据：建议保留最新记录，删除重复数据")
    if gaps:
        recommendations.append("  - 数据断档：建议补充缺失时间段的数据或说明原因")
    if volatility_anomalies:
        recommendations.append("  - 价格波动异常：建议核实是否为真实市场价格波动")
    if sample_issues:
        recommendations.append("  - 抽样问题：建议全面检查数据格式和完整性")
    
    if not recommendations:
        recommendations.append("  - 数据质量良好，继续保持当前数据采集和管理流程")
    
    for rec in recommendations:
        print(rec)
    
    print("\n5. 下一步操作建议:")
    if score < 80:
        print("  - 优先处理价格异常和日期异常数据")
        print("  - 建立数据质量监控机制")
        print("  - 定期执行数据质量检查")
    else:
        print("  - 继续保持当前数据质量标准")
        print("  - 建议每月执行一次数据质量检查")
        print("  - 建立数据异常自动告警机制")
    
    return score


def main():
    """主函数"""
    print("="*80)
    print("数据库鲈鱼价格数据质量检查")
    print("="*80)
    print("第一步：连接数据库并验证")
    
    try:
        conn = connect_to_database()
        print("数据库连接成功！")
        
        cursor = conn.cursor()
        
        # 验证连接
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result[0] == 1:
            print("数据库验证通过！")
        else:
            print("数据库验证失败！")
            return
        
        # 执行数据质量检查
        stats = get_basic_statistics(cursor)
        price_anomalies = check_price_anomalies(cursor)
        date_anomalies = check_date_anomalies(cursor)
        duplicates = check_duplicate_data(cursor)
        gaps = check_data_gaps(cursor)
        volatility_anomalies = check_price_volatility(cursor)
        samples, sample_issues = sample_verification(cursor)
        
        # 生成报告
        score = generate_report(
            cursor, stats, price_anomalies, date_anomalies, 
            duplicates, gaps, volatility_anomalies, samples, sample_issues
        )
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*80)
        print("数据质量检查完成！")
        print("="*80)
        
        return score
        
    except pymysql.Error as e:
        print(f"数据库连接失败：{e}")
        return 0


if __name__ == "__main__":
    main()
