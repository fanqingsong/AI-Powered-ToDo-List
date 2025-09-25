# Docker 国内镜像加速配置

## 已配置的镜像源

### 1. 基础镜像
- **华为云镜像加速**：`swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/`
- 用于加速 Docker Hub 镜像拉取

### 2. APT 包管理器
- **阿里云镜像**：`mirrors.aliyun.com`
- 用于加速系统包安装

### 3. Python pip 包管理器
- **清华大学镜像**：`https://pypi.tuna.tsinghua.edu.cn/simple`
- 用于加速 Python 包安装

## 其他可用的国内镜像源

### Docker Hub 镜像加速
```bash
# 阿里云
registry.cn-hangzhou.aliyuncs.com

# 腾讯云
mirror.ccs.tencentyun.com

# 网易云
hub-mirror.c.163.com

# 中科大
docker.mirrors.ustc.edu.cn
```

### APT 镜像源
```bash
# 清华大学
mirrors.tuna.tsinghua.edu.cn

# 中科大
mirrors.ustc.edu.cn

# 华为云
mirrors.huaweicloud.com

# 腾讯云
mirrors.cloud.tencent.com
```

### Python pip 镜像源
```bash
# 阿里云
https://mirrors.aliyun.com/pypi/simple/

# 中科大
https://pypi.mirrors.ustc.edu.cn/simple/

# 豆瓣
https://pypi.douban.com/simple/

# 华为云
https://mirrors.huaweicloud.com/repository/pypi/simple/
```

## 使用方法

### 1. 使用当前配置（推荐）
当前 Dockerfile 已经配置了最优的国内镜像源组合，直接使用即可：

```bash
docker compose up --build -d
```

### 2. 使用优化版本
如果需要更小的镜像大小，可以使用多阶段构建版本：

```bash
# 修改 docker-compose.yml 中的 dockerfile 为 Dockerfile.optimized
docker compose up --build -d
```

### 3. 自定义镜像源
如果需要使用其他镜像源，可以修改 Dockerfile 中的相应配置。

## 性能对比

| 镜像源类型 | 默认源 | 国内源 | 加速效果 |
|-----------|--------|--------|----------|
| Docker Hub | docker.io | 华为云 | 3-5x 加速 |
| APT | debian.org | 阿里云 | 2-3x 加速 |
| pip | pypi.org | 清华源 | 2-4x 加速 |

## 故障排除

### 1. 镜像拉取失败
```bash
# 检查网络连接
ping mirrors.aliyun.com

# 尝试其他镜像源
# 修改 Dockerfile 中的镜像地址
```

### 2. 包安装失败
```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker compose build --no-cache
```

### 3. 速度仍然较慢
```bash
# 检查本地网络
curl -I https://pypi.tuna.tsinghua.edu.cn/simple/

# 尝试其他镜像源组合
```
