#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from celery_app import celery_app
import time
import random
from datetime import datetime
import os

@celery_app.task(bind=True)
def long_running_task(self, duration=10):
    """模拟长时间运行的任务"""
    task_id = self.request.id

    # 更新任务状态
    self.update_state(
        state='PROGRESS',
        meta={'current': 0, 'total': 100, 'status': '任务开始...'}
    )

    for i in range(100):
        # 模拟工作
        time.sleep(duration / 100)

        # 更新进度
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i + 1,
                'total': 100,
                'status': f'处理中... {i + 1}%',
                'task_id': task_id
            }
        )

    return {'current': 100, 'total': 100, 'status': '任务完成!', 'result': 'success'}

@celery_app.task
def add_numbers(x, y):
    """简单的加法任务"""
    time.sleep(2)  # 模拟一些处理时间
    result = x + y
    print(f"🧮 计算完成: {x} + {y} = {result}")
    return f"{x} + {y} = {result}"

@celery_app.task
def process_data(data):
    """数据处理任务"""
    time.sleep(3)
    processed = [item * 2 for item in data]
    result = f"处理后的数据: {processed}"
    print(f"📊 {result}")
    return result

@celery_app.task
def send_email(to_email, subject):
    """模拟发送邮件任务"""
    time.sleep(5)
    result = f"邮件 '{subject}' 已发送到 {to_email}"
    print(f"📧 {result}")
    return result

@celery_app.task
def periodic_add(x, y):
    """定时任务示例"""
    result = x + y
    print(f"🕒 定时任务执行: {x} + {y} = {result} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return result

@celery_app.task
def cleanup_old_results():
    """清理旧结果的定时任务"""
    print(f"🧹 执行清理任务 at {datetime.now().strftime('%H:%M:%S')}")
    return "清理完成"

@celery_app.task
def health_check():
    """健康检查定时任务"""
    server_ip = os.getenv('SERVER_IP', '10.0.12.117')
    status = f"✅ 系统健康 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - IP: {server_ip}"
    print(status)
    return status

@celery_app.task
def generate_report(report_type):
    """生成报告任务"""
    progress_steps = [
        "收集数据...",
        "分析数据...",
        "生成图表...",
        "导出报告..."
    ]

    for i, step in enumerate(progress_steps):
        time.sleep(2)
        print(f"📈 生成报告进度: {step}")

    return f"{report_type}报告生成完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

@celery_app.task(bind=True)
def failing_task(self, fail_at_step=None):
    """模拟可能失败的任务"""
    steps = ["步骤1", "步骤2", "步骤3", "步骤4", "步骤5"]

    for i, step in enumerate(steps, 1):
        if fail_at_step and i == fail_at_step:
            raise Exception(f"任务在第 {i} 步失败: {step}")

        time.sleep(1)
        self.update_state(
            state='PROGRESS',
            meta={'current': i, 'total': len(steps), 'status': f'执行: {step}'}
        )

    return "所有步骤完成!"
