"""
Archivo de configuración para Passenger (usado por muchos hosts compartidos)
Este archivo debe estar en la raíz del proyecto (donde está manage.py)
"""

import sys
import os

# Agregar el directorio del proyecto al path de Python
sys.path.insert(0, os.path.dirname(__file__))

# Configurar el módulo de settings de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rh_project.settings_production')

# Importar la aplicación WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

