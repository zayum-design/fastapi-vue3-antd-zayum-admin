"""
SysAdmin 简化版 Repository
使用 EnhancedRepository 基类，代码量减少 80%
"""

from app.core.repository import EnhancedRepository
from app.modules.admin.sys_admin.models.sys_admin import SysAdmin
from app.modules.admin.sys_admin.schemas.sys_admin import SysAdminCreate, SysAdminUpdate


class SysAdminRepository(EnhancedRepository[SysAdmin, SysAdminCreate, SysAdminUpdate]):
    """
    SysAdmin 数据访问层

    仅需配置搜索字段和唯一字段，继承所有标准 CRUD 操作
    """

    # 可搜索字段
    DEFAULT_SEARCH_FIELDS = ["username", "nickname", "email", "mobile", "login_ip"]

    # 唯一字段（自动进行唯一性校验）
    DEFAULT_UNIQUE_FIELDS = ["username", "mobile", "email"]

    def __init__(self):
        super().__init__(SysAdmin)

    def get_by_username(self, db, username: str):
        """通过用户名获取（示例：添加自定义查询方法）"""
        return self.get_by(db, username=username)


# 单例实例（保持与旧版兼容）
sys_admin_repo = SysAdminRepository()
