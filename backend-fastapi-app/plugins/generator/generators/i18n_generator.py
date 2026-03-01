"""
I18n代码生成器
生成国际化JSON代码
"""

from sqlalchemy import Table
import json


class I18nGenerator:
    """I18n代码生成器类"""
    
    def generate(self, table: Table) -> str:
        """生成I18n JSON代码"""
        class_name = "".join(word.capitalize() for word in table.name.split("_"))
        
        # 构建I18n数据
        i18n_data = {
            table.name: {
                "title": f"{class_name}管理",
                "add": f"添加{class_name}",
                "edit": f"编辑{class_name}",
                "delete": f"删除{class_name}",
                "search": f"搜索{class_name}",
                "confirmDelete": f"确定要删除这个{class_name}吗？",
                "deleteSuccess": f"{class_name}删除成功",
                "deleteFailed": f"{class_name}删除失败",
                "createSuccess": f"{class_name}创建成功", 
                "createFailed": f"{class_name}创建失败",
                "updateSuccess": f"{class_name}更新成功",
                "updateFailed": f"{class_name}更新失败",
                "fetchFailed": f"获取{class_name}列表失败"
            }
        }
        
        # 添加字段翻译
        for col in table.columns:
            if col.name.lower() in ["id", "created_at", "updated_at"]:
                continue
                
            # 生成字段名称翻译
            field_name = self._generate_field_name(col.name)
            i18n_data[table.name][col.name] = field_name
            
            # 如果字段不可为空，添加必填错误信息
            if not col.nullable:
                i18n_data[table.name][f"{col.name}Required"] = f"{field_name}是必填项"
        
        # 转换为JSON字符串
        return json.dumps(i18n_data, ensure_ascii=False, indent=2)
    
    def _generate_field_name(self, column_name: str) -> str:
        """根据列名生成字段名称"""
        # 常见字段名称映射
        field_mapping = {
            "name": "名称",
            "title": "标题",
            "description": "描述",
            "content": "内容",
            "status": "状态",
            "type": "类型",
            "category": "分类",
            "price": "价格",
            "amount": "数量",
            "weight": "重量",
            "size": "尺寸",
            "color": "颜色",
            "brand": "品牌",
            "model": "型号",
            "serial": "序列号",
            "code": "代码",
            "url": "链接",
            "image": "图片",
            "avatar": "头像",
            "email": "邮箱",
            "phone": "电话",
            "mobile": "手机",
            "address": "地址",
            "city": "城市",
            "province": "省份",
            "country": "国家",
            "zipcode": "邮编",
            "username": "用户名",
            "password": "密码",
            "created_at": "创建时间",
            "updated_at": "更新时间",
            "deleted_at": "删除时间",
            "is_active": "是否激活",
            "is_deleted": "是否删除",
            "sort_order": "排序",
            "parent_id": "父级ID",
            "level": "层级",
            "path": "路径",
            "remark": "备注",
            "note": "备注",
            "memo": "备注"
        }
        
        # 如果列名在映射中，直接返回
        if column_name.lower() in field_mapping:
            return field_mapping[column_name.lower()]
        
        # 否则尝试从下划线分隔的名称生成
        words = column_name.split('_')
        if len(words) > 1:
            # 尝试翻译每个单词
            translated_words = []
            for word in words:
                if word.lower() in field_mapping:
                    translated_words.append(field_mapping[word.lower()])
                else:
                    translated_words.append(word)
            return ''.join(translated_words)
        
        # 最后返回原列名
        return column_name
