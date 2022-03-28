import os
from logging import config as logging_config

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

# Количество результатов на странице
PAGE_SIZE = 10

# Настройки Redis
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# Время хранения кэша 5 минут
CACHE_EXPIRE_IN_SECONDS = 60 * 5

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Локализация
LANGUAGE = os.getenv('LANGUAGE', 'ru')
LOCALE_PATH = os.getenv('LOCALE_PATH', 'locale')
