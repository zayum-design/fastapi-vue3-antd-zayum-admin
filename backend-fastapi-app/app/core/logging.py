"""
结构化日志配置
提供统一的日志格式和结构化日志支持
"""

import logging
import sys
from datetime import datetime
from typing import Any

from pythonjsonlogger import jsonlogger

from app.core.config import settings


class StructuredJsonFormatter(jsonlogger.JsonFormatter):
    """
    结构化 JSON 日志格式化器

    输出格式：
    {
        "timestamp": "2024-01-15T10:30:00.123456",
        "level": "INFO",
        "logger": "app.modules.admin",
        "message": "User logged in",
        "module": "auth",
        "function": "login",
        "line": 45,
        "extra": {
            "user_id": 123,
            "username": "admin"
        }
    }
    """

    def __init__(self, fmt: str | None = None, *args, **kwargs):
        if fmt is None:
            fmt = "%(timestamp)s %(level)s %(name)s %(message)s"
        super().__init__(fmt, *args, **kwargs)

    def add_fields(
        self, log_record: dict[str, Any], record: logging.LogRecord, message_dict: dict[str, Any]
    ) -> None:
        """添加自定义字段"""
        super().add_fields(log_record, record, message_dict)

        # 添加时间戳
        log_record["timestamp"] = datetime.utcnow().isoformat()

        # 重命名字段
        log_record["level"] = record.levelname
        log_record["logger"] = record.name

        # 添加位置信息
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # 添加上下文信息
        if hasattr(record, "extra"):
            log_record["extra"] = record.extra

        # 添加请求 ID（如果存在）
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id


class ColoredFormatter(logging.Formatter):
    """
    带颜色的控制台日志格式化器

    用于开发环境，提供更易读的日志输出
    """

    # ANSI 颜色代码
    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[35m",  # 紫色
        "RESET": "\033[0m",  # 重置
    }

    def format(self, record: logging.LogRecord) -> str:
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"

        return super().format(record)


def setup_logging():
    """
    配置日志系统

    根据环境配置不同的日志格式：
    - 开发环境：带颜色的控制台输出
    - 生产环境：结构化 JSON 输出
    """
    # 根日志器配置
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # 清除现有处理器
    root_logger.handlers = []

    # 注意：由于 use_enum_values=True，ENV 是字符串
    env_value = settings.ENV if isinstance(settings.ENV, str) else settings.ENV.value
    if env_value == "production":
        # 生产环境：JSON 格式
        formatter = StructuredJsonFormatter()
    else:
        # 开发环境：带颜色的格式
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        formatter = ColoredFormatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 配置第三方库日志级别
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)


class LoggerAdapter(logging.LoggerAdapter):
    """
    日志适配器

    提供便捷的 extra 字段添加功能

    Usage:
        logger = get_logger(__name__)
        logger.info("User action", extra={"user_id": 123, "action": "login"})

        # 或者使用上下文
        ctx_logger = logger.bind(request_id="abc-123")
        ctx_logger.info("Processing request")  # 自动包含 request_id
    """

    def __init__(self, logger: logging.Logger, extra: dict[str, Any] | None = None):
        super().__init__(logger, extra or {})

    def bind(self, **kwargs) -> "LoggerAdapter":
        """创建带有额外上下文的新适配器"""
        new_extra = {**self.extra, **kwargs}
        return LoggerAdapter(self.logger, new_extra)

    def process(self, msg: str, kwargs: Any) -> tuple:
        """处理日志记录"""
        extra = kwargs.get("extra", {})
        extra.update(self.extra)

        # 将 extra 保存到 record 中
        kwargs["extra"] = extra

        # 添加 extra 属性到 record
        if "extra" in kwargs:
            kwargs["extra"]["extra"] = kwargs["extra"].copy()

        return msg, kwargs

    def debug(self, msg: str, *args, **kwargs) -> None:
        """记录 DEBUG 级别日志"""
        self.log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        """记录 INFO 级别日志"""
        self.log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """记录 WARNING 级别日志"""
        self.log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        """记录 ERROR 级别日志"""
        self.log(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        """记录 CRITICAL 级别日志"""
        self.log(logging.CRITICAL, msg, *args, **kwargs)

    def exception(self, msg: str, *args, exc_info: bool = True, **kwargs) -> None:
        """记录异常日志"""
        kwargs["exc_info"] = exc_info
        self.error(msg, *args, **kwargs)


def get_logger(name: str) -> LoggerAdapter:
    """
    获取日志记录器

    Usage:
        from app.core.logging import get_logger

        logger = get_logger(__name__)
        logger.info("Message")
        logger.info("Message", extra={"key": "value"})

        # 带上下文的日志
        ctx_logger = logger.bind(request_id="abc")
        ctx_logger.info("Message")  # 自动包含 request_id
    """
    logger = logging.getLogger(name)
    return LoggerAdapter(logger)


# 兼容性导入，保留旧的导入方式
def get_structured_logger(name: str) -> LoggerAdapter:
    """获取结构化日志记录器（别名）"""
    return get_logger(name)
