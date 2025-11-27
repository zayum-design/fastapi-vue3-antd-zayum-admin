import os
import importlib
import json
from typing import Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import JSON, inspect
from sqlalchemy.orm import Session
from app.dependencies.database import SessionLocal

 
def get_sys_models() -> Dict[str, Any]:
    """获取所有sys_开头的模型类"""
    # 修正路径，因为文件现在在 install 目录中
    models_dir = os.path.join(os.path.dirname(__file__), "..", "app", "models")
    model_files = [f for f in os.listdir(models_dir)
                   if f.startswith("sys_") and f.endswith(".py")]
    print(f"📁 Found model files: {model_files}")

    models = {}
    for model_file in model_files:
        module_name = f"app.models.{model_file[:-3]}"
        try:
            module = importlib.import_module(module_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and hasattr(attr, "__tablename__") and not attr.__name__.startswith("_"):
                    print(f"✅ Found model: {attr.__name__} (from {module_name})")
                    models[attr.__name__] = attr
        except ImportError as e:
            print(f"❌ Error importing {module_name}: {e}")
    return models


def export_alembic_migration_data(db: Session, output_path: Optional[str] = None) -> None:
    """生成 Alembic 数据迁移脚本"""
    if output_path is None:
        output_path = "alembic/versions/auto_insert_data.py"
    models = get_sys_models()
    now_revision = datetime.now().strftime("%Y%m%d%H%M%S")

    header = [
        '"""insert initial data"""',
        "",
        "from datetime import datetime, date",
        "from decimal import Decimal",
        "from alembic import op",
        "import sqlalchemy as sa",
        "",
        f"revision = '{now_revision}'",
        "down_revision = None",
        "branch_labels = None",
        "depends_on = None",
        "",
        "def upgrade():"
    ]

    cleanup_code = ["\ndef downgrade():"]

    for model_name, model_class in models.items():
        table_name = getattr(model_class, "__tablename__", None)
        if not table_name:
            continue

        print(f"\n📦 Processing table: {table_name}")
        try:
            rows = db.query(model_class).all()
            if not rows:
                print(f"ℹ️  No data for table: {table_name}")
                continue

            # 构建列定义
            columns = []
            for col in model_class.__table__.columns:
                try:
                    coltype = type(col.type).__name__  # 更准确地识别类型
                    columns.append(f"sa.column('{col.name}', sa.{coltype})")
                except Exception as e:
                    print(f"⚠️ Skipping column {col.name} in {table_name} due to error: {e}")


            header.append(f"    table_{table_name} = sa.table(")
            header.append(f"        '{table_name}',")
            header.extend([f"        {col}," for col in columns])
            header.append("    )")

            header.append(f"    op.bulk_insert(table_{table_name}, [")
            for item in rows:
                data = {}
                for col in model_class.__table__.columns:
                    val = getattr(item, col.name)
                    if isinstance(val, (datetime, date)):
                        data[col.name] = f"datetime.fromisoformat('{val.isoformat()}')"
                    elif isinstance(val, Decimal):
                        # 检查字段类型，如果是 DECIMAL 类型则保持 Decimal，否则转换为 float
                        col_type = str(col.type).lower()
                        # 对于 SysPlugin 的 price 字段，虽然数据库类型是 DECIMAL，但 Python 类型是 float，需要转换
                        if 'decimal' in col_type and model_name == 'SysPlugin' and col.name == 'price':
                            data[col.name] = f"{float(val)}"
                        elif 'decimal' in col_type:
                            data[col.name] = f"Decimal('{str(val)}')"
                        else:
                            data[col.name] = f"{float(val)}"
                    elif hasattr(val, 'name') and hasattr(type(val), '__name__'):  # Enum
                        data[col.name] = f"{type(val).__name__}.{val.name}"
                    elif isinstance(val, dict):
                        json_str = json.dumps(val, ensure_ascii=False)
                        data[col.name] = repr(json_str)
                    else:
                        data[col.name] = repr(val)
                dict_str = "{ " + ", ".join([f"'{k}': {v}" for k, v in data.items()]) + " }"
                header.append(f"        {dict_str},")
            header.append("    ])\n")

            # 回滚语句（只处理带 id 的）
            ids = [str(getattr(item, "id", None)) for item in rows if getattr(item, "id", None)]
            if ids:
                cleanup_code.append(f"    op.execute(\"DELETE FROM {table_name} WHERE id IN ({','.join(ids)})\")")
                cleanup_code.append("")

            db.expunge_all()
        except Exception as e:
            print(f"❌ Error processing {table_name}: {e}")
            continue

    full_code = header + cleanup_code

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(full_code))
        print(f"\n✅ Migration script written to {output_path}")
    except Exception as e:
        print(f"❌ Failed to write migration script: {e}")

