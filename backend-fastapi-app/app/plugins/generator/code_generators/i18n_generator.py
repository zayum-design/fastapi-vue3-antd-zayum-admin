import json
import logging
from sqlalchemy import Table

logger = logging.getLogger(__name__)

def generate_vue_i18n_json(table: Table) -> str:
    """生成Vue国际化JSON数据"""
    translations = {
        "en": {
            table.name: {},
            "action": {
                "create": "Create",
                "edit": "Edit",
                "delete": "Delete",
                "operations": "Operations"
            },
            "message": {
                "createSuccess": "Create successfully",
                "updateSuccess": "Update successfully",
                "deleteSuccess": "Delete successfully",
                "confirmDelete": "Are you sure to delete this item?",
                "warning": "Warning"
            }
        },
        "zh-CN": {
            table.name: {},
            "action": {
                "create": "创建",
                "edit": "编辑",
                "delete": "删除",
                "operations": "操作"
            },
            "message": {
                "createSuccess": "创建成功",
                "updateSuccess": "更新成功",
                "deleteSuccess": "删除成功",
                "confirmDelete": "确认删除此条记录吗？",
                "warning": "警告"
            }
        }
    }

    # Add table column translations
    for col in table.columns:
        col_name = col.name
        translations["en"][table.name][col_name] = col_name.replace("_", " ").title()
        translations["zh-CN"][table.name][col_name] = col_name.replace("_", " ")

    return json.dumps(translations, indent=2, ensure_ascii=False)
