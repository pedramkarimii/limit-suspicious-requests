import os
from pathlib import Path
from datetime import timedelta
from decouple import config  # noqa

# Timezone and Localization Settings
USE_TZ = True
USE_I18N = True
LANGUAGE_CODE = "en-us"

# URL Configuration
ROOT_URLCONF = "config.urls"

# Authentication Settings
AUTH_USER_MODEL = 'account.User'
WSGI_APPLICATION = "config.wsgi.application"

# Time Zone Configuration
TIME_ZONE = config("TIME_ZONE", default="UTC")

# Debugging Configuration
DEBUG = config("DEBUG", cast=bool, default=True)

# Base Directory Path
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "apps"

# Default Auto Field for Models
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Secret Key for Cryptographic Signing
SECRET_KEY = config("SECRET_KEY", default="secret-key-!!!")

# Allowed Hosts Configuration
ALLOWED_HOSTS = (
    ["*"]
    if DEBUG
    else config(
        "ALLOWED_HOSTS", cast=lambda host: [h.strip() for h in host.split(",") if h]
    )
)

# Applications to Include
APPLICATIONS = ["account", "core"]

# Middleware Configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middlewares.LoginRequiredMiddleware'
]

# Template Settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Password Validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],

    'DEFAULT_THROTTLE_RATES': {
        'login_attempt': '3/h',
        'registration_attempt': '3/h',
    },

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Simple JWT Configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=20),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(minutes=20),
    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

# DRF Spectacular Settings for API Schema Generation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Achare',
    'DESCRIPTION': 'Limit Suspicious Requests',
    'VERSION': '1.0.0',
}

# Static and Media Files Configuration
STATIC_URL = "storage/static/"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "storage/media"

# Caching Configuration
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / "utility/cache",
    }
}

# Mode Handling: Development vs Production
if DEBUG:

    # Installed Apps for Development
    INSTALLED_APPS = [
        "jazzmin",  # Third-party
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # Third-party
        "rest_framework",
        "rest_framework.authtoken",
        "drf_spectacular",
        # Application
        *list(map(lambda app: f"apps.{app}", APPLICATIONS)),
    ]
    # Uncomment to set additional static files directory for development
    # STATICFILES_DIRS = [BASE_DIR / "storage/static"]

    # Database Configuration for Development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST"),
            "PORT": config("DB_PORT"),
        }
    }

    # Email Configuration for Development
    EMAIL_BACKEND = config("DEBUG_EMAIL_BACKEND")
    EMAIL_USE_TLS = config("DEBUG_EMAIL_USE_TLS", cast=bool, default=True)
    EMAIL_USE_SSL = config("DEBUG_EMAIL_USE_SSL", cast=bool, default=False)
    EMAIL_HOST = config("DEBUG_EMAIL_HOST")
    EMAIL_PORT = config("DEBUG_EMAIL_PORT")
    EMAIL_HOST_USER = config("DEBUG_EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = config("DEBUG_EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = config("DEBUG_DEFAULT_FROM_EMAIL")
else:

    # Trusted origins for CSRF protection in production
    CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS")

    # Static files configuration for production
    STATIC_ROOT = BASE_DIR / "storage/static/"

    # Installed Apps for Production
    INSTALLED_APPS = [
        "jazzmin",  # Third-party
        "django.contrib.auth",
        "django.contrib.contenttypes",
        # Third-party
        "rest_framework",
        "rest_framework.authtoken",
        "drf_spectacular",
        # Application
        *list(map(lambda app: f"apps.{app}", APPLICATIONS)),
    ]

    # Redis URL for caching
    REDIS_URL = f"redis://{config('REDIS_HOST')}:{config('REDIS_PORT')}"

    # Uncomment to use Redis for caching
    # CACHES = {
    #     "default": {
    #         "BACKEND": "django.core.cache.backends.redis.RedisCache",
    #         "LOCATION": REDIS_URL,
    #     }
    # }

    # Session engine configuration for production
    SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

    # Email configuration for production
    EMAIL_BACKEND = config("EMAIL_BACKEND")
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
    EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)
    EMAIL_HOST = config("EMAIL_HOST")
    EMAIL_PORT = config("EMAIL_PORT")
    EMAIL_HOST_USER = config("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")

    # AWS S3 Configuration for file storage
    DEFAULT_FILE_STORAGE = config('DEFAULT_FILE_STORAGE')
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_FILE_OVERWRITE = config('AWS_S3_FILE_OVERWRITE', cast=bool, default=False)
    AWS_SERVICE_NAME = config('AWS_SERVICE_NAME', default='s3')
    AWS_LOCAL_STORAGE = f"{BASE_DIR}/storage/aws/"
