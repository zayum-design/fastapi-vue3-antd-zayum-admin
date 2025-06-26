# server-app/app/plugins/generator/plugin.py
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

router = APIRouter()


# Pydantic models


class TablesResponse(BaseModel):
    code: int
    msg: str
    data: List[str]
    time: str


class FieldInfo(BaseModel):
    name: str
    type: str


class CodeGeneration(BaseModel):
    field_info: List[FieldInfo]
    model_code: str
    crud_code: str
    schemas_code: str
    api_code: str
    vue_code: str
    vue_i18n_json: str


class CodeGenerationResponse(BaseModel):
    code: int
    msg: str
    data: CodeGeneration
    time: str


# Get all table names
@router.get("/tables", tags=["generator"], response_model=TablesResponse)
def get_tables(db: Session = Depends(get_db)):
    try:
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        return success_response(tables)
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching tables: {str(e)}",
        )


# Generate code for a specific table
@router.get(
    "/code/{table_name}", tags=["generator"], response_model=CodeGenerationResponse
)
def generate_code(
    table_name: str,  
    fields: Optional[str] = 'all',
    operations:Optional[str] = 'create,read,update,delete',
    db: Session = Depends(get_db)
) -> CodeGenerationResponse:
    try:
        inspector = inspect(db.bind)
        if table_name not in inspector.get_table_names():
            raise HTTPException(
                status_code=404, detail=f"Table {table_name} not found in the database."
            )

        columns = inspector.get_columns(table_name)
        field_info = [
            FieldInfo(name=col["name"], type=str(col["type"])) for col in columns
        ]

        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=db.bind)

        model_code = generate_model_code(table)
        crud_code = generate_crud_code(inspector, table)
        schemas_code = generate_schemas(table)
        api_code = generate_crud_endpoints(table)
        vue_code = generate_vue_code(table,fields,operations)
        vue_i18n_json = generate_vue_i18n_json(table)

        return CodeGenerationResponse(
            code=0,
            msg="Code generation successful",
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
            detail=f"Error generating code for {table_name}: {str(e)}",
        )


import re
from pathlib import Path
from typing import Dict, List, Union
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.types import TypeEngine


def map_sql_type_to_ts(sql_type: TypeEngine) -> str:
    """Map SQL type to TypeScript type."""
    type_name = str(sql_type).lower()
    if "int" in type_name or "serial" in type_name:
        return "number"
    elif "decimal" in type_name or "numeric" in type_name or "float" in type_name or "double" in type_name:
        return "number"
    elif "bool" in type_name:
        return "boolean"
    elif "date" in type_name or "time" in type_name:
        return "string"
    elif "json" in type_name:
        return "any"
    else:
        return "string"


def default_value(sql_type: TypeEngine, server_default: str = None) -> str:
    """Get default value for a field based on its type."""
    type_name = str(sql_type).lower()
    
    if server_default:
        if server_default.startswith("'") and server_default.endswith("'"):
            return f"'{server_default[1:-1]}'"
        return server_default
    
    if "int" in type_name or "decimal" in type_name or "numeric" in type_name or "float" in type_name:
        return "0"
    elif "bool" in type_name:
        return "false"
    elif "date" in type_name or "time" in type_name:
        return "null"
    else:
        return "''"


