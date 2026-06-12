#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 API 状态
"""
import os
import requests

# 设置环境变量
os.environ['MYSQL_DSN'] = 'mysql://root:YOUR_PASSWORD@127.0.0.1:3306/fish_prices'

try:
    # 测试获取价格数据
    print('📡 测试价格 API...')
    response = requests.get('http://localhost:8080/api/prices?market_id=103&fish_id=1&start=2020-01-01&end=2026-12-31')
    print(f'价格 API 状态码: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'价格数据条数: {len(data)}')
    else:
        print(f'价格 API 错误: {response.text}')
    
    # 测试获取保存的时间段
    print('\n📡 测试保存的时间段 API...')
    response = requests.get('http://localhost:8080/api/saved-periods?type=solar&limit=20')
    print(f'保存的时间段 API 状态码: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'保存的时间段数量: {len(data)}')
    else:
        print(f'时间段 API 错误: {response.text}')
    
    # 测试获取市场列表
    print('\n📡 测试市场列表 API...')
    response = requests.get('http://localhost:8080/api/markets')
    print(f'市场列表 API 状态码: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'市场数量: {len(data)}')
    else:
        print(f'市场 API 错误: {response.text}')
    
    # 测试获取鱼类列表
    print('\n📡 测试鱼类列表 API...')
    response = requests.get('http://localhost:8080/api/fishes')
    print(f'鱼类列表 API 状态码: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'鱼类数量: {len(data)}')
    else:
        print(f'鱼类 API 错误: {response.text}')
    
except Exception as e:
    print(f'请求失败: {e}')
