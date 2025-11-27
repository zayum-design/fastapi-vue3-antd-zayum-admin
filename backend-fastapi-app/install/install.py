"""
安装模块主文件
负责处理系统安装过程中的数据库连接测试、数据导入和安装完成等操作
"""

import asyncio
from datetime import datetime, timezone
import os
from typing import Any, Dict
from sqlalchemy import text
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from app.utils.responses import error_response, success_response
from app.crud.sys_auth_admin import crud_sys_auth_admin
from app.utils.utils import modify_env_value
from app.crud.sys_admin import crud_sys_admin

# 创建安装路由
router = APIRouter(tags=["installation"])

# 数据库连接测试模块
from pydantic import BaseModel

import xmlrpc.client

class DatabaseConfig(BaseModel):
    """数据库连接配置模型"""

    host: str  # 数据库主机地址
    port: int  # 数据库端口号
    username: str  # 数据库用户名
    password: str  # 数据库密码
    database: str  # 数据库名称


@router.post("/test-db")
async def test_database_connection(config: DatabaseConfig):
    """
    测试数据库连接接口
    用于验证提供的数据库配置是否正确可用

    Args:
        config (DatabaseConfig): 包含数据库连接参数的对象

    Returns:
        JSONResponse: 成功返回连接信息，失败返回错误详情

    Raises:
        HTTPException: 当连接失败时抛出500错误
    """
    """
    测试数据库连接。

    尝试通过执行一个简单的查询来测试数据库是否可以正常连接。如果连接成功，返回成功的响应；否则，抛出HTTP异常。

    Args:
        config (DatabaseConfig): 数据库配置参数，包含:
            - host: 数据库主机地址
            - port: 数据库端口
            - username: 数据库用户名
            - password: 数据库密码
            - database: 数据库名称
        db (Session): 数据库会话对象。

    Returns:
        JSONResponse: 成功响应，包含消息 "数据库连接成功"。

    Raises:
        HTTPException: 如果数据库连接失败，抛出500错误并包含错误详情。
    """
    try:

        # 尝试使用提供的配置创建新连接
        # return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        test_conn_str = f"mysql+pymysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
        from sqlalchemy import create_engine

        test_engine = create_engine(test_conn_str)
        with test_engine.connect() as test_conn:
            test_conn.execute(text("SELECT 1"))
            modify_env_value(".env", "MYSQL_USER", config.username)
            modify_env_value(".env", "MYSQL_PASSWORD", config.password)
            modify_env_value(".env", "MYSQL_DB", config.database)
            modify_env_value(".env", "MYSQL_HOST", config.host)
            modify_env_value(".env", "MYSQL_PORT", str(config.port))

        # 重新加载main模块以应用新的数据库配置
        import importlib
        from app import main

        importlib.reload(main)

        # 测试当前数据库连接是否正常
        from app.dependencies.database import get_db

        db = next(get_db())
        db.execute(text("SELECT 1"))

        return success_response(
            msg="数据库连接成功",
            data={
                "details": {
                    "host": config.host,
                    "port": config.port,
                    "database": config.database,
                }
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {str(e)}")


# 数据导入顺序定义
IMPORT_ORDER = [
    "sys_admin",  # 系统管理员表
    "sys_user_balance_log",  # 用户余额日志表
    "sys_attachment",  # 附件表
    "sys_general_category",  # 通用分类表
    "sys_admin_rule",  # 管理员规则表
    "sys_admin_log",  # 管理员日志表
    "sys_user_rule",  # 用户规则表
    "sys_admin_group",  # 管理员组表
    "sys_plugin",  # 插件表
    "sys_user",  # 用户表
    "sys_user_score_log",  # 用户积分日志表
    "sys_attachment_category",  # 附件分类表
    "sys_user_group",  # 用户组表
    "sys_general_config",  # 通用配置表
]

from pydantic import BaseModel


class ImportRequest(BaseModel):
    """数据导入请求模型"""

    current_table: str | None = None  # 当前正在导入的表名
    import_options: list[str] | None = None  # 导入选项列表


@router.post("/import-db")
async def import_database(request: ImportRequest):
    """
    数据库数据导入接口
    按照预定义顺序导入系统基础数据

    Args:
        request (ImportRequest): 包含导入请求参数的对象

    Returns:
        JSONResponse: 返回导入进度和结果信息

    Raises:
        HTTPException: 当导入失败时抛出相应错误
    """
    # 动态获取数据库连接
    from app.dependencies.database import get_db

    db = next(get_db())

    # 导入所有需要的模型类
    from app.models.sys_admin import SysAdmin
    from app.models.sys_admin_group import SysAdminGroup
    from app.models.sys_admin_log import SysAdminLog
    from app.models.sys_admin_rule import SysAdminRule
    from app.models.sys_attachment import SysAttachment
    from app.models.sys_attachment_category import SysAttachmentCategory
    from app.models.sys_general_category import SysGeneralCategory
    from app.models.sys_general_config import SysGeneralConfig
    from app.models.sys_plugin import SysPlugin
    from app.models.sys_user import SysUser
    from app.models.sys_user_balance_log import SysUserBalanceLog
    from app.models.sys_user_group import SysUserGroup
    from app.models.sys_user_rule import SysUserRule
    from app.models.sys_user_score_log import SysUserScoreLog

    from install.generated.install_data import (
        import_SysAdmin,
        import_SysUserBalanceLog,
        import_SysAttachment,
        import_SysGeneralCategory,
        import_SysAdminRule,
        import_SysAdminLog,
        import_SysUserRule,
        import_SysAdminGroup,
        import_SysPlugin,
        import_SysUser,
        import_SysUserScoreLog,
        import_SysAttachmentCategory,
        import_SysUserGroup,
        import_SysGeneralConfig,
    )

    IMPORT_FUNCTIONS = {
        "sys_admin": import_SysAdmin,
        "sys_user_balance_log": import_SysUserBalanceLog,
        "sys_attachment": import_SysAttachment,
        "sys_general_category": import_SysGeneralCategory,
        "sys_admin_rule": import_SysAdminRule,
        "sys_admin_log": import_SysAdminLog,
        "sys_user_rule": import_SysUserRule,
        "sys_admin_group": import_SysAdminGroup,
        "sys_plugin": import_SysPlugin,
        "sys_user": import_SysUser,
        "sys_user_score_log": import_SysUserScoreLog,
        "sys_attachment_category": import_SysAttachmentCategory,
        "sys_user_group": import_SysUserGroup,
        "sys_general_config": import_SysGeneralConfig,
    }
    current_table = request.current_table
    """
    导入数据库。

    根据提供的导入选项，执行数据库导入操作。例如，可以选择创建数据库表或执行其他初始化任务。
    
    Args:
        db_form (dict): 数据库配置表单。
        import_options (list[str]): 要执行的导入选项（如创建表）。
        db (Session): 数据库会话对象。
    
    Returns:
        JSONResponse: 成功响应，包含消息 "数据库导入成功"。
    
    Raises:
        HTTPException: 如果导入过程中发生错误，抛出500错误并包含错误详情。
    """

    # 首次调用没有current_table时，从第一个表开始
    if not current_table:
        next_table = IMPORT_ORDER[0]
        return success_response(data={"next_table": next_table}, msg="准备开始导入数据")

    try:
        # 获取当前表索引
        current_index = IMPORT_ORDER.index(current_table)
    except ValueError:
        from app.utils.response_handlers import ErrorCode

        return error_response(
            error_code=ErrorCode.BAD_REQUEST, message=f"无效的表名: {current_table}"
        )

    # 检查并执行当前表导入
    try:
        import_func = IMPORT_FUNCTIONS[current_table]
        # 检查表是否有数据
        model = {
            "sys_admin": "SysAdmin",
            "sys_user_balance_log": "SysUserBalanceLog",
            "sys_attachment": "SysAttachment",
            "sys_general_category": "SysGeneralCategory",
            "sys_admin_rule": "SysAdminRule",
            "sys_admin_log": "SysAdminLog",
            "sys_user_rule": "SysUserRule",
            "sys_admin_group": "SysAdminGroup",
            "sys_plugin": "SysPlugin",
            "sys_user": "SysUser",
            "sys_user_score_log": "SysUserScoreLog",
            "sys_attachment_category": "SysAttachmentCategory",
            "sys_user_group": "SysUserGroup",
            "sys_general_config": "SysGeneralConfig",
        }[current_table]
        next_index = current_index + 1
        
        from sqlalchemy import inspect
        from app.dependencies.database import engine
        inspector = inspect(engine)
        
        print(f"🔍 开始导入表: {current_table}")
        if current_table == "sys_general_config":
            print("⚠️ 特别注意: 正在导入sys_general_config表")
            
        import_func(db, inspector)
        
        print(f"✅ 表 {current_table} 导入完成")
        db.commit()
        print(f"✅ 成功导入表: {current_table}")
        
        # 检查是否有下一个表
        if next_index >= len(IMPORT_ORDER):
            return success_response(
                data={
                    "next_table": None,
                    "progress": f"{len(IMPORT_ORDER)}/{len(IMPORT_ORDER)}",
                },
                msg="所有数据导入完成",
            )
            
        next_table = IMPORT_ORDER[next_index]
        return success_response(
            data={
                "next_table": next_table,
                "progress": f"{next_index}/{len(IMPORT_ORDER)}",
            },
            msg=f"表 {current_table} 导入成功",
        )
    except Exception as e:
        db.rollback()
        from app.utils.response_handlers import ErrorCode
        import traceback
        
        error_detail = f"导入表 {current_table} 失败: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ 错误详情: {error_detail}")
        
        return error_response(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=f"导入表 {current_table} 失败: {str(e)}",
            data={
                "error_table": current_table,
                "error_detail": str(e),
                "traceback": traceback.format_exc()
            },
        )
    # 所有表导入完成
    return success_response(
        data={"next_table": None, "progress": f"{next_index}/{len(IMPORT_ORDER)}"},
        msg="所有数据导入完成",
    )


# 安装完成模块
from pydantic import BaseModel


class AdminCreate(BaseModel):
    """管理员创建模型"""

    username: str  # 管理员用户名
    password: str  # 管理员密码
    email: str  # 管理员邮箱
    mobile: str  # 管理员手机号
    nickname: str  # 管理员昵称

 
@router.post("/complete")
async def complete_installation(request: Request, admin_data: AdminCreate):
    """
    完成系统安装接口
    创建初始管理员账户并标记安装完成

    Args:
        request (Request): FastAPI请求对象
        admin_data (AdminCreate): 管理员账户信息

    Returns:
        JSONResponse: 返回安装完成信息

    Raises:
        HTTPException: 当安装过程出现错误时抛出500错误
    """
    """
    完成安装并创建管理员账户

    Args:
        admin_data (AdminCreate): 管理员账号信息

    Returns:
        JSONResponse: 成功响应，包含消息 "安装完成，管理员已创建"
    """
    # 动态获取数据库连接
    from app.dependencies.database import get_db

    db = next(get_db())
    try:
        # 创建初始管理员账户（ID为1）
        from app.schemas.sys_admin import SysAdminCreate

        client_ip = request.client.host if request.client else "127.0.0.1"  # 获取客户端 IP 地址
        obj_in = SysAdminCreate(
            id=1,
            group_id=1,
            nickname="SupperAdmin",
            username=admin_data.username,
            password=admin_data.password,
            email=admin_data.email,
            mobile=admin_data.mobile,
            status="normal",
            login_ip=client_ip,
            login_at=datetime.now(timezone.utc),
            login_failure=0,
        )

        crud_sys_admin.create(db, obj_in=obj_in)

        # 创建安装锁定文件
        from pathlib import Path

        lock_file = Path(__file__).parent.parent.parent / "install.lock"
        with open(lock_file, "w") as f:
            f.write(f"Installation completed at: {datetime.now(timezone.utc)}")
 
        return success_response({"message": "安装完成，管理员已创建"})
    except Exception as e:
        # 如果发生异常，抛出500错误，返回具体的错误信息
        raise HTTPException(status_code=500, detail=f"完成安装失败: {str(e)}")
    
    
@router.post("/restart")
async def restart():
    import importlib
    from app import main

    importlib.reload(main)
    
    server = xmlrpc.client.ServerProxy("http://admin:88888888@127.0.0.1:9001/RPC2")
    try:
        server.supervisor.stopProcess("fastapi", True)
        server.supervisor.startProcess("fastapi", True)
        print("FastAPI 服务已重启")
    except Exception as e:
        print("重启失败：", e)
