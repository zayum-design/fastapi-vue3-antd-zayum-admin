"""
SysAdmin Service
提供管理员业务逻辑层
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.modules.admin.sys_admin.models.sys_admin import SysAdmin
from app.modules.admin.sys_admin.repositories.sys_admin import SysAdminRepository, sys_admin_repo
from app.modules.admin.sys_admin.schemas.sys_admin import SysAdminCreate, SysAdminUpdate
from app.services.base import BaseService
from app.utils.log_utils import logger


class SysAdminService(BaseService[SysAdmin, SysAdminCreate, SysAdminUpdate]):
    """
    管理员 Service

    处理管理员相关的业务逻辑：
    - 登录认证
    - 密码管理
    - 登录失败处理
    - Token 生成
    """

    # 最大登录失败次数
    MAX_LOGIN_FAILURES = 5

    def __init__(self, repository: SysAdminRepository = sys_admin_repo):
        super().__init__(repository)
        self._repo: SysAdminRepository = repository

    def authenticate(self, db: Session, username: str, password: str) -> SysAdmin | None:
        """
        管理员认证

        Args:
            db: 数据库会话
            username: 用户名
            password: 密码

        Returns:
            认证成功返回管理员，失败返回 None
        """
        admin = self._repo.get_by_username(db, username)

        if not admin:
            logger.warning("Login attempt for non-existent user: {username}")
            return None

        # 检查账户状态
        if admin.status != "normal":
            logger.warning("Login attempt for disabled account: {username}")
            return None

        # 检查登录失败次数
        if admin.login_failure >= self.MAX_LOGIN_FAILURES:
            logger.warning("Login attempt for locked account: {username}")
            return None

        # 验证密码
        if not admin.check_password(password):
            # 增加登录失败次数
            admin.login_failure += 1
            db.commit()
            logger.warning("Failed login attempt for {username} (failure {admin.login_failure})")
            return None

        # 登录成功，重置失败次数
        admin.login_failure = 0
        admin.login_at = datetime.now()
        db.commit()
        db.refresh(admin)  # 刷新对象状态，确保后续操作正常

        logger.info("Successful login: {username}")
        return admin

    def create_access_token_for_admin(self, admin: SysAdmin) -> str:
        """为管理员创建访问令牌"""
        return create_access_token(data={"sub": str(admin.id)})

    def create_admin(
        self, db: Session, obj_in: SysAdminCreate, created_by: int | None = None
    ) -> SysAdmin:
        """
        创建管理员（业务层包装）

        Args:
            db: 数据库会话
            obj_in: 创建数据
            created_by: 创建者ID（用于日志）
        """
        # 密码会在模型中自动哈希
        admin = self._repo.create(db, obj_in)
        logger.info("Admin created: {admin.username} by {created_by}")
        return admin

    def update_admin(
        self, db: Session, admin_id: int, obj_in: SysAdminUpdate, updated_by: int | None = None
    ) -> SysAdmin:
        """
        更新管理员（业务层包装）

        Args:
            db: 数据库会话
            admin_id: 管理员ID
            obj_in: 更新数据
            updated_by: 更新者ID（用于日志）
        """
        admin = self._repo.get_or_404(db, admin_id)
        updated = self._repo.update(db, admin, obj_in)
        logger.info("Admin updated: {updated.username} by {updated_by}")
        return updated

    def reset_password(
        self, db: Session, admin_id: int, new_password: str, reset_by: int | None = None
    ) -> SysAdmin:
        """
        重置密码

        Args:
            db: 数据库会话
            admin_id: 管理员ID
            new_password: 新密码
            reset_by: 操作者ID
        """
        admin = self._repo.get_or_404(db, admin_id)

        # 设置新密码（模型中会自动哈希）
        admin.password = new_password
        admin.login_failure = 0  # 重置登录失败次数
        db.commit()
        db.refresh(admin)

        logger.info("Password reset for admin: {admin.username} by {reset_by}")
        return admin

    def toggle_status(self, db: Session, admin_id: int) -> SysAdmin:
        """切换管理员状态（启用/禁用）"""
        admin = self._repo.get_or_404(db, admin_id)

        # 切换状态
        new_status = "hidden" if admin.status == "normal" else "normal"
        admin.status = new_status
        db.commit()
        db.refresh(admin)

        logger.info("Admin status toggled: {admin.username} -> {new_status}")
        return admin

    def unlock_account(self, db: Session, admin_id: int) -> SysAdmin:
        """解锁被锁定的账户"""
        admin = self._repo.get_or_404(db, admin_id)
        admin.login_failure = 0
        db.commit()
        db.refresh(admin)

        logger.info("Admin account unlocked: {admin.username}")
        return admin

    def get_admin_list(
        self,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 10,
        search: str | None = None,
        orderby: str | None = None,
        status: str | None = None,
        group_id: int | None = None,
    ) -> tuple[list[SysAdmin], int]:
        """
        获取管理员列表（支持高级过滤）
        """
        query = self._repo.query(db)

        # 应用状态过滤
        if status:
            query = query.filter(SysAdmin.status == status)

        # 应用分组过滤
        if group_id:
            query = query.filter(SysAdmin.group_id == group_id)

        # 获取总数
        total = query.count()

        # 应用搜索
        if search:
            query = query.search(search)

        # 应用排序
        if orderby:
            query = query.order_by_string(orderby)

        # 应用分页
        items = query.paginate(page, per_page).all()

        return items, total


# 全局 Service 实例
sys_admin_service = SysAdminService()
