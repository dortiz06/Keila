"""
ASGI config for rh_project project.
"""

import os

from django.core.asgi import get_asgi_application

# Usar settings_production solo si se especifica, sino usar settings para desarrollo
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rh_project.settings')

application = get_asgi_application()


