import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_admin
from app.core.utils.upload import Upload
from app.dependencies.database import get_db
from app.modules.admin.sys_admin.models.sys_admin import SysAdmin
from app.modules.admin.sys_attachment.crud.sys_attachment import crud_sys_attachment
from app.modules.admin.sys_attachment.schemas.sys_attachment import SysAttachmentCreate
from app.utils.responses import success_response

router = APIRouter(prefix="/upload", tags=["upload"], dependencies=[Depends(get_current_admin)])


# 根据允许的扩展名生成对应的MIME类型
def get_allowed_mime_types():
    """根据 settings.ALLOWED_EXTENSIONS 生成对应的 MIME 类型"""
    extension_to_mime = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "svg": "image/svg+xml",
        "svg+xml": "image/svg+xml",
        "pdf": "application/pdf",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "txt": "text/plain",
        "csv": "text/csv",
    }

    allowed_mime_types = set()
    for ext in settings.ALLOWED_EXTENSIONS:
        ext_lower = ext.lower().strip()
        if ext_lower in extension_to_mime:
            allowed_mime_types.add(extension_to_mime[ext_lower])
        else:
            # 如果没有找到对应的MIME类型，添加通用的类型
            if ext_lower in ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg"]:
                allowed_mime_types.add(f"image/{ext_lower}" if ext_lower != "jpg" else "image/jpeg")
            elif ext_lower in ["pdf"]:
                allowed_mime_types.add("application/pdf")
            elif ext_lower in ["txt", "csv", "json", "xml"]:
                allowed_mime_types.add(f"text/{ext_lower}" if ext_lower != "txt" else "text/plain")
            else:
                allowed_mime_types.add("application/octet-stream")

    # 添加一些常见的MIME类型作为默认值
    if not allowed_mime_types:
        allowed_mime_types = {
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "application/pdf",
            "text/plain",
            "text/csv",
        }

    return allowed_mime_types


ALLOWED_MIME_TYPES = get_allowed_mime_types()

uploader = Upload()


@router.post("")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    sub_dir: str = Form("images"),
    ext_param: str = "ext_param",
    admin: SysAdmin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    上传单个文件并保存文件数据到数据库（带文件验证）
    """

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.content_type}")

    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, detail=f"文件大小超过限制: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    await file.seek(0)

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

    attachment_data = {
        "cat_id": 1,
        "path_file": file_path,
        "file_name": saved_filename,
        "file_size": file_size,
        "mimetype": mimetype,
        "ext_param": ext_param,
        "storage": "local",
        "sha1": sha1,
        "att_type": "image" if result["is_image"] else "file",
        "admin_id": admin.id,
        "user_id": 0,
        "general_attachment_col": "some_value",
        "created_at": now,
        "updated_at": now,
    }

    crud_sys_attachment.create(db=db, obj_in=SysAttachmentCreate(**attachment_data))
    return success_response({"image_url": file_path})