def generate_vue_code(table: 'Table',
                      fields: str,
                      operations: str = 'create,read,update,delete') -> str:
    class_name = "".join(word.capitalize() for word in table.name.split("_")).replace(
        "Sys", ""
    )
    table_name = table.name
    api_table_name = table_name.replace("sys_", "")  # Remove 'sys_' prefix

    template_path = Path(__file__).parent / "template" / "vue_template" / "page.vue.tpl"
    if not template_path.exists():
        raise Exception(f"Template file not found at {template_path}")

    template = template_path.read_text()

    # Prepare fields
    form_items = ""
    form_rules = ""
    columns = ""
    interface_fields = ""
    current_item_fields = ""
    reset_fields = ""
    payload_fields = ""
    validation_checks = ""
    time_field_handlers = ""  # 用于处理时间字段的代码
    table_dot = api_table_name.replace("_", ".")

    # Common field patterns and their validation rules
    COMMON_FIELD_PATTERNS = {
        # Email fields
        'email': [
            "{ required: true, message: $t('{table_dot}.rules.email.required') }",
            "{ type: 'email', message: $t('{table_dot}.rules.email.invalid_format') }"
        ],
        # Phone/mobile fields
        'mobile|phone': [
            "{ required: true, message: $t('{table_dot}.rules.mobile.required') }",
            "{ pattern: /^1[3-9]\\d{9}$/, message: $t('{table_dot}.rules.mobile.invalid_format') }"
        ],
        # Password fields - 优化后的密码验证规则，使用 Promise 风格
        'password': [
            "{ required: mode.value === 'add', message: $t('{table_dot}.rules.required') }",
            "{ validator: (_: any, value: string) => {"
            "  const errors = [];"
            "  if (mode.value === 'edit' && !value) return Promise.resolve();"
            "  if (value && value.length < 6) errors.push($t('{table_dot}.rules.password.password_min_length'));"
            "  if (value && !/[A-Z]/.test(value)) errors.push($t('{table_dot}.rules.password.password_uppercase_required'));"
            "  if (value && !/[a-z]/.test(value)) errors.push($t('{table_dot}.rules.password.password_lowercase_required'));"
            "  if (value && !/\\d/.test(value)) errors.push($t('{table_dot}.rules.password.password_digit_required'));"
            "  return errors.length > 0 ? Promise.reject(errors.join('，')) : Promise.resolve();"
            "}}"
        ],
        # Username fields
        'username|account': [
            "{ required: true, message: $t('{table_dot}.rules.username.required') }",
            "{ min: 3, message: $t('{table_dot}.rules.username.min_length') }",
            "{ max: 20, message: $t('{table_dot}.rules.username.max_length') }",
            "{ pattern: /^[a-zA-Z0-9_]+$/, message: $t('{table_dot}.rules.username.invalid_chars') }"
        ],
        # Name fields
        'name|nickname|title': [
            "{ required: true, message: $t('{table_dot}.rules.nickname.required') }",
            "{ min: 2, message: $t('{table_dot}.rules.nickname.min_length') }",
            "{ max: 30, message: $t('{table_dot}.rules.nickname.max_length') }"
        ],
        # ID fields - 优化为 Promise 风格
        'group_id': [
            "{ required: true, message: $t('{table_dot}.rules.id.required') }",
            "{ validator: (_: any, value: number) => {"
            "  if (isNaN(value) || value <= 0) return Promise.reject($t('{table_dot}.rules.group_id.must_be_positive'));"
            "  return Promise.resolve();"
            "}}"
        ],
        # Status fields
        'status|state': [
            "{ required: true, message: $t('{table_dot}.rules.status.required') }"
        ],
        # Numeric fields - 优化为 Promise 风格
        'num|count|amount|price|total': [
            "{ validator: (_: any, value: number) => {",
            "  if (isNaN(value)) return Promise.reject($t('{table_dot}.rules.numeric.field_must_be_number'));",
            "  if (value < 0) return Promise.reject($t('{table_dot}.rules.numeric.must_be_non_negative'));",
            "  return Promise.resolve();",
            "}}"
        ],
        # URL fields
        'url|link|website': [
            "{ pattern: /^(https?:\\/\\/)?([\\da-z\\.-]+)\\.([a-z\\.]{2,6})([\\/\\w \\.-]*)*\\/?$/, message: $t('{table_dot}.rules.url.invalid_format') }"
        ]
    }

    for col in table.columns:
        field_name = col.name
        field_type = str(col.type)
        comment = str(col.comment)
        nullable = col.nullable
        python_default = (
            col.default.arg if col.default else None
        )  # Python-level default
        server_default = (
            str(col.server_default.arg) if col.server_default else None
        )  # Server-level default
        ts_type = map_sql_type_to_ts(col.type)

        # Interface fields
        if nullable:
            if "datetime" in field_type.lower() or "timestamp" in field_type.lower() or "date" in field_type.lower():
                interface_fields += f"{field_name}: string | null;\n  "
            else:
                interface_fields += f"{field_name}: {ts_type} | null;\n  "
        else:
            if "datetime" in field_type.lower() or "timestamp" in field_type.lower() or "date" in field_type.lower():
                interface_fields += f"{field_name}: string;\n  "
            else:
                interface_fields += f"{field_name}: {ts_type};\n  "

        # Current item fields
        current_item_fields += (
            f"{field_name}: {default_value(col.type, server_default)},\n      "
        )

        # Form items
        if field_name == "id":
            form_items += f"""
        <a-form-item :label="$t('{table_dot}.field.{field_name}')" v-if="mode !== 'add'">
        <a-input v-model:value="currentItem.{field_name}" :disabled="true" />
        </a-form-item>
            """
        elif field_name.lower() == "password":  # 处理 password 字段
            form_items += f"""
        <a-form-item :label="$t('{table_dot}.field.{field_name}')" name="{field_name}" :rules="formRules.{field_name}">
        <a-input-password
            v-model:value="currentItem.{field_name}"
            :disabled="mode === 'view'"
            placeholder="请输入密码"
        />
        </a-form-item>
            """
        elif isinstance(col.type, SqlEnum):
            # Handle enum fields with <a-select>
            enum_values = col.type.enums  # Extract enum values from SqlEnum type
            if enum_values:
                options = "\n".join(
                    f'<a-select-option value="{value}">{{{{ $t("common.{value}") }}}}</a-select-option>'
                    for value in enum_values
                )
                form_items += f"""
        <a-form-item :label="$t('{table_dot}.field.{field_name}')" {f'name="{field_name}" :rules="formRules.{field_name}"' if not nullable and field_name != "id" else ''}>
        <a-select
            v-model:value="currentItem.{field_name}"
            :disabled="mode === 'view'"
        >
            {options}
        </a-select>
        </a-form-item>
                """
            else:
                # Fallback to <a-input> if enum values are empty
                form_items += f"""
        <a-form-item :label="$t('{table_dot}.field.{field_name}')" {f'name="{field_name}" :rules="formRules.{field_name}"' if not nullable and field_name != "id" else ''}>
        <a-input v-model:value="currentItem.{field_name}" :disabled="mode === 'view'" />
        </a-form-item>
                """
        elif "datetime" in field_type.lower() or "timestamp" in field_type.lower():
            # Use a-date-picker for datetime fields
            form_items += f"""
        <a-form-item :label="$t('{table_dot}.field.{field_name}')" name="{field_name}">
        <a-date-picker
            v-model:value="currentItem.{field_name}"
            show-time
            :disabled="mode === 'view'"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
        />
        </a-form-item>
            """
            # 添加时间字段处理逻辑
            time_field_handlers += f"""
    if (currentItem.{field_name}) {{
        item.{field_name} = dayjs(currentItem.{field_name}).tz(TIME_ZONE);
    }}
            """
        elif "date" in field_type.lower():
            # Use a-date-picker for date fields (without time)
            form_items += f"""
        <a-form-item :label="$t('{table_dot}.field.{field_name}')" name="{field_name}">
        <a-date-picker
            v-model:value="currentItem.{field_name}"
            :disabled="mode === 'view'"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
        />
        </a-form-item>
            """
        else:
            form_items += f"""
        <a-form-item :label="$t('{table_dot}.field.{field_name}')" {f'name="{field_name}" :rules="formRules.{field_name}"' if not nullable and field_name != "id" else ''}>
        <a-input v-model:value="currentItem.{field_name}" :disabled="mode === 'view'" />
        </a-form-item>
            """

        # Form rules
        if not nullable and field_name != "id":
            rules = []
            matched_pattern = False
            
            # Check for common field patterns
            for pattern, pattern_rules in COMMON_FIELD_PATTERNS.items():
                if re.search(pattern, field_name, re.IGNORECASE):
                    matched_pattern = True
                    for rule in pattern_rules:
                        # 确保替换后的规则格式正确
                        formatted_rule = rule.replace("{table_dot}", table_dot)
                        # 移除可能的多余逗号
                        formatted_rule = formatted_rule.replace(",\n", "\n").strip()
                        rules.append(formatted_rule)
                    break
            
            # Default rules for fields not matching any pattern
            if not matched_pattern:
                # Basic required rule
                rules.append(f"{{ required: true, message: $t('{table_dot}.rules.{field_name}.required') }}")
                
                # Type-specific rules
                if isinstance(col.type, SqlEnum):
                    pass  # Enums don't need additional validation
                elif hasattr(col.type, "python_type"):
                    py_type = col.type.python_type
                    if py_type == int or py_type == float:
                        rules.append(
                            "{ validator: (_: any, value: number) => {\n"
                            f"  if (isNaN(value)) return Promise.reject($t('{table_dot}.rules.{field_name}.must_be_number'));\n"
                            "  return Promise.resolve();\n"
                            "}}"
                        )
                    elif py_type == str:
                        # For string fields, add length limits if they're not already handled by patterns
                        if not any(p in field_name.lower() for p in ['email', 'mobile', 'phone', 'url']):
                            rules.append(f"{{ max: 255, message: $t('{table_dot}.rules.{field_name}.max_length') }}")

            # Generate the rules block
            if rules:
                # 对多行规则进行特殊处理
                formatted_rules = []
                for rule in rules:
                    if '\n' in rule:
                        # 多行规则，添加适当缩进
                        lines = rule.split('\n')
                        formatted_rule = lines[0]
                        for line in lines[1:]:
                            formatted_rule += "\n    " + line.strip()
                        formatted_rules.append(formatted_rule)
                    else:
                        formatted_rules.append(rule)
                
                rules_str = ",\n    ".join(formatted_rules)
                form_rules += f"  {field_name}: [\n    {rules_str}\n  ],\n"

        # Columns
        if (fields!='all' and fields!='' and fields!=None):
            if (field_name in fields.split(',')):
                if field_name.lower() == "password":  # 不显示密码明文
                    columns += f"""{{ title: $t('{table_dot}.field.{field_name}'), dataIndex: '{field_name}', key: '{field_name}', customRender: () => '******' }},\n"""
                else:
                    columns += f"""{{ title: $t('{table_dot}.field.{field_name}'), dataIndex: '{field_name}', key: '{field_name}' }},\n"""
        else:
            if field_name.lower() == "password":  # 不显示密码明文
                columns += f"""{{ title: $t('{table_dot}.field.{field_name}'), dataIndex: '{field_name}', key: '{field_name}', customRender: () => '******' }},\n"""
            else:
                columns += f"""{{ title: $t('{table_dot}.field.{field_name}'), dataIndex: '{field_name}', key: '{field_name}' }},\n"""
        # Payload fields
        if field_name != "id":
            if "datetime" in field_type.lower() or "timestamp" in field_type.lower():
                payload_fields += f"{field_name}: currentItem.{field_name} ? dayjs(currentItem.{field_name}).format('YYYY-MM-DD HH:mm:ss') : null,\n      "
            elif "date" in field_type.lower():
                payload_fields += f"{field_name}: currentItem.{field_name} ? dayjs(currentItem.{field_name}).format('YYYY-MM-DD') : null,\n      "
            else:
                payload_fields += f"{field_name}: currentItem.{field_name},\n      "
                
        # Validation checks
        if not nullable and field_name != "id":
            validation_checks += f"if (!currentItem.{field_name}) {{\n    message.error($t('common.field_required'));\n    return;\n  }}\n      "

        # Reset fields
        if "datetime" in field_type.lower() or "timestamp" in field_type.lower():
            reset_fields += f"{field_name}: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss'),\n      "
        elif "date" in field_type.lower():
            reset_fields += f"{field_name}: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD'),\n      "
        else:
            reset_fields += (
                f"{field_name}: {default_value(col.type, server_default)},\n      "
            )

    # Add actions column
    columns += f"""{{ title: $t('common.actions'), key: 'actions', fixed: 'right', align: "center" }},\n"""


    operation_map = {
        'create': {
            'template': '''<AccessControl :codes="['{}.add','all']" type="code">
              <a-button
                type="primary"
                @click="openDialog(currentItem, 'add')"
              >
                <FileAddOutlined />
                {{{{ $t("common.add_item") }}}}
              </a-button>
            </AccessControl>''',
            'placeholder': '{}'
        },
        'update': {
            'template': '''<AccessControl :codes="['{}.edit','all']" type="code">
                    <a-button
                      size="small"
                      type="primary"
                      @click="openDialog(record, 'edit')"
                    >
                      <EditOutlined /> </a-button
                  ></AccessControl>''',
            'placeholder': '{}'
        },
        'delete': {
            'template': '''<AccessControl
                    :codes="['{}.delete','all']"
                    type="code"
                  >
                    <a-popconfirm
                      :title="$t('common.confirm_delete')"
                      :ok-text="$t('common.yes')"
                      :cancel-text="$t('common.no')"
                      @confirm="deleteItem(record.id)"
                    >
                      <a-button size="small" type="primary" danger>
                        <template #icon>
                          <DeleteOutlined />
                        </template>
                      </a-button>
                    </a-popconfirm>
                  </AccessControl>''',
            'placeholder': '{}'
        }
    }

    ops = [op.strip() for op in operations.split(',')]
    operation_result = []
    
    if 'update' in ops:
        operation_result.append(operation_map['update']['template'].format(api_table_name))
    if 'delete' in ops:
        operation_result.append(operation_map['delete']['template'].format(api_table_name))
    
    operation = '\n'.join(operation_result)
    
    create_btn = ''
    if 'create' in ops:
        create_btn = operation_map['create']['template'].format(api_table_name)
    # Replace placeholders in template
    vue_code = template
    vue_code = vue_code.replace("{{ class_name }}", class_name)
    vue_code = vue_code.replace("{{ table_name }}", table_name)
    vue_code = vue_code.replace("{{ api_table_name }}", api_table_name)
    vue_code = vue_code.replace("{{ form_items }}", form_items)
    vue_code = vue_code.replace("{{ form_rules }}", form_rules)
    vue_code = vue_code.replace("{{ columns }}", columns)
    vue_code = vue_code.replace("{{ interface_fields }}", interface_fields)
    vue_code = vue_code.replace("{{ current_item_fields }}", current_item_fields)
    vue_code = vue_code.replace("{{ payload_fields }}", payload_fields)
    vue_code = vue_code.replace("{{ validation_checks }}", validation_checks)
    vue_code = vue_code.replace("{{ reset_fields }}", reset_fields)
    vue_code = vue_code.replace("{{ time_field_handlers }}", time_field_handlers)
    vue_code = vue_code.replace("{{ operation }}", operation)
    vue_code = vue_code.replace("{{ create_btn }}", create_btn)

    return vue_code


