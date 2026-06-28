APP_NAME = "LinkOps API"
APP_SERVICE_NAME = "LinkOps Backend"
APP_ROUTER_TAG_ROOT = "Root"
APP_ROUTER_TAG_HEALTH = "Health"
APP_DESCRIPTION = (
    "Industrial Knowledge Intelligence Platform backend foundation "
    "for assets, documents, knowledge graph, RAG, IoT, MQTT, SCADA, and "
    "multi-agent AI capabilities."
)
APP_VERSION = "1.0.0"

API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

DEFAULT_TIMEZONE = "UTC"

SUPPORTED_FILE_TYPES = (
    "pdf",
    "docx",
    "txt",
    "csv",
    "xlsx",
    "png",
    "jpg",
    "jpeg",
)
MAX_UPLOAD_SIZE = 50 * 1024 * 1024

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200

REQUEST_ID_HEADER = "X-Request-ID"
DEFAULT_CONTEXT_VALUE = "-"
BACKEND_STARTUP_LOG_MESSAGE = "Starting LinkOps Backend..."
BACKEND_SHUTDOWN_LOG_MESSAGE = "Stopping LinkOps Backend..."

ROOT_WELCOME_MESSAGE = "Welcome to LinkOps API"
HEALTH_STATUS = "healthy"
HEALTH_STATUS_DEGRADED = "degraded"

VALIDATION_ERROR_MESSAGE = "Request validation failed"
HTTP_ERROR_MESSAGE = "HTTP error"
INTERNAL_ERROR_MESSAGE = "Internal server error"
HTTP_STATUS_VALIDATION_ERROR = 422
HTTP_STATUS_INTERNAL_ERROR = 500

DEFAULT_ENVIRONMENT = "development"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_DOCS_URL = "/docs"
DEFAULT_REDOC_URL = "/redoc"
DEFAULT_OPENAPI_URL = "/openapi.json"
DEFAULT_CORS_ORIGINS = ("http://localhost:3000", "http://127.0.0.1:3000")
DEFAULT_CORS_ALLOW_METHODS = ("*",)
DEFAULT_CORS_ALLOW_HEADERS = ("*",)

DEFAULT_DATABASE_URL = "postgresql+psycopg://linkops:linkops@postgres:5432/linkops"
DEFAULT_NEO4J_URI = "bolt://neo4j:7687"
DEFAULT_NEO4J_USER = "neo4j"
DEFAULT_NEO4J_PASSWORD = "linkops_neo4j"
DEFAULT_REDIS_URL = "redis://redis:6379/0"

DEFAULT_MINIO_ENDPOINT = "minio:9000"
DEFAULT_MINIO_ACCESS_KEY = "linkops"
DEFAULT_MINIO_SECRET_KEY = "linkops123"
DEFAULT_MINIO_SECURE = False
DEFAULT_MINIO_BUCKETS = (
    "documents",
    "thumbnails",
    "exports",
    "future-models",
)

DEFAULT_VECTOR_DIMENSION = 1536
DEFAULT_VECTOR_DISTANCE_METRIC = "cosine"

DEFAULT_FUTURE_AI_PROVIDER = "none"
DEFAULT_FUTURE_AI_MODEL = "none"
DEFAULT_COPILOT_MEMORY_WINDOW = 20

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | request_id=%(request_id)s | "
    "method=%(method)s | path=%(path)s | status_code=%(status_code)s | "
    "execution_time=%(execution_time)s | %(name)s | %(message)s"
)
