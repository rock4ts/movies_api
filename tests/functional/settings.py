from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict()
    service_host: str = '127.0.0.1'
    service_port: int = 8000
    elastic_host: str = '127.0.0.1'
    elastic_port: int = 9200
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379

    @property
    def service_url(self):
        return f'http://{self.service_host}:{self.service_port}'

    @property
    def elastic_url(self):
        return f'http://{self.elastic_host}:{self.elastic_port}'


test_settings = TestSettings()
