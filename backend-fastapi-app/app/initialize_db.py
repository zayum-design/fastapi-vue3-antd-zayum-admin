import os
import importlib
import json
from typing import Dict, Any
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import JSON, inspect
from sqlalchemy.orm import Session
from app.dependencies.database import SessionLocal

 
def get_sys_models() -> Dict[str, Any]:
    """获取所有sys_开头的模型类"""
    models_dir = os.path.join(os.path.dirname(__file__), "models")
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


def export_alembic_migration_data(db: Session, output_path: str = "alembic/auto_insert_data.py") -> None:
    """生成 Alembic 数据迁移脚本"""
    models = get_sys_models()
    now_revision = datetime.now().strftime("%Y%m%d%H%M%S")

    header = [
        '"""insert initial data"""',
        "",
        "from datetime import datetime"
        "from decimal import Decimal",
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
                        data[col.name] = f"Decimal('{str(val)}')"
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

def export_model_data_as_python_script(db: Session, output_path: str = "app/import_data.py") -> None:
    """导出模型数据为 Python 脚本，方便直接插入数据库"""
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

            body.append(f"        # 插入 {table_name} 表数据")
            for item in rows:
                data = {}
                for col in model_class.__table__.columns:
                    val = getattr(item, col.name)
                    if isinstance(val, (datetime, date)):
                        data[col.name] = f"datetime.fromisoformat('{val.isoformat()}')"
                    elif isinstance(val, Decimal):
                        data[col.name] = f"Decimal('{str(val)}')"
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
                body.append(f"        db.add({model_name}({kwargs_str}))")
            body.append("")
        except Exception as e:
            print(f"❌ Error exporting data for {table_name}: {e}")
            continue

    full_code = header + body + footer

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(full_code))
        print(f"\n✅ Import script written to {output_path}")
    except Exception as e:
        print(f"❌ Failed to write import script: {e}")

def export_step_install_data_script(db: Session, output_path: str = "app/install_data.py") -> None:
    """导出每个模型独立的导入函数，包含：表存在检查 -> 自动创建 -> 插入数据（即使无数据也创建表）"""
    models = get_sys_models()

    header = [
        '"""按模型逐步导入数据（含表结构检查），每个模型一个函数"""',
        "from datetime import datetime, date",
        "from decimal import Decimal",
        "from sqlalchemy import inspect, create_engine",
        "from sqlalchemy.orm import Session",
        "from app.dependencies.database import SessionLocal, SQLALCHEMY_DATABASE_URL",
        "from app.models import *",
        "",
        "engine = create_engine(SQLALCHEMY_DATABASE_URL)",
        "inspector = inspect(engine)",
        "",
    ]

    function_blocks = []

    for model_name, model_class in models.items():
        table_name = getattr(model_class, "__tablename__", None)
        if not table_name:
            continue

        func_lines = [
            f"def table_has_data(db: Session, model) -> bool:",
            f"    \"\"\"检查表中是否有数据\"\"\"",
            f"    return db.scalar(select(model).limit(1)) is not None",
            f"",
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
                    data = {}
                    for col in model_class.__table__.columns:
                        val = getattr(item, col.name)
                        if isinstance(val, (datetime, date)):
                            data[col.name] = f"datetime.fromisoformat('{val.isoformat()}')"
                        elif isinstance(val, Decimal):
                            data[col.name] = f"Decimal('{str(val)}')"
                        elif hasattr(val, 'name') and hasattr(type(val), '__name__'):  # Enum
                            data[col.name] = f"{type(val).__name__}.{val.name}"
                        elif isinstance(val, dict):
                            data[col.name] = repr(val)
                        else:
                            data[col.name] = repr(val)
                    kwargs_str = ", ".join([f"{k}={v}" for k, v in data.items()])
                    func_lines.append(f"      db.add({model_name}({kwargs_str}))")
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
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
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
    finally:
        db.close()


if __name__ == "__main__":
    main()
