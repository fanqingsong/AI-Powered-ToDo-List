#!/usr/bin/env python3
"""
硅基流动API连接测试脚本
测试API接口是否可用
"""

import requests
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('/home/song/workspace/me/AI-Powered-ToDo-List/backend/.env')

def test_siliconflow_api():
    """测试硅基流动API连接"""
    print("=" * 60)
    print("硅基流动API连接测试")
    print("=" * 60)
    
    # 获取配置
    api_key = os.getenv('SILICONFLOW_API_KEY')
    base_url = os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')
    model = os.getenv('SILICONFLOW_MODEL', 'deepseek-chat')
    
    print(f"API密钥: {api_key[:10]}..." if api_key and len(api_key) > 10 else f"API密钥: {api_key}")
    print(f"基础URL: {base_url}")
    print(f"模型: {model}")
    print()
    
    if not api_key or api_key == 'your_siliconflow_api_key':
        print("❌ 错误: 未设置有效的API密钥")
        return False
    
    # 测试API端点
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 测试数据
    test_data = {
        "model": model,
        "messages": [
            {"role": "user", "content": "你好，请简单回复'测试成功'"}
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    print("正在测试API连接...")
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    print()
    
    try:
        # 发送请求
        response = requests.post(
            url, 
            headers=headers, 
            json=test_data,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API连接成功！")
            print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 检查响应格式
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"AI回复: {content}")
                return True
            else:
                print("⚠️ 响应格式异常")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def test_openai_compatible():
    """测试OpenAI兼容性"""
    print("\n" + "=" * 60)
    print("OpenAI兼容性测试")
    print("=" * 60)
    
    api_key = os.getenv('SILICONFLOW_API_KEY')
    base_url = os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')
    
    if not api_key or api_key == 'your_siliconflow_api_key':
        print("❌ 未设置API密钥")
        return False
    
    # 使用OpenAI格式测试
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ OpenAI兼容性测试通过")
            return True
        else:
            print(f"❌ 兼容性测试失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 兼容性测试异常: {e}")
        return False

def test_available_models():
    """测试可用模型列表"""
    print("\n" + "=" * 60)
    print("可用模型测试")
    print("=" * 60)
    
    api_key = os.getenv('SILICONFLOW_API_KEY')
    base_url = os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')
    
    if not api_key or api_key == 'your_siliconflow_api_key':
        print("❌ 未设置API密钥")
        return False
    
    # 测试模型列表端点
    url = f"{base_url}/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print("✅ 模型列表获取成功")
            print(f"可用模型: {json.dumps(models, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"❌ 模型列表获取失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 模型列表测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("硅基流动API综合测试")
    print("=" * 60)
    
    # 测试API连接
    api_test = test_siliconflow_api()
    
    # 测试OpenAI兼容性
    compat_test = test_openai_compatible()
    
    # 测试模型列表
    models_test = test_available_models()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    if api_test:
        print("🎉 硅基流动API连接正常！")
        print("✅ 可以正常使用硅基流动接口")
    else:
        print("❌ 硅基流动API连接失败")
        print("请检查：")
        print("1. API密钥是否正确")
        print("2. 网络连接是否正常")
        print("3. 硅基流动服务是否可用")
    
    if compat_test:
        print("✅ OpenAI兼容性正常")
    else:
        print("❌ OpenAI兼容性有问题")
    
    if models_test:
        print("✅ 模型列表获取正常")
    else:
        print("❌ 模型列表获取失败")

if __name__ == "__main__":
    main()
