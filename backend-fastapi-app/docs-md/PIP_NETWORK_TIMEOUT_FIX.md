# PIP 网络超时问题解决方案

## 问题描述
在Docker构建过程中，pip安装依赖包时出现网络超时错误：
```
pip._vendor.urllib3.exceptions.ReadTimeoutError: HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Read timed out.
```

## 解决方案

### 方案1：使用国内镜像源（推荐）
已更新主Dockerfile，使用清华镜像源：
- 镜像源：`https://pypi.tuna.tsinghua.edu.cn/simple`
- 超时时间：120秒
- 重试次数：3次

### 方案2：使用阿里云镜像源
如果清华源不稳定，可以使用阿里云镜像源：
```dockerfile
RUN pip install --no-cache-dir \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    --timeout=120 \
    --retries=3 \
    -r requirements.txt
```

### 方案3：分步安装大包
对于特别大的包（如SQLAlchemy），可以单独安装：
```dockerfile
# 先安装大包
RUN pip install --no-cache-dir \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    --timeout=300 \
    --retries=5 \
    sqlalchemy==2.0.36

# 再安装其他依赖
RUN pip install --no-cache-dir \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    --timeout=120 \
    --retries=3 \
    -r requirements.txt
```

### 方案4：使用环境变量配置
在Dockerfile中设置环境变量：
```dockerfile
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
ENV PIP_TIMEOUT=120
ENV PIP_RETRIES=3
```

## 其他优化建议

### 1. 安装系统编译工具
对于需要编译的包，确保安装必要的系统工具：
```dockerfile
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*
```

### 2. 清理缓存
使用`--no-cache-dir`避免缓存占用空间。

### 3. 分层构建
将依赖安装和应用代码复制分开，利用Docker缓存：
```dockerfile
# 依赖层
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用层
COPY . .
```

## 可用的国内镜像源

1. **清华大学**：`https://pypi.tuna.tsinghua.edu.cn/simple`
2. **阿里云**：`https://mirrors.aliyun.com/pypi/simple/`
3. **豆瓣**：`https://pypi.douban.com/simple/`
4. **华为云**：`https://repo.huaweicloud.com/repository/pypi/simple`

## 测试命令
重新构建Docker镜像：
```bash
docker build -t your-app-name .
```

## 注意事项
- 如果仍然遇到超时问题，可以进一步增加超时时间到300秒
- 对于特别不稳定的网络，可以考虑使用代理服务器
- 确保Docker守护进程有足够的网络权限
