#!/bin/bash

echo "=== Flask + Celery + Redis Docker 启动脚本 ==="

# 获取本机 IP 地址
EXTERNAL_SERVER="8.8.8.8"
LOCAL_IP=""
if ping -c 1 $EXTERNAL_SERVER &> /dev/null; then
    LOCAL_IP=$(ip route get $EXTERNAL_SERVER | grep -oP 'src \K\S+')
    echo "本地 IP: $LOCAL_IP"
else
    echo "本地网络不可用."
    exit 1
fi

OLD_IP="10.0.12.117"
echo "开始替换IP地址..."
echo "旧IP: $OLD_IP → 新IP: $LOCAL_IP"

# 查找并替换所有文件（除脚本自身）
find . -type f ! -name "$(basename "$0")" -exec grep -l "$OLD_IP" {} \; | while read file; do
    echo "处理文件: $file"
    sed -i "s/$OLD_IP/$LOCAL_IP/g" "$file"
done
echo "替换完成！"

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请启动 Docker 服务"
    exit 1
fi

# 停止现有服务
echo "停止现有服务..."
docker-compose down

# 构建和启动服务
echo "构建 Docker 镜像..."
docker-compose build

echo "启动服务..."
docker-compose up -d

echo "等待服务启动..."
sleep 15

# 运行健康检查
echo "运行健康检查..."
docker-compose exec flask-celery-app python healthcheck.py

echo ""
echo "=== 启动完成 ==="
echo "📊 Flask 应用: http://$LOCAL_IP:5000"
echo "📈 Flower 监控: http://$LOCAL_IP:5555"
echo "🗄️ Redis: $LOCAL_IP:6379"
echo ""
echo "🐳 容器状态: docker-compose ps"
echo "📋 服务日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"
