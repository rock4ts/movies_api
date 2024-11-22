from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict()
    project_name: str = 'Some project name'
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    elastic_host: str = '127.0.0.1'
    elastic_port: int = 9200

    @property
    def elastic_url(self):
        return f'http://{self.elastic_host}:{self.elastic_port}'


settings = Settings()
