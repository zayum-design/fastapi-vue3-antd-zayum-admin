"""
CRUD 迁移脚本
将旧版 CRUD 类迁移到新版 Repository 模式

Usage:
    python scripts/migrate_crud.py app/modules/admin/sys_admin
    python scripts/migrate_crud.py --all  # 迁移所有模块
"""
import re
import argparse
from pathlib import Path
from typing import List, Tuple


# 模板
REPOSITORY_TEMPLATE = '''"""
{model_name} 简化版 Repository
使用 EnhancedRepository 基类，代码量减少 80%
"""
from app.core.repository import EnhancedRepository
from app.modules.admin.{module_name}.models.{model_file} import {model_class}
from app.modules.admin.{module_name}.schemas.{schema_file} import {create_schema}, {update_schema}


class {repo_class}(EnhancedRepository[{model_class}, {create_schema}, {update_schema}]):
    """
    {model_class} 数据访问层
    
    仅需配置搜索字段和唯一字段，继承所有标准 CRUD 操作
    """
    
    # 可搜索字段
    DEFAULT_SEARCH_FIELDS = {search_fields}
    
    # 唯一字段（自动进行唯一性校验）
    DEFAULT_UNIQUE_FIELDS = {unique_fields}
    
    def __init__(self):
        super().__init__({model_class})


# 单例实例（保持与旧版兼容）
{crud_instance} = {repo_class}()
'''


API_TEMPLATE = '''"""
{model_name} 简化版 API
使用 CRUDRouter，代码量减少 90%
"""
from app.api.crud_router import CRUDRouter
from app.modules.admin.{module_name}.repository import {repo_class}
from app.modules.admin.{module_name}.schemas.{schema_file} import {create_schema}, {update_schema}

# 创建 Repository 实例
repository = {repo_class}()

# 使用通用 CRUD Router，一行代码创建所有标准接口
router = CRUDRouter(
    prefix="{prefix}",
    tags={tags},
    repository=repository,
    create_schema={create_schema},
    update_schema={update_schema},
    resource_name="{resource_name}",
    max_per_page=200
).get_router()


# 如果需要自定义接口，可以在这里添加
# @router.post("/custom-action")
# async def custom_action(...):
#     ...
'''


def extract_search_fields(crud_content: str) -> List[str]:
    """从 CRUD 文件中提取搜索字段"""
    # 查找 SEARCHABLE_FIELDS
    match = re.search(r'SEARCHABLE_FIELDS\s*=\s*\[(.*?)\]', crud_content, re.DOTALL)
    if match:
        fields_str = match.group(1)
        # 提取字段名
        fields = re.findall(r"['\"](\w+)['\"]", fields_str)
        return fields
    return []


def extract_unique_fields(model_content: str) -> List[str]:
    """从模型文件中提取唯一字段（简单启发式）"""
    unique_fields = []
    # 常见唯一字段
    common_unique = ['username', 'email', 'mobile', 'phone', 'code', 'name']
    for field in common_unique:
        if field in model_content.lower():
            unique_fields.append(field)
    return unique_fields


def get_schema_names(model_name: str) -> Tuple[str, str, str]:
    """生成 Schema 类名"""
    base = model_name.replace('Sys', '')
    return (
        f"{model_name}Create",
        f"{model_name}Update",
        f"{model_name}"
    )


def migrate_module(module_path: Path, dry_run: bool = False) -> bool:
    """
    迁移单个模块
    
    Args:
        module_path: 模块路径
        dry_run: 是否仅预览，不实际写入
    
    Returns:
        是否成功
    """
    module_name = module_path.name
    
    # 查找模型文件
    models_dir = module_path / 'models'
    crud_dir = module_path / 'crud'
    api_dir = module_path / 'api'
    
    if not models_dir.exists():
        print(f"❌ {module_name}: 未找到 models 目录")
        return False
    
    # 获取模型文件
    model_files = list(models_dir.glob('*.py'))
    model_files = [f for f in model_files if f.name != '__init__.py']
    
    if not model_files:
        print(f"❌ {module_name}: 未找到模型文件")
        return False
    
    for model_file in model_files:
        model_content = model_file.read_text()
        
        # 提取模型类名
        match = re.search(r'class\s+(\w+)\s*\(', model_content)
        if not match:
            continue
        
        model_class = match.group(1)
        model_base_name = model_file.stem
        
        # 生成文件名
        repo_file = module_path / 'repository.py'
        api_v2_file = api_dir / f'{model_base_name}_v2.py'
        
        # 获取 CRUD 文件内容（如果存在）
        crud_file = crud_dir / f'{model_base_name}.py'
        search_fields = []
        if crud_file.exists():
            crud_content = crud_file.read_text()
            search_fields = extract_search_fields(crud_content)
        
        unique_fields = extract_unique_fields(model_content)
        
        create_schema, update_schema, _ = get_schema_names(model_class)
        repo_class = f"{model_class}Repository"
        crud_instance = f"crud_{model_base_name}"
        
        # 生成 Repository 代码
        repo_code = REPOSITORY_TEMPLATE.format(
            model_name=model_class,
            module_name=module_name,
            model_file=model_base_name,
            model_class=model_class,
            schema_file=model_base_name,
            create_schema=create_schema,
            update_schema=update_schema,
            repo_class=repo_class,
            search_fields=search_fields or "[]",
            unique_fields=unique_fields or "[]",
            crud_instance=crud_instance
        )
        
        # 生成 API 代码
        prefix = module_name.replace('sys_', '/')
        api_code = API_TEMPLATE.format(
            model_name=model_class,
            module_name=module_name,
            repo_class=repo_class,
            schema_file=model_base_name,
            create_schema=create_schema,
            update_schema=update_schema,
            prefix=prefix,
            tags=f"['{module_name}']",
            resource_name=model_class.replace('Sys', '')
        )
        
        if dry_run:
            print(f"\n{'='*60}")
            print(f"📦 模块: {module_name}")
            print(f"📝 模型: {model_class}")
            print(f"\n📄 将生成: {repo_file}")
            print(repo_code[:500] + "..." if len(repo_code) > 500 else repo_code)
            print(f"\n📄 将生成: {api_v2_file}")
            print(api_code[:500] + "..." if len(api_code) > 500 else api_code)
        else:
            # 写入文件
            repo_file.write_text(repo_code)
            api_dir.mkdir(exist_ok=True)
            api_v2_file.write_text(api_code)
            print(f"✅ {module_name}: 已生成 {repo_file.name} 和 {api_v2_file.name}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='迁移 CRUD 到 Repository 模式')
    parser.add_argument('path', nargs='?', help='模块路径')
    parser.add_argument('--all', action='store_true', help='迁移所有模块')
    parser.add_argument('--dry-run', action='store_true', help='仅预览，不写入')
    
    args = parser.parse_args()
    
    base_path = Path('app/modules/admin')
    
    if args.all:
        # 迁移所有模块
        modules = [d for d in base_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        print(f"发现 {len(modules)} 个模块，开始迁移...\n")
        
        success_count = 0
        for module in modules:
            if migrate_module(module, args.dry_run):
                success_count += 1
        
        print(f"\n{'='*60}")
        print(f"✅ 成功: {success_count}/{len(modules)}")
        
    elif args.path:
        # 迁移指定模块
        module_path = Path(args.path)
        if migrate_module(module_path, args.dry_run):
            print("\n✅ 迁移成功")
        else:
            print("\n❌ 迁移失败")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
