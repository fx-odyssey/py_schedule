#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, session
from celery_app import celery_app
from tasks import long_running_task, add_numbers, process_data, send_email, generate_report, failing_task
from celery.result import AsyncResult
import uuid
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# 获取服务器IP用于显示
SERVER_IP = os.getenv('SERVER_IP', '10.0.12.117')

@app.before_request
def make_session_permanent():
    session.permanent = True
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

@app.route('/')
def index():
    return render_template('index.html', server_ip=SERVER_IP)

@app.route('/start_long_task', methods=['POST'])
def start_long_task():
    """启动长时间运行的任务"""
    try:
        duration = int(request.form.get('duration', 10))
        task = long_running_task.delay(duration)
        return jsonify({'task_id': task.id}), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/start_add_task', methods=['POST'])
def start_add_task():
    """启动加法任务"""
    try:
        x = int(request.form.get('x', 5))
        y = int(request.form.get('y', 3))
        task = add_numbers.delay(x, y)
        return jsonify({'task_id': task.id}), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/start_process_data', methods=['POST'])
def start_process_data():
    """启动数据处理任务"""
    try:
        data_str = request.form.get('data', '1,2,3,4,5')
        data = [int(x) for x in data_str.split(',')]
        task = process_data.delay(data)
        return jsonify({'task_id': task.id}), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/start_email_task', methods=['POST'])
def start_email_task():
    """启动邮件发送任务"""
    try:
        email = request.form.get('email', 'user@example.com')
        subject = request.form.get('subject', '测试邮件')
        task = send_email.delay(email, subject)
        return jsonify({'task_id': task.id}), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/start_report_task', methods=['POST'])
def start_report_task():
    """启动报告生成任务"""
    try:
        report_type = request.form.get('report_type', '销售')
        task = generate_report.delay(report_type)
        return jsonify({'task_id': task.id}), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/start_failing_task', methods=['POST'])
def start_failing_task():
    """启动可能失败的任务"""
    try:
        fail_at_step = request.form.get('fail_at_step')
        fail_at_step = int(fail_at_step) if fail_at_step else None
        task = failing_task.delay(fail_at_step)
        return jsonify({'task_id': task.id}), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/task_status/<task_id>')
def task_status(task_id):
    """查询任务状态"""
    try:
        task_result = AsyncResult(task_id, app=celery_app)

        response = {
            'task_id': task_id,
            'state': task_result.state,
            'status': 'Pending...'
        }

        if task_result.state == 'PENDING':
            response.update({
                'status': '任务等待中...'
            })
        elif task_result.state == 'PROGRESS':
            response.update(task_result.info or {})
            response['status'] = task_result.info.get('status', '处理中...')
        elif task_result.state == 'SUCCESS':
            response.update({
                'status': '任务完成!',
                'result': task_result.result
            })
        elif task_result.state == 'FAILURE':
            response.update({
                'status': '任务失败!',
                'result': str(task_result.info)
            })

        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """健康检查端点"""
    try:
        # 测试 Redis 连接
        import redis
        redis_host = os.getenv('REDIS_HOST', 'redis')
        r = redis.Redis(host=redis_host, port=6379, socket_connect_timeout=5)
        redis_status = 'connected' if r.ping() else 'disconnected'
    except Exception as e:
        redis_status = f'error: {str(e)}'

    return jsonify({
        'status': 'healthy',
        'server_ip': SERVER_IP,
        'redis': redis_status,
        'timestamp': datetime.now().isoformat(),
        'services': ['flask', 'celery-worker', 'celery-beat', 'flower', 'redis']
    })

@app.route('/info')
def info():
    """系统信息"""
    return jsonify({
        'server_ip': SERVER_IP,
        'flask_port': 5000,
        'flower_port': 5555,
        'redis_port': 6379,
        'access_urls': {
            'flask_app': f'http://{SERVER_IP}:5000',
            'flower_monitor': f'http://{SERVER_IP}:5555',
            'redis': f'redis://{SERVER_IP}:6379'
        }
    })

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error', 'message': str(error)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))

    print("=" * 60)
    print("🚀 Flask + Celery + Redis 多任务调度系统")
    print("=" * 60)
    print(f"📊 Flask 应用: http://{SERVER_IP}:{port}")
    print(f"📈 Flower 监控: http://{SERVER_IP}:5555")
    print(f"🗄️  Redis: {SERVER_IP}:6379")
    print("=" * 60)

    try:
        app.run(host=host, port=port, debug=False)
    except Exception as e:
        print(f"❌ Flask 启动失败: {e}")
        import traceback
        traceback.print_exc()
