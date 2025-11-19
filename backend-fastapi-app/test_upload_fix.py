#!/usr/bin/env python3
"""
测试上传功能修复的脚本
"""

import requests
import json
import os

def test_upload_endpoint():
    """测试上传接口是否正常工作"""
    
    # 首先获取有效的 token
    login_url = "http://localhost:8000/api/admin/auth/login"
    login_data = {
        "username": "admin",  # 根据实际情况修改
        "password": "admin123"  # 根据实际情况修改
    }
    
    try:
        # 尝试登录获取 token
        login_response = requests.post(login_url, json=login_data)
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get('data', {}).get('token')
            print(f"成功获取 token: {token[:20]}...")
            
            # 测试上传接口
            upload_url = "http://localhost:8000/api/admin/upload"
            
            # 创建一个测试图片文件
            test_image_path = "test_image.png"
            with open(test_image_path, 'wb') as f:
                # 创建一个简单的 PNG 文件头
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x00\x00\x00\x00IEND\xaeB`\x82')
            
            # 上传文件
            with open(test_image_path, 'rb') as f:
                files = {'file': ('test.png', f, 'image/png')}
                data = {'sub_dir': 'images'}
                headers = {'Authorization': f'Bearer {token}'}
                
                upload_response = requests.post(upload_url, files=files, data=data, headers=headers)
                
                print(f"上传响应状态码: {upload_response.status_code}")
                print(f"上传响应内容: {upload_response.text}")
                
                if upload_response.status_code == 200:
                    print("✅ 上传功能修复成功！")
                else:
                    print("❌ 上传功能仍有问题")
            
            # 清理测试文件
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
                
        else:
            print(f"登录失败: {login_response.status_code} - {login_response.text}")
            
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

def check_server_status():
    """检查服务器状态"""
    try:
        response = requests.get("http://localhost:8000/docs")
        print(f"服务器状态: ✅ 运行正常 (状态码: {response.status_code})")
    except Exception as e:
        print(f"服务器状态: ❌ 无法连接 - {e}")

if __name__ == "__main__":
    print("=== 测试上传功能修复 ===")
    check_server_status()
    print("\n=== 测试上传接口 ===")
    test_upload_endpoint()
