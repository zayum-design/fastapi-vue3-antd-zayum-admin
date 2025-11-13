"""
环境检查和初始化模块
"""
import os
import shutil
from app.utils.log_utils import logger


def check_environment() -> bool:
    """
    检查环境配置
    
    Returns:
        bool: 环境是否配置正确
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(root_dir, ".env")
    env_example_path = os.path.join(root_dir, ".env.example")
    
    # 检查 .env 文件是否存在
    if not os.path.exists(env_path):
        if os.path.exists(env_example_path):
            try:
                shutil.copyfile(env_example_path, env_path)
                # 确保文件写入完成
                with open(env_path, 'r') as f:
                    content = f.read()
                    if not content:
                        raise ValueError("创建.env文件失败，内容为空")
                logger.info("已从.env.example创建.env文件")
            except Exception as e:
                logger.error(f"创建.env文件失败: {str(e)}")
                raise
        else:
            logger.error("缺少.env.example文件，无法创建.env")
            raise FileNotFoundError("缺少.env.example文件")
    else:
        # 验证.env文件是否包含必要配置
        with open(env_path, 'r') as f:
            content = f.read()
            required_keys = ['MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DB', 'MYSQL_HOST', 'MYSQL_PORT']
            missing_keys = [key for key in required_keys if f"{key}=" not in content]
            if missing_keys:
                logger.error(f".env文件缺少必要配置: {', '.join(missing_keys)}")
                raise ValueError(f"缺少必要配置: {', '.join(missing_keys)}")
    
    return True


def is_application_installed() -> bool:
    """
    检查应用是否已安装
    
    Returns:
        bool: 是否已安装
    """
    install_lock_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
        "install.lock"
    )
    return os.path.exists(install_lock_path)
