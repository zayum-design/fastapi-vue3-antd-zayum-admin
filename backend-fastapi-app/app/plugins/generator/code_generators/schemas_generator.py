import datetime
import decimal
import enum
import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import (
    BOOLEAN,
    DATE,
    DATETIME,
    DECIMAL,
    INTEGER,
    SMALLINT,
    TEXT,
    VARCHAR,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    inspect,
    MetaData,
    Table,
    Enum as SqlEnum,
    JSON,
)
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
from pathlib import Path
from app.utils.responses import success_response
from app.dependencies.database import get_db
from app.core.security import get_current_admin
from app.utils.utils import snake_to_human_readable_special
from app.utils.log_utils import logger


def generate_schemas(table: Table) -> str:
    class_name = "".join(word.capitalize() for word in table.name.split("_"))
    columns = table.columns

    # Start building the schema string
    schemas = (
        "from datetime import datetime, date, timezone\n"
        "from decimal import Decimal\n"
        "from typing import Optional, Literal\n"
        "from pydantic import BaseModel, Field, EmailStr, field_validator\n"
        "from fastapi_babel import _\n"
        "import re\n\n\n"
    )

    # Base schema
    schemas += f"class {class_name}Base(BaseModel):\n"
    for col in columns:
        col_name = col.name
        col_type = map_sql_type_to_pydantic(col)
        nullable = col.nullable

        # Handle Optional fields
        if nullable or col.default is not None:
            type_annotation = f"Optional[{col_type}]"
            default = " = None"
        else:
            type_annotation = col_type
            default = " = Field(...)"

        # Handle special cases

        if col_name.lower() in ["created_at", "updated_at"]:
            type_annotation = "datetime"
            default = " = Field(default_factory=lambda: datetime.now(timezone.utc))"
            field_definition = f"    {col_name}: {type_annotation}{default}"
        elif "email" in col_name.lower():
            field_type = "EmailStr"
            if nullable or col.default is not None:
                type_annotation = f"Optional[{field_type}]"
                default = " = None"
            else:
                type_annotation = field_type
                default = " = Field(...)"
            field_definition = f"    {col_name}: {type_annotation}{default}"
        elif col_name.lower() in ["gender", "status"]:
            # Example literals, you might need to customize based on actual enums
            if col_name.lower() == "gender":
                literals = "'female', 'male'"
            elif col_name.lower() == "status":
                literals = "'normal', 'hidden'"
            type_annotation = f"Literal[{literals}]"
            if nullable or col.default is not None:
                type_annotation = f"Optional[{type_annotation}]"
                default = " = None"
            field_definition = f"    {col_name}: {type_annotation}{default}"
        else:
            field_definition = f"    {col_name}: {type_annotation}{default}"

        # Handle max_length for String types
        if isinstance(col.type, String):
            max_length = (
                col.type.length
                if hasattr(col.type, "length") and col.type.length
                else None
            )
            if "max_length" not in field_definition:
                if "Field(...)" in field_definition or "Field(None" in field_definition:
                    # 提取 Field 的参数部分
                    default_value = default.split('=')[1].strip()
                    field_args = [default_value]
                    if max_length is not None:
                        field_args.append(f"max_length={max_length}")
                    field_args_str = ", ".join(field_args)
                    field_definition = f"    {col_name}: {type_annotation} = Field({field_args_str})"
    


        schemas += field_definition + "\n"

    # Add validators
    validators = generate_field_validators(columns)
    schemas += validators

    # Config class
    schemas += "\n    class Config:\n"
    schemas += "        orm_mode = True\n"
    schemas += "        arbitrary_types_allowed = True\n"
    # Add json_encoders if needed, e.g., for Decimal
    has_decimal = any(isinstance(col.type, (DECIMAL, Float)) for col in columns)
    if has_decimal:
        schemas += "        json_encoders = {\n"
        schemas += "            Decimal: lambda v: str(v)\n"
        schemas += "        }\n"

    schemas += "\n\n"

    # Create schema
    schemas += f"class {class_name}Create({class_name}Base):\n"
    schemas += "    pass\n\n"

    # Update schema
    schemas += f"class {class_name}Update(BaseModel):\n"
    for col in columns:
        col_name = col.name
        if col_name.lower() in ["id", "created_at", "updated_at"]:
            continue  # Typically, these fields are not updated directly
        col_type = map_sql_type_to_pydantic(col)
        
        # Make all fields optional in Update
        if "email" in col_name.lower():
            field_type = "EmailStr"
            type_annotation = f"Optional[{field_type}]"
            default = " = None"
        elif col_name.lower() in ["gender", "status"]:
            if col_name.lower() == "gender":
                literals = "'female', 'male'"
            elif col_name.lower() == "status":
                literals = "'normal', 'hidden'"
            type_annotation = f"Optional[Literal[{literals}]]"
            default = " = None"
        else:
            type_annotation = f"Optional[{col_type}]"
            default = " = None"

        # Handle max_length for String types
        if isinstance(col.type, String):
            max_length = (
                col.type.length
                if hasattr(col.type, "length") and col.type.length
                else None
            )
            if max_length is not None:
                field_definition = f"    {col_name}: {type_annotation} = Field(None, max_length={max_length})"
            else:
                field_definition = f"    {col_name}: {type_annotation} = Field(None)"
        else:
            field_definition = f"    {col_name}: {type_annotation}{default}"


        schemas += field_definition + "\n"

    # Add validators for Update schema if needed
    # Optionally, reuse the same validators as Base

    schemas += "\n    class Config:\n"
    schemas += "        orm_mode = True\n\n"

    # InDBBase schema
    schemas += f"class {class_name}InDBBase({class_name}Base):\n"
    schemas += "    pass\n\n"

    # Final schema
    schemas += f"class {class_name}({class_name}InDBBase):\n    pass\n\n"

    return schemas