def map_sql_type_to_ts(col_type) -> str:
    if isinstance(col_type, SqlEnum):
        return "string"
    if hasattr(col_type, "python_type"):
        py_type = col_type.python_type
        if py_type == int:
            return "number"
        elif py_type == float:
            return "number"
        elif py_type == bool:
            return "boolean"
        elif py_type == str:
            return "string"
        elif py_type == bytes:
            return "string"
        elif py_type in [datetime.datetime, datetime.date]:
            return "string"
    return "any"


def default_value(col_type, server_default) -> str:
    if isinstance(col_type, SqlEnum):
        return f"'{col_type.enums[0]}'"
    if hasattr(col_type, "python_type"):
        py_type = col_type.python_type
        if py_type == int:
            return "0"
        elif py_type == float:
            return "0.0"
        elif py_type == bool:
            return "false"
        elif py_type == str:
            return "''"
        elif py_type == bytes:
            return "''"
        elif py_type in [datetime.datetime]:
            return "dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss')"
        elif py_type in [datetime.date]:
            return "dayjs().tz(TIME_ZONE).format('YYYY-MM-DD')"
        elif py_type in [decimal.Decimal]:
            return "0.0"
    return "null"


def generate_model_code(table: Table, exclude_columns: List[str] = None) -> str:
    if exclude_columns is None:
        exclude_columns = []
    exclude_columns = set(exclude_columns) | {"created_at", "updated_at"}

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
        "from typing import Literal",
        "from datetime import date, datetime",
        "from sqlalchemy import (",
        "    Column, Integer, String, Boolean, DateTime, DECIMAL, SMALLINT, TEXT, DATE, DATETIME, UniqueConstraint, CheckConstraint, JSON, Enum, text",
        ")",
        "from sqlalchemy.orm import validates",
        "from sqlalchemy.ext.declarative import declarative_base",
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
        if isinstance(col.type, SqlEnum) and col.name.lower() not in exclude_columns:
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
        if col.name.lower() in exclude_columns:
            continue

        col_name = col.name
        col_type = col.type
        nullable = col.nullable
        primary_key = col.primary_key
        default = col.server_default.arg if col.server_default else None
        server_default = col.server_default if col.server_default else None

        # Check if this is a password field
        if any(field in col_name.lower() for field in PASSWORD_FIELDS):
            has_password = True
            col_name = '_password'  # Use private attribute convention
            column_name_in_db = col.name

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
            line = f"    {col_name}: str = Column('{column_name_in_db}', {column_type}, nullable=True"
        else:
            line = f"    {col_name}: {py_type} = Column({column_type}"
            if not nullable:
                line += ", nullable=False"
            else:
                line += ", nullable=True"

            if primary_key:
                line += ", primary_key=True"
                if len(primary_key_columns) == 1 and isinstance(col_type, (INTEGER, SMALLINT)):
                    line += ", autoincrement=True"

            if server_default is not None:
                # Fix for default using TextClause
                line += f", server_default=text({repr(str(server_default.arg))})"

        line += ")"
        column_definitions.append(line)

        # Skip validation for nullable fields
        if nullable:
            continue

        # Add validation based on field name and type
        if isinstance(col_type, VARCHAR) and col.name.lower() not in exclude_columns:
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
        col.name for col in table.columns if col.name.lower() not in exclude_columns
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


