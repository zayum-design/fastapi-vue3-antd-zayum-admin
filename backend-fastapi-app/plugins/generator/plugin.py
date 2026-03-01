"""
代码生成器插件主文件
提供数据库表到代码的自动生成功能
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.dependencies.database import get_db
from app.core.security import get_current_admin
from app.utils.responses import success_response
from app.utils.log_utils import logger

from .services.code_generation_service import CodeGenerationService
from .core.types import TablesResponse, CodeGenerationResponse


# 初始化路由和服务
router = APIRouter(tags=["generator"], dependencies=[Depends(get_current_admin)])
code_generation_service = CodeGenerationService()

# 创建表的请求模型
class TableFieldCreate(BaseModel):
    name: str
    type: str
    length: Optional[str] = None
    nullable: bool = True
    primaryKey: bool = False
    autoIncrement: bool = False
    defaultValue: Optional[str] = None
    comment: Optional[str] = None

class TableCreateRequest(BaseModel):
    table_name: str
    database_type: str = "mysql"
    table_comment: Optional[str] = None
    fields: List[TableFieldCreate]

class TableCreateResponse(BaseModel):
    code: int
    msg: str
    data: Optional[str] = None
    time: str

@router.get("/", tags=["generator"])
def read_generator():
    """代码生成器主页"""
    return {"message": "代码生成器插件"}


@router.get("/tables", tags=["generator"], response_model=TablesResponse)
def get_tables(db: Session = Depends(get_db)):
    """
    获取数据库中的所有表名
    
    Returns:
        TablesResponse: 包含表名列表的响应
    """
    try:
        tables = code_generation_service.get_tables()
        return success_response(tables)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取表列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取表列表失败: {str(e)}",
        )


@router.get(
    "/code/{table_name}", tags=["generator"], response_model=CodeGenerationResponse
)
def generate_code(
    table_name: str,
    fields: str = 'all',
    operations: str = 'create,read,update,delete',
    db: Session = Depends(get_db)
) -> CodeGenerationResponse:
    """
    为指定表生成代码
    
    Args:
        table_name (str): 表名
        fields (str): 字段选择，默认为'all'
        operations (str): 操作类型，默认为'create,read,update,delete'
        db (Session): 数据库会话
        
    Returns:
        CodeGenerationResponse: 包含生成代码的响应
    """
    try:
        return code_generation_service.generate_code(table_name, fields, operations)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"为表 {table_name} 生成代码失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"为表 {table_name} 生成代码失败: {str(e)}",
        )


@router.post("/create-table", tags=["generator"], response_model=TableCreateResponse)
def create_table(
    request: TableCreateRequest,
    db: Session = Depends(get_db)
) -> TableCreateResponse:
    """
    创建数据库表
    
    Args:
        request (TableCreateRequest): 创建表的请求数据
        db (Session): 数据库会话
        
    Returns:
        TableCreateResponse: 创建表的响应
    """
    try:
        # 检查表是否已存在
        existing_tables = code_generation_service.get_tables()
        if request.table_name in existing_tables:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"表 '{request.table_name}' 已存在"
            )
        
        # 根据数据库类型生成SQL
        sql = ""
        if request.database_type == "mysql":
            sql = _generate_mysql_sql(request.table_name, request.table_comment, request.fields)
        elif request.database_type == "postgresql":
            sql = _generate_postgresql_sql(request.table_name, request.table_comment, request.fields)
        elif request.database_type == "sqlite":
            sql = _generate_sqlite_sql(request.table_name, request.table_comment, request.fields)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的数据库类型: {request.database_type}"
            )
        
        # 执行SQL创建表
        logger.info(f"创建表SQL: {sql}")
        
        try:
            # 执行SQL语句
            from sqlalchemy import text
            db.execute(text(sql))
            db.commit()
            
            # 验证表是否创建成功
            from sqlalchemy import inspect
            from app.dependencies.database import engine
            
            # 使用全局的engine而不是db.bind
            inspector = inspect(engine)
            created_tables = inspector.get_table_names()
            
            if request.table_name in created_tables:
                logger.info(f"表 '{request.table_name}' 创建成功")
                response = success_response(f"表 '{request.table_name}' 创建成功")
                return TableCreateResponse(**response)
            else:
                logger.error(f"表 '{request.table_name}' 创建失败，表未出现在数据库列表中")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"表 '{request.table_name}' 创建失败，请检查数据库权限和SQL语法"
                )
                
        except Exception as sql_error:
            db.rollback()
            logger.error(f"执行SQL失败: {str(sql_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"执行SQL失败: {str(sql_error)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建表失败: {str(e)}",
        )

def _generate_mysql_sql(table_name: str, table_comment: Optional[str], fields: List[TableFieldCreate]) -> str:
    """生成MySQL创建表SQL"""
    sql = f"CREATE TABLE `{table_name}` (\n"
    
    field_definitions = []
    for field in fields:
        definition = f"  `{field.name}` {field.type.upper()}"
        
        # 添加长度（如果适用）
        if field.length and (field.type.lower() in ['varchar', 'decimal', 'float', 'double']):
            definition += f"({field.length})"
        
        # 添加NOT NULL
        if not field.nullable:
            definition += " NOT NULL"
        
        # 添加自增
        if field.autoIncrement:
            definition += " AUTO_INCREMENT"
        
        # 添加默认值
        if field.defaultValue:
            if field.type.lower() in ['varchar', 'text', 'datetime', 'timestamp']:
                definition += f" DEFAULT '{field.defaultValue}'"
            else:
                definition += f" DEFAULT {field.defaultValue}"
        
        # 添加注释
        if field.comment:
            definition += f" COMMENT '{field.comment}'"
        
        field_definitions.append(definition)
    
    sql += ",\n".join(field_definitions)
    
    # 添加主键
    primary_keys = [field.name for field in fields if field.primaryKey]
    if primary_keys:
        sql += f",\n  PRIMARY KEY (`{'`, `'.join(primary_keys)}`)"
    
    sql += "\n)"
    
    # 添加表注释
    if table_comment:
        sql += f" COMMENT='{table_comment}'"
    
    sql += ";\n"
    
    return sql

def _generate_postgresql_sql(table_name: str, table_comment: Optional[str], fields: List[TableFieldCreate]) -> str:
    """生成PostgreSQL创建表SQL"""
    sql = f'CREATE TABLE "{table_name}" (\n'
    
    field_definitions = []
    for field in fields:
        definition = f'  "{field.name}" {field.type}'
        
        # 添加长度（如果适用）
        if field.length and (field.type.lower() in ['varchar', 'numeric']):
            definition += f"({field.length})"
        
        # 添加NOT NULL
        if not field.nullable:
            definition += " NOT NULL"
        
        # 添加自增（PostgreSQL使用SERIAL）
        if field.autoIncrement and field.type.lower() == 'integer':
            definition = f'  "{field.name}" SERIAL'
            if not field.nullable:
                definition += " NOT NULL"
        
        # 添加默认值
        if field.defaultValue:
            if field.type.lower() in ['varchar', 'text', 'timestamp']:
                definition += f" DEFAULT '{field.defaultValue}'"
            else:
                definition += f" DEFAULT {field.defaultValue}"
        
        field_definitions.append(definition)
    
    sql += ",\n".join(field_definitions)
    
    # 添加主键
    primary_keys = [field.name for field in fields if field.primaryKey]
    if primary_keys:
        sql += f',\n  PRIMARY KEY ("{"\", \"".join(primary_keys)}")'
    
    sql += "\n);\n"
    
    # 添加表注释
    if table_comment:
        sql += f"COMMENT ON TABLE \"{table_name}\" IS '{table_comment}';\n"
    
    # 添加字段注释
    for field in fields:
        if field.comment:
            sql += f"COMMENT ON COLUMN \"{table_name}\".\"{field.name}\" IS '{field.comment}';\n"
    
    return sql

def _generate_sqlite_sql(table_name: str, table_comment: Optional[str], fields: List[TableFieldCreate]) -> str:
    """生成SQLite创建表SQL"""
    sql = f'CREATE TABLE "{table_name}" (\n'
    
    field_definitions = []
    for field in fields:
        definition = f'  "{field.name}" {field.type}'
        
        # 添加NOT NULL
        if not field.nullable:
            definition += " NOT NULL"
        
        # 添加主键（SQLite的主键定义方式不同）
        if field.primaryKey:
            definition += " PRIMARY KEY"
        
        # 添加自增（SQLite使用AUTOINCREMENT）
        if field.autoIncrement and field.primaryKey:
            definition += " AUTOINCREMENT"
        
        # 添加默认值
        if field.defaultValue:
            if field.type.upper() == 'TEXT':
                definition += f" DEFAULT '{field.defaultValue}'"
            else:
                definition += f" DEFAULT {field.defaultValue}"
        
        field_definitions.append(definition)
    
    sql += ",\n".join(field_definitions)
    
    sql += "\n);\n"
    
    # SQLite不支持表注释，但我们可以添加注释作为SQL注释
    if table_comment:
        sql = f"-- {table_comment}\n{sql}"
    
    return sql

def register(api_router: APIRouter):
    """
    注册插件路由
    
    Args:
        api_router (APIRouter): 主应用的路由器
    """
    api_router.include_router(
        router,
        prefix="/api/plugins/generator",
        tags=["generator"],
        dependencies=[Depends(get_current_admin)],
    )
    logger.info("代码生成器插件路由注册成功")


def unregister(api_router: APIRouter):
    """
    注销插件路由
    
    Args:
        api_router (APIRouter): 主应用的路由器
    """
    # FastAPI不支持动态路由移除，此处为占位符
    logger.info("代码生成器插件路由注销")
    pass
