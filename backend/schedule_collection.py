#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时采集任务
"""
import schedule
import time
import subprocess
import os


def job():
    """定时执行采集任务"""
    print("开始定时采集...")
    # 切换到项目根目录
    os.chdir('/Users/zcy/IdeaProjects/fish-price-platform')
    subprocess.run(['python', 'backend/run_batch_collection.py'])
    print("定时采集完成")


# 每周一上午 9 点执行
schedule.every().monday.at("09:00").do(job)

print("定时任务已启动，按 Ctrl+C 停止")
while True:
    schedule.run_pending()
    time.sleep(60)
