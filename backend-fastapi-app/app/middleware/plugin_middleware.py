from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.models.sys_plugin import SysPlugin
from fastapi import Depends
from app.utils.log_utils import logger
from app.core.config import settings
class PluginMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, get_db):
        super().__init__(app)

        self.get_db = get_db

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path.startswith("/api/v1/plugins/"):
            return await call_next(request)

        # 检查是否请求的是某个插件的路由
        parts = path.strip("/").split("/")
        arrow_routes = settings.ARROW_ROUTES
        if len(parts) >= 2 and parts[0] == "api" and parts[1] == "v1":
            if len(parts) >= 3 and parts[2] in arrow_routes:
                # 非插件路由，不处理
                return await call_next(request)
            if len(parts) >= 4:
                plugin_uuid = parts[2]
                # 检查插件是否启用
                async with self.get_db() as db:
                    plugin = db.query(SysPlugin).filter(SysPlugin.uuid == plugin_uuid).first()
                    if not plugin or not plugin.enabled:
                        return JSONResponse(status_code=404, content={"detail": "Plugin not found or not enabled."})
        return await call_next(request)
