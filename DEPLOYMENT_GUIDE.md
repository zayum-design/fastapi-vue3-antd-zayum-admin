# FastAPI + Vue3 管理系统部署指南

## 概述

本指南详细说明如何通过一行命令部署 FastAPI + Vue3 + Ant Design 管理系统到服务器，并配置宝塔面板进行域名绑定。

## 系统要求

- Linux 服务器 (推荐 Ubuntu 20.04+ 或 CentOS 7+)
- Docker 20.10+
- Docker Compose 1.29+
- 宝塔面板 (可选，用于域名管理)

## 快速部署

### 一行命令部署

```bash
# 下载部署脚本并执行
curl -sSL https://raw.githubusercontent.com/zayum-design/fastapi-vue3-antd-zayum-admin/main/deploy.sh | bash
```

或者：

```bash
# 如果已经下载项目
./deploy.sh
```

### 部署完成后显示信息

部署完成后，脚本会显示以下信息：

```
🎉 部署完成！
==========================================
📊 服务访问信息：
前端地址: http://localhost:8080
后端API: http://localhost:8000
数据库: localhost:5432

🔧 管理命令：
查看日志: docker-compose logs -f
停止服务: docker-compose down
重启服务: docker-compose restart
==========================================
```

## 详细部署步骤

### 1. 环境准备

#### 安装 Docker 和 Docker Compose

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | bash
sudo systemctl enable docker
sudo systemctl start docker

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 安装宝塔面板 (可选)

```bash
# CentOS
yum install -y wget && wget -O install.sh http://download.bt.cn/install/install_6.0.sh && sh install.sh

# Ubuntu/Debian
wget -O install.sh http://download.bt.cn/install/install-ubuntu_6.0.sh && sudo bash install.sh
```

### 2. 项目部署

#### 方法一：Git 克隆部署

```bash
# 克隆项目
git clone https://github.com/zayum-design/fastapi-vue3-antd-zayum-admin.git
cd fastapi-vue3-antd-zayum-admin

# 一键部署
./deploy.sh
```

#### 方法二：直接下载部署脚本

```bash
# 下载部署脚本
wget https://raw.githubusercontent.com/zayum-design/fastapi-vue3-antd-zayum-admin/main/deploy.sh
chmod +x deploy.sh

# 执行部署
./deploy.sh
```

### 3. 宝塔面板配置

#### 添加站点

1. 登录宝塔面板
2. 点击「网站」→「添加站点」
3. 输入域名（如：admin.yourdomain.com）
4. 选择 PHP 版本为「纯静态」
5. 创建数据库（可选）

#### 配置反向代理

**前端反向代理配置：**

1. 在站点设置中点击「反向代理」
2. 添加反向代理：
   - 代理名称：frontend
   - 目标URL：http://localhost:8080
   - 发送域名：$host

**后端API反向代理配置：**

1. 添加第二个反向代理：
   - 代理名称：api
   - 目标URL：http://localhost:8000
   - 发送域名：$host
   - 代理目录：/api

#### 配置SSL证书

1. 在站点设置中点击「SSL」
2. 选择「Let's Encrypt」
3. 勾选域名并申请证书
4. 开启强制HTTPS

### 4. 环境配置

#### 修改端口配置（可选）

如果需要修改默认端口，编辑 `docker-compose.yml`：

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # 修改为 8001:8000
  frontend:
    ports:
      - "8081:80"    # 修改为 8081:80
```

#### 数据库配置

默认数据库配置：
- 主机：db (容器内) 或 localhost (宿主机)
- 端口：5432
- 数据库：zayum_admin
- 用户名：admin
- 密码：admin123

修改数据库配置：
```bash
# 编辑 .env 文件（如果存在）
# 或修改 docker-compose.yml 中的环境变量
```

### 5. 服务管理

#### 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f
docker-compose logs -f backend    # 仅查看后端日志
docker-compose logs -f frontend   # 仅查看前端日志

# 查看服务状态
docker-compose ps

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh
```

#### 服务监控

```bash
# 检查服务健康状态
curl http://localhost:8000/health
curl http://localhost:8080

# 查看系统资源
docker stats
```

### 6. 故障排除

#### 常见问题

**问题1：端口被占用**
```bash
# 检查端口占用
netstat -tulpn | grep :8000
netstat -tulpn | grep :8080

# 停止占用端口的进程
sudo kill -9 <PID>
```

**问题2：容器启动失败**
```bash
# 查看详细错误信息
docker-compose logs

# 重新构建镜像
docker-compose build --no-cache
```

**问题3：数据库连接失败**
```bash
# 检查数据库容器状态
docker-compose ps db

# 进入数据库容器检查
docker-compose exec db psql -U admin -d zayum_admin
```

#### 日志分析

```bash
# 查看所有服务日志
docker-compose logs

# 实时查看日志
docker-compose logs -f

# 查看特定时间段的日志
docker-compose logs --since="2024-01-01" --until="2024-01-02"
```

## 安全配置

### 防火墙配置

```bash
# 开放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 8000  # 后端API（开发环境）
sudo ufw allow 8080  # 前端（开发环境）

# 启用防火墙
sudo ufw enable
```

### 数据库安全

1. 修改默认密码
2. 限制数据库访问IP
3. 定期备份数据

## 备份与恢复

### 数据库备份

```bash
# 备份数据库
docker-compose exec db pg_dump -U admin zayum_admin > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker-compose exec -T db psql -U admin -d zayum_admin < backup.sql
```

### 项目备份

```bash
# 备份整个项目
tar -czf fastapi-vue3-admin-backup-$(date +%Y%m%d).tar.gz ./

# 恢复项目
tar -xzf fastapi-vue3-admin-backup-20240101.tar.gz
```

## 性能优化

### 容器资源限制

在 `docker-compose.yml` 中添加资源限制：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
    restart: unless-stopped
```

### 启用缓存

```bash
# 添加 Redis 服务到 docker-compose.yml
redis:
  image: redis:alpine
  ports:
    - "6379:6379"
```

## 更新部署

### 更新代码

```bash
# 拉取最新代码
git pull origin main

# 重新部署
./deploy.sh
```

### 更新镜像

```bash
# 拉取最新镜像并重新部署
docker-compose pull
docker-compose up -d
```

## 联系方式

如有问题，请通过以下方式联系：
- GitHub Issues: [项目 Issues](https://github.com/zayum-design/fastapi-vue3-antd-zayum-admin/issues)
- 邮箱：support@easyiit.com

---

**注意**: 本部署指南会根据项目更新而更新，请定期查看最新版本。
