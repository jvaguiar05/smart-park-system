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
        "DIRS": [BASE_DIR / "templates"],
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
    "DESCRIPTION": "API para sistema de gerenciamento inteligente de estacionamentos",
    "VERSION": "v1",
    "SERVE_INCLUDE_SCHEMA": False,
    "TAGS": [
        {
            "name": "Authentication",
            "description": "Endpoints de autenticação e autorização",
        },
        {"name": "Clients", "description": "Gerenciamento de clientes do sistema"},
        {
            "name": "Client Members",
            "description": "Gerenciamento de membros de clientes",
        },
        {"name": "Establishments", "description": "Gerenciamento de estabelecimentos"},
        {"name": "Lots", "description": "Gerenciamento de estacionamentos/lotes"},
        {"name": "Slots", "description": "Gerenciamento de vagas de estacionamento"},
        {"name": "Slot Status", "description": "Status atual das vagas"},
        {
            "name": "Slot Status History",
            "description": "Histórico de mudanças de status das vagas",
        },
        {"name": "Events", "description": "Sistema de eventos de status das vagas"},
        {"name": "Cameras", "description": "Gerenciamento de câmeras de monitoramento"},
        {
            "name": "Camera Monitoring",
            "description": "Monitoramento e heartbeats das câmeras",
        },
        {
            "name": "API Keys",
            "description": "Gerenciamento de chaves de API para hardware",
        },
        {
            "name": "Hardware Integration",
            "description": "Endpoints para integração com hardware",
        },
        {
            "name": "Catalog - Store Types",
            "description": "Tipos de estabelecimento disponíveis",
        },
        {
            "name": "Catalog - Vehicle Types",
            "description": "Tipos de veículos disponíveis",
        },
        {"name": "Catalog - Slot Types", "description": "Tipos de vagas disponíveis"},
        {
            "name": "Public API",
            "description": "Endpoints públicos para consulta de informações",
        },
    ],
    "COMPONENT_SPLIT_REQUEST": True,
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

# CORS
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
