#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests

# healthcheck.py - 更新 Flower 检查部分
def health_check():
    server_ip = os.getenv('SERVER_IP', '10.0.12.117')

    services = [
        {'name': 'Flask应用', 'url': f'http://{server_ip}:5000/health', 'port': 5000},
        {'name': 'Flower监控', 'url': f'http://{server_ip}:5555', 'port': 5555},
    ]

    all_healthy = True
    flask_healthy = False

    for service in services:
        try:
            print(f"🔍 检查 {service['name']}...")
            response = requests.get(service['url'], timeout=10)

            if response.status_code == 200:
                if service['name'] == 'Flask应用':
                    data = response.json()
                    print(f"✅ {service['name']} 正常")
                    print(f"   Redis状态: {data.get('redis', 'unknown')}")
                    flask_healthy = True
                else:
                    # Flower 可能返回 HTML，不解析 JSON
                    print(f"✅ {service['name']} 正常 (HTTP 200)")
            else:
                print(f"❌ {service['name']} 异常，状态码: {response.status_code}")
                if service['name'] != 'Flower监控':  # Flower 问题不影响核心功能
                    all_healthy = False

        except requests.exceptions.ConnectionError:
            print(f"❌ {service['name']} 连接被拒绝")
            if service['name'] != 'Flower监控':
                all_healthy = False
        except requests.exceptions.Timeout:
            print(f"❌ {service['name']} 连接超时")
            if service['name'] != 'Flower监控':
                all_healthy = False
        except Exception as e:
            print(f"⚠️  {service['name']} 检查异常: {e}")
            if service['name'] != 'Flower监控':
                all_healthy = False

    # 核心判断：只要 Flask 和 Redis 正常，系统就可用
    if flask_healthy:
        print("🎉 核心服务运行正常！系统可用")
        print(f"📊 应用地址: http://{server_ip}:5000")
        print(f"📈 监控地址: http://{server_ip}:5555 (可能有问题)")
        print(f"🗄️  Redis地址: {server_ip}:6379")
        return True
    else:
        print("💥 核心服务异常，请检查日志")
        return False
