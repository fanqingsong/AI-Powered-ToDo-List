# 使用华为云镜像加速
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

COPY ./celery/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./celery/src ./src

CMD ["celery", "-A", "src.celery_app", "worker", "--loglevel=info"]


