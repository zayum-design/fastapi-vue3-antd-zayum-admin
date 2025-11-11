# backend-fastapi-app/app/core/handlers.py

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import OperationalError, IntegrityError
from fastapi.responses import JSONResponse
import pymysql
from fastapi_babel import _
from app.utils.responses import error_response
from app.utils.response_handlers import ErrorCode
from app.utils.log_utils import logger

async def validation_exception_handler(request: Request, exc: Exception):
    if not isinstance(exc, RequestValidationError):
        # 如果不是RequestValidationError，让其他处理器处理
        raise exc
    
    errors = exc.errors()
    logger.error(f"Request validation error: {errors}")
    
    prefixes_to_remove = ["Value error, "]
    
    def clean_message(msg: str) -> str:
        for prefix in prefixes_to_remove:
            if msg.startswith(prefix):
                return msg[len(prefix):]
        return msg
    
    formatted_errors = [
        {"message": clean_message(error['msg'])}
        for error in errors
    ]
    
    return error_response(
        ErrorCode.BAD_REQUEST,
        message="Validation error",
        data={"errors": formatted_errors}
    )

async def http_exception_handler(request: Request, exc: Exception):
    if not isinstance(exc, StarletteHTTPException):
        # 如果不是HTTPException，让其他处理器处理
        raise exc
    
    if exc.status_code == 404:
        return error_response(
            ErrorCode.NOT_FOUND,
            message="Resource not found",
            data={"errors": [f"Route {request.url.path} does not exist"]}
        )
    
    error_code = next((code for code in ErrorCode if code.value == exc.status_code), None)
    logger.error(f"HTTP exception occurred error_code: {error_code}")
    
    if error_code is None:
        error_code = ErrorCode.INTERNAL_SERVER_ERROR
        logger.error(f"HTTP exception occurred: {exc.detail}", exc_info=True)
    
    return error_response(
        error_code,
        message="HTTP Error Occurred",
        data={"errors": [exc.detail] if isinstance(exc.detail, str) else exc.detail}
    )

async def value_error_exception_handler(request: Request, exc: Exception):
    if not isinstance(exc, ValueError):
        # 如果不是ValueError，让其他处理器处理
        raise exc
    
    logger.error(f"ValueError: {str(exc)}", exc_info=True)
    return error_response(ErrorCode.BAD_REQUEST, message="Value error", data={"errors": [str(exc)]})

async def generic_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, StarletteHTTPException):
        raise exc
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    if isinstance(exc, AttributeError):
        return error_response(
            ErrorCode.BAD_REQUEST,
            message="Invalid attribute access",
            data={"errors": [str(exc)]}
        )
    return error_response(
        ErrorCode.INTERNAL_SERVER_ERROR,
        message="Internal Server Error",
        data={"errors": [str(exc)]}
    )

async def integrity_error_handler(request: Request, exc: Exception):
    if not isinstance(exc, IntegrityError):
        # 如果不是IntegrityError，让其他处理器处理
        raise exc
    
    if isinstance(exc.orig, pymysql.MySQLError):
        error_msg = str(exc.orig.args[1]) if exc.orig.args else 'Database integrity error'
        error_code = exc.orig.args[0] if exc.orig.args else 500
    else:
        error_msg = 'Database integrity error'
        error_code = 500
        
    return error_response(
        ErrorCode.DATABASE_ERROR,
        message="Data conflict",
        data={
            "errors": [error_msg],
            "code": error_code
        }
    )

async def operational_error_handler(request: Request, exc: Exception):
    if not isinstance(exc, OperationalError):
        # 如果不是OperationalError，让其他处理器处理
        raise exc
    
    error_detail = str(exc.orig) if isinstance(exc.orig, pymysql.MySQLError) else 'Database Error'
    return error_response(
        ErrorCode.DATABASE_ERROR,
        message="Database Error",
        data={"errors": [error_detail]}
    )
