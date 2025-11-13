"""
FastAPI 应用主入口
模块化重构版本 - 简化代码结构
"""
from fastapi.responses import HTMLResponse

from app.core.application import create_fastapi_app, configure_middleware, configure_exception_handlers
from app.core.environment import is_application_installed
from app.core.lifespan import lifespan
from app.core.swagger import get_custom_swagger_ui

# 创建 FastAPI 应用实例（包含生命周期管理）
app = create_fastapi_app(lifespan=lifespan)

# 检查应用是否已安装
is_installed = is_application_installed()

# 配置中间件
configure_middleware(app, is_installed=is_installed)

# 配置异常处理器
configure_exception_handlers(app)

# 自定义 Swagger UI 路由，使用多重 CDN 备用方案
@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def custom_swagger_ui():
    """自定义 Swagger UI 页面，使用多重 CDN 备用方案确保可用性"""
    return get_custom_swagger_ui()