def export_model_data_as_python_script(db: Session, output_path: Optional[str] = None) -> None:
    """导出模型数据为 Python 脚本，方便直接插入数据库"""
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "generated", "import_data.py")
    models = get_sys_models()

    header = [
        '"""导入模型数据脚本，不依赖 Alembic"""',
        "from datetime import datetime, date",
        "from decimal import Decimal",
        "from sqlalchemy.orm import Session",
        "from app.dependencies.database import SessionLocal",
        "from app.models import *",
        "",
        "def import_data():",
        "    db = SessionLocal()",
        "    try:"
    ]

    footer = [
        "    finally:",
        "        db.commit()",
        "        db.close()",
        "",
        "if __name__ == '__main__':",
        "    import_data()"
    ]

    body = []

    for model_name, model_class in models.items():
        table_name = getattr(model_class, "__tablename__", None)
        if not table_name:
            continue

        try:
            rows = db.query(model_class).all()
            if not rows:
                continue

            # 检查是否为规则类表，使用批量数据处理
            if "rule" in table_name.lower():
                body.append(f"        # 插入 {table_name} 表数据")
                body.append(f"        {table_name}_data = [")
                
                for item in rows:
                    data = []
                    for col in model_class.__table__.columns:
                        val = getattr(item, col.name)
                        if isinstance(val, (datetime, date)):
                            data.append(f"datetime.fromisoformat('{val.isoformat()}')")
                        elif isinstance(val, Decimal):
                            # 检查字段类型，如果是 DECIMAL 类型则保持 Decimal，否则转换为 float
                            col_type = str(col.type).lower()
                            # 对于 SysPlugin 的 price 字段，虽然数据库类型是 DECIMAL，但 Python 类型是 float，需要转换
                            if 'decimal' in col_type and model_name == 'SysPlugin' and col.name == 'price':
                                data.append(f"{float(val)}")
                            elif 'decimal' in col_type:
                                data.append(f"Decimal('{str(val)}')")
                            else:
                                data.append(f"{float(val)}")
                        elif isinstance(val, dict):
                            data.append(repr(val))
                        else:
                            data.append(repr(val))
                    data_str = "(" + ", ".join(data) + ")"
                    body.append(f"            {data_str},")
                
                body.append("        ]")
                body.append("")
                body.append(f"        for {table_name}_item in {table_name}_data:")
                body.append(f"            item = {model_name}()")
                
                for i, col in enumerate(model_class.__table__.columns):
                    body.append(f"            item.{col.name} = {table_name}_item[{i}]")
                
                body.append(f"            db.add(item)")
                body.append("")
            else:
                # 对于非规则类表，使用原来的方式
                body.append(f"        # 插入 {table_name} 表数据")
                for item in rows:
                    data = {}
                    for col in model_class.__table__.columns:
                        val = getattr(item, col.name)
                        if isinstance(val, (datetime, date)):
                            data[col.name] = f"datetime.fromisoformat('{val.isoformat()}')"
                        elif isinstance(val, Decimal):
                            # 检查字段类型，如果是 DECIMAL 类型则保持 Decimal，否则转换为 float
                            col_type = str(col.type).lower()
                            # 对于 SysPlugin 的 price 字段，虽然数据库类型是 DECIMAL，但 Python 类型是 float，需要转换
                            if 'decimal' in col_type and model_name == 'SysPlugin' and col.name == 'price':
                                data[col.name] = f"{float(val)}"
                            elif 'decimal' in col_type:
                                data[col.name] = f"Decimal('{str(val)}')"
                            else:
                                data[col.name] = f"{float(val)}"
                        elif hasattr(val, 'name') and hasattr(type(val), '__name__'):  # Enum
                            data[col.name] = f"{type(val).__name__}.{val.name}"
                        elif isinstance(val, dict):
                            if isinstance(col.type, JSON) or "json" in str(col.type).lower():
                                data[col.name] = repr(val)  # ✅ 保留 dict 格式
                            else:
                                json_str = json.dumps(val, ensure_ascii=False)
                                data[col.name] = f'"{json_str}"'
                        else:
                            data[col.name] = repr(val)
                    kwargs_str = ", ".join([f"{k}={v}" for k, v in data.items()])
                    body.append(f"        {table_name.lower()} = {model_name}()")
                    for k, v in data.items():
                        body.append(f"        {table_name.lower()}.{k} = {v}")
                    body.append(f"        db.add({table_name.lower()})")
                body.append("")
        except Exception as e:
            print(f"❌ Error exporting data for {table_name}: {e}")
            continue

    full_code = header + body + footer

    try:
        # 确保目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:  # 只有当路径包含目录时才创建
            os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(full_code))
        print(f"\n✅ Import script written to {output_path}")
    except Exception as e:
        print(f"❌ Failed to write import script: {e}")

