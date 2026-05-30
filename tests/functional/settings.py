import json
from typing import Any

from pydantic_settings import BaseSettings


class ElasticTestSettings(BaseSettings):
    elastic_host: str = "127.0.0.1"
    elastic_port: int = 9201

    movies_index: str = "movies"
    genres_index: str = "genres"
    persons_index: str = "persons"

    genres_mapping_path: str = "tests/functional/elasticsearch_indexes/genres.json"
    movies_mapping_path: str = "tests/functional/elasticsearch_indexes/movies.json"
    persons_mapping_path: str = "tests/functional/elasticsearch_indexes/persons.json"

    @property
    def elastic_url(self) -> str:
        return f"http://{self.elastic_host}:{self.elastic_port}"

    @property
    def genres_mapping(self) -> dict[str, Any]:
        with open(self.genres_mapping_path, "r") as f:
            return json.load(f)

    @property
    def movies_mapping(self) -> dict[str, Any]:
        with open(self.movies_mapping_path, "r") as f:
            return json.load(f)

    @property
    def persons_mapping(self) -> dict:
        with open(self.persons_mapping_path, "r") as f:
            return json.load(f)


class RedisTestSettings(BaseSettings):
    redis_host: str = "127.0.0.1"
    redis_port: int = 6378


class WebAppTestSettings(BaseSettings):
    service_host: str = "127.0.0.1"
    service_port: int = 8001

    @property
    def service_url(self) -> str:
        return f"http://{self.service_host}:{self.service_port}"


es_test_settings = ElasticTestSettings()
redis_test_settings = RedisTestSettings()
webapp_test_settings = WebAppTestSettings()
