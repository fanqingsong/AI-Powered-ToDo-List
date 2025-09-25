# 开发模式：使用 Node.js 镜像
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/node:18-alpine

# 设置工作目录
WORKDIR /app

# 配置国内镜像源加速
RUN npm config set registry https://registry.npmmirror.com

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码（在开发模式下会被 volume 挂载覆盖）
COPY . .

# 暴露端口（Vite 开发服务器默认端口 3000）
EXPOSE 3000

# 设置环境变量
ENV NODE_ENV=development

# 启动 Vite 开发服务器
CMD ["npm", "run", "dev"]