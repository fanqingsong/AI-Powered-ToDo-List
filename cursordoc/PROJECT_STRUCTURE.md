# 项目文档和测试脚本整理说明

## 目录结构

根据项目规范，文档和测试脚本已按以下方式整理：

### 📁 cursordoc/ - 项目文档目录
包含所有项目相关的文档文件：

- **AI 功能文档**：
  - `AI_AUTH_DIAGNOSIS_REPORT.md` - AI 认证诊断报告
  - `AI_INTELLIGENCE_OPTIMIZATION_REPORT.md` - AI 智能优化报告
  - `AI_NATIVE_OPTIMIZATION_REPORT.md` - AI 原生优化报告
  - `AI_USER_INFO_OPTIMIZATION_REPORT.md` - AI 用户信息优化报告
  - `CONVERSATION_PERSISTENCE_SUMMARY.md` - 对话持久化总结

- **集成文档**：
  - `AZURE_OPENAI_SETUP.md` - Azure OpenAI 设置指南
  - `SILICONFLOW_INTEGRATION.md` - SiliconFlow 集成文档
  - `LANGGRAPH_README.md` - LangGraph 使用说明

- **功能文档**：
  - `ADMIN_AUTO_INIT_README.md` - 管理员自动初始化说明
  - `USER_MANAGEMENT_README.md` - 用户管理说明
  - `LAYOUT_OPTIMIZATION_REPORT.md` - 布局优化报告
  - `README-ANALYTICS.md` - 分析功能说明

- **部署文档**：
  - `DOCKER_README.md` - Docker 部署说明
  - `docker-mirrors.md` - Docker 镜像加速配置

### 📁 cursortest/ - 测试脚本目录
包含所有测试和诊断脚本：

- **API 测试**：
  - `test_endpoints.py` - API 端点测试
  - `test_azure_openai.py` - Azure OpenAI API 测试
  - `test_siliconflow_api.py` - SiliconFlow API 测试
  - `test_postgres_tasks.py` - PostgreSQL 任务测试

- **前端测试**：
  - `test_frontend_auth.js` - 前端认证测试
  - `test_frontend_login.js` - 前端登录测试
  - `test_note_auth.html` - 笔记认证测试页面

- **功能测试**：
  - `test_admin_init.py` - 管理员初始化测试
  - `test_ai_intelligence.sh` - AI 智能功能测试
  - `test_conversation_persistence.sh` - 对话持久化测试

- **诊断工具**：
  - `diagnose_azure.py` - Azure 服务诊断
  - `migrate_tasks.py` - 任务迁移工具

### 📁 项目根目录
保留核心项目文件：

- `README.md` - 项目主要说明文档
- `LICENSE.md` - 项目许可证
- `docker-compose.yml` - Docker 编排配置
- `docker-compose.prod.yml` - 生产环境配置
- 各种启动脚本（`start-*.sh`）
- 清理脚本（`clean-all.sh`）

## 使用说明

1. **查看文档**：所有详细文档都在 `cursordoc/` 目录中
2. **运行测试**：所有测试脚本都在 `cursortest/` 目录中
3. **快速开始**：查看根目录的 `README.md` 了解基本使用方法

## 维护规范

- 新生成的文档请放入 `cursordoc/` 目录
- 新生成的测试脚本请放入 `cursortest/` 目录
- 保持目录结构清晰，便于维护和查找

---
*此文档由 AI 助手自动生成，遵循项目规范*
