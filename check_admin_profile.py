#!/usr/bin/env python
"""Script para verificar y crear perfil del usuario admin"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rh_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from empleados.models import Perfil

User = get_user_model()
username = 'admin'

try:
    user = User.objects.get(username=username)
    print(f'Usuario encontrado: {user.username}')
    
    try:
        perfil = Perfil.objects.get(usuario=user)
        print(f'✅ Perfil encontrado: {perfil.tipo_perfil}')
        print(f'   Departamento: {perfil.departamento.nombre if perfil.departamento else "Sin departamento"}')
    except Perfil.DoesNotExist:
        print('⚠️  El usuario admin NO tiene perfil asociado.')
        print('   Esto puede causar problemas al iniciar sesión.')
        print('   ¿Deseas crear un perfil ADMIN para este usuario?')
        print('   (Puedes hacerlo desde el admin de Django después de iniciar sesión)')
        
except User.DoesNotExist:
    print(f'❌ El usuario "{username}" no existe.')
except Exception as e:
    print(f'❌ Error: {e}')

