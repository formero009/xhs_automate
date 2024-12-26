import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BASE_PATH = Path(__file__).parent.resolve()

# 图片相关配置
ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'png,jpg,jpeg').split(','))
UPLOAD_FOLDER = os.path.join(BASE_PATH, os.getenv('UPLOAD_FOLDER', 'upload/images'))
OUTPUT_FOLDER = os.path.join(BASE_PATH, os.getenv('OUTPUT_FOLDER', 'output/images'))

# OpenAI配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE')
OPENAI_ENHANCE_MODEL = os.getenv('OPENAI_ENHANCE_MODEL', 'gpt-4o')
OPENAI_CAPTION_MODEL = os.getenv('OPENAI_CAPTION_MODEL', 'gpt-4o')

# 腾讯翻译配置
TENCENT_SECRET_ID = os.getenv('TENCENT_SECRET_ID')
TENCENT_SECRET_KEY = os.getenv('TENCENT_SECRET_KEY')
TENCENT_SERVICE = os.getenv('TENCENT_SERVICE', 'tmt')
TENCENT_HOST = os.getenv('TENCENT_HOST', 'tmt.tencentcloudapi.com')
TENCENT_VERSION = os.getenv('TENCENT_VERSION', '2018-03-21')
TENCENT_REGION = os.getenv('TENCENT_REGION', 'ap-beijing')

# 小红书 cookie 配置
XHS_COOKIE = os.getenv('XHS_COOKIE')

# SQLite database configuration
DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///app.db')

# pinterest 爬虫配置，用于训练模型
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, os.getenv('IMAGE_DIR', 'spider/images'))

# 确保必要的目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)