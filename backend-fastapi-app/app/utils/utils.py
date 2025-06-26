import re
import os

def camel_to_snake(name: str) -> str:
    """
    将驼峰命名转换为蛇形命名（snake_case）。
    
    参数:
        name (str): 驼峰命名的字符串（如 SysAdmin）。
    
    返回:
        str: 转换后的蛇形命名字符串（如 sys_admin）。
    """
    # 第一步：在小写字母与大写字母之间添加下划线，如 SysAdmin -> Sys_Admin
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    # 第二步：处理多个大写字母连续的情况，如 JSONData -> json_data
    snake = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    return snake

def snake_to_camel(name: str) -> str:
    """
    将蛇形命名（snake_case）转换为驼峰命名（CamelCase）。
    
    参数:
        name (str): 蛇形命名的字符串（如 sys_admin）。
    
    返回:
        str: 驼峰命名的字符串（如 SysAdmin）。
    """
    # 如果是空字符串或全是下划线，返回空字符串
    if not name or name.replace('_', '') == '':
        return ''
    
    # 按下划线分割并对每部分首字母大写，然后合并
    components = name.split('_')
    if not components:
        return ''
    
    camel_case_name = ''.join(word.title() for word in components)
    return camel_case_name

def snake_to_human_readable_special(name: str) -> str:
    """
    将蛇形命名（snake_case）转换为人类可读的格式（每个单词首字母大写，并以空格分隔），
    并对特定单词（如 'id'）进行特殊处理（全大写）。
    
    参数:
        name (str): 蛇形命名的字符串（如 sys_admin_id）。
    
    返回:
        str: 人类可读的字符串（如 Sys Admin ID）。
    """
    # 定义需要特殊处理的词，例如 id 应该变为 ID
    special_cases = {'id': 'ID'}
    
    # 将字符串按下划线分割并分别转换
    components = name.split('_')
    human_readable_name = ' '.join(
        special_cases.get(word.lower(), word.capitalize()) for word in components
    )
    
    return human_readable_name

def print_directory_structure(path, indent_level=0):
    """
    以树状结构打印指定路径下的文件夹和文件结构。
    
    参数:
        path (str): 要打印的目录路径。
        indent_level (int): 当前缩进层级，用于递归显示层级结构。
    """
    for item in os.listdir(path):
        # 打印当前项，使用缩进表示层级
        print('  ' * indent_level + '|-- ' + item)
        
        # 构建完整路径
        item_path = os.path.join(path, item)
        
        # 如果是目录，则递归打印其子结构
        if os.path.isdir(item_path):
            print_directory_structure(item_path, indent_level + 1)

def modify_env_value(file_path: str, key: str, new_value: str):
    """
    修改 `.env` 文件中指定的 key 的值，如果不存在该 key 则添加。
    
    参数:
        file_path (str): `.env` 文件的路径。
        key (str): 要修改或添加的键名。
        new_value (str): 要设置的新值。
    """
    lines = []
    key_found = False

    # 逐行读取 `.env` 文件内容
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # 如果该行是以目标 key 开头，则替换为新的值
            if line.strip().startswith(f"{key}="):
                lines.append(f"{key}={new_value}\n")
                key_found = True
            else:
                lines.append(line)
    
    # 如果文件中没有该 key，则添加一行
    if not key_found:
        lines.append(f"{key}={new_value}\n")

    # 将修改后的内容写回 `.env` 文件
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
