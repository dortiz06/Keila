"""
Configuración específica para PythonAnywhere
Copia este archivo y reemplaza 'tuusuario' con tu usuario de PythonAnywhere
"""
from .settings import *
import os

# ⚠️ IMPORTANTE: Reemplaza 'tuusuario' con tu usuario de PythonAnywhere
PYTHONANYWHERE_USER = 'tuusuario'  # CAMBIAR ESTO

# Configuración de seguridad
DEBUG = False
ALLOWED_HOSTS = [
    f'{PYTHONANYWHERE_USER}.pythonanywhere.com',
    'www.pythonanywhere.com',  # Por si acaso
]

# Base de datos MySQL de PythonAnywhere
# Formato: usuario$nombre_db
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': f'{PYTHONANYWHERE_USER}$rh_system',  # Formato requerido por PythonAnywhere
        'USER': PYTHONANYWHERE_USER,
        'PASSWORD': os.environ.get('DB_PASSWORD', 'tu_password_mysql_aqui'),  # Cambiar esto
        'HOST': f'{PYTHONANYWHERE_USER}.mysql.pythonanywhere-services.com',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}

# Archivos estáticos
# Ajusta estas rutas según donde esté tu proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = f'/home/{PYTHONANYWHERE_USER}/Keila/staticfiles'  # Ajusta si tu carpeta tiene otro nombre
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Archivos media
MEDIA_ROOT = f'/home/{PYTHONANYWHERE_USER}/Keila/media'
MEDIA_URL = '/media/'

# Secret Key - Genera uno nuevo para producción
# Puedes usar: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = os.environ.get('SECRET_KEY', 'GENERA-UN-SECRET-KEY-NUEVO-AQUI')

# Seguridad
# PythonAnywhere maneja SSL, así que estos pueden ser False en el plan gratuito
SECURE_SSL_REDIRECT = False  # Cambiar a True si tienes SSL personalizado
SESSION_COOKIE_SECURE = False  # Cambiar a True si usas HTTPS
CSRF_COOKIE_SECURE = False  # Cambiar a True si usas HTTPS
CSRF_TRUSTED_ORIGINS = [
    f'https://{PYTHONANYWHERE_USER}.pythonanywhere.com',
]

# Configuración de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': f'/home/{PYTHONANYWHERE_USER}/Keila/logs/django.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Crear directorio de logs si no existe
os.makedirs(f'/home/{PYTHONANYWHERE_USER}/Keila/logs', exist_ok=True)

# Configuraciones adicionales
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

