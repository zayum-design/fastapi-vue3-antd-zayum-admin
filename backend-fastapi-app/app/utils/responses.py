from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi_babel import _
from app.utils.response_handlers import ErrorCode,ErrorMessage
from app.utils.log_utils import logger

def get_current_time(): 
    """
    获取当前时间的字符串格式。
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def success_response(data, msg="Success"):
    """
    格式化成功响应。
    :param data: 返回的数据
    :param msg: 可选的成功消息，默认为"Success"
    :return: 格式化后的响应字典
    """
    return {
        "code": 0,
        "msg": msg,
        "data": data,
        "time": get_current_time()
    }

def error_response(
    error_code: ErrorCode, 
    message: str = "An unexpected error occurred on the server.", 
    data: Optional[dict] = None, 
    e: Exception = None
):
    """
    格式化错误响应。
    :param error_code: 错误码
    :param message: 自定义错误消息，如果未提供，则使用默认消息
    :param data: 额外的错误数据
    :param e: 异常信息，仅用于日志记录
    :return: FastAPI JSONResponse 对象
    """
    if message is None:
        # 如果未提供自定义消息，使用默认的错误消息
        message = ErrorMessage[error_code.name].value

    # 这里使用 error_code.name 来取值
    error = ErrorMessage[error_code.name].value

    if e:
        # 仅在日志中记录详细的异常信息，不在响应中包含
        error += f" | {str(e)}"
    
    return JSONResponse(
        status_code=error_code.value,
        content={
            "code": 0,
            "msg": message,
            "data": data if data is not None else {},
            "time": get_current_time()
        }
    )



def not_authenticated_response():
    """
    未认证时的统一响应。
    :return: 格式化的未认证响应字典
    """
    return {
        "code": 0,
        "msg": "Not authenticated",
        "data": {},
        "time": get_current_time(),
    }
