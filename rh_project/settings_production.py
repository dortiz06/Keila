"""
Configuración de producción para el Sistema de Recursos Humanos
"""

from .settings import *
import os

# Configuración de seguridad para producción
DEBUG = False

# Actualizar ALLOWED_HOSTS con el dominio correcto
ALLOWED_HOSTS = [
    'sistemagk.grupokeila.com',
    'www.sistemagk.grupokeila.com',
    '155.138.199.138',
    'sistemagk.gruaskeila.com.mx',
    'www.sistemagk.gruaskeila.com.mx',
    'localhost',
    '127.0.0.1'
]

# Configuración CSRF para HTTPS
CSRF_TRUSTED_ORIGINS = [
    'https://sistemagk.grupokeila.com',
    'https://www.sistemagk.grupokeila.com',
    'http://155.138.199.138',
    'https://sistemagk.gruaskeila.com.mx',
    'https://www.sistemagk.gruaskeila.com.mx',
    'http://sistemagk.gruaskeila.com.mx',
    'http://www.sistemagk.gruaskeila.com.mx',
]

# Base de datos de producción (PostgreSQL)
# Usar variables de entorno o valores por defecto
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'Grupokeila_db'),
        'USER': os.environ.get('DB_USER', 'daniel'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'Keila2025@'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Configuración de archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configuración de archivos de medios
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuración de seguridad
SECRET_KEY = os.environ.get('SECRET_KEY', 'cambiar-en-produccion')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True

# Configuración de sesiones
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Configuración de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Crear directorio de logs si no existe
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
