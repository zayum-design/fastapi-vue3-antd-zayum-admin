"""
代码生成器配置
"""

from typing import List, Set


class GeneratorConfig:
    """代码生成器配置类"""
    
    # 排除的字段名
    EXCLUDED_COLUMNS: Set[str] = {"created_at", "updated_at"}
    
    # 字段类型映射
    EMAIL_FIELDS: List[str] = ['email', 'e_mail', 'mail']
    MOBILE_FIELDS: List[str] = ['mobile', 'phone', 'telephone', 'cellphone']
    USERNAME_FIELDS: List[str] = ['username', 'login', 'user_name', 'account']
    URL_FIELDS: List[str] = ['avatar', 'image', 'url', 'link', 'website', 'photo']
    PASSWORD_FIELDS: List[str] = ['password', 'passwd', 'pwd']
    NAME_FIELDS: List[str] = ['name', 'fullname', 'nickname', 'display_name']
    ID_FIELDS: List[str] = ['id_card', 'identity', 'identification', 'ssn']
    
    # 分页配置
    MAX_PER_PAGE: int = 200
    DEFAULT_PER_PAGE: int = 10
    
    # 操作配置
    DEFAULT_OPERATIONS: str = 'create,read,update,delete'
    DEFAULT_FIELDS: str = 'all'
