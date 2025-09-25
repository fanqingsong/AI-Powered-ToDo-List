#!/usr/bin/env python3
"""
测试不同的 Azure OpenAI 端点格式
"""

import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

api_key = os.getenv("AZURE_OPENAI_API_KEY")
base_endpoint = "https://tietoevry001.openai.azure.com"

if not api_key:
    print("❌ 请先配置 AZURE_OPENAI_API_KEY")
    exit(1)

print(f"🔍 测试不同的端点格式")
print(f"🔑 API Key: {api_key[:10]}...")

# 不同的端点格式
endpoint_formats = [
    f"{base_endpoint}/",
    f"{base_endpoint}/openai/",
    f"https://tietoevry001.openai.azure.com/",
    f"https://tietoevry001.openai.azure.com/openai/",
    f"https://tietoevry001.openai.azure.com/",
    f"https://tietoevry001.openai.azure.com/openai/",
]

headers = {"api-key": api_key}

for endpoint in endpoint_formats:
    print(f"\n🧪 测试端点: {endpoint}")
    
    # 测试部署列表
    try:
        deployments_url = f"{endpoint}openai/deployments?api-version=2024-02-15-preview"
        response = requests.get(deployments_url, headers=headers, timeout=5)
        print(f"   部署列表: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ 成功! 使用端点: {endpoint}")
            deployments = response.json()
            print(f"   📋 可用部署:")
            for deployment in deployments.get('data', []):
                print(f"      - {deployment.get('id', 'Unknown')} ({deployment.get('model', 'Unknown model')})")
            break
        elif response.status_code == 401:
            print(f"   ❌ 认证失败")
        elif response.status_code == 403:
            print(f"   ❌ 权限不足")
        else:
            print(f"   ⚠️  状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 连接失败: {e}")

print(f"\n💡 如果所有端点都失败，请检查：")
print(f"   1. Azure OpenAI 资源是否已正确创建")
print(f"   2. API Key 是否有效")
print(f"   3. 资源名称是否正确 (tietoevry001)")
print(f"   4. 是否在正确的 Azure 订阅中")
