from pathlib import Path
import environ
from datetime import timedelta

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent  # .../backend/smartpark
ROOT_DIR = BASE_DIR.parent.parent  # .../ (raiz do repo)

# Envs (lê .env na raiz do repo)
env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_SECRET_KEY=(str, "CHANGE_ME"),
    DJANGO_ALLOWED_HOSTS=(list, ["*"]),
    DATABASE_URL=(str, "postgresql://postgres:postgres@localhost:5432/smart-park-db"),
    CORS_ALLOWED_ORIGINS=(list, []),
)
environ.Env.read_env(ROOT_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    # apps do projeto
    "apps.core",
    "apps.accounts",
    "apps.tenants",
    "apps.catalog",
    "apps.hardware",
    "apps.events",
    "apps.public",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # CORS deve vir cedo
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "smartpark.urls"
WSGI_APPLICATION = "smartpark.wsgi.application"
ASGI_APPLICATION = "smartpark.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR.parent / "templates"],  # Aponta para backend/templates
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
STATIC_URL = "static/"

# DB via DATABASE_URL
DATABASES = {"default": env.db("DATABASE_URL")}

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

# DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Swagger/Schema
SPECTACULAR_SETTINGS = {
    "TITLE": "SmartPark API",
    "DESCRIPTION": "Sistema de gerenciamento de estacionamentos inteligentes",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SERVERS": [
        {"url": "http://localhost:8000", "description": "Development server"},
    ],
    "TAGS": [
        # ============ ACCOUNTS APP ============
        {
            "name": "Accounts - Authentication",
            "description": "🔐 Endpoints para autenticação de usuários (login, logout, refresh token)",
        },
        {
            "name": "Accounts - Users",
            "description": "👤 Endpoints para gerenciamento de usuários (perfil, busca, validação)",
        },
        # ============ CATALOG APP ============
        {
            "name": "Catalog - Public",
            "description": "🌐 Endpoints públicos do catálogo (estabelecimentos, vagas)",
        },
        {
            "name": "Catalog - Types",
            "description": "📓 Tipos de entidades (estabelecimentos, veículos, vagas)",
        },
        # ============ TENANTS APP ============
        {
            "name": "Tenants - Clients",
            "description": "🏢 Gerenciamento de clientes do sistema",
        },
        {
            "name": "Tenants - Client Members",
            "description": "👥 Gerenciamento de membros de clientes",
        },
        {
            "name": "Tenants - Establishments",
            "description": "🏬 Gerenciamento de estabelecimentos",
        },
        {
            "name": "Tenants - Lots",
            "description": "🏞️ Gerenciamento de estacionamentos/lotes",
        },
        {
            "name": "Tenants - Slots",
            "description": "🚙 Gerenciamento de vagas de estacionamento",
        },
        {"name": "Tenants - Slot Status", "description": "📊 Status atual das vagas"},
        {
            "name": "Tenants - Slot Status History",
            "description": "📈 Histórico de mudanças de status das vagas",
        },
        # ============ HARDWARE APP ============
        {
            "name": "Hardware - Cameras",
            "description": "📹 Gerenciamento de câmeras de monitoramento",
        },
        {
            "name": "Hardware - Camera Monitoring",
            "description": "📡 Monitoramento e heartbeats das câmeras",
        },
        {
            "name": "Hardware - API Keys",
            "description": "🔑 Gerenciamento de chaves de API para hardware",
        },
        {
            "name": "Hardware - Integration",
            "description": "🔗 Endpoints para integração com hardware",
        },
        # ============ EVENTS APP ============
        {
            "name": "Events - System Events",
            "description": "⚡ Sistema de eventos de status das vagas",
        },
        {
            "name": "Events - Analytics",
            "description": "📊 Eventos e análises do sistema",
        },
    ],
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    "SORT_OPERATIONS": False,
}

# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

# CORS Configuration
# Para desenvolvimento, permitir todos os origins
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
else:
    CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS", default=[])
    CORS_ALLOW_CREDENTIALS = True

# Headers permitidos
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-api-key",
    "x-signature",
    "x-timestamp",
]

# Métodos permitidos
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# Permite cookies/credenciais em requests CORS
CORS_EXPOSE_HEADERS = [
    "content-type",
    "x-csrftoken",
]

# CSRF Configuration para APIs
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS", default=[])

# Para desenvolvimento, permitir CSRF menos restritivo
if DEBUG:
    CSRF_COOKIE_HTTPONLY = False  # Permite JS acessar o cookie CSRF
    CSRF_COOKIE_SAMESITE = "Lax"  # Menos restritivo para desenvolvimento
