# Docker 部署优化说明

## 问题描述

在执行私有部署时，Docker 构建会在 apt-get 步骤卡死，具体表现为：
```
#25 DONE 0.0s
#11 [backend 4/6] RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*
```

## 问题原因分析

1. **网络连接问题**：默认的 Debian 镜像源（deb.debian.org）在国内访问可能较慢或不稳定
2. **超时设置不足**：默认的构建超时时间可能不够
3. **缺乏重试机制**：构建失败后没有自动重试
4. **缓存策略问题**：Docker 构建缓存可能失效

## 优化方案

### 1. Dockerfile 优化

已对 `backend-fastapi-app/Dockerfile` 进行以下优化：

```dockerfile
# 使用国内Debian镜像源替换默认源
RUN sed -i.bak 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    sed -i.bak 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    rm -f /etc/apt/sources.list.bak

# 优化 apt-get 命令
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
```

### 2. 部署脚本优化

已对 `deploy-private.sh` 进行以下优化：

1. **增加重试机制**：后端镜像构建最多重试 3 次
2. **延长超时时间**：后端构建超时从 600 秒延长到 900 秒
3. **使用 host 网络**：构建时使用 `--network=host` 避免网络隔离问题
4. **简化构建选项**：构建失败时尝试简化构建方式
5. **优雅降级**：构建失败时尝试使用现有镜像启动

### 3. 构建策略优化

1. **分阶段构建**：优先使用缓存构建，避免重复下载
2. **增量构建**：使用 `--no-cache=false` 充分利用 Docker 缓存
3. **并行构建**：前后端镜像可以并行构建（在脚本中实现）

## 使用说明

### 快速测试优化效果

```bash
# 1. 测试 Docker 构建（本地）
cd backend-fastapi-app
docker build -t test-backend .

# 2. 执行优化后的部署脚本
chmod +x deploy-private.sh
./deploy-private.sh docker
```

### 部署模式选择

1. **docker 模式**（推荐）：使用优化后的 Docker 构建策略
2. **manual 模式**：传统手动部署，适合网络环境较好的情况
3. **auto 模式**：全自动部署，适合 CI/CD 环境

### 故障排除

如果部署仍然卡死，可以尝试：

1. **检查网络连接**：
   ```bash
   ping mirrors.tuna.tsinghua.edu.cn
   ```

2. **手动测试 apt-get**：
   ```bash
   docker run --rm -it python:3.9-slim bash -c "apt-get update && apt-get install -y gcc"
   ```

3. **使用代理**（如果需要）：
   ```bash
   # 在 Dockerfile 中添加代理设置
   ENV http_proxy=http://your-proxy:port
   ENV https_proxy=http://your-proxy:port
   ```

4. **跳过构建使用现有镜像**：
   ```bash
   # 修改部署脚本，注释掉构建部分，直接使用 docker-compose up -d
   ```

## 性能对比

| 优化前 | 优化后 |
|--------|--------|
| apt-get 可能卡死 | 使用国内镜像源，速度稳定 |
| 单次构建，失败即终止 | 最多重试 3 次 |
| 600 秒超时 | 900 秒超时 + 重试机制 |
| 无网络优化 | 使用 host 网络模式 |

## 注意事项

1. **镜像源选择**：如果清华源不稳定，可以切换到阿里云镜像源
2. **网络环境**：确保服务器可以访问国内镜像源
3. **磁盘空间**：定期清理 Docker 缓存和旧镜像
4. **日志查看**：部署失败时查看 `deploy-private.log` 获取详细信息

## 进一步优化建议

1. **使用多阶段构建**：减少最终镜像大小
2. **使用 .dockerignore**：排除不必要的文件
3. **镜像分层优化**：将不常变化的依赖放在底层
4. **使用 BuildKit**：启用 Docker BuildKit 提高构建性能

## 联系支持

如果优化后问题仍然存在，请：
1. 查看部署日志：`tail -f deploy-private.log`
2. 检查服务器 Docker 日志：`journalctl -u docker`
3. 联系系统管理员检查网络配置
