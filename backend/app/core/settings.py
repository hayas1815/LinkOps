import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from app.core.constants import (
    API_PREFIX,
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
    DEFAULT_CORS_ALLOW_HEADERS,
    DEFAULT_CORS_ALLOW_METHODS,
    DEFAULT_CORS_ORIGINS,
    DEFAULT_DATABASE_URL,
    DEFAULT_DOCS_URL,
    DEFAULT_ENVIRONMENT,
    DEFAULT_LOG_LEVEL,
    DEFAULT_MINIO_ACCESS_KEY,
    DEFAULT_MINIO_BUCKETS,
    DEFAULT_MINIO_ENDPOINT,
    DEFAULT_MINIO_SECRET_KEY,
    DEFAULT_MINIO_SECURE,
    DEFAULT_NEO4J_PASSWORD,
    DEFAULT_NEO4J_URI,
    DEFAULT_NEO4J_USER,
    DEFAULT_OPENAPI_URL,
    DEFAULT_REDIS_URL,
    DEFAULT_REDOC_URL,
    DEFAULT_VECTOR_DIMENSION,
    DEFAULT_VECTOR_DISTANCE_METRIC,
    DEFAULT_FUTURE_AI_PROVIDER,
    DEFAULT_FUTURE_AI_MODEL,
)


def _get_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _get_csv(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value.strip() == "":
        return default
    return tuple(item.strip() for item in raw_value.split(",") if item.strip())


class Settings(BaseModel):
    """Application configuration loaded from environment variables."""

    app_name: str = Field(default=APP_NAME)
    app_version: str = Field(default=APP_VERSION)
    app_description: str = Field(default=APP_DESCRIPTION)
    environment: Literal["local", "development", "staging", "production"] = Field(
        default=DEFAULT_ENVIRONMENT
    )
    debug: bool = Field(default=False)

    api_v1_prefix: str = Field(default=API_PREFIX)
    docs_url: str | None = Field(default=DEFAULT_DOCS_URL)
    redoc_url: str | None = Field(default=DEFAULT_REDOC_URL)
    openapi_url: str | None = Field(default=DEFAULT_OPENAPI_URL)

    cors_origins: tuple[str, ...] = Field(default=DEFAULT_CORS_ORIGINS)
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: tuple[str, ...] = Field(default=DEFAULT_CORS_ALLOW_METHODS)
    cors_allow_headers: tuple[str, ...] = Field(default=DEFAULT_CORS_ALLOW_HEADERS)

    log_level: str = Field(default=DEFAULT_LOG_LEVEL)

    database_url: str = Field(default=DEFAULT_DATABASE_URL)
    neo4j_uri: str = Field(default=DEFAULT_NEO4J_URI)
    neo4j_user: str = Field(default=DEFAULT_NEO4J_USER)
    neo4j_password: str = Field(default=DEFAULT_NEO4J_PASSWORD)
    redis_url: str = Field(default=DEFAULT_REDIS_URL)

    minio_endpoint: str = Field(default=DEFAULT_MINIO_ENDPOINT)
    minio_access_key: str = Field(default=DEFAULT_MINIO_ACCESS_KEY)
    minio_secret_key: str = Field(default=DEFAULT_MINIO_SECRET_KEY)
    minio_secure: bool = Field(default=DEFAULT_MINIO_SECURE)
    minio_buckets: tuple[str, ...] = Field(default=DEFAULT_MINIO_BUCKETS)

    vector_dimension: int = Field(default=DEFAULT_VECTOR_DIMENSION)
    vector_distance_metric: str = Field(default=DEFAULT_VECTOR_DISTANCE_METRIC)

    future_ai_provider: str = Field(default=DEFAULT_FUTURE_AI_PROVIDER)
    future_ai_model: str = Field(default=DEFAULT_FUTURE_AI_MODEL)

    openai_api_key: str | None = Field(default=None)
    supabase_url: str | None = Field(default=None)
    supabase_key: str | None = Field(default=None)

    @classmethod
    def from_environment(cls) -> "Settings":
        load_dotenv()
        return cls(
            app_name=os.getenv("APP_NAME", APP_NAME),
            app_version=os.getenv("APP_VERSION", APP_VERSION),
            app_description=os.getenv("APP_DESCRIPTION", APP_DESCRIPTION),
            environment=os.getenv("APP_ENV", DEFAULT_ENVIRONMENT),
            debug=_get_bool("APP_DEBUG", False),
            api_v1_prefix=os.getenv("API_V1_PREFIX", API_PREFIX),
            docs_url=os.getenv("DOCS_URL", DEFAULT_DOCS_URL),
            redoc_url=os.getenv("REDOC_URL", DEFAULT_REDOC_URL),
            openapi_url=os.getenv("OPENAPI_URL", DEFAULT_OPENAPI_URL),
            cors_origins=_get_csv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS),
            cors_allow_credentials=_get_bool("CORS_ALLOW_CREDENTIALS", True),
            cors_allow_methods=_get_csv(
                "CORS_ALLOW_METHODS", DEFAULT_CORS_ALLOW_METHODS
            ),
            cors_allow_headers=_get_csv(
                "CORS_ALLOW_HEADERS", DEFAULT_CORS_ALLOW_HEADERS
            ),
            log_level=os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL),
            database_url=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
            neo4j_uri=os.getenv("NEO4J_URI", DEFAULT_NEO4J_URI),
            neo4j_user=os.getenv("NEO4J_USER", DEFAULT_NEO4J_USER),
            neo4j_password=os.getenv("NEO4J_PASSWORD", DEFAULT_NEO4J_PASSWORD),
            redis_url=os.getenv("REDIS_URL", DEFAULT_REDIS_URL),
            minio_endpoint=os.getenv("MINIO_ENDPOINT", DEFAULT_MINIO_ENDPOINT),
            minio_access_key=os.getenv("MINIO_ACCESS_KEY", DEFAULT_MINIO_ACCESS_KEY),
            minio_secret_key=os.getenv("MINIO_SECRET_KEY", DEFAULT_MINIO_SECRET_KEY),
            minio_secure=_get_bool("MINIO_SECURE", DEFAULT_MINIO_SECURE),
            minio_buckets=_get_csv("MINIO_BUCKETS", DEFAULT_MINIO_BUCKETS),
            vector_dimension=int(
                os.getenv("VECTOR_DIMENSION", str(DEFAULT_VECTOR_DIMENSION))
            ),
            vector_distance_metric=os.getenv(
                "VECTOR_DISTANCE_METRIC", DEFAULT_VECTOR_DISTANCE_METRIC
            ),
            future_ai_provider=os.getenv(
                "FUTURE_AI_PROVIDER", DEFAULT_FUTURE_AI_PROVIDER
            ),
            future_ai_model=os.getenv("FUTURE_AI_MODEL", DEFAULT_FUTURE_AI_MODEL),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY"),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_environment()
