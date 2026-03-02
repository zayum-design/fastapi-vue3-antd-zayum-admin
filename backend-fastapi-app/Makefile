# =============================================================================
# FastAPI 项目 Makefile
# =============================================================================
# 提供便捷的测试和开发命令
# =============================================================================

.PHONY: help test test-unit test-integration test-e2e test-coverage lint format clean

# 默认目标
help:
	@echo "FastAPI 项目管理命令"
	@echo ""
	@echo "测试命令:"
	@echo "  make test              运行所有测试"
	@echo "  make test-unit         运行单元测试"
	@echo "  make test-integration  运行集成测试"
	@echo "  make test-e2e          运行端到端测试"
	@echo "  make test-coverage     运行测试并生成覆盖率报告"
	@echo ""
	@echo "代码质量:"
	@echo "  make lint              运行代码检查"
	@echo "  make format            格式化代码"
	@echo ""
	@echo "其他:"
	@echo "  make clean             清理缓存文件"
	@echo "  make install-dev       安装开发依赖"

# 测试命令
test:
	pytest tests/ -v --tb=short

test-unit:
	pytest tests/unit -v -m unit --tb=short

test-integration:
	pytest tests/integration -v -m integration --tb=short

test-e2e:
	pytest tests/e2e -v -m e2e --tb=short

test-coverage:
	pytest tests/ --cov=app --cov-report=term-missing --cov-report=html:htmlcov --cov-report=xml:coverage.xml -v

# 代码质量命令
lint:
	flake8 app/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 app/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	black app/ tests/
	isort app/ tests/

# 格式化检查
check-format:
	black --check --diff app/ tests/
	isort --check-only --diff app/ tests/

# 清理命令
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage coverage.xml test-results.xml
	rm -rf htmlcov/

# 安装开发依赖
install-dev:
	pip install pytest pytest-asyncio pytest-cov httpx
	pip install black isort flake8

# 运行特定模块的测试
test-auth:
	pytest tests/ -v -m auth --tb=short

test-security:
	pytest tests/ -v -m security --tb=short

# 持续监视测试
watch:
	ptw tests/ -- -v

# 生成测试报告
report:
	pytest tests/ --html=report.html --self-contained-html -v