# Generate CRUD code
def generate_crud_code(
    inspector: any,
    table: Table,
    searchable_fields: Optional[List[str]] = None
) -> str:
    class_name = "".join(word.capitalize() for word in table.name.split("_"))
    primary_key_column = list(table.primary_key.columns)[0].name
    primary_key_type = "int" # 假设主键总是 int, 可以根据实际情况调整
    if hasattr(list(table.primary_key.columns)[0].type, 'python_type'):
        pk_python_type = list(table.primary_key.columns)[0].type.python_type
        if pk_python_type == str:
            primary_key_type = "str"
        elif pk_python_type == int:
            primary_key_type = "int"
        # 可以根据需要添加更多类型映射

    # Get unique constraints
    unique_constraints = inspector.get_unique_constraints(table.name)
    unique_columns = set()
    composite_unique_constraints = []

    # Process constraints
    for constraint in unique_constraints:
        if "column_names" in constraint:
            columns = constraint["column_names"]
            if len(columns) == 1:
                unique_columns.add(columns[0])
            else:
                composite_unique_constraints.append(columns)

    # Determine searchable fields
    if searchable_fields is None:
        search_columns = [col.name for col in table.columns if (isinstance(col.type, (String, TEXT, VARCHAR)) and col.name !='password')]
    else:
        search_columns = [col for col in searchable_fields if col in [c.name for c in table.columns]] # 确保提供的字段存在于表中

    # Generate imports
    imports = (
        f"from typing import List, Optional, Dict, Any, Union, TYPE_CHECKING\n"
        f"from fastapi_babel import _\n"
        f"from sqlalchemy.orm import Session, Query\n"
        f"from sqlalchemy import and_, or_\n"
        f"from app.models.{table.name} import {class_name}\n"
        f"from app.schemas.{table.name} import {class_name}Create, {class_name}Update\n"
        f"from app.utils.log_utils import logger\n\n"
        f"# Forward declaration for QueryBuilder to avoid circular import issues\n"
        f"if TYPE_CHECKING:\n"
        f"    class QueryBuilder{class_name}:\n"
        f"        pass\n\n"
    )

    # Start CRUD class
    crud_class = f"class CRUD{class_name}:\n"

    # Add SEARCHABLE_FIELDS class variable
    if search_columns:
        crud_class += f"    SEARCHABLE_FIELDS = {search_columns}\n\n"
    else:
        crud_class += f"    SEARCHABLE_FIELDS: List[str] = [] # No searchable fields defined\n\n"


    # get method
    crud_class += f"    def get(self, db: Session, {primary_key_column}: {primary_key_type}) -> Optional[{class_name}]:\n" # 使用 primary_key_type
    crud_class += f'        """Get {class_name} by ID"""\n'
    crud_class += f"        return db.get({class_name},{primary_key_column})\n\n"

    # Private methods
    crud_class += f"    def _apply_search_filter(self, query: Query, search: Optional[str]) -> Query:\n" # Type hint Query
    crud_class += f'        """Apply search filter"""\n'
    crud_class += f"        if not search or not self.SEARCHABLE_FIELDS:\n" # 简化条件
    crud_class += f"            return query\n"
    crud_class += f"        \n"
    crud_class += f'        search_pattern = f"%{{search}}%"\n'
    crud_class += f"        filters = []\n"
    crud_class += f"        for field in self.SEARCHABLE_FIELDS:\n"
    crud_class += f"            if hasattr({class_name}, field):\n" # Check if field exists on model
    crud_class += f"                filters.append(getattr({class_name}, field).ilike(search_pattern))\n"
    crud_class += f"        if not filters:\n" # If no valid searchable fields found
    crud_class += f"             return query\n"
    crud_class += f"        return query.filter(or_(*filters))\n\n"

    crud_class += f"    def _apply_order_by(self, query: Query, orderby: Optional[str]) -> Query:\n" # Type hint Query
    crud_class += f'        """Apply ordering"""\n'
    crud_class += f"        if not orderby:\n"
    crud_class += f"            return query\n"
    crud_class += f"        \n"
    crud_class += f"        try:\n"
    crud_class += f'            field, direction = orderby.rsplit("_", 1)\n'
    crud_class += f"            if not hasattr({class_name}, field):\n" # Check if field exists
    crud_class += f'                logger.error(_(f"Invalid sort field: {{field}} for model {class_name}"))\n'
    crud_class += f"                return query\n"
    crud_class += f"            order_column = getattr({class_name}, field)\n"
    crud_class += f'            if direction.lower() == "asc":\n' # Use lower() for case-insensitivity
    crud_class += f"                return query.order_by(order_column.asc())\n"
    crud_class += f'            elif direction.lower() == "desc":\n'
    crud_class += f"                return query.order_by(order_column.desc())\n"
    crud_class += f'            logger.warning(_(f"Invalid sort direction: {{direction}} for field {{field}}"))\n' # Log invalid direction
    crud_class += f"            return query\n"
    crud_class += f"        except ValueError: # Handles rsplit error if '_' not found\n"
    crud_class += f'            logger.error(_("Invalid orderby format. Expected format: field_direction"))\n'
    crud_class += f"            return query\n"
    crud_class += f"        except AttributeError: # Should be caught by hasattr check, but as a fallbacky\n"
    crud_class += f'            logger.error(_(f"Sort field does not exist on model {class_name}"))\n'
    crud_class += f"            return query\n\n"

    # filter method
    crud_class += f"    def filter(self, db: Session, *criterion) -> 'QueryBuilder{class_name}':\n"
    crud_class += f'        """\n'
    crud_class += f'        Apply custom SQLAlchemy filter criteria and return a QueryBuilder instance.\n'
    crud_class += f'        Allows for chainable calls like .get_all(), .get_multi(), etc.\n'
    crud_class += f'        Args:\n'
    crud_class += f'            db (Session): SQLAlchemy database session.\n'
    crud_class += f'            *criterion: One or more SQLAlchemy filter expressions\n'
    crud_class += f'                        (e.g., {class_name}.name == "example", {class_name}.status == 1).\n'
    crud_class += f'        """\n'
    crud_class += f"        initial_query = db.query({class_name})\n"
    crud_class += f"        if criterion:\n"
    crud_class += f"            initial_query = initial_query.filter(*criterion)\n"
    crud_class += f"        return QueryBuilder{class_name}(db=db, query=initial_query, crud_base=self)\n\n"

    # get_multi method
    crud_class += f"    def get_multi(\n"
    crud_class += f"        self, \n"
    crud_class += f"        db: Session, \n"
    crud_class += f"        page: int = 1, \n"
    crud_class += f"        per_page: int = 10, \n"
    crud_class += f"        search: Optional[str] = None, \n"
    crud_class += f"        orderby: Optional[str] = None,\n"
    crud_class += f"        base_query: Optional[Query] = None\n" # Added base_query
    crud_class += f"    ) -> List[{class_name}]:\n"
    crud_class += f'        """Get paginated list of {class_name} records"""\n'
    crud_class += f"        page = max(1, page)\n"
    crud_class += f"        per_page = max(1, min(per_page, 100))\n"
    crud_class += f"        \n"
    crud_class += f"        query = base_query if base_query is not None else db.query({class_name})\n" # Use base_query if provided
    crud_class += f"        query = self._apply_search_filter(query, search)\n"
    crud_class += f"        query = self._apply_order_by(query, orderby)\n"
    crud_class += f"        \n"
    crud_class += f"        return query.offset((page - 1) * per_page).limit(per_page).all()\n\n"

    # get_all method
    crud_class += f"    def get_all(\n"
    crud_class += f"        self, \n"
    crud_class += f"        db: Session, \n"
    crud_class += f"        search: Optional[str] = None, \n"
    crud_class += f"        orderby: Optional[str] = None,\n"
    crud_class += f"        base_query: Optional[Query] = None\n" # Added base_query
    crud_class += f"    ) -> List[{class_name}]:\n"
    crud_class += f'        """Get all {class_name} records"""\n'
    crud_class += f"        query = base_query if base_query is not None else db.query({class_name})\n" # Use base_query if provided
    crud_class += f"        query = self._apply_search_filter(query, search)\n"
    crud_class += f"        query = self._apply_order_by(query, orderby)\n"
    crud_class += f"        return query.all()\n\n"

    # get_total method
    crud_class += f"    def get_total(self, db: Session, search: Optional[str] = None, base_query: Optional[Query] = None) -> int:\n" # Added base_query
    crud_class += f'        """Get total count of {class_name} records"""\n'
    crud_class += f"        query = base_query if base_query is not None else db.query({class_name})\n" # Use base_query if provided
    crud_class += f"        query = self._apply_search_filter(query, search)\n"
    crud_class += f"        # Order by is not needed for count\n"
    crud_class += f"        return query.count()\n\n"

    # create method
    crud_class += f"    def create(self, db: Session, obj_in: {class_name}Create) -> {class_name}:\n"
    crud_class += f'        """Create new {class_name} record with uniqueness validation"""\n'
    crud_class += f"        try:\n"
    for col in unique_columns:
        crud_class += f"            # Check {col} uniqueness\n"
        crud_class += f"            if hasattr(obj_in, '{col}') and getattr(obj_in, '{col}') is not None:\n" # Check if None
        crud_class += f"                existing = db.query({class_name}).filter(\n"
        crud_class += f"                    {class_name}.{col} == getattr(obj_in, '{col}')\n"
        crud_class += f"                ).first()\n"
        crud_class += f"                if existing:\n"
        crud_class += f"                    raise ValueError(_(f\"Duplicate value for {col}: '{{getattr(obj_in, '{col}')}}'\"))\n\n"
    for i, columns in enumerate(composite_unique_constraints, 1):
        columns_str = ', '.join(columns)
        crud_class += f"            # Check composite uniqueness constraint {i} (fields: {columns_str})\n"
        crud_class += f"            filters = []\n"
        crud_class += f"            all_fields_present = True\n"
        for col_idx, col in enumerate(columns):
            crud_class += f"            if hasattr(obj_in, '{col}') and getattr(obj_in, '{col}') is not None:\n"
            crud_class += f"                filters.append({class_name}.{col} == getattr(obj_in, '{col}'))\n"
            crud_class += f"            else:\n"
            crud_class += f"                all_fields_present = False # If any part of composite key is None, skip check or handle as per policy\n"
            crud_class += f"                # Depending on DB, NULLs might not be considered equal for unique constraints.\n"
            crud_class += f"                # For now, if any part is None, we assume it won't cause a unique violation by itself.\n"
            crud_class += f"                # If your DB treats NULLs as equal in unique constraints, this logic needs adjustment.\n"
            crud_class += f"                break\n" # Break inner loop if a field is missing/None
        crud_class += f"            if all_fields_present and len(filters) == {len(columns)}:\n"
        crud_class += f"                existing = db.query({class_name}).filter(and_(*filters)).first()\n"
        crud_class += f"                if existing:\n"
        crud_class += f"                    values_str = ', '.join([f\"{{getattr(obj_in, '{c}')}}\" for c in {columns}])\n"
        crud_class += f"                    raise ValueError(_(f\"Duplicate combination of values for fields: {columns_str}. Values: [{values_str}]\"))\n\n"
    crud_class += f"            db_obj = {class_name}(**obj_in.model_dump(exclude_unset=True))\n"
    crud_class += f"            db.add(db_obj)\n"
    crud_class += f"            db.commit()\n"
    crud_class += f"            db.refresh(db_obj)\n"
    crud_class += f"            return db_obj\n"
    crud_class += f"        except Exception:\n"
    crud_class += f"            db.rollback()\n"
    crud_class += f"            logger.error(f\"Failed to create {class_name}\", exc_info=True)\n"
    crud_class += f"            raise\n\n"

    # update method
    crud_class += f"    def update(\n"
    crud_class += f"        self, \n"
    crud_class += f"        db: Session, \n"
    crud_class += f"        db_obj: {class_name}, \n"
    crud_class += f"        obj_in: Union[Dict[str, Any], {class_name}Update]\n"
    crud_class += f"    ) -> {class_name}:\n"
    crud_class += f'        """Update existing {class_name} record with uniqueness validation"""\n'
    crud_class += f"        try:\n"
    crud_class += f"            update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)\n"
    for col in unique_columns:
        crud_class += f"            # Check {col} uniqueness if being changed\n"
        crud_class += f"            if '{col}' in update_data and update_data['{col}'] is not None:\n" # Check if None
        crud_class += f"                new_{col} = update_data['{col}']\n"
        crud_class += f"                if new_{col} != getattr(db_obj, '{col}'):\n"
        crud_class += f"                    existing = db.query({class_name}).filter(\n"
        crud_class += f"                        {class_name}.{col} == new_{col},\n"
        crud_class += f"                        {class_name}.{primary_key_column} != getattr(db_obj, '{primary_key_column}')\n"
        crud_class += f"                    ).first()\n"
        crud_class += f"                    if existing:\n"
        crud_class += f"                        raise ValueError(_(f\"Duplicate value for {col}: '{{new_{col}}}'\"))\n\n"
    for i, columns in enumerate(composite_unique_constraints, 1):
        columns_str = ', '.join(columns)
        crud_class += f"            # Check composite uniqueness constraint {i} (fields: {columns_str})\n"
        crud_class += f"            # This check is complex: only validate if all involved fields are present in update_data\n"
        crud_class += f"            # and at least one of them is changing, and none are being set to None (unless allowed by DB).\n"
        crud_class += f"            fields_to_check = {{f: update_data.get(f, getattr(db_obj, f)) for f in {columns}}}\n"
        crud_class += f"            is_changing = any(update_data.get(f) is not None and update_data.get(f) != getattr(db_obj, f) for f in {columns})\n"
        crud_class += f"            all_parts_not_none = all(fields_to_check[f] is not None for f in {columns})\n\n"
        crud_class += f"            if is_changing and all_parts_not_none:\n"
        crud_class += f"                filters = [{class_name}.{primary_key_column} != getattr(db_obj, '{primary_key_column}')]\n"
        for col in columns:
            crud_class += f"                filters.append({class_name}.{col} == fields_to_check['{col}'])\n"
        crud_class += f"                existing = db.query({class_name}).filter(and_(*filters)).first()\n"
        crud_class += f"                if existing:\n"
        crud_class += f"                    values_str = ', '.join([f\"{{fields_to_check['{c}']}}\" for c in {columns}])\n"
        crud_class += f"                    raise ValueError(_(f\"Duplicate combination of values for fields: {columns_str}. Values: [{values_str}]\"))\n\n"

    crud_class += f"            for field, value in update_data.items():\n"
    crud_class += f"                if hasattr(db_obj, field):\n" # Ensure field exists before setting
    crud_class += f"                    setattr(db_obj, field, value)\n"
    crud_class += f"            \n"
    crud_class += f"            db.commit()\n"
    crud_class += f"            db.refresh(db_obj)\n"
    crud_class += f"            return db_obj\n"
    crud_class += f"        except Exception:\n"
    crud_class += f"            db.rollback()\n"
    # Assuming the model always has an 'id' field for logging, or use primary_key_column
    id_attr_for_log = "id" if "id" in [c.name for c in table.columns] else primary_key_column
    crud_class += f"            logger.error(f\"Failed to update {class_name} ({{db_obj.{id_attr_for_log}}})\", exc_info=True)\n"
    crud_class += f"            raise\n\n"

    # remove method
    crud_class += f"    def remove(self, db: Session, {primary_key_column}: {primary_key_type}) -> Optional[{class_name}]:\n" # 使用 primary_key_type
    crud_class += f'        """Delete {class_name} by ID"""\n'
    crud_class += f"        try:\n"
    crud_class += f"            obj = self.get(db, {primary_key_column}) # Use self.get for consistency\n"
    crud_class += f"            if obj:\n"
    crud_class += f"                db.delete(obj)\n"
    crud_class += f"                db.commit()\n"
    crud_class += f"            return obj\n"
    crud_class += f"        except Exception:\n"
    crud_class += f"            db.rollback()\n"
    crud_class += f"            logger.error(f\"Failed to delete {class_name} (ID: {{{primary_key_column}}})\", exc_info=True)\n"
    crud_class += f"            raise\n\n"

    # Add QueryBuilder class
    query_builder_class = f"\n# Helper class for chainable query building\n"
    query_builder_class += f"class QueryBuilder{class_name}:\n"
    query_builder_class += f"    def __init__(self, db: Session, query: Query, crud_base: CRUD{class_name}):\n"
    query_builder_class += f"        self._db: Session = db\n"
    query_builder_class += f"        self._query: Query = query\n"
    query_builder_class += f"        self._crud_base: CRUD{class_name} = crud_base\n\n"

    query_builder_class += f"    def filter(self, *criterion) -> 'QueryBuilder{class_name}':\n"
    query_builder_class += f'        """Apply additional filter criteria to the current query."""\n'
    query_builder_class += f"        if criterion:\n"
    query_builder_class += f"            self._query = self._query.filter(*criterion)\n"
    query_builder_class += f"        return self\n\n"

    query_builder_class += f"    def _get_effective_db(self, db_param: Optional[Session]) -> Session:\n"
    query_builder_class += f'        """Determine the actual database session to use. Prefers the initial session."""\n'
    query_builder_class += f"        if db_param is not None and db_param is not self._db:\n"
    query_builder_class += f'            logger.warning(\n'
    query_builder_class += f'                "QueryBuilder method called with a DB session different from its initial one. "\n'
    query_builder_class += f'                "The initial session will be used for the query execution."\n'
    query_builder_class += f'            )\n'
    query_builder_class += f"        return self._db\n\n"

    query_builder_class += f"    def get_all(self, db: Optional[Session] = None, search: Optional[str] = None, orderby: Optional[str] = None) -> List[{class_name}]:\n"
    query_builder_class += f'        """Execute the query and return all results, applying optional search and ordering."""\n'
    query_builder_class += f"        effective_db = self._get_effective_db(db)\n"
    query_builder_class += f"        return self._crud_base.get_all(db=effective_db, search=search, orderby=orderby, base_query=self._query)\n\n"

    query_builder_class += f"    def get_multi(\n"
    query_builder_class += f"        self, \n"
    query_builder_class += f"        db: Optional[Session] = None,\n"
    query_builder_class += f"        page: int = 1, \n"
    query_builder_class += f"        per_page: int = 10, \n"
    query_builder_class += f"        search: Optional[str] = None, \n"
    query_builder_class += f"        orderby: Optional[str] = None\n"
    query_builder_class += f"    ) -> List[{class_name}]:\n"
    query_builder_class += f'        """Execute the query with pagination, applying optional search and ordering."""\n'
    query_builder_class += f"        effective_db = self._get_effective_db(db)\n"
    query_builder_class += f"        return self._crud_base.get_multi(\n"
    query_builder_class += f"            db=effective_db, \n"
    query_builder_class += f"            page=page, \n"
    query_builder_class += f"            per_page=per_page, \n"
    query_builder_class += f"            search=search, \n"
    query_builder_class += f"            orderby=orderby, \n"
    query_builder_class += f"            base_query=self._query\n"
    query_builder_class += f"        )\n\n"

    query_builder_class += f"    def get_total(self, db: Optional[Session] = None, search: Optional[str] = None) -> int:\n"
    query_builder_class += f'        """Execute the query to get the total count of records, applying optional search."""\n'
    query_builder_class += f"        effective_db = self._get_effective_db(db)\n"
    query_builder_class += f"        return self._crud_base.get_total(db=effective_db, search=search, base_query=self._query)\n\n"

    query_builder_class += f"    def all(self) -> List[{class_name}]:\n"
    query_builder_class += f'        """Directly execute .all() on the current query object."""\n'
    query_builder_class += f"        return self._query.all()\n\n"

    query_builder_class += f"    def first(self) -> Optional[{class_name}]:\n"
    query_builder_class += f'        """Directly execute .first() on the current query object."""\n'
    query_builder_class += f"        return self._query.first()\n\n"
    
    query_builder_class += f"    def count(self) -> int:\n"
    query_builder_class += f'        """Directly execute .count() on the current query object."""\n'
    query_builder_class += f"        return self._query.count()\n"


    # Instantiate CRUD class
    instantiation = f"\n\ncrud_{table.name} = CRUD{class_name}()\n"

    # Combine all parts
    full_code = imports + crud_class + query_builder_class + instantiation
    return full_code

 
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
    schemas += "    id: Optional[int] = None\n"
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
    primary_keys = [col.name for col in table.primary_key.columns]
    for pk in primary_keys:
        schemas += f"    {pk}: int\n"
    for col in columns:
        if col.name in primary_keys or col.name in [
            "created_at",
            "updated_at",
            "password",
        ]:
            continue
        col_type = map_sql_type_to_pydantic(col)
        if isinstance(col.type, DateTime):
            schemas += f"    {col.name}: Optional[datetime] = None\n"
        elif isinstance(col.type, SqlEnum):
            enum_values = [f"'{e}'" for e in col.type.enums]
            type_annotation = f"Optional[Literal[{', '.join(enum_values)}]]"
            schemas += f"    {col.name}: {type_annotation} = None\n"
        elif "email" in col.name.lower():
            schemas += f"    {col.name}: Optional[EmailStr] = None\n"
        else:
            pydantic_type = map_sql_type_to_pydantic(col)
            if pydantic_type.startswith("Literal"):
                schemas += f"    {col.name}: Optional[{pydantic_type}] = None\n"
            else:
                schemas += f"    {col.name}: Optional[{pydantic_type}] = None\n"

    # Config class for InDBBase
    schemas += "\n    class Config:\n"
    schemas += "        orm_mode = True\n\n"

    # Final schema
    schemas += f"class {class_name}({class_name}InDBBase):\n    pass\n\n"

    return schemas

