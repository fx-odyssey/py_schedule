#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from celery import Celery
import os

def make_celery():
    # 使用环境变量或默认值
    redis_host = os.getenv('REDIS_HOST', 'redis')
    server_ip = os.getenv('SERVER_IP', '10.0.12.117')

    redis_url = f'redis://{redis_host}:6379/0'

    print(f"🚀 Celery 配置: Redis URL = {redis_url}")
    print(f"🌐 服务器IP: {server_ip}")

    celery = Celery(
        'flask_celery_demo',
        broker=redis_url,
        backend=redis_url,
        include=['tasks']
    )

    # Celery 配置
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Shanghai',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=300,
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        broker_connection_retry_on_startup=True,
    )

    # 定时任务配置
    celery.conf.beat_schedule = {
        'periodic-add-task': {
            'task': 'tasks.periodic_add',
            'schedule': 30.0,  # 每30秒执行一次
            'args': (10, 20)
        },
        'cleanup-old-results': {
            'task': 'tasks.cleanup_old_results',
            'schedule': 60.0,  # 每60秒执行一次
        },
        'health-check-task': {
            'task': 'tasks.health_check',
            'schedule': 45.0,  # 每45秒执行一次
        }
    }

    return celery

celery_app = make_celery()

# 测试 Redis 连接
def test_redis_connection():
    try:
        import redis
        redis_host = os.getenv('REDIS_HOST', 'redis')
        r = redis.Redis(host=redis_host, port=6379, socket_connect_timeout=10)
        if r.ping():
            print("✅ Redis 连接成功")
            return True
        else:
            print("❌ Redis 连接失败")
            return False
    except Exception as e:
        print(f"❌ Redis 连接错误: {e}")
        return False

# 在启动时测试连接
if test_redis_connection():
    print("🎉 Celery 应用初始化完成")
else:
    print("💥 Celery 应用初始化失败")
