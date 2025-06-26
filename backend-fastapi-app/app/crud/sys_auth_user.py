from typing import List, Optional
from fastapi_babel import _
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.sys_user import SysUser
from app.schemas.sys_user import SysUserCreate
from app.utils.log_utils import logger

class CRUDSysAuthUser:
    def get(self, db: Session, id: int) -> Optional[SysUser]:
        """根据唯一ID获取SysUser。"""
        return db.query(SysUser).filter(SysUser.id == id).first()
    
    def get_by_name(self, db: Session, username: str) -> Optional[SysUser]:
        return db.query(SysUser).filter(SysUser.username == username).first()
    
    def set_password(self, db: Session, db_obj: SysUser, password: str) -> SysUser:
        db_obj.set_password(password)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
crud_sys_auth_user = CRUDSysAuthUser()
