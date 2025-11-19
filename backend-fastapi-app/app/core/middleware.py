# backend-fastapi-app/app/core/middleware.py

import json
from typing import Callable, Awaitable
from fastapi import Request, HTTPException
from requests import Session
from starlette.middleware.base import BaseHTTPMiddleware
from app.crud.sys_admin_log import crud_sys_admin_log
from app.schemas.sys_admin_log import SysAdminLogCreate
from app.core.security import get_current_admin
from app.dependencies.database import get_db

def filter_sensitive_data(data: dict) -> dict:
    """递归过滤敏感数据"""
    if isinstance(data, dict):
        return {k: ('*' if 'password' in k.lower() else filter_sensitive_data(v)) for k, v in data.items()}
    elif isinstance(data, list):
        return [filter_sensitive_data(item) for item in data]
    return data

class AdminLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable]):
        admin = None
        auth_header = request.headers.get("authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer "):]
            db = next(get_db())
            try:
                admin = get_current_admin(token=token, db=db)
                if not admin:
                    raise HTTPException(status_code=401, detail="Invalid credentials")
                request.state.admin = admin  # 存入 request 状态
            except Exception as e:
                print(f"Error in auth: {e}")
                raise e
            finally:
                db.close()
        
        # 仅记录 POST、PUT、DELETE 请求日志，并排除日志删除接口和文件上传接口
        if (request.method in {"POST", "PUT", "DELETE"} and 
            not request.url.path.startswith("/api/admin/admin/log/delete/") and 
            not request.url.path.startswith("/api/admin/auth") and
            not request.url.path.startswith("/api/admin/upload")):
            try:
                body_bytes = await request.body()
                body_text = body_bytes.decode() if body_bytes else ""
                params = json.loads(body_text) if body_text else {}
            except (json.JSONDecodeError, UnicodeDecodeError):
                params = {}

            filtered_params = filter_sensitive_data(params)
            admin_obj = getattr(request.state, "admin", None)
            admin_id = admin_obj.id if admin_obj else 1
            username = admin_obj.username if admin_obj else "unknown"
            
            log_data = SysAdminLogCreate(
                id=None,  # id 是可选的，设为 None
                admin_id=admin_id,
                username=username,
                url=str(request.url),
                title=request.method,
                content=json.dumps(filtered_params, ensure_ascii=False),
                useragent=request.headers.get("user-agent", ""),  
                ip=request.client.host if request.client else "",
            )

            db = next(get_db())
            try:
                crud_sys_admin_log.create(db, log_data)
            except Exception as e:
                print(f"Error in log creation: {e}")
                raise e
            finally:
                db.close()

        response = await call_next(request)
        return response
