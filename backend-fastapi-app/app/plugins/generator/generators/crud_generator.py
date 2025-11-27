"""
CRUD代码生成器
生成数据库操作代码
"""

from typing import List, Optional
from sqlalchemy import inspect, Table
from sqlalchemy.orm import Session
from fastapi_babel import _


class CrudGenerator:
    """CRUD代码生成器类"""
    
    def generate(self, inspector, table: Table) -> str:
        """生成CRUD代码"""
        class_name = "".join(word.capitalize() for word in table.name.split("_"))
        
        # 获取主键列
        primary_key_columns = [col.name for col in table.primary_key.columns]
        primary_key = primary_key_columns[0] if primary_key_columns else "id"
        
        # 获取所有列名
        all_columns = [col.name for col in table.columns]
        
        # 构建CRUD代码
        crud_code = f'''"""
{table.name} 表的CRUD操作
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.{table.name} import {class_name}
from app.schemas.{table.name} import {class_name}Create, {class_name}Update
from fastapi_babel import _


class CRUD{class_name}:
    """{class_name} CRUD操作类"""

    def get(self, db: Session, {primary_key}: int) -> Optional[{class_name}]:
        """根据ID获取单个记录"""
        return db.query({class_name}).filter({class_name}.{primary_key} == {primary_key}).first()

    def get_multi(
        self,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        orderby: Optional[str] = None
    ) -> List[{class_name}]:
        """获取多条记录，支持分页、搜索和排序"""
        query = db.query({class_name})
        
        # 搜索功能
        if search:
            search_conditions = []
            for column in {all_columns}:
                if hasattr({class_name}, column):
                    search_conditions.append(getattr({class_name}, column).ilike(f"%{{search}}%"))
            if search_conditions:
                query = query.filter(or_(*search_conditions))
        
        # 排序功能
        if orderby:
            if orderby.endswith('_desc'):
                field = orderby[:-5]
                if hasattr({class_name}, field):
                    query = query.order_by(getattr({class_name}, field).desc())
            else:
                if hasattr({class_name}, orderby):
                    query = query.order_by(getattr({class_name}, orderby))
        
        # 分页功能
        if per_page > 0:
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
        
        return query.all()

    def get_total(self, db: Session, search: Optional[str] = None) -> int:
        """获取总记录数"""
        query = db.query({class_name})
        
        # 搜索功能
        if search:
            search_conditions = []
            for column in {all_columns}:
                if hasattr({class_name}, column):
                    search_conditions.append(getattr({class_name}, column).ilike(f"%{{search}}%"))
            if search_conditions:
                query = query.filter(or_(*search_conditions))
        
        return query.count()

    def create(self, db: Session, *, obj_in: {class_name}Create) -> {class_name}:
        """创建新记录"""
        db_obj = {class_name}(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: {class_name},
        obj_in: {class_name}Update
    ) -> {class_name}:
        """更新记录"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, {primary_key}: int) -> {class_name}:
        """删除记录"""
        obj = db.query({class_name}).get({primary_key})
        db.delete(obj)
        db.commit()
        return obj


crud_{table.name} = CRUD{class_name}()
'''
        return crud_code