def map_sql_type_to_pydantic(col: Column) -> str:
    """Map SQLAlchemy column types to Pydantic types."""
    if isinstance(col.type, SqlEnum):
        enum_values = [f"'{e}'" for e in col.type.enums]
        return f"Literal[{', '.join(enum_values)}]"
    elif isinstance(col.type, Boolean):
        return "bool"
    elif isinstance(col.type, Integer):
        return "int"
    elif isinstance(col.type, String):
        return "str"
    elif isinstance(col.type, DateTime):
        return "datetime"
    elif isinstance(col.type, DECIMAL) or isinstance(col.type, Float):
        return "Decimal"
    elif isinstance(col.type, JSON):  # Handle JSON type
        return "dict"
    elif "email" in col.name.lower():
        return "EmailStr"
    else:
        return "str"



def generate_field_validators(columns: List[Column]) -> str:
    """Generate field validators based on column names and types."""
    validators = ""
    for col in columns:
        col_name = col.name
        col_type = col.type

        # Username Validator
        if col_name.lower() == "username":
            validators += f"""
    @field_validator('{col_name}')
    def validate_{col_name}(cls, v):
        if not re.match(r'^[A-Za-z][A-Za-z0-9_]{{2,31}}$', v):
            raise ValueError(_('Username must start with a letter, can contain letters, numbers, and underscores, and be 3-32 characters long.'))
        return v
"""

        # Password Validator
        if col_name.lower() == "password":
            validators += f"""
    @field_validator('{col_name}')
    def validate_{col_name}(cls, v):
        if len(v) < 6:
            raise ValueError(_('Password must be at least 6 characters long.'))
        if not re.search(r'[A-Z]', v):
            raise ValueError(_('Password must contain at least one uppercase letter.'))
        if not re.search(r'[a-z]', v):
            raise ValueError(_('Password must contain at least one lowercase letter.'))
        if not re.search(r'\\d', v):
            raise ValueError(_('Password must contain at least one digit.'))
        return v
"""

        # Email Validator
        if "email" in col_name.lower():
            validators += f"""
    @field_validator('{col_name}')
    def validate_{col_name}(cls, v):
        email_regex = r'^[A-Za-z0-9\\._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{{2,}}$'
        if not re.match(email_regex, v) or len(v) > 100:
            raise ValueError(_('A valid email address is required.'))
        return v
"""

        # Mobile Validator
        if col_name.lower() == "mobile":
            validators += f"""
    @field_validator('{col_name}')
    def validate_{col_name}(cls, v):
        if not v.isdigit():
            raise ValueError(_('Mobile number must contain only digits.'))
        if not (10 <= len(v) <= 16):
            raise ValueError(_('Mobile number must be between 10 and 16 digits long.'))
        return v
"""

        # Gender Validator
        if col_name.lower() == "gender":
            validators += f"""
    @field_validator('{col_name}')
    def validate_{col_name}(cls, v):
        if v not in ['female', 'male']:
            raise ValueError(_('{col_name.upper()} should be either female or male'))
        return v
"""

        # Status Validator
        if col_name.lower() == "status":
            validators += f"""
    @field_validator('{col_name}')
    def validate_{col_name}(cls, v):
        if v not in ['normal', 'hidden']:
            raise ValueError(_('{col_name.upper()} should be either normal or hidden'))
        return v
"""

        # Add more validators as needed based on column names and requirements

    return validators
