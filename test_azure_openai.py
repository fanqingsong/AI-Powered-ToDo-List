#!/usr/bin/env python3
"""
Azure OpenAI 部署名称测试脚本
"""

import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取配置
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

if not api_key or not endpoint:
    print("❌ 请先配置 AZURE_OPENAI_API_KEY 和 AZURE_OPENAI_ENDPOINT")
    exit(1)

print(f"🔍 测试 Azure OpenAI 配置")
print(f"📍 端点: {endpoint}")
print(f"🔑 API Key: {api_key[:10]}...")

# 常见的部署名称
deployment_names = [
    "gpt-4o-mini",
    "gpt-35-turbo",
    "gpt-3.5-turbo", 
    "gpt-4",
    "gpt-4-turbo",
    "text-davinci-003",
    "text-davinci-002",
    "code-davinci-002"
]

# 测试每个部署名称
for deployment in deployment_names:
    print(f"\n🧪 测试部署名称: {deployment}")
    
    # 构建 URL
    url = f"{endpoint}openai/deployments/{deployment}/chat/completions?api-version=2024-02-15-preview"
    
    # 请求头
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    # 请求体
    data = {
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 成功! 部署名称 '{deployment}' 可用")
            result = response.json()
            print(f"📝 响应: {result.get('choices', [{}])[0].get('message', {}).get('content', '')}")
            break
        elif response.status_code == 404:
            print(f"❌ 404 - 部署名称 '{deployment}' 不存在")
        else:
            print(f"⚠️  {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")

print(f"\n💡 如果所有部署名称都失败，请检查：")
print(f"   1. API Key 是否正确")
print(f"   2. 端点 URL 是否正确")
print(f"   3. 是否已创建部署")
print(f"   4. 部署名称是否与 Azure 门户中的完全一致")
