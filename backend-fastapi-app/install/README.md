# 安装模块文档

## 概述

`backend-fastapi-app/install` 文件夹包含了系统安装所需的所有脚本和模块。这些文件负责处理系统的初始安装过程，包括数据库连接测试、数据导入、安装状态检查等功能。

## 文件结构

```
install/
├── __init__.py              # 模块初始化文件
├── initialize_db.py         # 数据库初始化脚本
├── install_check.py         # 安装检查接口
├── install.py               # 安装模块主文件
├── generated/               # 生成的安装文件
│   ├── __init__.py
│   ├── import_data.py      # 导入模型数据脚本
│   ├── install_data.py     # 分步导入数据脚本
│   └── install_20251130.sql # MySQL安装SQL脚本
└── module/                  # 模块目录（当前为空）
```

## 各文件功能说明

### 1. initialize_db.py

**功能**：数据库初始化脚本，用于导出现有数据库中的数据并生成各种格式的安装脚本。

**主要函数**：

- `get_sys_models()` - 获取所有以 `sys_` 开头的模型类
- `export_alembic_migration_data()` - 生成 Alembic 数据迁移脚本
- `export_model_data_as_python_script()` - 导出模型数据为 Python 脚本
- `export_mysql_data_script()` - 导出 MySQL 数据插入脚本（包含表结构创建）
- `export_step_install_data_script()` - 导出分步导入数据脚本

**使用方法**：
```bash
# 在项目根目录运行
cd backend-fastapi-app
python -m install.initialize_db
```

**输出文件**：
- `alembic/versions/auto_insert_data.py` - Alembic 迁移脚本
- `install/generated/import_data.py` - Python 导入脚本
- `install/generated/install_data.py` - 分步导入脚本
- `install/generated/install_YYYYMMDD.sql` - MySQL SQL 脚本

### 2. install_check.py

**功能**：安装检查接口，用于检查系统是否已经安装。

**API 端点**：
- `POST /install_check` - 检查安装锁定文件是否存在