def generate_crud_endpoints(table: Table) -> str:
    """
    Generate FastAPI CRUD endpoints for a given SQLAlchemy table,
    adhering to specific routing and response patterns.

    Args:
        table (Table): The SQLAlchemy table object for which to generate endpoints.

    Returns:
        str: A string containing the generated FastAPI CRUD endpoint code.
    """
    # Derive class name by capitalizing each part of the table name
    class_name = "".join(word.capitalize() for word in table.name.split("_"))

    # Assume the first primary key column is the identifier
    primary_key_column = list(table.primary_key.columns)[0].name

    # Start constructing the API code as a string
    api_code = f"""from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi_babel import _
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.core.security import get_current_admin
from app.crud.{table.name} import crud_{table.name}
from app.schemas.{table.name} import {class_name}Create, {class_name}Update
from app.utils.responses import success_response
from app.utils.response_handlers import ErrorCode
from app.models.{table.name} import {class_name} as {class_name}Model

# Initialize the API router for {table.name} endpoints
router = APIRouter(
    prefix="/{table.name.removeprefix('sys_').replace('_', '/')}", tags=["{table.name.removeprefix('sys_')}"], dependencies=[Depends(get_current_admin)]
)

# Set the maximum per_page limit
MAX_PER_PAGE = 200
"""

    # Generate the list endpoint with pagination, search, and sorting
    api_code += f"""@router.get("/list")
def read_{table.name}_list(
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    orderby: Optional[str] = None,  # Sorting field and direction, e.g., "name_asc"
    db: Session = Depends(get_db)
):
    \"\"\"
    Retrieve a list of {class_name} records with optional pagination, search, and sorting.

    Args:
        page (int, optional): The page number to retrieve. Defaults to 1.
        per_page (int, optional): Number of records per page. Use -1 to retrieve all records. Defaults to 10.
        search (str, optional): A search string to filter records by relevant fields.
        orderby (str, optional): Sorting rule, e.g., "field_asc" or "field_desc".
        db (Session): Database session dependency.

    Returns:
        JSON response containing the list of records, total count, current page, and records per page.
    \"\"\"
    # If per_page is -1, set it to the maximum allowed value
    if per_page == -1:
        per_page = MAX_PER_PAGE  # Set per_page to the maximum value (200)
    
    # Ensure per_page is within the allowed range
    per_page = min(per_page, MAX_PER_PAGE)
    
    # Ensure page and per_page are at least 1
    page = max(page, 1)
    
    # Retrieve paginated records with search and sorting
    items = crud_{table.name}.get_multi(db, page=page, per_page=per_page, search=search, orderby=orderby)
    total = crud_{table.name}.get_total(db, search=search)
    
    response_page = page
    response_per_page = per_page

    # Prepare the response data
    return success_response(
        {{
            "items": [item.to_dict() for item in items],  # Convert each model instance to a dictionary
            "total": total,
            "page": response_page,
            "per_page": response_per_page,
        }}
    )
"""

    # Generate the single item retrieval endpoint
    api_code += f"""@router.get("/{{{primary_key_column}}}")
def read_{table.name}({primary_key_column}: int, db: Session = Depends(get_db)):
    \"\"\"
    Retrieve a single {class_name} record by its unique ID.

    Args:
        {primary_key_column} (int): The unique identifier of the {class_name}.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the record's data.
    \"\"\"
    db_obj = crud_{table.name}.get(db, {primary_key_column}={primary_key_column})
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("{class_name} not found."))
    # Return the record's data as a dictionary
    return success_response(db_obj.to_dict())
"""

    # Generate the create endpoint
    api_code += f"""@router.post("/create")
def create_{table.name}(obj_in: {class_name}Create, db: Session = Depends(get_db)):
    \"\"\"
    Create a new {class_name} record.

    Args:
        obj_in ({class_name}Create): The schema containing the record's creation data.
        db (Session): Database session dependency.

    Returns:
        JSON response containing the ID of the newly created record.
    \"\"\"
    ret = crud_{table.name}.create(db, obj_in=obj_in)
    # Return the ID of the inserted record
    return success_response({{"insert_id": ret.{primary_key_column}}})
"""

    # Generate the update endpoint
    api_code += f"""@router.put("/update/{{{primary_key_column}}}")
def update_{table.name}({primary_key_column}: int, obj_in: {class_name}Update, db: Session = Depends(get_db)):
    \"\"\"
    Update an existing {class_name} record.

    Args:
        {primary_key_column} (int): The unique identifier of the {class_name} to update.
        obj_in ({class_name}Update): The schema containing the updated data.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the updated record's data.
    \"\"\"
    db_obj = crud_{table.name}.get(db, {primary_key_column}={primary_key_column})
    if not db_obj:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("{class_name} not found."))
    # Update the record with the provided data
    updated_obj = crud_{table.name}.update(
        db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True)
    )
    # Return the updated record's data as a dictionary
    return success_response(updated_obj.to_dict())
"""

    # Generate the delete endpoint
    api_code += f"""@router.delete("/delete/{{{primary_key_column}}}")
def delete_{table.name}({primary_key_column}: int, db: Session = Depends(get_db)):
    \"\"\"
    Delete a {class_name} record by its unique ID.

    Args:
        {primary_key_column} (int): The unique identifier of the {class_name} to delete.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response indicating successful deletion.
    \"\"\"
    db_obj = crud_{table.name}.get(db, {primary_key_column}={primary_key_column})
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("{class_name} not found."))
    # Remove the record from the database
    crud_{table.name}.remove(db, {primary_key_column}={primary_key_column})
    # Return an empty success response
    return success_response({{}})
"""

    return api_code