def export_mysql_data_script(db: Session, output_path: Optional[str] = None) -> None:
    """导出 MySQL 数据插入脚本（包含表结构创建）"""
    if output_path is None:
        current_date = datetime.now().strftime("%Y%m%d")
        output_path = os.path.join(os.path.dirname(__file__), "generated", f"install_{current_date}.sql")
    
    models = get_sys_models()
    
    sql_lines = [
        "-- MySQL 数据库安装脚本",
        "-- 生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "",
        "SET NAMES utf8mb4;",
        "SET FOREIGN_KEY_CHECKS = 0;",
        "",
    ]
    
    for model_name, model_class in models.items():
        table_name = getattr(model_class, "__tablename__", None)
        if not table_name:
            continue

        print(f"\n📦 Processing MySQL table: {table_name}")
        try:
            # 检查表是否存在
            sql_lines.append(f"-- 检查并创建表 {table_name}")
            sql_lines.append(f"DROP TABLE IF EXISTS `{table_name}`;")
            sql_lines.append("")
            
            # 生成创建表语句
            create_table_sql = generate_create_table_sql(model_class, table_name)
            sql_lines.append(create_table_sql)
            sql_lines.append("")
            
            rows = db.query(model_class).all()
            if not rows:
                print(f"ℹ️  No data for table: {table_name}")
                continue

            # 插入数据
            sql_lines.append(f"-- 插入 {table_name} 表数据")
            for item in rows:
                columns = []
                values = []
                
                for col in model_class.__table__.columns:
                    val = getattr(item, col.name)
                    if val is None:
                        values.append("NULL")
                    elif isinstance(val, (datetime, date)):
                        values.append(f"'{val.isoformat()}'")
                    elif isinstance(val, Decimal):
                        values.append(f"'{str(val)}'")
                    elif isinstance(val, dict):
                        json_str = json.dumps(val, ensure_ascii=False)
                        values.append(f"'{json_str}'")
                    elif isinstance(val, list):
                        json_str = json.dumps(val, ensure_ascii=False)
                        values.append(f"'{json_str}'")
                    elif hasattr(val, 'name') and hasattr(type(val), '__name__'):  # Enum
                        values.append(f"'{val.name}'")
                    else:
                        # 转义特殊字符
                        escaped_val = str(val).replace("'", "''").replace("\\", "\\\\")
                        values.append(f"'{escaped_val}'")
                    
                    columns.append(f"`{col.name}`")
                
                columns_str = ", ".join(columns)
                values_str = ", ".join(values)
                sql_lines.append(f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({values_str});")
            
            sql_lines.append("")
            
        except Exception as e:
            print(f"❌ Error processing MySQL table {table_name}: {e}")
            continue
    
    sql_lines.append("SET FOREIGN_KEY_CHECKS = 1;")
    
    try:
        # 确保目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:  # 只有当路径包含目录时才创建
            os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(sql_lines))
        print(f"✅ MySQL 数据脚本写入成功: {output_path}")
    except Exception as e:
        print(f"❌ 写入 MySQL 数据脚本失败: {e}")

