"""
全局异常处理器
"""

import pymysql
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions import BusinessException
from app.utils.log_utils import logger


def format_response(
    code: int, message: str, data: dict = {}, status_code: int = 200
) -> JSONResponse:
    """统一响应格式"""
    from datetime import datetime

    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "msg": message,
            "data": data if data is not None else {},
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    )


async def business_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """业务异常处理器"""
    be = exc  # type: BusinessException
    logger.warning(
        f"Business exception: {be.message}",
        extra={"code": be.code, "path": request.url.path, "method": request.method},
    )
    return format_response(
        code=be.code, message=be.message, data=be.data, status_code=be.status_code
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """请求验证错误处理器"""
    ve = exc  # type: RequestValidationError
    errors = ve.errors()

    # 格式化错误信息
    formatted_errors = []
    for error in errors:
        msg = error.get("msg", "")
        # 移除 "Value error, " 前缀
        if msg.startswith("Value error, "):
            msg = msg[13:]
        formatted_errors.append(
            {"field": ".".join(str(x) for x in error.get("loc", [])), "message": msg}
        )

    logger.warning(
        f"Validation error: {formatted_errors}",
        extra={"path": request.url.path, "method": request.method},
    )

    return format_response(
        code=1001, message="Validation error", data={"errors": formatted_errors}, status_code=400
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """HTTP 异常处理器"""
    he = exc  # type: StarletteHTTPException
    if he.status_code == 404:
        logger.info("Resource not found: {request.url.path}")
        return format_response(
            code=1004,
            message="Resource not found",
            data={"path": request.url.path},
            status_code=404,
        )

    logger.warning(
        f"HTTP exception {he.status_code}: {he.detail}",
        extra={"path": request.url.path, "method": request.method},
    )

    return format_response(code=he.status_code, message=str(he.detail), status_code=he.status_code)


async def value_error_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """ValueError 处理器"""
    logger.warning(
        f"Value error: {exc!s}", extra={"path": request.url.path, "method": request.method}
    )
    return format_response(code=1001, message=str(exc), status_code=400)


async def integrity_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """数据库完整性错误处理器"""
    ie = exc  # type: IntegrityError
    if isinstance(ie.orig, pymysql.MySQLError):
        error_msg = str(ie.orig.args[1]) if ie.orig.args else "Database integrity error"
        error_code = ie.orig.args[0] if ie.orig.args else 500
    else:
        error_msg = "Database integrity error"
        error_code = 500

    logger.error(
        f"Database integrity error: {error_msg}",
        extra={"path": request.url.path, "method": request.method, "db_code": error_code},
        exc_info=True,
    )

    return format_response(
        code=1005,
        message="Data conflict",
        data={"errors": [error_msg], "db_code": error_code},
        status_code=409,
    )


async def operational_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """数据库操作错误处理器"""
    oe = exc  # type: OperationalError
    error_detail = str(oe.orig) if isinstance(oe.orig, pymysql.MySQLError) else "Database Error"

    logger.error(
        f"Database operational error: {error_detail}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=True,
    )

    return format_response(
        code=1006, message="Database error", data={"errors": [error_detail]}, status_code=500
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器（兜底）"""
    # 避免处理已经被处理的异常类型
    if isinstance(exc, (BusinessException, StarletteHTTPException, RequestValidationError)):
        raise exc

    logger.error(
        f"Unhandled exception: {exc!s}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=True,
    )

    # 根据异常类型返回不同响应
    if isinstance(exc, AttributeError):
        return format_response(
            code=1001,
            message="Invalid attribute access",
            data={"errors": [str(exc)]},
            status_code=400,
        )

    return format_response(
        code=500,
        message="Internal server error",
        data={"errors": [str(exc)] if str(exc) else ["An unexpected error occurred"]},
        status_code=500,
    )
