"""
Schema代码生成器
生成Pydantic Schema代码
"""

from sqlalchemy import Table
from sqlalchemy.types import BOOLEAN, INTEGER, SMALLINT, VARCHAR, DATE, DATETIME, DECIMAL, JSON, TEXT
from sqlalchemy import Enum as SqlEnum


class SchemasGenerator:
    """Schema代码生成器类"""
    
    def generate(self, table: Table) -> str:
        """生成Schema代码"""
        class_name = "".join(word.capitalize() for word in table.name.split("_"))
        
        # 构建Schema代码
        schemas_code = f'''"""
{table.name} 表的Schema定义
"""

from typing import Optional
from pydantic import BaseModel
from datetime import date, datetime


class {class_name}Base(BaseModel):
    """{class_name}基础Schema"""
'''
        
        # 添加字段定义
        for col in table.columns:
            if col.name.lower() in ["created_at", "updated_at"]:
                continue
                
            col_type = col.type
            nullable = col.nullable
            
            # 确定Python类型
            if isinstance(col_type, SqlEnum):
                py_type = "str"
            elif isinstance(col_type, BOOLEAN):
                py_type = "bool"
            elif isinstance(col_type, (INTEGER, SMALLINT)):
                py_type = "int"
            elif isinstance(col_type, (VARCHAR, TEXT)):
                py_type = "str"
            elif isinstance(col_type, DATE):
                py_type = "date"
            elif isinstance(col_type, DATETIME):
                py_type = "datetime"
            elif isinstance(col_type, DECIMAL):
                py_type = "float"
            elif isinstance(col_type, JSON):
                py_type = "dict"
            else:
                py_type = "str"
            
            # 处理可空性
            if nullable:
                field_type = f"Optional[{py_type}] = None"
            else:
                field_type = py_type
            
            schemas_code += f"    {col.name}: {field_type}\n"
        
        # 创建Schema
        schemas_code += f'''

class {class_name}Create({class_name}Base):
    """创建{class_name}的Schema"""
    pass


class {class_name}Update({class_name}Base):
    """更新{class_name}的Schema"""
    pass


class {class_name}InDB({class_name}Base):
    """数据库中的{class_name} Schema"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
'''
        return schemas_code
