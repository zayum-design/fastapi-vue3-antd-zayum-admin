from typing import List, Optional
from fastapi_babel import _
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.sys_admin import SysAdmin
from app.schemas.sys_admin import SysAdminCreate,SysAdminUpdate
from app.utils.log_utils import logger

class CRUDSysAuthAdmin:
    def get(self, db: Session, id: int) -> Optional[SysAdmin]:
        """根据唯一ID获取SysAdmin。"""
        return db.query(SysAdmin).filter(SysAdmin.id == id).first()
    
    def get_by_name(self, db: Session, username: str) -> Optional[SysAdmin]:
        """根据用户名获取SysAdmin。"""
        return db.query(SysAdmin).filter(SysAdmin.username == username).first()
    
    def set_password(self, db: Session, db_obj: SysAdmin, password: str) -> SysAdmin:
        """设置SysAdmin对象的密码并保存到数据库。"""
        db_obj.set_password(password)  # 设置密码
        db.commit()  # 提交事务
        db.refresh(db_obj)  # 刷新对象，获取更新后的数据
        return db_obj
    
    def upsert_admin(self, db: Session, admin_upsert: SysAdminUpdate) -> SysAdmin:
        """
        如果管理员ID为1的用户不存在，则插入一个新的管理员；否则，更新ID为1的管理员信息。
        
        Args:
            db (Session): 数据库会话
            admin_create (SysAdminCreate): 新管理员的数据
            admin_update (SysAdminUpdate): 用于更新的管理员数据
        
        Returns:
            SysAdmin: 插入或更新后的管理员信息
        """
        # 查找ID为1的管理员
        db_admin = self.get(db, id=1)
        
        if db_admin:
            # 如果管理员已存在，则更新其信息
            for field, value in admin_upsert.model_dump(exclude_unset=True).items():
                setattr(db_admin, field, value)  # 设置管理员字段的更新值
            
            # 更新密码时使用set_password方法
            if admin_upsert.password:
                self.set_password(db, db_admin, admin_upsert.password)
            
            db.commit()  # 提交事务
            db.refresh(db_admin)  # 刷新对象，获取更新后的数据
            return db_admin
        else:
            # 如果管理员不存在，则插入新的管理员
            new_admin = SysAdmin(**admin_upsert.model_dump())  # 使用管理员创建数据生成新管理员对象
            # 如果有密码，调用set_password方法设置密码
            if admin_upsert.password:
                self.set_password(db, new_admin, admin_upsert.password)
            
            db.add(new_admin)  # 将新管理员对象添加到会话
            db.commit()  # 提交事务
            db.refresh(new_admin)  # 刷新对象，获取更新后的数据
            return new_admin

# 实例化CRUDSysAuthAdmin类
crud_sys_auth_admin = CRUDSysAuthAdmin()
