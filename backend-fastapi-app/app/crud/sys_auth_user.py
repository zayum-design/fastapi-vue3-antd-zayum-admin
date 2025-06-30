from typing import List, Optional
from datetime import datetime, timezone
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
    
    def create(self, db: Session, obj_in: SysUserCreate) -> SysUser:
        db_obj = SysUser()
        db_obj.username = str(obj_in.username)
        db_obj._password = str(obj_in.password)
        db_obj.user_group_id = int(1)
        db_obj.status = 'normal'
        db_obj.level = int(0)
        db_obj.nickname = str(obj_in.username)
        db_obj.gender = 'male'
        db_obj.score = int(0)
        db_obj.balance = float(0.0)
        if hasattr(obj_in, 'email') and obj_in.email:
            db_obj.email = str(obj_in.email)
        if hasattr(obj_in, 'mobile') and obj_in.mobile:
            db_obj.mobile = str(obj_in.mobile)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
crud_sys_auth_user = CRUDSysAuthUser()
