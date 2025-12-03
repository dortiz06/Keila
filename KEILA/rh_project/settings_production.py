"""
Configuración de producción para el Sistema de Recursos Humanos
"""

from .settings import *
import os

# Configuración de seguridad para producción
DEBUG = False
ALLOWED_HOSTS = [
    "sistemagk.grupokeila.com",
    "www.sistemagk.grupokeila.com",
    "155.138.199.138",
    "vps.gruaskeila.com.mx",
    "127.0.0.1",
    "localhost",
]

# Configuración CSRF para HTTPS
CSRF_TRUSTED_ORIGINS = [
    'https://sistemagk.grupokeila.com',
    'https://www.sistemagk.grupokeila.com',
    'https://vps.gruaskeila.com.mx',
    'http://155.138.199.138',
    'http://127.0.0.1',
    'http://localhost',
]

# Base de datos de producción (PostgreSQL recomendado)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'rh_system'),
        'USER': os.environ.get('DB_USER', 'rh_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Configuración de archivos estáticos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configuración de archivos de medios
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuración de seguridad
SECRET_KEY = os.environ.get('SECRET_KEY', 'cambiar-en-produccion')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Configuración de sesiones
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Configuración de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'empleados': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'rh_project': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'WARNING',
    },
}

# Crear directorio de logs si no existe
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)


