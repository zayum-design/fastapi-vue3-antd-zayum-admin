# FastAPI 测试文档

## 测试框架
本项目使用pytest作为测试框架，配合FastAPI的TestClient进行接口测试。

## 测试文件结构
测试文件位于`backend-fastapi-app/tests/`目录下，按照功能模块划分：
- `test_admin*.py`: 管理员相关接口测试
- `test_user*.py`: 用户相关接口测试  
- `test_*.py`: 其他功能模块测试
- `conftest.py`: 测试公共配置

## 运行测试

### 运行全部测试
```bash
pytest --cache-clear -v -p no:warnings
```

### 运行特定模块测试
```bash
pytest tests/test_user.py -v -p no:warnings
```

### 生成测试覆盖率报告
```bash
pytest --cov=app --cov-report=html
```

## 测试编写规范

1. 每个测试文件对应一个功能模块
2. 测试类/函数命名格式：`test_<功能>_<场景>`
3. 测试文件应包含：
   - 必要的fixture（测试客户端、数据库会话等）
   - 测试数据生成函数
   - 标准CRUD测试用例
   - 边界条件测试

## 测试覆盖率要求
- 接口测试覆盖率 ≥ 90%
- 核心业务逻辑覆盖率 ≥ 95%

## 常用断言方法
- `assert response.status_code == 200`
- `assert "data" in response.json()`
- `assert db_obj is not None`

## 注意事项
1. 测试数据使用随机值避免冲突
2. 每个测试用例后回滚数据库变更
3. 测试文件按功能模块组织
4. 使用`-p no:warnings`参数忽略警告信息
