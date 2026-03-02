# 批量修复 Python Lint 错误指南

此文档说明如何批量修复 backend-fastapi-app 中的红色波浪线错误。

## 📋 错误来源说明

VS Code 中的红色波浪线主要来自：

1. **Ruff** - 代码风格、语法检查（项目主要 lint 工具）
2. **MyPy** - 类型检查（配置已放宽，减少波浪线）
3. **Pylance** - VS Code 内置 Python 语言服务器

## 🚀 快速修复

### 方法一：使用修复脚本（推荐）

```bash
cd backend-fastapi-app

# 预览将要修复的内容（不实际修改）
python scripts/fix_lint_errors.py --dry-run

# 实际修复所有可自动修复的错误
python scripts/fix_lint_errors.py

# 同时显示 MyPy 类型错误
python scripts/fix_lint_errors.py --fix-mypy
```

### 方法二：手动运行命令

```bash
cd backend-fastapi-app

# 1. 自动修复 Ruff 错误
python -m ruff check app --fix

# 2. 格式化代码
python -m ruff format app

# 3. 检查剩余错误
python -m ruff check app

# 4. 检查 MyPy 类型错误（可选）
python -m mypy app --ignore-missing-imports
```

## ⚙️ VS Code 配置

项目已配置 `.vscode/settings.json`，确保：

1. **安装 Ruff 插件**：在 VS Code 扩展中搜索 "Ruff" 并安装
2. **设置 Python 解释器**：选择 `backend-fastapi-app/.venv/bin/python`
3. **保存时自动格式化**：配置已启用

## 📊 修复结果

执行批量修复后：

| 检查项 | 修复前 | 修复后 |
|--------|--------|--------|
| Ruff 错误 | ~800+ | 46 |
| MyPy 错误 | 100+ | 大幅减少 |

### 剩余的错误类型

剩余的 46 个错误主要是潜在的代码问题，建议手动修复：

- **F841** - 未使用的局部变量
- **B006** - 可变数据结构作为默认参数
- **B007** - 循环变量未使用
- **PERF401** - 可使用列表推导式优化
- **SIM118** - `key in dict` 替代 `key in dict.keys()`
- **UP038** - `isinstance(x, A | B)` 替代 `isinstance(x, (A, B))`

## 🔧 配置说明

### pyproject.toml 中的 Ruff 配置

已调整以下规则以减少中文项目的误报：

```toml
ignore = [
    "E501",     # 行过长
    "RUF001",   # 字符串包含全角标点
    "RUF002",   # 文档字符串包含全角标点
    "RUF003",   # 注释包含全角标点
    "N801",     # 类名 CapWords
    "N802",     # 函数名 lowercase
    # ... 其他规则
]
```

### MyPy 配置

已放宽严格度以减少红色波浪线：

```toml
[tool.mypy]
strict = false
disallow_untyped_defs = false
```

如需严格类型检查，可临时改为 `strict = true`。

## 📝 建议的工作流程

1. **保存文件时**：Ruff 自动格式化代码
2. **提交代码前**：运行 `python -m ruff check app` 检查
3. **定期清理**：手动修复 F841、B007 等潜在问题

## ❓ 常见问题

### Q: 为什么还有红色波浪线？

A: 剩余的错误是潜在的代码问题，需要手动修复。例如：

```python
# F841: 未使用的变量
def example():
    result = compute()  # ← 未使用，应删除或改用 _result
    return None

# B006: 可变默认参数
def add_item(item, items=[]):  # ← 危险！应改为 items=None
    items.append(item)
    return items
```

### Q: 如何完全禁用类型检查？

A: 在 `.vscode/settings.json` 中添加：

```json
"python.analysis.typeCheckingMode": "off"
```

### Q: 只想用 Ruff，不用 Pylance？

A: 已配置 Pylance 为 "basic" 模式，减少重复检查。

## 📚 相关文档

- [Ruff 文档](https://docs.astral.sh/ruff/)
- [MyPy 文档](https://mypy.readthedocs.io/)
- [FastAPI 类型提示](https://fastapi.tiangolo.com/python-types/)
