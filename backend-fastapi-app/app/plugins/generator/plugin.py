"""
代码生成器插件主文件
提供数据库表到代码的自动生成功能
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.core.security import get_current_admin
from app.utils.responses import success_response
from app.utils.log_utils import logger

from .services.code_generation_service import CodeGenerationService
from .core.types import TablesResponse, CodeGenerationResponse


# 初始化路由和服务
router = APIRouter(tags=["generator"], dependencies=[Depends(get_current_admin)])
code_generation_service = CodeGenerationService()
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
