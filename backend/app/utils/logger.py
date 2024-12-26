import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 创建日志目录
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 创建logger实例
logger = logging.getLogger('app')
logger.setLevel(logging.INFO)

# 创建按日期命名的日志文件
log_file = os.path.join(LOG_DIR, f'app_{datetime.now().strftime("%Y%m%d")}.log')

# 创建文件处理器
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)

# 创建控制台处理器
console_handler = logging.StreamHandler()

# 设置日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s'
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加处理器
logger.addHandler(file_handler)
logger.addHandler(console_handler) 