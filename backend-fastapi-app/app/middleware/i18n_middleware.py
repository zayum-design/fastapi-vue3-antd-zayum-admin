# app/middleware/i18n_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi_babel import Babel
from app.utils.log_utils import logger

class I18nMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, babel: Babel):
        super().__init__(app)
        self.babel = babel

    async def dispatch(self, request: Request, call_next):
        # 从请求头中获取 'Accept-Language'
        accept_language = request.headers.get('Accept-Language', self.babel.config.BABEL_DEFAULT_LOCALE)
        
        # 设置当前的语言环境
        self.babel.locale = accept_language
        logger.info(f"Locale set to {accept_language} for request {request.url}")
        
        # 继续处理请求
        response = await call_next(request)
        return response
