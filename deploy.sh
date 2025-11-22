#!/bin/bash

# 一键部署脚本 - FastAPI + Vue3 管理系统
# 使用方法: ./deploy.sh

set -e

echo "🚀 开始部署 FastAPI + Vue3 管理系统..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "📦 构建并启动容器..."
docker-compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."

# 检查后端服务
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端服务运行正常"
else
    echo "⚠️  后端服务可能还在启动中，请稍后检查"
fi

# 检查前端服务
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ 前端服务运行正常"
else
    echo "⚠️  前端服务可能还在启动中，请稍后检查"
fi

# 显示部署信息
echo ""
echo "🎉 部署完成！"
echo "=========================================="
echo "📊 服务访问信息："
echo "前端地址: http://localhost:8080"
echo "后端API: http://localhost:8000"
echo "数据库: localhost:5432"
echo ""
echo "🔧 管理命令："
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
echo "重启服务: docker-compose restart"
echo "=========================================="
echo ""
echo "💡 宝塔面板配置提示："
echo "1. 在宝塔面板中添加站点"
echo "2. 反向代理配置："
echo "   - 前端: 代理到 http://localhost:8080"
echo "   - 后端API: 代理到 http://localhost:8000"
echo "3. 配置域名和SSL证书"
echo ""
echo "📝 更多详细配置请查看 DEPLOYMENT_GUIDE.md"
