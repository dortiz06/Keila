#!/usr/bin/env python
"""Script para restablecer la contraseña del usuario admin"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rh_project.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'admin'
new_password = 'admin123'

try:
    user = User.objects.get(username=username)
    user.set_password(new_password)
    user.save()
    print(f'✅ Contraseña del usuario "{username}" restablecida exitosamente.')
    print(f'   Nueva contraseña: {new_password}')
except User.DoesNotExist:
    print(f'❌ El usuario "{username}" no existe.')
except Exception as e:
    print(f'❌ Error: {e}')

