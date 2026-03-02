"""
代码生成器类型定义
"""

from typing import List
from pydantic import BaseModel


class FieldInfo(BaseModel):
    """字段信息"""
    name: str
    type: str


class CodeGeneration(BaseModel):
    """代码生成结果"""
    field_info: List[FieldInfo]
    model_code: str
    crud_code: str
    schemas_code: str
    api_code: str
    vue_code: str
    vue_i18n_json: str


class CodeGenerationResponse(BaseModel):
    """代码生成响应"""
    code: int
    msg: str
    data: CodeGeneration
    time: str


class TablesResponse(BaseModel):
    """数据库表列表响应"""
    code: int
    msg: str
    data: List[str]
    time: str
