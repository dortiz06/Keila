"""
Configuración de producción para el Sistema de Recursos Humanos
"""

from .settings import *
import os

# Configuración de seguridad para producción
DEBUG = False
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    'tu-dominio.com',
    'sistemagk.gruaskeila.com.mx',
    'www.sistemagk.gruaskeila.com.mx',
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

# Configuración de sesiones
# Si usas HTTPS, cambia estos a True
SESSION_COOKIE_SECURE = False  # Cambiar a True si usas HTTPS
CSRF_COOKIE_SECURE = False  # Cambiar a True si usas HTTPS
CSRF_TRUSTED_ORIGINS = [
    'https://sistemagk.gruaskeila.com.mx',
    'http://sistemagk.gruaskeila.com.mx',
    'https://www.sistemagk.gruaskeila.com.mx',
    'http://www.sistemagk.gruaskeila.com.mx',
]

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


