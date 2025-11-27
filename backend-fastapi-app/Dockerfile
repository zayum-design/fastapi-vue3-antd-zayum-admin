# 使用官方Python基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量，使用国内镜像源并增加超时时间
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
ENV PIP_TIMEOUT=120
ENV PIP_RETRIES=3

# 复制依赖文件
COPY requirements.txt .

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 安装依赖（使用国内镜像源和重试机制）
RUN pip install --no-cache-dir --timeout=120 --retries=3 -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["supervisord", "-c", "supervisord/supervisord.conf"]