def generate_create_table_sql(model_class, table_name: str) -> str:
    """生成创建表的 SQL 语句"""
    columns_sql = []
    
    for col in model_class.__table__.columns:
        col_sql = f"  `{col.name}`"
        
        # 处理数据类型
        if hasattr(col.type, 'length'):
            if str(col.type).startswith('VARCHAR'):
                col_sql += f" VARCHAR({col.type.length})"
            elif str(col.type).startswith('CHAR'):
                col_sql += f" CHAR({col.type.length})"
            else:
                col_sql += f" {str(col.type)}"
        else:
            col_sql += f" {str(col.type)}"
        
        # 处理主键
        if col.primary_key:
            col_sql += " PRIMARY KEY"
        
        # 处理自增
        if col.autoincrement:
            col_sql += " AUTO_INCREMENT"
        
        # 处理可为空
        if not col.nullable:
            col_sql += " NOT NULL"
        
        # 处理默认值
        if col.default is not None:
            if hasattr(col.default, 'arg'):
                default_value = col.default.arg
                if isinstance(default_value, str):
                    col_sql += f" DEFAULT '{default_value}'"
                else:
                    col_sql += f" DEFAULT {default_value}"
        
        columns_sql.append(col_sql)
    
    # 生成完整的 CREATE TABLE 语句
    create_sql = f"CREATE TABLE `{table_name}` (\n"
    create_sql += ",\n".join(columns_sql)
    create_sql += "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
    
    return create_sql

