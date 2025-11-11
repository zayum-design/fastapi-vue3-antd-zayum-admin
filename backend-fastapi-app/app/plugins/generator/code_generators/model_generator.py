from typing import List, Literal, Optional, Set
import logging
from datetime import date, datetime
from sqlalchemy import (DECIMAL, SMALLINT, TEXT, DATE, 
    DATETIME, UniqueConstraint, JSON, text, Table, FetchedValue,
    String, Enum as SqlEnum
)
from sqlalchemy.types import BOOLEAN, INTEGER, SMALLINT, VARCHAR, TypeEngine
from sqlalchemy.orm import Mapped, mapped_column, validates
from fastapi_babel import _

logger = logging.getLogger(__name__)

def generate_model_code(table: 'Table', exclude_columns: Optional[List[str]] = None) -> str:
    exclude_columns_set: Set[str] = set(exclude_columns) if exclude_columns else set()
    exclude_columns_set |= {"created_at", "updated_at"}

    # Common field names for validation
    EMAIL_FIELDS = ['email', 'e_mail', 'mail']
    MOBILE_FIELDS = ['mobile', 'phone', 'telephone', 'cellphone']
    USERNAME_FIELDS = ['username', 'login', 'user_name', 'account']
    URL_FIELDS = ['avatar', 'image', 'url', 'link', 'website', 'photo']
    PASSWORD_FIELDS = ['password', 'passwd', 'pwd']
    NAME_FIELDS = ['name', 'fullname', 'nickname', 'display_name']
    ID_FIELDS = ['id_card', 'identity', 'identification', 'ssn']

    class_name = "".join(word.capitalize() for word in table.name.split("_"))
    primary_key_columns = [col.name for col in table.primary_key.columns]

    imports = [
        "import re",
        "import logging",
        "import bcrypt",
        "from typing import Literal, Optional",
        "from datetime import date, datetime",
        "from sqlalchemy import (",
        "    FetchedValue, String, Integer, Boolean, DateTime, DECIMAL, SMALLINT, TEXT, DATE, DATETIME, UniqueConstraint, CheckConstraint, JSON, Enum, text",
        ")",
        "from sqlalchemy.orm import Mapped, mapped_column, validates",
        "from .mixins import TimestampMixin",
        "from app.models import Base",
        "from fastapi_babel import _",
        "",
        "logger = logging.getLogger(__name__)",
        "",
        "# ENUM definitions",
    ]

    enum_definitions = []
    column_definitions = []
    constraints = []
    unique_constraints = [c for c in table.constraints if isinstance(c, UniqueConstraint)]

    enum_fields = {}
    for col in table.columns:
        if isinstance(col.type, SqlEnum) and col.name.lower() not in exclude_columns_set:
            enum_var_name = f"{col.name.capitalize()}Enum"
            enum_values = col.type.enums
            enum_fields[col.name] = enum_var_name
            enum_str = f'{enum_var_name} = Enum({", ".join(repr(v) for v in enum_values)}, name="{col.name.lower()}_enum", create_constraint=True)'
            enum_definitions.append(enum_str)

    if unique_constraints:
        uc_list = []
        for uc in unique_constraints:
            cols = ", ".join(f"'{col.name}'" for col in uc.columns)
            uc_list.append(f"UniqueConstraint({cols}, name='{uc.name}')")
        constraints.append(f"    __table_args__ = ({', '.join(uc_list)},)")
    else:
        constraints.append("    __table_args__ = ()")

    class_def = [f"class {class_name}(TimestampMixin, Base):"]
    class_def.append(f"    __tablename__ = '{table.name}'")
    class_def.extend(constraints)
    class_def.append("")

    # Track password field for special handling
    has_password = False

    for col in table.columns:
        if col.name.lower() in exclude_columns_set:
            continue

        col_name = col.name
        col_type = col.type
        nullable = col.nullable
        primary_key = col.primary_key
        default = col.server_default.arg if col.server_default else None
        server_default = col.server_default if col.server_default else None

        # Initialize column_name_in_db for all cases
        column_name_in_db: str = col.name
        
        # Check if this is a password field
        if any(field in col_name.lower() for field in PASSWORD_FIELDS):
            has_password = True
            col_name = '_password'  # Use private attribute convention

        # Determine type annotation and column type
        if isinstance(col_type, SqlEnum):
            enum_var_name = enum_fields[col_name]
            literal_type = f"Literal[{', '.join(repr(v) for v in col_type.enums)}]"
            py_type = literal_type
            column_type = enum_var_name
        elif isinstance(col_type, BOOLEAN):
            py_type = "bool"
            column_type = "Boolean"
        elif isinstance(col_type, INTEGER):
            py_type = "int"
            column_type = "Integer"
        elif isinstance(col_type, SMALLINT):
            py_type = "int"
            column_type = "SMALLINT"
        elif isinstance(col_type, TEXT):
            py_type = "str"
            column_type = "TEXT"
        elif isinstance(col_type, VARCHAR):
            py_type = "str"
            column_type = f"String({col_type.length})"
        elif isinstance(col_type, DATE):
            py_type = "date"
            column_type = "DATE"
        elif isinstance(col_type, DATETIME):
            py_type = "datetime"
            column_type = "DATETIME"
        elif isinstance(col_type, DECIMAL):
            py_type = "float"
            column_type = f"DECIMAL({col_type.precision}, {col_type.scale})"
        elif isinstance(col_type, JSON):
            py_type = "dict"
            column_type = "JSON"
        else:
            py_type = "str"
            column_type = "VARCHAR(200)"

        # Handle password field specially
        if col_name == '_password':
            line = f"    {col_name}: Mapped[Optional[str]] = mapped_column('{column_name_in_db}', {column_type}, nullable=True"
        else:
            line = f"    {col_name}: Mapped[{py_type}] = mapped_column({column_type}"
            if not nullable:
                line += ", nullable=False"
            else:
                line += ", nullable=True"

            if primary_key:
                line += ", primary_key=True"
                if len(primary_key_columns) == 1 and isinstance(col_type, (INTEGER, SMALLINT)):
                    line += ", autoincrement=True"

            if server_default is not None:
                # Handle server default value
                if isinstance(server_default, FetchedValue):
                    line += ", server_default=FetchedValue()"
                else:
                    try:
                        if hasattr(server_default, 'arg'):
                            default_value = str(server_default.arg)
                        else:
                            default_value = str(server_default)
                        line += f", server_default=text({repr(default_value)})"
                    except Exception:
                        line += ", server_default=None"

        line += ")"
        column_definitions.append(line)

        # Skip validation for nullable fields
        if nullable:
            continue

        # Add validation based on field name and type
        if isinstance(col_type, VARCHAR) and col.name.lower() not in exclude_columns_set:
            validation_rule = None
            lower_col_name = col_name.lower()
            
            # Only create one validator per column - prioritize more specific validations
            if any(field in lower_col_name for field in EMAIL_FIELDS):
                validation_rule = f"""
    @validates("{col_name}")
    def validate_{col_name}(self, key, address):
        if not address:
            raise ValueError(_("Email is required"))
        if "@" not in address:
            logger.error(f"Invalid email address provided: {{address}}")
            raise ValueError(_("Invalid email address"))
        if len(address) > {col_type.length}:
            logger.error(f"Email too long: {{address}} (max {col_type.length} chars)")
            raise ValueError(_(f"Email too long (max {col_type.length} characters)"))
        return address
                """
            elif any(field in lower_col_name for field in MOBILE_FIELDS) and col_type.length == 11:
                validation_rule = f"""
    @validates("{col_name}")
    def validate_{col_name}(self, key, mobile):
        if not mobile:
            raise ValueError(_("Mobile number is required"))
        if not mobile.isdigit():
            logger.error(f"Mobile number contains non-digit characters: {{mobile}}")
            raise ValueError(_("Mobile number must contain only digits"))
        if len(mobile) != 11:
            logger.error(f"Mobile number length is not 11 digits: {{mobile}}")
            raise ValueError(_("Mobile number must be 11 digits long"))
        return mobile
                """
            elif any(field in lower_col_name for field in USERNAME_FIELDS):
                validation_rule = f"""
    @validates("{col_name}")
    def validate_{col_name}(self, key, username):
        if not username:
            raise ValueError(_("Username is required"))
        if not username.isalnum():
            logger.error(f"Username contains non-alphanumeric characters: {{username}}")
            raise ValueError(_("Username must be alphanumeric"))
        if len(username) > {col_type.length}:
            logger.error(f"Username too long: {{username}} (max {col_type.length} chars)")
            raise ValueError(_(f"Username too long (max {col_type.length} characters)"))
        return username
                """
            elif any(field in lower_col_name for field in URL_FIELDS):
                validation_rule = f"""
    @validates("{col_name}")
    def validate_{col_name}(self, key, url):
        if not url:
            raise ValueError(_("URL is required"))
        if not (url.startswith('http://') or url.startswith('https://')):
            logger.error(f"Invalid URL format: {{url}}")
            raise ValueError(_("URL must start with http:// or https://"))
        if len(url) > {col_type.length}:
            logger.error(f"URL too long: {{url}} (max {col_type.length} chars)")
            raise ValueError(_(f"URL too long (max {col_type.length} characters)"))
        return url
                """
            elif any(field in lower_col_name for field in NAME_FIELDS):
                validation_rule = f"""
    @validates("{col_name}")
    def validate_{col_name}(self, key, name):
        if not name:
            raise ValueError(_("Name is required"))
        if not re.match(r'^[\\w\\s\\-\\.]+$', name):
            logger.error(f"Invalid characters in name: {{name}}")
            raise ValueError(_("Name contains invalid characters"))
        if len(name) > {col_type.length}:
            logger.error(f"Name too long: {{name}} (max {col_type.length} chars)")
            raise ValueError(_(f"Name too long (max {col_type.length} characters)"))
        return name
                """
            elif any(field in lower_col_name for field in ID_FIELDS):
                validation_rule = f"""
    @validates("{col_name}")
    def validate_{col_name}(self, key, id_number):
        if not id_number:
            raise ValueError(_("ID is required"))
        if not re.match(r'^[\\w\\d\\-]+$', id_number):
            logger.error(f"Invalid characters in ID: {{id_number}}")
            raise ValueError(_("ID contains invalid characters"))
        if len(id_number) > {col_type.length}:
            logger.error(f"ID too long: {{id_number}} (max {col_type.length} chars)")
            raise ValueError(_(f"ID too long (max {col_type.length} characters)"))
        return id_number
                """
            else:
                # Generic length validation for other non-nullable string fields
                if col_type.length and col_type.length < 255:
                    validation_rule = f"""
    @validates("{col_name}")
    def validate_{col_name}_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > {col_type.length}:
            logger.error(f"Value too long for {{key}}: {{value}} (max {col_type.length} chars)")
            raise ValueError(_(f"Value too long (max {col_type.length} characters)"))
        return value
                    """
            
            if validation_rule:
                column_definitions.append(validation_rule)

    # __repr__ method
    if len(primary_key_columns) == 1:
        pk = primary_key_columns[0]
        repr_str = f"    def __repr__(self):\n        return f'<{class_name}({pk}={{self.{pk}}})>'"
    else:
        pk_repr = ", ".join([f"{pk}={{self.{pk}}}" for pk in primary_key_columns])
        repr_str = f"    def __repr__(self):\n        return f'<{class_name}({pk_repr})>'"

    # from_dict method
    valid_keys = {
        col.name for col in table.columns if col.name.lower() not in exclude_columns_set
    }
    from_dict_str = f"""
    @classmethod
    def from_dict(cls, data: dict) -> '{class_name}':
        valid_keys = {valid_keys}
        filtered_data = {{key: value for key, value in data.items() if key in valid_keys}}
        return cls(**filtered_data)
    """

    # to_dict method
    to_dict_str = f"""
    def to_dict(self) -> dict:
        result_dict = {{}}
        for column in self.__table__.columns:
            if column.key in {PASSWORD_FIELDS}:
                continue
            value = getattr(self, column.key, None)
            result_dict[column.key] = value
        return result_dict
    """

    # Add password property if password field exists
    password_property = ""
    if has_password:
        password_property = f"""
    @property
    def password(self):
        '''密码属性（只读）'''
        return self._password
    
    @password.setter
    def password(self, pw: str):
        '''设置用户密码，并进行加密'''
        if not pw:
            raise ValueError(_("Password cannot be empty"))
        if len(pw) < 8:
            raise ValueError(_("Password must be at least 8 characters"))
        pw_hash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
        self._password = pw_hash.decode('utf8')

    def check_password(self, pw: str) -> bool:
        '''校验用户密码'''
        if not pw:
            return False
        if len(pw) < 8:
            return False
        if self._password:
            try:
                expected_hash = self._password.encode('utf8')
                return bcrypt.checkpw(pw.encode('utf8'), expected_hash)
            except ValueError:
                return False
        return False
        """

    # Combine all parts
    lines = imports + enum_definitions + [""] + class_def + column_definitions + ["", repr_str, from_dict_str, "", to_dict_str]
    
    if password_property:
        lines.append(password_property)
    
    model_code = "\n".join(lines)

    return model_code
