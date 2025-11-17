#!/usr/bin/env python3
"""
测试 notifications API 接口
"""
import sys
import os
import requests
import json

# 添加后端路径到系统路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend-fastapi-app'))

def test_notifications_api():
    """测试 notifications API 接口"""
    base_url = "http://localhost:8000/api/admin"
    
    print("=== 测试 Notifications API ===")
    
    # 测试获取通知列表
    print("\n1. 测试获取通知列表...")
    try:
        response = requests.get(f"{base_url}/notifications/list")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except requests.exceptions.ConnectionError:
        print("连接失败 - 请确保后端服务正在运行")
        print("启动命令: cd backend-fastapi-app && python -m app.main")
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_notifications_api()
