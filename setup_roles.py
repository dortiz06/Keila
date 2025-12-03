#!/usr/bin/env python
"""Script para crear grupos y permisos básicos (RH, JEFES, EMPLEADOS)
Ejecutar: python manage.py shell < setup_roles.py
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from empleados.models import Vacacion

print('Creando grupos...')

rh, _ = Group.objects.get_or_create(name='RH')
jefes, _ = Group.objects.get_or_create(name='JEFES')
empleados, _ = Group.objects.get_or_create(name='EMPLEADOS')

ct_vac = ContentType.objects.get_for_model(Vacacion)

# RH puede añadir/cambiar/ver vacaciones
perms_rh = Permission.objects.filter(content_type=ct_vac, codename__in=[
    'add_vacacion', 'change_vacacion', 'view_vacacion'
])
rh.permissions.set(perms_rh)

# Jefe: puede ver y cambiar (aprobar via vista), no crear
perms_jefe = Permission.objects.filter(content_type=ct_vac, codename__in=[
    'change_vacacion', 'view_vacacion'
])
jefes.permissions.set(perms_jefe)

# Empleado: ver y añadir (sus propias solicitudes)
perms_emp = Permission.objects.filter(content_type=ct_vac, codename__in=[
    'add_vacacion', 'view_vacacion'
])
empleados.permissions.set(perms_emp)

print('✓ Grupos y permisos configurados')

