# app/api/common/health.py

from fastapi import APIRouter, Depends
from sqlalchemy.sql import text
from app.dependencies.database import get_db, DatabaseConnectionError
from sqlalchemy.orm import Session
import time

router = APIRouter()

@router.get("/health/database")
async def check_database_health(db: Session = Depends(get_db)):
    """检查数据库连接健康状态"""
    try:
        start_time = time.time()
        # 执行简单的查询测试连接
        result = db.execute(text("SELECT 1 as status, NOW() as timestamp"))
        row = result.fetchone()
        end_time = time.time()
        
        response_time = round((end_time - start_time) * 1000, 2)  # 毫秒
        
        return {
            "status": "healthy",
            "database": "connected",
            "response_time_ms": response_time,
            "timestamp": row[1].isoformat() if row else None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

@router.get("/health/connection-pool")
async def check_connection_pool():
    """检查连接池状态"""
    try:
        from app.dependencies.database import engine
        if engine is None:
            return {
                "status": "unhealthy",
                "connection_pool": "not_initialized"
            }
        
        # 测试连接池是否正常工作
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            test_result = result.scalar()
            
        return {
            "status": "healthy",
            "connection_pool": "active",
            "test_result": test_result
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "connection_pool": "error",
            "error": str(e)
        }
