from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging

# 创建路由器
router = APIRouter(tags=["demo-plugin"])

# 配置日志
logger = logging.getLogger(__name__)

@router.get("/hello")
async def hello():
    """Hello World API"""
    logger.info("Hello World API被调用")
    return JSONResponse(content={
        "code": 0,
        "message": "success",
        "data": {
            "message": "Hello World from Demo Plugin!",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    })

@router.get("/info")
async def plugin_info():
    """插件信息"""
    return {
        "name": "demo-plugin",
        "version": "1.0.0",
        "description": "这是一个示例插件",
        "author": "System Admin",
        "status": "active",
        "endpoints": [
            "/api/plugins/demo-plugin/hello",
            "/api/plugins/demo-plugin/info"
        ]
    }

@router.post("/echo")
async def echo(data: dict):
    """回声测试"""
    return {
        "code": 0,
        "message": "success",
        "data": {
            "received": data,
            "echo": "This is from demo plugin"
        }
    }

@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "demo-plugin",
        "timestamp": "2024-01-01T00:00:00Z"
    }
