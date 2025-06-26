import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger():
    log_dir = os.path.join("logs", datetime.now().strftime("%Y-%m-%d"))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_filename = datetime.now().strftime("%Y-%m-%d %H:%M") + ".log"
    log_filepath = os.path.join(log_dir, log_filename)

    # 创建 logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)  # 只设置为 INFO，显示所有 INFO 及以上的日志

    # 创建文件处理器，只记录 ERROR 及以上的日志
    file_handler = RotatingFileHandler(log_filepath, maxBytes=2*1024*1024, backupCount=10)
    file_handler.setLevel(logging.ERROR)  # 只记录 ERROR 日志到文件
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # 创建控制台处理器，显示 INFO 及以上的日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # 控制台显示所有 INFO 及以上的日志
    console_formatter = logging.Formatter('%(message)s - %(asctime)s - %(levelname)s\n')
    console_handler.setFormatter(console_formatter)

    # 将处理器添加到 logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# 在模块加载时设置日志
logger = setup_logger()
