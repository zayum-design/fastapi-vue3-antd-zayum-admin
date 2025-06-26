import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from app.core.config import settings


router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.get("/{folder_path:path}/{file_name}", name="get_attachment")
async def get_attachment(folder_path: str, file_name: str):
    """
    根据不同的文件夹路径返回文件
    """
    # 拼接文件夹路径
    file_path = os.path.join(settings.UPLOAD_DIR, folder_path, file_name)
    
    # 检查文件是否存在
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(file_path)