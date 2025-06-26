import os
import hashlib
from pathlib import Path
import logging
from fastapi import APIRouter, HTTPException
from aiohttp import ClientSession
from aiofile import async_open

# Set up logging
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/download", tags=["Download"])

class DownloadService:
    def __init__(self):
        self.temp_dir = Path("temp_downloads").resolve()  # 使用项目根目录的相对路径
        self.temp_dir.mkdir(parents=True, exist_ok=True)  # 确保创建多级目录
        logger.info(f"下载临时目录已初始化: {self.temp_dir}")

    async def download_plugin(self, url: str) -> Path:
        """安全下载插件包"""
        try:
            logger.info(f"开始下载插件包: {url}")
            async with ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"下载源不可用, 状态码: {response.status}")
                        raise HTTPException(502, "下载源不可用")

                    file_hash = hashlib.sha256(url.encode()).hexdigest()
                    temp_path = self.temp_dir / f"{file_hash}.zip"
                    logger.info(f"插件下载完成，保存路径: {temp_path}")

                    async with async_open(temp_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(1024*1024):  # 1MB chunks
                            await f.write(chunk)
                    
                    logger.info(f"插件下载并保存到: {temp_path}")
                    return temp_path
        except Exception as e:
            logger.error(f"下载失败: {str(e)}", exc_info=True)
            raise HTTPException(500, f"下载失败: {str(e)}")

    async def cleanup(self, path: Path):
        """清理临时文件"""
        try:
            if path.exists():
                os.remove(path)
                logger.info(f"已清理临时文件: {path}")
        except Exception as e:
            logger.error(f"清理文件失败: {path}", exc_info=True)
            print(f"清理文件失败: {str(e)}")

download_service = DownloadService()

@router.post("/plugin")
async def download_plugin_endpoint(url: str):
    temp_file = None
    try:
        logger.info(f"请求下载插件: {url}")
        temp_file = await download_service.download_plugin(url)
        return {
            "status": "downloaded",
            "path": str(temp_file),
            "size": temp_file.stat().st_size
        }
    except HTTPException as he:
        logger.warning(f"HTTP错误: {he.detail}", exc_info=True)
        raise he
    except Exception as e:
        if temp_file and temp_file.exists():
            await download_service.cleanup(temp_file)
        logger.error(f"插件下载失败: {url}", exc_info=True)
        raise HTTPException(500, f"下载处理失败: {str(e)}")
