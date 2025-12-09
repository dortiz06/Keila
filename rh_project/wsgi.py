"""
WSGI config for rh_project project.
"""

import os

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'rh_project.settings_production'
)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

