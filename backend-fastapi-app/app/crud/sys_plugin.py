from typing import List, Optional
from fastapi_babel import _
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.sys_plugin import SysPlugin
from app.schemas.sys_plugin import SysPluginCreate
from app.utils.log_utils import logger

class CRUDSysPlugin:
    def get(self, db: Session, id: int) -> Optional[SysPlugin]:
        """根据唯一ID获取SysPlugin。"""
        return db.query(SysPlugin).filter(SysPlugin.id == id).first()
    
    def get_by_uuid(self, db: Session, uuid: str) -> Optional[SysPlugin]:
        """根据唯一ID获取SysPlugin。"""
        return db.query(SysPlugin).filter(SysPlugin.uuid == uuid).first()

    def get_multi(self, db: Session, page: int = 1, per_page: int = 10, search: Optional[str] = None, orderby: Optional[str] = None) -> List[SysPlugin]:
        """
        分页获取多个SysPlugin记录，可选模糊搜索和排序。

        Args:
            db (Session): 数据库会话。
            page (int, optional): 页码，默认1。
            per_page (int, optional): 每页记录数，默认10。
            search (str, optional): 模糊搜索关键词。
            orderby (str, optional): 排序字段和方向，例如 'field_asc'。

        Returns:
            List[SysPlugin]: 指定页的SysPlugin对象列表。
        """
        if page < 1:
            page = 1  # 确保页码至少为1

        skip = (page - 1) * per_page  # 计算跳过的记录数

        query = db.query(SysPlugin)

        # 如果提供了搜索关键词，应用模糊搜索
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    SysPlugin.title.ilike(search_pattern),
                    SysPlugin.author.ilike(search_pattern),
                    SysPlugin.uuid.ilike(search_pattern),
                    SysPlugin.description.ilike(search_pattern),
                    SysPlugin.version.ilike(search_pattern),
                    SysPlugin.download_url.ilike(search_pattern),
                    SysPlugin.md5_hash.ilike(search_pattern),
                    SysPlugin.setting_menu.ilike(search_pattern),
                    SysPlugin.status.ilike(search_pattern),
                )
            )

        # 应用排序
        if orderby:
            try:
                field, direction = orderby.rsplit("_", 1)
                if direction == "asc":
                    query = query.order_by(getattr(SysPlugin, field).asc())
                elif direction == "desc":
                    query = query.order_by(getattr(SysPlugin, field).desc())
            except AttributeError:
                logger.error(_("排序字段或方向无效：%(orderby)s", orderby=orderby))

        # 应用分页
        return query.offset(skip).limit(per_page).all()

    def get_all(self, db: Session, search: Optional[str] = None, orderby: Optional[str] = None) -> List[SysPlugin]:
        """获取所有SysPlugin记录，可选模糊搜索和排序。"""
        query = db.query(SysPlugin)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    SysPlugin.title.ilike(search_pattern),
                    SysPlugin.author.ilike(search_pattern),
                    SysPlugin.uuid.ilike(search_pattern),
                    SysPlugin.description.ilike(search_pattern),
                    SysPlugin.version.ilike(search_pattern),
                    SysPlugin.download_url.ilike(search_pattern),
                    SysPlugin.md5_hash.ilike(search_pattern),
                    SysPlugin.setting_menu.ilike(search_pattern),
                    SysPlugin.status.ilike(search_pattern),
                )
            )

        if orderby:
            try:
                field, direction = orderby.rsplit("_", 1)
                if direction == "asc":
                    query = query.order_by(getattr(SysPlugin, field).asc())
                elif direction == "desc":
                    query = query.order_by(getattr(SysPlugin, field).desc())
            except AttributeError:
                logger.error(_("排序字段或方向无效：%(orderby)s", orderby=orderby))

        return query.all()

    def get_total(self, db: Session, search: Optional[str] = None) -> int:
        """获取SysPlugin记录的总数，可选模糊搜索。"""
        query = db.query(SysPlugin)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    SysPlugin.title.ilike(search_pattern),
                    SysPlugin.author.ilike(search_pattern),
                    SysPlugin.uuid.ilike(search_pattern),
                    SysPlugin.description.ilike(search_pattern),
                    SysPlugin.version.ilike(search_pattern),
                    SysPlugin.download_url.ilike(search_pattern),
                    SysPlugin.md5_hash.ilike(search_pattern),
                    SysPlugin.setting_menu.ilike(search_pattern),
                    SysPlugin.status.ilike(search_pattern),
                )
            )

        return query.count()

    def create(self, db: Session, obj_in: SysPluginCreate) -> SysPlugin:
        """
        创建一个新的SysPlugin记录，并验证唯一性。

        Args:
            db (Session): 数据库会话。
            obj_in (SysPluginCreate): 创建所需的数据。

        Raises:

        Returns:
            SysPlugin: 新创建的SysPlugin对象。
        """
        db_obj = SysPlugin(**obj_in.model_dump(exclude_unset=True))
        db.add(db_obj)
        db.flush()
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: SysPlugin, obj_in: dict) -> SysPlugin:
        """
        更新现有的SysPlugin记录，并验证唯一性。

        Args:
            db (Session): 数据库会话。
            db_obj (SysPlugin): 需要更新的SysPlugin对象。
            obj_in (dict): 包含更新字段的字典。

        Raises:

        Returns:
            SysPlugin: 更新后的SysPlugin对象。
        """

        for field, value in obj_in.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int) -> SysPlugin:
        """根据唯一ID删除SysPlugin。"""
        obj = db.query(SysPlugin).filter(SysPlugin.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

crud_sys_plugin = CRUDSysPlugin()
