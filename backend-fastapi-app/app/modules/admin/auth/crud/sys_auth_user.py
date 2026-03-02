from sqlalchemy.orm import Session

from app.modules.admin.sys_user.models.sys_user import SysUser
from app.modules.admin.sys_user.schemas.sys_user import SysUserCreate


class CRUDSysAuthUser:
    def get(self, db: Session, id: int) -> SysUser | None:
        """根据唯一ID获取SysUser。"""
        return db.query(SysUser).filter(SysUser.id == id).first()

    def get_by_name(self, db: Session, username: str) -> SysUser | None:
        return db.query(SysUser).filter(SysUser.username == username).first()

    def set_password(self, db: Session, db_obj: SysUser, password: str) -> SysUser:
        db_obj.set_password(password)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create(self, db: Session, obj_in: SysUserCreate) -> SysUser:
        db_obj = SysUser()
        db_obj.username = str(obj_in.username)
        db_obj._password = str(obj_in.password)
        db_obj.user_group_id = 1
        db_obj.status = "normal"
        db_obj.level = 0
        db_obj.nickname = str(obj_in.username)
        db_obj.gender = "male"
        db_obj.score = 0
        db_obj.balance = 0.0
        if hasattr(obj_in, "email") and obj_in.email:
            db_obj.email = str(obj_in.email)
        if hasattr(obj_in, "mobile") and obj_in.mobile:
            db_obj.mobile = str(obj_in.mobile)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


crud_sys_auth_user = CRUDSysAuthUser()
