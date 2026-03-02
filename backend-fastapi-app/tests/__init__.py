"""
FastAPI 项目测试包

本包包含项目的所有测试代码，包括：
- 单元测试 (unit/): 测试独立的函数和类
- 集成测试 (integration/): 测试 API 端点和数据库交互
- 端到端测试 (e2e/): 测试完整业务流程
- 测试固件 (fixtures/): 测试数据和辅助工具

运行测试：
    pytest                        # 运行所有测试
    pytest -m unit               # 仅运行单元测试
    pytest -m integration        # 仅运行集成测试
    pytest -v --tb=short         # 详细输出，简短错误追踪
    pytest --cov=app             # 带覆盖率报告
"""