def export_step_install_data_script(db: Session, output_path: Optional[str] = None) -> None:
    """导出每个模型独立的导入函数，包含：表存在检查 -> 自动创建 -> 插入数据（即使无数据也创建表）"""
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "generated", "install_data.py")
    models = get_sys_models()

    header = [
        '"""按模型逐步导入数据（含表结构检查），每个模型一个函数"""',
        "from datetime import datetime, date",
        "from decimal import Decimal",
        "from sqlalchemy import inspect, create_engine, select",
        "from sqlalchemy.orm import Session",
        "from app.dependencies.database import SessionLocal",
        "from app.core.config import settings",
        "from app.models import *",
        "",
        "engine = create_engine(settings.DATABASE_URL)",
        "inspector = inspect(engine)",
        "",
        "def table_has_data(db: Session, model) -> bool:",
        "    \"\"\"检查表中是否有数据\"\"\"",
        "    return db.scalar(select(model).limit(1)) is not None",
        "",
    ]

    function_blocks = []

    for model_name, model_class in models.items():
        table_name = getattr(model_class, "__tablename__", None)
        if not table_name:
            continue

        func_lines = [
            f"def import_{model_name}(db: Session):",
            f"    \"\"\"导入 {model_name} 数据\"\"\"",
            f"    if '{table_name}' not in inspector.get_table_names():",
            f"        print('🔧 创建表: {table_name}')",
            f"        {model_name}.__table__.create(bind=engine)",
            f"    else:",
            f"        print('✅ 表已存在: {table_name}')",
        ]

        try:
            rows = db.query(model_class).all()
            if rows:
                func_lines.append(f"    if not table_has_data(db, {model_name}):")
                func_lines.append(f"      print('📥 导入数据: {model_name}')")
                
                for item in rows:
                    func_lines.append(f"      {model_name.lower()}_item = {model_name}()")
                    for col in model_class.__table__.columns:
                        val = getattr(item, col.name)
                        if val is None:
                            # 根据字段类型处理 None 值
                            col_type = str(col.type).lower()
                            if 'datetime' in col_type or 'timestamp' in col_type:
                                func_lines.append(f"      {model_name.lower()}_item.{col.name} = datetime.fromisoformat('1970-01-01T00:00:00')")
                            elif 'decimal' in col_type or 'float' in col_type or 'double' in col_type:
                                func_lines.append(f"      {model_name.lower()}_item.{col.name} = 0.0")
                            elif 'int' in col_type:
                                func_lines.append(f"      {model_name.lower()}_item.{col.name} = 0")
                            elif 'varchar' in col_type or 'char' in col_type or 'text' in col_type:
                                func_lines.append(f"      {model_name.lower()}_item.{col.name} = ''")
                            else:
                                func_lines.append(f"      {model_name.lower()}_item.{col.name} = None")
                        elif isinstance(val, (datetime, date)):
                            func_lines.append(f"      {model_name.lower()}_item.{col.name} = datetime.fromisoformat('{val.isoformat()}')")
                        elif isinstance(val, Decimal):
                            # 检查字段类型，如果是 DECIMAL 类型则保持 Decimal，否则转换为 float
                            col_type = str(col.type).lower()
                            # 对于 SysPlugin 的 price 字段，虽然数据库类型是 DECIMAL，但 Python 类型是 float，需要转换
                            if 'decimal' in col_type and model_name == 'SysPlugin' and col.name == 'price':
                                func_lines.append(f"      {model_name.lower()}_item.{col.name} = {float(val)}")
                            elif 'decimal' in col_type:
                                func_lines.append(f"      {model_name.lower()}_item.{col.name} = Decimal('{str(val)}')")
                            else:
                                func_lines.append(f"      {model_name.lower()}_item.{col.name} = {float(val)}")
                        elif hasattr(val, 'name') and hasattr(type(val), '__name__'):  # Enum
                            func_lines.append(f"      {model_name.lower()}_item.{col.name} = {type(val).__name__}.{val.name}")
                        elif isinstance(val, dict):
                            # 检查字段类型，如果是JSON类型则保持dict，否则转换为字符串
                            col_type = str(col.type).lower()
                            if 'json' in col_type or isinstance(col.type, JSON):
                                func_lines.append(f"      {model_name.lower()}_item.{col.name} = {repr(val)}")
                            else:
                                json_str = json.dumps(val, ensure_ascii=False)
                                func_lines.append(f"      {model_name.lower()}_item.{col.name} = '{json_str}'")
                        elif isinstance(val, str) and val == '{}' and col.name == 'permission':
                            # 特殊处理：如果 permission 字段是字符串 '{}'，则转换为空字典
                            col_type = str(col.type).lower()
                            if 'json' in col_type or isinstance(col.type, JSON):
                                func_lines.append(f"      {model_name.lower()}_item.{col.name} = {{}}")
                            else:
                                func_lines.append(f"      {model_name.lower()}_item.{col.name} = '{val}'")
                        else:
                            func_lines.append(f"      {model_name.lower()}_item.{col.name} = {repr(val)}")
                    func_lines.append(f"      db.add({model_name.lower()}_item)")
            else:
                func_lines.append(f"    print('ℹ️  表 {table_name} 无初始数据，无需导入')")
        except Exception as e:
            print(f"❌ Error exporting model {model_name}: {e}")
            continue

        func_lines.append("")
        function_blocks.append("\n".join(func_lines))

    footer = [
        "",
        "def run_all():",
        "    db = SessionLocal()",
        "    try:"
    ]
    for model_name in models:
        footer.append(f"        import_{model_name}(db)")
    footer.extend([
        "        db.commit()",
        "    finally:",
        "        db.close()",
        "",
        "if __name__ == '__main__':",
        "    run_all()"
    ])

    full_code = header + function_blocks + footer

    try:
        # 确保目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:  # 只有当路径包含目录时才创建
            os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(full_code))
        print(f"✅ 写入分步导入脚本成功: {output_path}")
    except Exception as e:
        print(f"❌ 写入失败: {e}")



        
        
        

def main():
    db = SessionLocal()
    try:
        export_alembic_migration_data(db)
        export_model_data_as_python_script(db)
        export_step_install_data_script(db)
        export_mysql_data_script(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
