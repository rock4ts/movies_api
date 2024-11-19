from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8')
    project_name: str = 'Some project name'
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    elastic_host: str = '127.0.0.1'
    elastic_port: int = 9200
    elastic_url: str = f"http://{elastic_host}:{elastic_port}"


settings = Settings()