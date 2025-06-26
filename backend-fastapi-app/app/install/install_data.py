from sqlalchemy.orm import Session
from sqlalchemy import inspect, select
from app.dependencies.database import engine

# 导入各模块的初始化函数
from .module.sys_module import (
    import_SysAdmin,
    import_SysAdminGroup,
    import_SysAdminLog,
    import_SysAdminRule,
    import_SysPlugin
)
from .module.user_module import (
    import_SysUser,
    import_SysUserBalanceLog,
    import_SysUserScoreLog,
    import_SysUserRule,
    import_SysUserGroup
)
from .module.general_module import (
    import_SysGeneralCategory,
    import_SysGeneralConfig
)
from .module.attachment_module import (
    import_SysAttachment,
    import_SysAttachmentCategory
)

inspector = inspect(engine)

def table_has_data(db: Session, model) -> bool:
    """检查表中是否有数据"""
    return db.scalar(select(model).limit(1)) is not None

def install_all_data(db: Session):
    """安装所有初始化数据"""
    # 系统相关表
    import_SysAdmin(db, inspector)
    import_SysAdminGroup(db, inspector)
    import_SysAdminLog(db, inspector)
    import_SysAdminRule(db, inspector)
    import_SysPlugin(db, inspector)
    
    # 用户相关表
    import_SysUser(db, inspector)
    import_SysUserBalanceLog(db, inspector)
    import_SysUserScoreLog(db, inspector)
    import_SysUserRule(db, inspector)
    import_SysUserGroup(db, inspector)
    
    # 通用配置表
    import_SysGeneralCategory(db, inspector)
    import_SysGeneralConfig(db, inspector)
    
    # 附件相关表
    import_SysAttachment(db, inspector)
    import_SysAttachmentCategory(db, inspector)
    
    db.commit()
    print("✅ 所有数据初始化完成")
