	"""
Configuración de producción para el Sistema de Recursos Humanos
"""

# No usar asterisco (*) aquí.
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

import os

# Configuración de seguridad para producción
DEBUG = False
<<<<<<< HEAD

ALLOWED_HOSTS = [
    "sistemagk.gruaskeila.com.mx",
    "www.sistemagk.gruaskeila.com.mx",
    "localhost",
    "127.0.0.1",
]


CSRF_TRUSTED_ORIGINS = [
    'https://sistemagk.gruaskeila.com.mx',
    'https://www.sistemagk.gruaskeila.com.mx',
]


=======
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    'tu-dominio.com',
    'sistemagk.gruaskeila.com.mx',
    'www.sistemagk.gruaskeila.com.mx',
]
>>>>>>> origin/ALEX

# Base de datos de producción (PostgreSQL recomendado)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Grupokeila_db',
        'USER': 'daniel',
        'PASSWORD': 'Keila2025@',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Configuración de archivos estáticos
<<<<<<< HEAD

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATIC_URL = '/static/'

"""
# No STATICFILES_DIRS aquí, es solo para desarrollo.
=======
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
>>>>>>> origin/ALEX
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
"""

ROOT_URLCONF = 'rh_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'rh_project.wsgi.application'


# Configuración de archivos de medios
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuración de seguridad

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True

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

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'empleados',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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


