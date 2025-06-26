import os
from fastapi import APIRouter
from app.utils.responses import success_response

# 创建安装路由
router = APIRouter()


@router.post("/install_check")
def check_install_lock():
    """
    安装检查接口
    安装模式下不使用任何数据库表
    """
    try:
        # 获取项目根目录
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        install_lock_path = os.path.join(base_dir, "install.lock")

        # 仅检查文件是否存在，不涉及数据库操作
        return success_response(
            data={"installed": os.path.exists(install_lock_path)},
        )
    except Exception as e:
        # 简单错误处理，不依赖 gettext
        return {
            "code": 500,
            "message": "Install check failed",
            "data": {
                "installed": False,
                "error": str(e)
            }
        }
