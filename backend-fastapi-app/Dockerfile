# 使用官方Python基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量，使用国内镜像源并增加超时时间
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
ENV PIP_TIMEOUT=120
ENV PIP_RETRIES=3

# 使用国内Debian镜像源替换默认源，解决apt-get卡死问题
RUN sed -i.bak 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    sed -i.bak 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    rm -f /etc/apt/sources.list.bak

# 复制依赖文件
COPY requirements.txt .

# 安装系统依赖（增加重试机制和超时设置）
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 安装Python依赖（使用国内镜像源和重试机制）
RUN pip install --no-cache-dir --timeout=120 --retries=3 -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["supervisord", "-c", "supervisord/supervisord.conf"]
