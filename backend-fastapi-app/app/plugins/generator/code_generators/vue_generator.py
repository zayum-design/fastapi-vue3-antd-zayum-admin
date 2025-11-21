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
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
import logging
from pathlib import Path
from sqlalchemy.types import TypeEngine

logger = logging.getLogger(__name__)
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
            getattr(col.default, 'arg', None) if col.default else None
        )  # Python-level default
        server_default = (
            str(getattr(col.server_default, 'arg', None)) if col.server_default else None
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
        if "datetime" in field_type.lower() or "timestamp" in field_type.lower():
            current_item_fields += f"{field_name}: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss'),\n      "
        elif "date" in field_type.lower():
            current_item_fields += f"{field_name}: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD'),\n      "
        elif "int" in field_type.lower() or "decimal" in field_type.lower() or "numeric" in field_type.lower() or "float" in field_type.lower():
            current_item_fields += f"      {field_name}: 0,\n"
        else:
            default_val = default_value(col.type, server_default)
            if isinstance(default_val, str):
                if default_val.startswith("'") and default_val.endswith("'"):
                    default_val = default_val[1:-1]
                current_item_fields += f"      {field_name}: '{default_val}',\n"
            else:
                current_item_fields += f"      {field_name}: {default_val},\n"

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
                    columns += f"""{{ title: $t('{table_dot}.field.{field_name}'), dataIndex: '{field_name}', key: '{field_name}', sorter: true, sortDirections: ['ascend', 'descend'] }},\n"""
        else:
            if field_name.lower() == "password":  # 不显示密码明文
                columns += f"""{{ title: $t('{table_dot}.field.{field_name}'), dataIndex: '{field_name}', key: '{field_name}', customRender: () => '******' }},\n"""
            else:
                columns += f"""{{ title: $t('{table_dot}.field.{field_name}'), dataIndex: '{field_name}', key: '{field_name}', sorter: true, sortDirections: ['ascend', 'descend'] }},\n"""
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


def default_value(sql_type: TypeEngine, server_default: Optional[str] = None) -> Union[str, int]:
    """Get default value for a field based on its type."""
    type_name = str(sql_type).lower()
    
    if server_default is not None:
        if server_default.startswith("'") and server_default.endswith("'"):
            return f"'{server_default[1:-1]}'"
        return server_default
    
    if "int" in type_name or "decimal" in type_name or "numeric" in type_name or "float" in type_name:
        return 0  # 数字类型直接返回数字0
    elif "bool" in type_name:
        return "false"
    elif "datetime" in type_name or "timestamp" in type_name:
        return "dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss')"
    elif "date" in type_name:
        return "dayjs().tz(TIME_ZONE).format('YYYY-MM-DD')"
    else:
        return "''"
