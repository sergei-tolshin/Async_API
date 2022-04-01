import os
from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    # Настройки FastAPI
    SERVICE_HOST: str = os.getenv('SERVICE_HOST', '127.0.0.1')
    SERVICE_PORT: int = int(os.getenv('SERVICE_PORT', 8000))
    SERVICE_URL: str = f'http://{SERVICE_HOST}:{SERVICE_PORT}'

    # Настройки Redis
    REDIS_HOST: str = os.getenv('REDIS_HOST', '127.0.0.1')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))

    # Настройки Elasticsearch
    ELASTIC_HOST: str = os.getenv('ELASTIC_HOST', '127.0.0.1')
    ELASTIC_PORT: int = int(os.getenv('ELASTIC_PORT', 9200))
    ELASTIC_URL: str = f'{ELASTIC_HOST}:{ELASTIC_PORT}'
    ELASTIC_FILMS_INDEX: str = 'movies'
    ELASTIC_GENRE_INDEX: str = 'genres'
    ELASTIC_PERSON_INDEX: str = 'persons'

    BASE_DIR = Path(__file__).resolve().parent
    TEST_DATA_PATH = BASE_DIR / 'testdata'


config = Settings()
