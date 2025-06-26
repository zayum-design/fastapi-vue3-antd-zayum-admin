from enum import Enum
from fastapi import HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY
)

from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_204_NO_CONTENT,
    HTTP_203_NON_AUTHORITATIVE_INFORMATION,
    HTTP_205_RESET_CONTENT,
    HTTP_206_PARTIAL_CONTENT
)

# 错误码枚举类，使用数字状态码与错误类型
class ErrorCode(Enum):
    OK = HTTP_200_OK
    BAD_REQUEST = HTTP_400_BAD_REQUEST
    NOT_FOUND = HTTP_404_NOT_FOUND
    INTERNAL_SERVER_ERROR = HTTP_500_INTERNAL_SERVER_ERROR
    UNAUTHORIZED = HTTP_401_UNAUTHORIZED
    FORBIDDEN = HTTP_403_FORBIDDEN
    CONFLICT = HTTP_409_CONFLICT
    UNPROCESSABLE_ENTITY = HTTP_422_UNPROCESSABLE_ENTITY
    DATABASE_ERROR = HTTP_500_INTERNAL_SERVER_ERROR

# 错误信息类，描述每个状态码的含义
class ErrorMessage(Enum):
    OK = "Request successful."
    BAD_REQUEST = "The request could not be understood or was missing required parameters."
    NOT_FOUND = "Resource not found."
    INTERNAL_SERVER_ERROR = "An unexpected error occurred on the server."
    UNAUTHORIZED = "Unauthorized access."
    FORBIDDEN = "Forbidden request."
    CONFLICT = "Request conflicts with the current state of the server."
    UNPROCESSABLE_ENTITY = "The request is well-formed but could not be followed due to semantic errors."
    DATABASE_ERROR = "Database operation failed."  # 新增数据库错误描述

# 统一的异常处理函数
def raise_error(error_code: ErrorCode):
    """
    Helper function to raise HTTPException with specific error code and message.
    """
    message = ErrorMessage[error_code.name].value
    raise HTTPException(status_code=error_code.value, detail={"error_code": error_code.name, "message": message})

 
# 成功状态码枚举类
class SuccessCode(Enum):
    OK = HTTP_200_OK
    CREATED = HTTP_201_CREATED
    ACCEPTED = HTTP_202_ACCEPTED
    NO_CONTENT = HTTP_204_NO_CONTENT
    NON_AUTHORITATIVE_INFORMATION = HTTP_203_NON_AUTHORITATIVE_INFORMATION
    RESET_CONTENT = HTTP_205_RESET_CONTENT
    PARTIAL_CONTENT = HTTP_206_PARTIAL_CONTENT

# 成功信息类，描述每个成功状态码的含义
class SuccessMessage(Enum):
    OK = "Request successful."
    CREATED = "Resource successfully created."
    ACCEPTED = "Request accepted for processing, but processing has not been completed."
    NO_CONTENT = "Request successfully processed, no response to send."
    NON_AUTHORITATIVE_INFORMATION = "Request successful, but information is from a third party."
    RESET_CONTENT = "Request successful, reset document view."
    PARTIAL_CONTENT = "Partial content returned."

# 统一的成功响应处理函数
def respond_with_success(status_code: SuccessCode, additional_data=None):
    """
    Helper function to return a success response with specific status code and message.
    Optionally includes additional data in the response.
    """
    message = SuccessMessage[status_code.name].value
    response = {"status_code": status_code.name, "message": message}
    if additional_data:
        response.update(additional_data)
    return response