**返回格式**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "installed": true/false
  }
}
```

**工作原理**：检查 `backend-fastapi-app/install.lock` 文件是否存在，如果存在则表示系统已安装。

### 3. install.py

**功能**：安装模块主文件，包含完整的安装流程API。

**API 端点**：

#### 3.1 数据库连接测试
- `POST /test-db` - 测试数据库连接

**请求体**：
```json
{
  "host": "localhost",
  "port": 3306,
  "username": "root",
  "password": "password",
  "database": "zayum_admin"
}
```

**功能**：测试数据库连接是否正常，如果成功则更新 `.env` 文件中的数据库配置。

#### 3.2 数据导入
- `POST /import-db` - 导入数据库数据

**请求体**：
```json
{
  "current_table": "sys_admin",
  "import_options": []
}
```

**导入顺序**：
1. sys_admin - 系统管理员表
2. sys_user_balance_log - 用户余额日志表
3. sys_attachment - 附件表
4. sys_general_category - 通用分类表
5. sys_admin_rule - 管理员规则表
6. sys_admin_log - 管理员日志表
7. sys_user_rule - 用户规则表
8. sys_admin_group - 管理员组表
9. sys_plugin - 插件表
10. sys_user - 用户表
11. sys_user_score_log - 用户积分日志表
12. sys_attachment_category - 附件分类表
13. sys_user_group - 用户组表
14. sys_general_config - 通用配置表

**工作原理**：按照预定义顺序逐个导入表数据，支持断点续传。

#### 3.3 安装完成
- `POST /complete` - 完成系统安装

**请求体**：
```json
{
  "username": "admin",
  "password": "admin123",
  "email": "admin@example.com",
  "mobile": "13800138000",
  "nickname": "系统管理员"
}
```

**功能**：创建初始管理员账户并创建安装锁定文件。

#### 3.4 重启服务
- `POST /restart` - 重启 FastAPI 服务

**功能**：通过 Supervisor 重启 FastAPI 服务以应用新的配置。

### 4. generated/ 文件夹

#### 4.1 import_data.py
**功能**：导入模型数据脚本，不依赖 Alembic，可以直接执行导入数据。

**使用方法**：
```bash
cd backend-fastapi-app
python -m install.generated.import_data
```

#### 4.2 install_data.py
**功能**：分步导入数据脚本，每个模型一个导入函数，包含表存在检查和自动创建功能。

**使用方法**：
```bash
cd backend-fastapi-app
python -m install.generated.install_data
```

#### 4.3 install_20251130.sql
**功能**：MySQL 数据库安装脚本，包含完整的表结构和初始数据。

**使用方法**：
```sql
-- 在 MySQL 中执行
source backend-fastapi-app/install/generated/install_20251130.sql
```

## 安装流程

### 步骤 1：准备环境
1. 确保 MySQL 数据库服务已启动
2. 创建空数据库（如 `zayum_admin`）
3. 复制 `.env.example` 为 `.env` 并配置基本参数

### 步骤 2：运行安装脚本
1. 生成安装数据文件（如果需要）：
   ```bash
   cd backend-fastapi-app
   python -m install.initialize_db
   ```

2. 启动 FastAPI 服务：
   ```bash
   python -m app.main
   ```

### 步骤 3：通过 API 安装
1. **测试数据库连接**：
   ```bash
   curl -X POST http://localhost:8000/api/install/test-db \
     -H "Content-Type: application/json" \
     -d '{
       "host": "localhost",
       "port": 3306,
       "username": "root",
       "password": "password",
       "database": "zayum_admin"
     }'
   ```

2. **导入数据库数据**：
   ```bash
   # 开始导入
   curl -X POST http://localhost:8000/api/install/import-db \
     -H "Content-Type: application/json" \
     -d '{"current_table": null}'
   
   # 继续导入（根据返回的 next_table 参数）
   curl -X POST http://localhost:8000/api/install/import-db \
     -H "Content-Type: application/json" \
     -d '{"current_table": "sys_admin"}'
   ```

3. **完成安装**：
   ```bash
   curl -X POST http://localhost:8000/api/install/complete \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "password": "admin123",
       "email": "admin@example.com",
       "mobile": "13800138000",
       "nickname": "系统管理员"
     }'
   ```

### 步骤 4：验证安装
1. 检查安装状态：
   ```bash
   curl -X POST http://localhost:8000/api/install/install-check
   ```

2. 使用创建的管理员账户登录系统。

## 注意事项

1. **数据库权限**：确保数据库用户有创建表、插入数据等权限。
2. **环境配置**：安装前需要正确配置 `.env` 文件。
3. **安装锁定**：安装完成后会创建 `install.lock` 文件，防止重复安装。
4. **数据安全**：安装过程中创建的管理员账户密码应妥善保管。
5. **错误处理**：如果安装过程中出现错误，查看日志文件获取详细错误信息。

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 MySQL 服务是否运行
   - 验证数据库连接参数是否正确
   - 检查防火墙设置

2. **数据导入失败**
   - 检查数据库表是否已存在冲突数据
   - 查看生成的安装脚本是否正确
   - 检查数据库字符集设置（推荐使用 utf8mb4）

3. **安装锁定文件问题**
   - 如果需要重新安装，删除 `install.lock` 文件
   - 确保有权限创建和写入文件

### 日志查看
安装过程中的日志会输出到控制台，也可以通过查看应用日志文件获取详细信息。

## 开发说明

### 添加新的系统表
如果需要添加新的系统表到安装流程中：

1. 在 `app/models/` 目录下创建新的模型文件
2. 在 `install.py` 的 `IMPORT_ORDER` 列表中添加表名
3. 在 `IMPORT_FUNCTIONS` 字典中添加对应的导入函数
4. 重新生成安装数据文件：
   ```bash
   python -m install.initialize_db
   ```

### 自定义安装流程
可以通过修改 `install.py` 中的 API 端点和逻辑来自定义安装流程。

## 版本历史

- v1.0.0：初始版本，包含完整的安装功能
- v1.0.1：修复数据库连接测试问题
- v1.0.2：优化数据导入流程，支持断点续传

## 联系支持

如果在安装过程中遇到问题，请查看项目文档或联系技术支持。

---

*最后更新：2026年1月22日*
