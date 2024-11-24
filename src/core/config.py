from logging import config as logging_config

from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    model_config = SettingsConfigDict()
    project_name: str = 'Some project name'
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    elastic_host: str = '127.0.0.1'
    elastic_port: int = 9200
    debug: bool = False

    @property
    def elastic_url(self):
        return f'http://{self.elastic_host}:{self.elastic_port}'


settings = Settings()
