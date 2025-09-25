# Docker 部署指南

本项目已使用 Docker Compose 进行容器化封装，可以通过一个命令启动整个应用。

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装：
- Docker
- Docker Compose

### 2. 镜像加速配置

本项目已配置多个国内镜像源，大幅提升构建速度：

- **Docker Hub**: 华为云镜像加速
- **APT 包管理**: 阿里云镜像源
- **Python pip**: 清华大学镜像源

运行测试脚本验证连接：
```bash
./test-mirrors.sh
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp env.example .env

# 编辑 .env 文件，填入您的 Azure 配置
nano .env
```

### 4. 启动应用

#### 方式一：使用启动脚本（推荐）
```bash
./start.sh
```

#### 方式二：直接使用 Docker Compose
```bash
# 构建并启动服务
docker compose up --build -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
```

### 5. 访问应用

- 应用地址：http://localhost:3000
- API 文档：http://localhost:3000/docs
- 健康检查：http://localhost:3000/api/health

## 🚀 镜像加速优化

### 已配置的国内镜像源

| 服务类型 | 镜像源 | 加速效果 |
|---------|--------|----------|
| Docker Hub | 华为云 | 3-5x 加速 |
| APT 包管理 | 阿里云 | 2-3x 加速 |
| Python pip | 清华大学 | 2-4x 加速 |

### 测试镜像源连接
```bash
# 测试所有镜像源连接状态
./test-mirrors.sh

# 测试构建速度
./test-build.sh
```

### 使用优化版本
```bash
# 修改 docker-compose.yml 中的 dockerfile 为 Dockerfile.optimized
# 使用多阶段构建，进一步减小镜像大小
```

## 常用命令

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 重启服务
docker compose restart

# 查看日志
docker compose logs -f

# 进入容器
docker compose exec todo-app bash

# 重新构建镜像
docker compose up --build -d

# 清理所有资源
docker compose down -v --rmi all
```

## 环境变量说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API 密钥 | `your-azure-openai-api-key` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI 端点 | `https://your-resource.openai.azure.com/` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Azure OpenAI 部署名称 | `gpt-35-turbo` |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API 版本 | `2024-02-15-preview` |
| `OPENAI_API_KEY` | 标准 OpenAI API 密钥 | `your-openai-api-key` |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | `your-anthropic-api-key` |

## 数据持久化

- 数据库文件存储在 `./data/` 目录中
- 容器重启后数据不会丢失

## 故障排除

### 1. 服务启动失败
```bash
# 查看详细日志
docker compose logs todo-app

# 检查容器状态
docker compose ps
```

### 2. 端口冲突
如果 3000 端口被占用，可以修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "3001:3000"  # 改为 3001 端口
```

### 3. 权限问题
```bash
# 确保启动脚本有执行权限
chmod +x start.sh
```

### 4. 清理重建
```bash
# 完全清理并重建
docker compose down -v --rmi all
docker compose up --build -d
```

## 开发模式

如果需要开发时实时更新代码，可以取消注释 `docker-compose.yml` 中的卷挂载：

```yaml
volumes:
  - ./data:/app/data
  - ./src:/app/src      # 取消注释
  - ./public:/app/public # 取消注释
```

## 生产部署

生产环境建议：
1. 使用具体的镜像标签而不是 `latest`
2. 配置适当的资源限制
3. 使用外部数据库而不是 SQLite
4. 配置 HTTPS 和域名
5. 设置适当的日志级别和监控
