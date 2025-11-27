# Docker 网络问题解决方案

## 问题描述
Docker构建过程中出现基础镜像拉取失败：
```
ERROR: failed to solve: python:3.9-slim: failed to resolve source metadata for docker.io/library/python:3.9-slim: unexpected status from HEAD request to https://fwk83r73.mirror.aliyuncs.com/v2/library/python/manifests/3.9-slim?ns=docker.io: 403 Forbidden
```

## 解决方案

### 方案1：重置Docker镜像源配置
```bash
# 重置Docker镜像源配置
docker system prune -a --volumes
```

然后重新配置镜像源或使用默认配置。

### 方案2：使用国内Docker镜像源
在Docker Desktop中配置镜像源：
1. 打开Docker Desktop
2. 进入Settings → Docker Engine
3. 修改registry-mirrors配置：
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://registry.docker-cn.com"
  ]
}
```

### 方案3：使用代理服务器
如果网络环境需要代理：
```bash
# 设置Docker代理
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
docker build -t fastapi-backend-fixed .
```

### 方案4：使用预下载的基础镜像
```bash
# 先拉取基础镜像
docker pull python:3.9-slim

# 再构建应用
docker build -t fastapi-backend-fixed .
```

### 方案5：使用不同的基础镜像标签
尝试使用其他可用的Python镜像：
```dockerfile
# 使用不同的标签
FROM python:3.9

# 或者使用alpine版本
FROM python:3.9-alpine
```

## 立即解决方案

### 1. 清理Docker缓存并重试
```bash
# 清理所有Docker缓存
docker system prune -a --volumes

# 重新拉取基础镜像
docker pull python:3.9-slim

# 重新构建
cd backend-fastapi-app && docker build -t fastapi-backend-fixed .
```

### 2. 临时禁用镜像源
在Docker Desktop中临时禁用registry-mirrors配置，使用官方源。

### 3. 检查网络连接
```bash
# 测试网络连接
ping docker.io
curl -I https://docker.io

# 检查代理设置
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

## 推荐的镜像源配置

### 中科大镜像源
```json
{
  "registry-mirrors": ["https://docker.mirrors.ustc.edu.cn"]
}
```

### 网易镜像源
```json
{
  "registry-mirrors": ["https://hub-mirror.c.163.com"]
}
```

### 阿里云镜像源（需要账户）
```json
{
  "registry-mirrors": ["https://your-code.mirror.aliyuncs.com"]
}
```

## 验证解决方案
```bash
# 验证Docker配置
docker info

# 测试镜像拉取
docker pull hello-world

# 构建应用
cd backend-fastapi-app && docker build -t fastapi-backend-fixed .
```

## 注意事项
- 如果使用公司网络，可能需要配置代理
- 某些镜像源可能需要注册账户
- 定期清理Docker缓存可以解决很多网络问题
- 确保Docker Desktop有足够的系统资源
