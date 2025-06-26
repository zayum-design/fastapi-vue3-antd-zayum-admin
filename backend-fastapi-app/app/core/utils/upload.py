import os
import uuid
import hashlib
from datetime import datetime

from fastapi import HTTPException, UploadFile
from app.core.config import settings


class Upload:
    """
    上传类示例：
      - 检查文件大小、扩展名
      - 计算哈希
      - 按 "UPLOAD_DIR/时间戳随机数.扩展名" 存储
      - 返回相对路径 (即文件名) 方便后续访问
    """

    def __init__(self):
        self.max_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = [ext.lower().strip() for ext in settings.ALLOWED_EXTENSIONS]
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    def _check_file_size(self, file: UploadFile) -> int:
        file.file.seek(0, 2)  # 移到末尾
        file_size = file.file.tell()
        file.file.seek(0)    # 回到开头
        if file_size > self.max_size:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制: {file_size} bytes，限制为 {self.max_size} bytes."
            )
        return file_size

    def _check_file_extension(self, filename: str):
        extension = filename.split(".")[-1].lower()
        if extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"不允许的文件拓展名: .{extension}, "
                    f"允许的拓展名: {self.allowed_extensions}"
                )
            )

    def _compute_sha1(self, file: UploadFile) -> str:
        hasher = hashlib.sha1()
        chunk_size = 8192
        while True:
            chunk = file.file.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
        file.file.seek(0)
        return hasher.hexdigest()

    def _write_file(self, file: UploadFile, save_path: str):
        chunk_size = 8192
        with open(save_path, "wb") as f:
            while True:
                chunk = file.file.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
        file.file.seek(0)

    def save_file(self, file: UploadFile, ext_param: str = "test", sub_dir: str = None, filename: str = None) -> dict:
        """
        保存文件并返回各种信息：
          - file_name: 源文件名
          - saved_filename: 最终存储在 UPLOAD_DIR 中的文件名
          - relative_path: 这里就是 saved_filename （相对于 UPLOAD_DIR）
          - size: 文件大小
          - is_image: 是否图片（基于扩展名判断）
          - mimetype: 文件 content_type
          - ext_param: 可扩展参数
          - sha1: 文件的 SHA-1
          - general_attachmentcol: 业务自定义字段
        """
        # 1. 检查大小 / 扩展名
        file_size = self._check_file_size(file)
        self._check_file_extension(file.filename)

        # 2. 计算 SHA1
        sha1_val = self._compute_sha1(file)

        # 3. 如果指定了文件名，则使用指定的文件名，否则按 "时间戳 + 随机字符串" 生成文件名
        if filename:
            extension = file.filename.split(".")[-1].lower()
            saved_filename = f"{filename}.{extension}"
        else:
            now = datetime.now()
            time_str = now.strftime('%Y%m%d%H%M%S')  # 20250305121035
            random_str = uuid.uuid4().hex[:6]        # abc123
            extension = file.filename.split(".")[-1].lower()
            saved_filename = f"{time_str}{random_str}.{extension}"

        # 4. 如果指定了子目录，创建子目录
        if sub_dir:
            sub_dir_path = os.path.join(self.upload_dir, sub_dir)
            os.makedirs(sub_dir_path, exist_ok=True)
            save_path = os.path.join(sub_dir_path, saved_filename)
        else:
            save_path = os.path.join(self.upload_dir, saved_filename)

        # 5. 写入文件
        self._write_file(file, save_path)

        # 6. 是否图片
        image_extensions = {"jpg", "jpeg", "png", "gif", "bmp", "webp"}
        is_image = extension in image_extensions

        # 7. 返回信息
        return {
            "file_name": file.filename,
            "saved_filename": saved_filename,  # 供访问接口使用
            "absolute_path": os.path.abspath(save_path),
            # 返回完整路径，包括 UPLOAD_DIR
            "relative_path": os.path.join(self.upload_dir, os.path.relpath(save_path, self.upload_dir)).replace('./', '/'),
            "size": file_size,
            "is_image": is_image,
            "mimetype": file.content_type,
            "ext_param": ext_param,
            "sha1": sha1_val,
            "general_attachment_col": "some_value"
        }
