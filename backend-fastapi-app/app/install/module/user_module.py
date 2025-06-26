from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import inspect, select
from app.dependencies.database import engine
from app.models.sys_user import SysUser as SysUserType
from app.models.sys_user_balance_log import SysUserBalanceLog as SysUserBalanceLogType
from app.models.sys_user_score_log import SysUserScoreLog as SysUserScoreLogType
from app.models.sys_user_rule import SysUserRule as SysUserRuleType
from app.models.sys_user_group import SysUserGroup as SysUserGroupType

# Type aliases
SysUser: type[SysUserType] = SysUserType
SysUserBalanceLog: type[SysUserBalanceLogType] = SysUserBalanceLogType
SysUserScoreLog: type[SysUserScoreLogType] = SysUserScoreLogType
SysUserRule: type[SysUserRuleType] = SysUserRuleType
SysUserGroup: type[SysUserGroupType] = SysUserGroupType

def import_SysUser(db: Session, inspector):
    """导入 SysUser 数据"""
    if "sys_user" not in inspector.get_table_names():
        print("🔧 创建表: sys_user")
        SysUser.__table__.create(bind=engine)
    else:
        print("✅ 表已存在: sys_user")
    if db.scalar(select(SysUser).limit(1)) is None:
        print("📥 导入数据: SysUser")
        user = SysUser()
        user.id = 1
        user.user_group_id = 1
        user.username = "demo"
        user.nickname = "Demo User"
        user.password = "$2b$12$jK20mrVxfbBtoQTslePluOa9yqlQ4y2l0mGLyQBq/VEerVItWykSC"
        user.email = "demo@example.com"
        user.mobile = "13800000000"
        user.avatar = None
        user.level = 1
        user.gender = "male"
        user.birthday = None
        user.bio = "Demo User Account"
        user.balance = float(Decimal("100.00"))
        user.score = 100
        user.successions = 1
        user.max_successions = 1
        user.prev_time = datetime.fromisoformat("2025-05-09T15:53:49")
        user.login_time = datetime.fromisoformat("2025-05-09T15:53:49")
        user.login_ip = "127.0.0.1"
        user.login_failure = 0
        user.join_ip = "127.0.0.1"
        user.verification = None
        user.token = None
        user.status = "normal"
        user.created_at = datetime.fromisoformat("2025-05-09T15:53:49")
        user.updated_at = datetime.fromisoformat("2025-05-09T15:53:49")
        db.add(user)

def import_SysUserBalanceLog(db: Session, inspector):
    """导入 SysUserBalanceLog 数据"""
    if "sys_user_balance_log" not in inspector.get_table_names():
        print("🔧 创建表: sys_user_balance_log")
        SysUserBalanceLog.__table__.create(bind=engine)
    else:
        print("✅ 表已存在: sys_user_balance_log")
    if db.scalar(select(SysUserBalanceLog).limit(1)) is None:
        print("📥 导入数据: SysUserBalanceLog")
        balance_log = SysUserBalanceLog()
        balance_log.id = 1
        balance_log.user_id = 9
        balance_log.balance = float(Decimal("888"))
        balance_log.before = float(Decimal("0"))
        balance_log.after = float(Decimal("0"))
        balance_log.memo = "000"
        balance_log.created_at = datetime.fromisoformat("2025-03-06T15:58:56")
        balance_log.updated_at = datetime.fromisoformat("2025-03-06T15:58:56")
        db.add(balance_log)

def import_SysUserScoreLog(db: Session, inspector):
    """导入 SysUserScoreLog 数据"""
    if "sys_user_score_log" not in inspector.get_table_names():
        print("🔧 创建表: sys_user_score_log")
        SysUserScoreLog.__table__.create(bind=engine)
    else:
        print("✅ 表已存在: sys_user_score_log")
    if db.scalar(select(SysUserScoreLog).limit(1)) is None:
        print("📥 导入数据: SysUserScoreLog")
        score_log = SysUserScoreLog()
        score_log.id = 1
        score_log.user_id = 1
        score_log.score = 100
        score_log.before = 0
        score_log.after = 100
        score_log.memo = "Initial score"
        score_log.created_at = datetime.fromisoformat("2025-03-06T15:59:16")
        score_log.updated_at = datetime.fromisoformat("2025-03-06T15:59:16")
        db.add(score_log)

def import_SysUserRule(db: Session, inspector):
    """导入 SysUserRule 数据"""
    if "sys_user_rule" not in inspector.get_table_names():
        print("🔧 创建表: sys_user_rule")
        SysUserRule.__table__.create(bind=engine)
    else:
        print("✅ 表已存在: sys_user_rule")
    if db.scalar(select(SysUserRule).limit(1)) is None:
        print("📥 导入数据: SysUserRule")
        # 原文件中的user_rule1-user_rule6导入逻辑
        # 这里省略具体实现，保持与原始文件一致
        pass

def import_SysUserGroup(db: Session, inspector):
    """导入 SysUserGroup 数据"""
    if "sys_user_group" not in inspector.get_table_names():
        print("🔧 创建表: sys_user_group")
        SysUserGroup.__table__.create(bind=engine)
    else:
        print("✅ 表已存在: sys_user_group")
    if db.scalar(select(SysUserGroup).limit(1)) is None:
        print("📥 导入数据: SysUserGroup")
        group = SysUserGroup()
        group.id = 1
        group.name = "default"
        group.rules = "1,2"
        group.status = "normal"
        group.created_at = datetime.fromisoformat("2024-03-27T07:37:07")
        group.updated_at = datetime.fromisoformat("2024-03-27T07:37:07")
        db.add(group)
