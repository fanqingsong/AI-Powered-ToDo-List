#!/usr/bin/env python3
"""
Azure OpenAI 诊断脚本
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

print(f"🔍 Azure OpenAI 诊断")
print(f"📍 端点: {endpoint}")
print(f"🔑 API Key: {api_key[:10]}...")

# 测试基本连接
print(f"\n1️⃣ 测试基本连接...")
try:
    # 尝试访问部署列表端点
    deployments_url = f"{endpoint}openai/deployments?api-version=2024-02-15-preview"
    headers = {"api-key": api_key}
    
    response = requests.get(deployments_url, headers=headers, timeout=10)
    print(f"📊 状态码: {response.status_code}")
    
    if response.status_code == 200:
        deployments = response.json()
        print(f"✅ 成功获取部署列表!")
        print(f"📋 可用部署:")
        for deployment in deployments.get('data', []):
            print(f"   - {deployment.get('id', 'Unknown')} ({deployment.get('model', 'Unknown model')})")
    elif response.status_code == 401:
        print(f"❌ 认证失败 - 请检查 API Key")
    elif response.status_code == 403:
        print(f"❌ 权限不足 - 请检查 API Key 权限")
    elif response.status_code == 404:
        print(f"❌ 资源未找到 - 请检查端点 URL")
    else:
        print(f"⚠️  其他错误: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ 连接失败: {e}")

# 测试不同的 API 版本
print(f"\n2️⃣ 测试不同 API 版本...")
api_versions = ["2024-02-15-preview", "2024-06-01", "2023-12-01-preview", "2023-05-15"]

for version in api_versions:
    try:
        test_url = f"{endpoint}openai/deployments?api-version={version}"
        response = requests.get(test_url, headers=headers, timeout=5)
        print(f"   API 版本 {version}: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ 推荐使用 API 版本: {version}")
            break
    except:
        print(f"   API 版本 {version}: 连接失败")

print(f"\n3️⃣ 测试端点格式...")
# 检查端点格式
if not endpoint.endswith('/'):
    print(f"⚠️  端点 URL 应该以 '/' 结尾")
    print(f"   当前: {endpoint}")
    print(f"   建议: {endpoint}/")

print(f"\n💡 下一步操作建议:")
print(f"   1. 登录 Azure 门户 (https://portal.azure.com)")
print(f"   2. 导航到您的 Azure OpenAI 资源")
print(f"   3. 在 '模型部署' 部分查看可用的部署名称")
print(f"   4. 确保部署状态为 '成功'")
print(f"   5. 复制确切的部署名称到环境变量中")
