# main.py
from datetime import datetime
import os
import uuid
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, HTTPException
from fastapi.responses import FileResponse
from app.dependencies.database import get_db
from sqlalchemy.orm import Session
from app.crud.sys_attachment import crud_sys_attachment
from app.schemas.sys_attachment import SysAttachmentCreate
from app.core.utils.upload import Upload
from app.utils.responses import success_response
from app.core.config import settings
from app.schemas.sys_admin import SysAdmin
from app.core.security import get_current_admin
from app.utils.log_utils import logger
from app.core.security import get_current_admin

router = APIRouter(
    prefix="/upload", tags=["upload"], dependencies=[Depends(get_current_admin)]
)

# 在全局创建一个 Uploader 实例
uploader = Upload()


@router.post("")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    sub_dir: str = Form("images"),  # 可选参数 sub_dir，默认为 "images"
    ext_param: str = "ext_param",
    admin: SysAdmin = Depends(get_current_admin),
    db: Session = Depends(get_db),  # 使用依赖注入获取数据库会话
):
    """
    上传单个文件并保存文件数据到数据库
    """

    if sub_dir == "avatar":
        random_str = uuid.uuid4().hex[:6]
        result = uploader.save_file(
            file,
            ext_param=ext_param,
            sub_dir=sub_dir,
            filename=f"avatar_{admin.id}_{random_str}",
        )
    else:
        result = uploader.save_file(file, ext_param=ext_param, sub_dir=sub_dir)

    saved_filename = result["saved_filename"]
    file_path = result["relative_path"]
    file_size = result["size"]
    mimetype = result["mimetype"]
    sha1 = result["sha1"]
    now = datetime.utcnow()

    # 生成 SysAttachment 创建所需的数据
    attachment_data = {
        "path_file": file_path,
        "file_name": saved_filename,
        "file_size": file_size,
        "mimetype": mimetype,
        "ext_param": ext_param,
        "storage": "local",  # 你可以根据实际情况设置存储类型
        "sha1": sha1,
        "att_type": (
            "image" if result["is_image"] else "file"
        ),  # 判断文件类型，图片或文件
        "admin_id": admin.id,  # 设置上传文件的管理员ID
        "user_id": 0,  # 设置上传文件的用户ID，这里假设为 0
        "general_attachment_col": "some_value",  # 自定义字段，如果没有可以为空
        "created_at": now,  # 当前时间作为 created_at
        "updated_at": now,  # 当前时间作为 updated_at
    }

    # 创建 SysAttachment 记录
    crud_sys_attachment.create(db=db, obj_in=SysAttachmentCreate(**attachment_data))
    # 返回成功响应
    return success_response({"image_url": file_path})
