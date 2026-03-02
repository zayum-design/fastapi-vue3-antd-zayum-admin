"""
代码生成服务
提供统一的代码生成接口
"""

from typing import List
import datetime
from sqlalchemy import MetaData, Table, inspect
from fastapi import HTTPException, status

from ..core.types import FieldInfo, CodeGeneration, CodeGenerationResponse
from ..core.config import GeneratorConfig
from ..generators.model_generator import ModelGenerator
from ..generators.crud_generator import CrudGenerator
from ..generators.schemas_generator import SchemasGenerator
from ..generators.api_generator import ApiGenerator
from ..generators.vue_generator import VueGenerator
from ..generators.i18n_generator import I18nGenerator


class CodeGenerationService:
    """代码生成服务类"""
    
    def __init__(self):
        self.config = GeneratorConfig()
        self.model_generator = ModelGenerator()
        self.crud_generator = CrudGenerator()
        self.schemas_generator = SchemasGenerator()
        self.api_generator = ApiGenerator()
        self.vue_generator = VueGenerator()
        self.i18n_generator = I18nGenerator()
    
    def get_tables(self) -> List[str]:
        """获取数据库中的所有表名"""
        try:
            from app.dependencies.database import get_engine
            engine = get_engine()
            inspector = inspect(engine)
            return inspector.get_table_names()
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取表列表失败: {str(e)}",
            )
    
    def generate_code(
        self, 
        table_name: str, 
        fields: str = GeneratorConfig.DEFAULT_FIELDS,
        operations: str = GeneratorConfig.DEFAULT_OPERATIONS
    ) -> CodeGenerationResponse:
        """为指定表生成代码"""
        try:
            from app.dependencies.database import get_engine
            engine = get_engine()
            
            inspector = inspect(engine)
            if table_name not in inspector.get_table_names():
                raise HTTPException(
                    status_code=404, 
                    detail=f"表 {table_name} 在数据库中不存在"
                )

            # 获取表字段信息
            columns = inspector.get_columns(table_name)
            field_info = [
                FieldInfo(name=col["name"], type=str(col["type"])) 
                for col in columns
            ]

            # 加载表结构
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=engine)

            # 生成各种代码
            model_code = self.model_generator.generate(table)
            crud_code = self.crud_generator.generate(inspector, table)
            schemas_code = self.schemas_generator.generate(table)
            api_code = self.api_generator.generate(table)
            vue_code = self.vue_generator.generate(table, fields, operations)
            vue_i18n_json = self.i18n_generator.generate(table)

            # 构建响应
            return CodeGenerationResponse(
                code=0,
                msg="代码生成成功",
                data=CodeGeneration(
                    field_info=field_info,
                    model_code=model_code,
                    crud_code=crud_code,
                    schemas_code=schemas_code,
                    api_code=api_code,
                    vue_code=vue_code,
                    vue_i18n_json=vue_i18n_json,
                ),
                time=datetime.datetime.now().isoformat(),
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"为表 {table_name} 生成代码失败: {str(e)}",
            )
