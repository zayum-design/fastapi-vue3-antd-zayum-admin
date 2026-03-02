# 增强功能安装指南

本文档说明如何安装和使用优化后的增强功能。

## 核心功能（无需额外安装）

以下功能无需额外依赖即可使用：

- ✅ **EnhancedRepository** - 增强版 Repository 基类
- ✅ **CRUDRouter** - 通用 CRUD 路由生成器
- ✅ **改进的会话管理** - DatabaseSessionManager
- ✅ **统一验证工具** - Validators
- ✅ **缓存装饰器** - 内存缓存模式

## 增强功能（需要额外安装）

### 1. API 限流 (slowapi)

启用基于 slowapi 的 API 限流功能：

```bash
# 方式1: 使用 pip 安装
pip install slowapi==0.1.9

# 方式2: 使用项目配置安装
pip install -e ".[enhanced]"
```

安装后，限流装饰器将自动生效：

```python
from app.core.rate_limiter import rate_limit, RateLimitConfig

@router.post("/login")
@rate_limit(RateLimitConfig.LOGIN)  # 5次/分钟
async def login(...):
    ...
```

**未安装时的行为**：
- 装饰器不会报错
- 限流功能不生效（无限制）
- 日志会提示：`slowapi not installed, rate limiting disabled`

### 2. Redis 缓存 (推荐)

启用 Redis 缓存以获得更好的性能：

```bash
# 安装带 hiredis 优化的 redis 客户端
pip install redis[hiredis]==5.2.1
```

然后在 `.env` 中配置：

```env
CACHE_TYPE=redis
REDIS_URL=redis://localhost:6379/0
```

**使用内存缓存时**：
- 无需额外安装
- 缓存仅在单个进程内有效
- 重启后缓存丢失
- 适合开发和测试环境

## 完整安装所有增强功能

```bash
# 进入项目目录
cd backend-fastapi-app

# 安装核心依赖
pip install -r requirements.txt

# 安装增强依赖（可选）
pip install slowapi==0.1.9
pip install redis[hiredis]==5.2.1
```

或者使用 pyproject.toml：

```bash
pip install -e ".[enhanced,dev]"
```

## 功能对比

| 功能 | 基础版 | 增强版 | 说明 |
|------|--------|--------|------|
| Repository | ✅ | ✅ | 无需额外依赖 |
| CRUD Router | ✅ | ✅ | 无需额外依赖 |
| 会话管理 | ✅ | ✅ | 无需额外依赖 |
| 验证工具 | ✅ | ✅ | 无需额外依赖 |
| 内存缓存 | ✅ | ✅ | 无需额外依赖 |
| API 限流 | ❌ | ✅ | 需安装 slowapi |
| Redis 缓存 | ❌ | ✅ | 需配置 Redis |

## 生产环境建议

对于生产环境，建议安装所有增强功能：

```bash
# 1. 安装核心依赖
pip install -r requirements.txt

# 2. 安装 slowapi（API 限流）
pip install slowapi==0.1.9

# 3. 配置 Redis（缓存 + 限流存储）
# 在 .env 文件中设置 CACHE_TYPE=redis
```

## 故障排除

### 问题：无法导入 slowapi

**现象**：
```
ImportError: No module named 'slowapi'
```

**解决**：
```bash
pip install slowapi==0.1.9
```

或者忽略（代码已做兼容处理）：
- 限流功能将被禁用
- 其他功能正常工作

### 问题：Redis 连接失败

**现象**：
```
Failed to connect to Redis for rate limiting
```

**解决**：
1. 检查 Redis 服务是否运行
2. 检查 `.env` 中的 REDIS_URL 配置
3. 或者切换到内存模式：
   ```env
   CACHE_TYPE=simple
   ```

## 验证安装

```bash
# 检查 slowapi
python -c "import slowapi; print('slowapi:', slowapi.__version__)"

# 检查 redis
python -c "import redis; print('redis:', redis.__version__)"

# 运行应用
python -m app.main
```
