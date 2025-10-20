# Azure OpenAI 配置指南

## 🔍 当前状态

您的 Azure OpenAI 配置遇到了 404 错误，这通常表示以下问题之一：

1. **资源不存在**：Azure OpenAI 资源可能未正确创建
2. **API Key 无效**：提供的 API Key 可能已过期或无效
3. **资源名称错误**：`tietoevry001` 可能不是正确的资源名称
4. **权限问题**：API Key 可能没有访问权限

## 🛠️ 解决步骤

### 1. 验证 Azure OpenAI 资源

1. 登录 [Azure 门户](https://portal.azure.com)
2. 搜索 "Azure OpenAI"
3. 检查是否存在名为 `tietoevry001` 的资源
4. 如果没有，需要先创建 Azure OpenAI 资源

### 2. 获取正确的配置信息

在 Azure 门户中找到您的 Azure OpenAI 资源后：

1. **获取端点 URL**：
   - 在资源概览页面找到 "终结点"
   - 格式通常为：`https://your-resource-name.openai.azure.com/`

2. **获取 API Key**：
   - 在左侧菜单中点击 "密钥和终结点"
   - 复制 "密钥 1" 或 "密钥 2"

3. **获取部署名称**：
   - 在左侧菜单中点击 "模型部署"
   - 查看已创建的部署名称
   - 确保部署状态为 "成功"

### 3. 创建模型部署（如果还没有）

如果还没有部署，需要：

1. 在 Azure 门户中进入您的 Azure OpenAI 资源
2. 点击 "模型部署" → "创建新部署"
3. 选择模型（如 GPT-3.5-turbo 或 GPT-4）
4. 输入部署名称（如 `gpt-35-turbo`）
5. 等待部署完成

### 4. 更新环境变量

一旦获得正确的配置信息，更新 `.env` 文件：

```bash
# Azure OpenAI 配置
AZURE_OPENAI_API_KEY=your_actual_api_key
AZURE_OPENAI_ENDPOINT=https://your-actual-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_actual_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 5. 重启应用

```bash
docker compose restart
```

## 🧪 测试配置

使用提供的测试脚本验证配置：

```bash
# 测试部署名称
python3 test_azure_openai.py

# 诊断连接问题
python3 diagnose_azure.py

# 测试端点格式
python3 test_endpoints.py
```

## 🔄 临时解决方案

在解决 Azure OpenAI 配置问题之前，应用会运行在降级模式下：

- ✅ **任务管理功能**：完全可用
- ⚠️ **AI 聊天功能**：显示配置提示

您仍然可以：
- 创建、查看、更新、删除任务
- 使用 REST API 进行任务管理
- 访问 Web 界面

## 📞 获取帮助

如果仍然遇到问题，请：

1. 检查 Azure 订阅是否有效
2. 确认 Azure OpenAI 服务是否在您的区域可用
3. 验证 API Key 的权限设置
4. 联系 Azure 支持团队

## 🎯 成功配置后的功能

一旦 Azure OpenAI 配置正确，您将能够：

- 与 AI 助手进行自然语言对话
- 通过聊天创建和管理任务
- 获得智能的任务管理建议
- 享受完整的 AI 功能体验
