#!/bin/bash

# 测试部署脚本基本功能
echo "🧪 测试部署脚本基本功能..."

# 测试语法检查
echo "1. 检查部署脚本语法..."
bash -n deploy.sh
if [ $? -eq 0 ]; then
    echo "✅ 部署脚本语法正确"
else
    echo "❌ 部署脚本语法有误"
    exit 1
fi

# 测试一行部署脚本语法
echo "2. 检查一行部署脚本语法..."
bash -n one_line_deploy.sh
if [ $? -eq 0 ]; then
    echo "✅ 一行部署脚本语法正确"
else
    echo "❌ 一行部署脚本语法有误"
    exit 1
fi

# 检查文件权限
echo "3. 检查文件权限..."
if [ -x "deploy.sh" ]; then
    echo "✅ deploy.sh 有执行权限"
else
    echo "❌ deploy.sh 没有执行权限"
fi

if [ -x "one_line_deploy.sh" ]; then
    echo "✅ one_line_deploy.sh 有执行权限"
else
    echo "❌ one_line_deploy.sh 没有执行权限"
fi

# 检查必要文件是否存在
echo "4. 检查必要文件..."
required_files=("docker-compose.yml" "deploy.sh" "one_line_deploy.sh" "DEPLOYMENT_GUIDE.md")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 不存在"
    fi
done

# 显示部署信息预览
echo ""
echo "📋 部署信息预览："
echo "=========================================="
echo "前端地址: http://localhost:8080"
echo "后端API: http://localhost:8000"
echo "数据库: localhost:5432"
echo "=========================================="

echo ""
echo "🎉 测试完成！部署脚本准备就绪。"
echo ""
echo "💡 使用方法："
echo "1. 一行部署: ./one_line_deploy.sh"
echo "2. 详细部署: ./deploy.sh"
echo "3. 查看文档: cat DEPLOYMENT_GUIDE.md"
