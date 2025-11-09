# 使用华为云镜像加速
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 配置国内 APT 镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 配置国内 pip 镜像源（作为备用）
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 安装 uv（优先使用 pip 安装，失败则使用官方安装脚本）
RUN pip install --timeout=300 --retries=5 uv || \
    (curl -LsSf https://astral.sh/uv/install.sh | sh)
ENV PATH="/root/.cargo/bin:$PATH"

# 配置 uv 使用国内镜像源
ENV UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV UV_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# 复制 pyproject.toml 和 uv.lock（如果存在）
COPY pyproject.toml ./
COPY uv.lock* ./

# 使用 uv 安装 Python 依赖
# uv sync 会创建虚拟环境并安装所有依赖
# 使用 --no-install-project 只安装依赖，不构建项目本身
RUN uv sync --frozen --no-install-project || uv sync --no-install-project

# 将虚拟环境的 bin 目录添加到 PATH
ENV PATH="/app/.venv/bin:$PATH"

# 复制应用代码
COPY . .

# 创建数据库目录
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 3000

# 启动命令（使用虚拟环境中的 uvicorn）
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "3000"]
