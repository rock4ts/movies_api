import json
import os

from dotenv import load_dotenv
from pydantic import HttpUrl
from pydantic_settings import BaseSettings


class BaseTestSettings(BaseSettings):
    # Если в окружении уже есть переменные, нужно их переписать
    def __init__(self, **data):
        env_file_path = data.pop('env_file_path', '.env.tests-local')

        if os.path.exists(env_file_path):
            load_dotenv(env_file_path, override=True)

        super().__init__(**data)


class ElasticTestSettings(BaseTestSettings):
    elastic_host: str = '127.0.0.1'
    elastic_port: int = 9200

    movies_index: str = 'movies'
    genres_index: str = 'genres'
    persons_index: str = 'persons'

    genres_mapping_path: str = "src/testdata/schema/es_schema_genres.json"
    movies_mapping_path: str = "src/testdata/schema/es_schema_movies.json"
    persons_mapping_path: str = "src/testdata/schema/es_schema_persons.json"

    @property
    def elastic_url(self) -> HttpUrl:
        return f'http://{self.elastic_host}:{self.elastic_port}'

    @property
    def genres_mapping(self)  -> dict:
        with open(self.genres_mapping_path, 'r') as f:
            return json.load(f)

    @property
    def movies_mapping(self) -> dict:
        with open(self.movies_mapping_path, 'r') as f:
            return json.load(f)

    @property
    def persons_mapping(self) -> dict:
        with open(self.persons_mapping_path, 'r') as f:
            return json.load(f)


class RedisTestSettings(BaseTestSettings):
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379


class WebAppTestSettings(BaseTestSettings):
    service_host: str = '127.0.0.1'
    service_port: int = 8000

    @property
    def service_url(self) -> HttpUrl:
        return f'http://{self.service_host}:{self.service_port}'


es_test_settings = ElasticTestSettings(env_file_path='.env.tests-local')
redis_test_settings = RedisTestSettings(env_file_path='.env.tests-local')
webapp_test_settings = WebAppTestSettings(env_file_path='.env.tests-local')
