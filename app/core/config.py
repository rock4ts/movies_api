from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    host: str = Field(validation_alias="REDIS_HOST")
    port: int = Field(validation_alias="REDIS_PORT")


class ElasticSettings(BaseSettings):
    host: str = Field(validation_alias="ELASTIC_HOST")
    port: int = Field(validation_alias="ELASTIC_PORT")

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


class JWTSettings(BaseSettings):
    algorithm: str = "RS256"
    public_key_path: str = "certs/jwt-public.pem"

    @cached_property
    def public_key(self) -> bytes:
        with open(self.public_key_path, "rb") as key_file:
            return key_file.read()


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    debug: bool = False
    project_name: str = "Some project name"

    film_index: str = "movies"
    genre_index: str = "genres"
    person_index: str = "persons"

    authjwt_secret_key: str = "secret"


settings = Settings()
jwt_settings = JWTSettings()
redis_settings = RedisSettings()
elastic_settings = ElasticSettings()