import json


def generate_vue_i18n_json(table: Table) -> str:
    """
    Generate Vue i18n JSON data in English with the following structure:
    {
        "field": {
            "table_name": "Display Name",
            "field_name": "Display Name"
        },
        "rules": {
            "field_name": {
                "required": "Error message",
                "invalid_format": "Error message"
            }
        }
    }

    :param table: SQLAlchemy Table object containing table and column info
    :return: JSON string with i18n data
    """
    # Process table name
    table_name = table.name.replace("sys_", "")  # Remove 'sys_' prefix
    table_name_lower = table_name.lower()
    
    # Initialize i18n data structure
    i18n_data = {
        "field": {},
        "rules": {}
    }
    
    # Add table display name
    i18n_data["field"][table_name_lower] = " ".join(
        word.capitalize() for word in table_name_lower.split("_")
    )
    i18n_data["field"][f"{table_name_lower}_manage"] = (
        f"{i18n_data['field'][table_name_lower]} Manager"
    )
    
    # Common field patterns and their validation rules
    COMMON_FIELD_PATTERNS = {
        'email': ['email', 'e_mail', 'mail'],
        'mobile': ['mobile', 'phone', 'telephone', 'cellphone'],
        'username': ['username', 'login', 'user_name', 'account'],
        'password': ['password', 'passwd', 'pwd'],
        'name': ['name', 'fullname', 'nickname', 'display_name'],
        'id': ['.*_id', 'id$'],
        'numeric': ['num', 'count', 'amount', 'price', 'total'],
        'url': ['url', 'link', 'website', 'avatar', 'image', 'photo']
    }

    # Process columns
    for col in table.columns:
        field_name = col.name
        field_name_lower = field_name.lower()
        
        # Determine field display name
        if col.comment:  # Use comment if available
            field_name_display = col.comment
        else:  # Convert field name to display format
            field_name_display = " ".join(
                word.capitalize() for word in field_name.split("_")
            )
        
        # Add field display name
        i18n_data["field"][field_name_lower] = field_name_display
        
        # Add validation rules for non-nullable fields (except id)
        nullable = col.nullable
        if not nullable and field_name != "id":
            # Initialize rules for this field
            i18n_data["rules"][field_name_lower] = {}
            
            # Required rule
            i18n_data["rules"][field_name_lower]["required"] = (
                f"{field_name_display} is required"
            )
            
            # Check for common field patterns
            matched_pattern = None
            for pattern, fields in COMMON_FIELD_PATTERNS.items():
                if any(re.search(field, field_name_lower) for field in fields):
                    matched_pattern = pattern
                    break
            
            # Add pattern-specific rules
            if matched_pattern == 'email':
                i18n_data["rules"][field_name_lower]["invalid_format"] = (
                    f"Please enter a valid {field_name_display}"
                )
            elif matched_pattern == 'mobile':
                i18n_data["rules"][field_name_lower]["invalid_format"] = (
                    f"Please enter a valid {field_name_display} (11 digits)"
                )
            elif matched_pattern == 'username':
                i18n_data["rules"][field_name_lower]["min_length"] = (
                    f"{field_name_display} must be at least 3 characters"
                )
                i18n_data["rules"][field_name_lower]["max_length"] = (
                    f"{field_name_display} must be at most 20 characters"
                )
                i18n_data["rules"][field_name_lower]["invalid_chars"] = (
                    f"{field_name_display} can only contain letters, numbers and underscores"
                )
            elif matched_pattern == 'password':
                i18n_data["rules"][field_name_lower]["min_length"] = (
                    f"{field_name_display} must be at least 6 characters"
                )
                i18n_data["rules"][field_name_lower]["uppercase_required"] = (
                    f"{field_name_display} must contain at least one uppercase letter"
                )
                i18n_data["rules"][field_name_lower]["lowercase_required"] = (
                    f"{field_name_display} must contain at least one lowercase letter"
                )
                i18n_data["rules"][field_name_lower]["digit_required"] = (
                    f"{field_name_display} must contain at least one digit"
                )
            elif matched_pattern == 'numeric':
                i18n_data["rules"][field_name_lower]["must_be_number"] = (
                    f"{field_name_display} must be a number"
                )
                i18n_data["rules"][field_name_lower]["must_be_non_negative"] = (
                    f"{field_name_display} cannot be negative"
                )
            elif matched_pattern == 'url':
                i18n_data["rules"][field_name_lower]["invalid_format"] = (
                    f"Please enter a valid {field_name_display} URL"
                )
            elif matched_pattern == 'id':
                i18n_data["rules"][field_name_lower]["must_be_positive"] = (
                    f"{field_name_display} must be a positive integer"
                )
            elif isinstance(col.type, (Integer, Float, DECIMAL)):
                i18n_data["rules"][field_name_lower]["must_be_number"] = (
                    f"{field_name_display} must be a number"
                )
            elif isinstance(col.type, String) and hasattr(col.type, 'length'):
                i18n_data["rules"][field_name_lower]["max_length"] = (
                    f"{field_name_display} must be at most {col.type.length} characters"
                )

    # Convert to JSON string
    return json.dumps(i18n_data, ensure_ascii=False, indent=2)


# Register and unregister functions
@router.get("/", tags=["generator"])
def read_generator():
    return {"message": "Generator Plugin"}


from .api.endpoint1 import router as endpoint1_router

router.include_router(endpoint1_router)


def register(api_router: APIRouter):
    api_router.include_router(
        router,
        prefix="/plugins/generator",
        tags=["generator"],
        dependencies=[Depends(get_current_admin)],
    )
    logger.info("Generator plugin routes registered.")


def unregister(api_router: APIRouter):
    # FastAPI does not support dynamic route removal, so this is a placeholder
    logger.info("Generator plugin routes unregistered.")
    pass
