"""
SysAdmin Repository
提供管理员数据访问层
"""

from sqlalchemy.orm import Session

from app.modules.admin.sys_admin.models.sys_admin import SysAdmin
from app.modules.admin.sys_admin.schemas.sys_admin import SysAdminCreate, SysAdminUpdate
from app.repositories.base import BaseRepository


class SysAdminRepository(BaseRepository[SysAdmin, SysAdminCreate, SysAdminUpdate]):
    """
    管理员 Repository

    提供管理员相关的数据访问方法
    """

    DEFAULT_SEARCH_FIELDS = ["username", "nickname", "email", "mobile"]
    DEFAULT_UNIQUE_FIELDS = ["username", "mobile", "email"]

    def __init__(self):
        super().__init__(SysAdmin)
        self.set_searchable_fields(self.DEFAULT_SEARCH_FIELDS)
        self.set_unique_fields(self.DEFAULT_UNIQUE_FIELDS)

    def get_by_username(self, db: Session, username: str) -> SysAdmin | None:
        """通过用户名获取管理员"""
        return self.get_by(db, username=username)

    def get_by_email(self, db: Session, email: str) -> SysAdmin | None:
        """通过邮箱获取管理员"""
        return self.get_by(db, email=email)

    def get_by_mobile(self, db: Session, mobile: str) -> SysAdmin | None:
        """通过手机号获取管理员"""
        return self.get_by(db, mobile=mobile)

    def authenticate(self, db: Session, username: str, password: str) -> SysAdmin | None:
        """
        验证管理员密码

        Args:
            db: 数据库会话
            username: 用户名
            password: 明文密码

        Returns:
            验证成功返回管理员对象，失败返回 None
        """
        admin = self.get_by_username(db, username)
        if not admin:
            return None

        if not admin.check_password(password):
            return None

        return admin


# 全局 Repository 实例
sys_admin_repo = SysAdminRepository()
