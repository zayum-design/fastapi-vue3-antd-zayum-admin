# 数据库健康检查功能说明

## 概述

本文档介绍了为解决数据库连接丢失问题而实现的数据库健康检查功能。该功能提供了实时监控数据库连接状态和连接池健康状态的API端点。

## 问题背景

在之前的版本中，系统偶尔会出现以下错误：
```
DatabaseConnectionError: 数据库会话无效: (pymysql.err.OperationalError) (2013, 'Lost connection to MySQL server during query')
```

这通常是由于：
- MySQL的wait_timeout设置较短
- 连接池配置不够优化
- 网络连接不稳定

## 解决方案

### 1. 优化的数据库连接配置

在 `app/dependencies/database.py` 中进行了以下优化：

```python
def create_db_engine():
    """创建数据库引擎"""
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # 在从连接池获取连接前执行ping测试
        echo=False,
        pool_size=5,  # 增加连接池大小
        max_overflow=10,  # 增加最大溢出连接数
        pool_recycle=3600,  # 1小时回收连接，避免MySQL wait_timeout问题
        pool_timeout=30,  # 增加连接获取超时时间
        connect_args={
            'connect_timeout': 15,  # 增加连接超时时间
            'read_timeout': 30,  # 增加读取超时时间
            'write_timeout': 30,  # 增加写入超时时间
            'charset': 'utf8mb4',
            'autocommit': True,  # 启用自动提交
            'client_flag': 0,  # 清除可能导致问题的客户端标志
        }
    )
    return engine
```

### 2. 健康检查API端点

#### 数据库连接健康检查
**端点**: `GET /api/common/health/database`

**功能**: 检查数据库连接状态和响应时间

**响应示例**:
```json
{
    "status": "healthy",
    "database": "connected",
    "response_time_ms": 0.2,
    "timestamp": "2025-11-20T18:03:57"
}
```

**错误响应示例**:
```json
{
    "status": "unhealthy",
    "database": "disconnected",
    "error": "数据库连接错误信息",
    "timestamp": "2025-11-20T18:03:57Z"
}
```

#### 连接池健康检查
**端点**: `GET /api/common/health/connection-pool`

**功能**: 检查数据库连接池状态

**响应示例**:
```json
{
    "status": "healthy",
    "connection_pool": "active",
    "test_result": 1
}
```

**错误响应示例**:
```json
{
    "status": "unhealthy",
    "connection_pool": "error",
    "error": "连接池错误信息"
}
```

## 使用方法

### 1. 手动测试
使用curl命令测试健康检查端点：

```bash
# 测试数据库连接
curl -s http://localhost:8000/api/common/health/database | python -m json.tool

# 测试连接池
curl -s http://localhost:8000/api/common/health/connection-pool | python -m json.tool
```

### 2. 集成监控
可以将这些端点集成到监控系统中，实现：
- 实时监控数据库连接状态
- 监控数据库响应时间
- 预警数据库连接问题

### 3. 故障排查
当出现数据库连接问题时，可以：
1. 首先检查健康检查端点状态
2. 根据返回的错误信息定位问题
3. 检查MySQL服务状态和配置

## 技术实现细节

### 文件结构
```
backend-fastapi-app/
├── app/
│   ├── dependencies/
│   │   └── database.py          # 优化的数据库连接配置
│   └── api/
│       └── common/
│           └── health.py        # 健康检查API端点
└── DATABASE_HEALTH_CHECK_README.md
```

### 关键特性

1. **连接预检**: 使用 `pool_pre_ping=True` 确保连接有效性
2. **连接回收**: 设置 `pool_recycle=3600` 避免MySQL wait_timeout问题
3. **超时控制**: 配置连接、读取、写入超时时间
4. **错误处理**: 提供清晰的错误信息和状态码
5. **性能监控**: 包含响应时间测量

## 配置参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| pool_size | 5 | 连接池大小 |
| max_overflow | 10 | 最大溢出连接数 |
| pool_recycle | 3600 | 连接回收时间(秒) |
| pool_timeout | 30 | 连接获取超时时间(秒) |
| connect_timeout | 15 | 连接建立超时时间(秒) |
| read_timeout | 30 | 读取操作超时时间(秒) |
| write_timeout | 30 | 写入操作超时时间(秒) |

## 故障排查指南

### 常见问题及解决方案

1. **数据库连接超时**
   - 检查MySQL服务是否运行
   - 验证数据库连接参数
   - 检查网络连接

2. **连接池耗尽**
   - 增加pool_size和max_overflow参数
   - 检查是否有连接泄漏
   - 优化数据库查询性能

3. **响应时间过长**
   - 检查数据库服务器负载
   - 优化数据库索引
   - 检查网络延迟

### 监控建议

建议在生产环境中：
- 定期调用健康检查端点
- 设置响应时间阈值告警
- 监控连接池使用情况
- 记录历史健康状态

## 版本历史

- v1.0.0: 初始版本，实现基础健康检查功能
- 优化数据库连接配置，解决连接丢失问题

## 联系方式

如有问题或建议，请联系系统管理员或开发团队。
