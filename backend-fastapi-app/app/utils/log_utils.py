"""
日志工具模块
提供结构化日志记录功能（向后兼容版本）

注意：新代码推荐使用 app.core.logging 模块
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# 导入新的日志系统
from app.core.logging import (
    get_logger as _get_new_logger,
)
from app.core.logging import (
    setup_logging as _setup_new_logging,
)

# ============== 向后兼容的类 ==============


class StructuredLogFormatter(logging.Formatter):
    """
    结构化日志格式化器（兼容版本）
    推荐使用 app.core.logging.StructuredJsonFormatter
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加额外字段
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False, default=str)


class ColoredFormatter(logging.Formatter):
    """
    带颜色的控制台日志格式化器（兼容版本）
    推荐使用 app.core.logging.ColoredFormatter
    """

    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[35m",  # 紫色
        "RESET": "\033[0m",  # 重置
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        formatted = f"{color}[{record.levelname}]{reset} {record.getMessage()}"

        # 添加额外信息
        if hasattr(record, "extra") and record.extra:
            extra_str = " ".join(f"{k}={v}" for k, v in record.extra.items())
            formatted += f" | {extra_str}"

        return formatted


# ============== 向后兼容的函数 ==============


def setup_logger(
    name: str = "zayum",
    log_dir: str = "./logs",
    level: int = logging.INFO,
    console_output: bool = True,
    file_output: bool = True,
) -> logging.Logger:
    """
    设置日志记录器（兼容版本）

    推荐使用 app.core.logging.setup_logging() 进行全局配置
    然后使用 app.core.logging.get_logger() 获取记录器

    Args:
        name: 日志记录器名称
        log_dir: 日志文件目录
        level: 日志级别
        console_output: 是否输出到控制台
        file_output: 是否输出到文件

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = ColoredFormatter()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # 文件处理器
    if file_output:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        today_log_dir = log_path / today
        today_log_dir.mkdir(exist_ok=True)

        log_file = today_log_dir / f"{datetime.now().strftime('%Y-%m-%d %H:%M')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_formatter = StructuredLogFormatter()
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


class LoggerAdapter(logging.LoggerAdapter):
    """
    带上下文的日志适配器（兼容版本）
    推荐使用 app.core.logging.LoggerAdapter
    """

    def __init__(self, logger: logging.Logger, extra: dict[str, Any] | None = None):
        super().__init__(logger, extra or {})

    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple:
        """处理日志消息，添加额外上下文"""
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs

    def bind(self, **kwargs) -> "LoggerAdapter":
        """
        创建带有额外上下文的新适配器

        新功能：支持链式上下文绑定
        """
        new_extra = {**self.extra, **kwargs}
        return LoggerAdapter(self.logger, new_extra)

    def debug(self, msg: str, extra: dict[str, Any] | None = None, **kwargs):
        """记录 DEBUG 级别日志"""
        self.log(logging.DEBUG, msg, extra=extra, **kwargs)

    def info(self, msg: str, extra: dict[str, Any] | None = None, **kwargs):
        """记录 INFO 级别日志"""
        self.log(logging.INFO, msg, extra=extra, **kwargs)

    def warning(self, msg: str, extra: dict[str, Any] | None = None, **kwargs):
        """记录 WARNING 级别日志"""
        self.log(logging.WARNING, msg, extra=extra, **kwargs)

    def error(self, msg: str, extra: dict[str, Any] | None = None, **kwargs):
        """记录 ERROR 级别日志"""
        self.log(logging.ERROR, msg, extra=extra, **kwargs)

    def critical(self, msg: str, extra: dict[str, Any] | None = None, **kwargs):
        """记录 CRITICAL 级别日志"""
        self.log(logging.CRITICAL, msg, extra=extra, **kwargs)

    def log(self, level: int, msg: str, extra: dict[str, Any] | None = None, **kwargs):
        """记录日志"""
        if extra:
            merged_extra = {**self.extra, **extra}
            kwargs["extra"] = {"extra": merged_extra}
        super().log(level, msg, **kwargs)


# ============== 全局日志记录器（保持兼容） ==============

_base_logger = setup_logger()
logger = LoggerAdapter(_base_logger)


# ============== 公共 API ==============


def get_logger(name: str | None = None, extra: dict[str, Any] | None = None) -> LoggerAdapter:
    """
    获取日志记录器

    兼容旧代码，推荐使用 app.core.logging.get_logger()

    Args:
        name: 日志记录器名称，None 使用默认记录器
        extra: 额外的上下文信息

    Returns:
        LoggerAdapter: 日志适配器
    """
    if name:
        log = logging.getLogger(name)
    else:
        log = _base_logger

    return LoggerAdapter(log, extra or {})


def set_log_level(level: str):
    """
    设置日志级别

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    log_level = level_map.get(level.upper(), logging.INFO)
    _base_logger.setLevel(log_level)
    for handler in _base_logger.handlers:
        handler.setLevel(log_level)


# ============== 重新导出新的日志系统（便于迁移） ==============

__all__ = [
    # 兼容类
    "StructuredLogFormatter",
    "ColoredFormatter",
    "LoggerAdapter",
    # 兼容函数
    "setup_logger",
    "get_logger",
    "set_log_level",
    # 全局实例
    "logger",
    # 新的日志系统（便于迁移）
    "_get_new_logger",
    "_setup_new_logging",
]
