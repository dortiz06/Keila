#!/usr/bin/env python
"""
Script para crear usuarios de prueba (Usuario10 a Usuario15)
con departamento Ventas y antigüedad mínima de 1 año
Ejecutar con: python crear_usuarios_prueba.py
o desde Django shell: python manage.py shell < crear_usuarios_prueba.py
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rh_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from datetime import date, timedelta
from empleados.models import Perfil, Departamento

User = get_user_model()

def crear_usuarios_prueba():
    """Crea usuarios de prueba del 10 al 15 con departamento Ventas y antigüedad mínima de 1 año"""
    print('Creando usuarios de prueba...\n')
    
    # Obtener o crear el departamento "Ventas"
    try:
        departamento_ventas = Departamento.objects.get(nombre__iexact='Ventas', activo=True)
        print(f'✓ Departamento "Ventas" encontrado: {departamento_ventas.nombre}\n')
    except Departamento.DoesNotExist:
        # Crear el departamento si no existe
        departamento_ventas = Departamento.objects.create(
            nombre='Ventas',
            descripcion='Departamento de Ventas',
            activo=True
        )
        print(f'✓ Departamento "Ventas" creado\n')
    
    # Fechas de contratación diferentes (mínimo 1 año de antigüedad)
    # Distribuidas en diferentes meses para pruebas
    hoy = date.today()
    fechas_contratacion = [
        hoy - timedelta(days=365 + 30),   # Usuario10: ~1 año y 1 mes
        hoy - timedelta(days=365 + 60),   # Usuario11: ~1 año y 2 meses
        hoy - timedelta(days=365 + 90),   # Usuario12: ~1 año y 3 meses
        hoy - timedelta(days=365 + 120),  # Usuario13: ~1 año y 4 meses
        hoy - timedelta(days=365 + 150),  # Usuario14: ~1 año y 5 meses
        hoy - timedelta(days=365 + 180),  # Usuario15: ~1 año y 6 meses
    ]
    
    usuarios_creados = 0
    usuarios_existentes = 0
    
    # Crear usuarios del 10 al 15 (6 usuarios)
    for idx, i in enumerate(range(10, 16)):
        username = f'usuario{i}'
        first_name = f'Usuario{i}'
        last_name = 'Prueba'
        email = f'usuario{i}@prueba.com'
        password = f'prueba{i}'
        fecha_contratacion = fechas_contratacion[idx]
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            print(f'⚠️  El usuario {username} ya existe. Omitiendo...\n')
            usuarios_existentes += 1
            continue
        
        try:
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Esperar un momento para que el signal se ejecute
            import time
            time.sleep(0.1)
            
            # El perfil se crea automáticamente por el signal, pero necesitamos actualizarlo
            # Si no existe, crearlo manualmente
            if hasattr(user, 'perfil'):
                perfil = user.perfil
            else:
                # Si el signal no funcionó, crear el perfil manualmente
                from empleados.models import Perfil
                perfil = Perfil.objects.create(
                    usuario=user,
                    tipo_perfil='EMPLEADO',
                    fecha_contratacion=date.today(),
                    numero_empleado=f"EMP{user.id:04d}",
                    puesto="Por definir"
                )
            
            # Actualizar el perfil con los datos correctos
            perfil.tipo_perfil = 'EMPLEADO'
            perfil.departamento = departamento_ventas
            perfil.fecha_contratacion = fecha_contratacion
            perfil.numero_empleado = f'PRUEBA{i:03d}'
            perfil.puesto = 'Empleado de Prueba'
            perfil.activo = True
            perfil.save()
                
                # Calcular antigüedad para mostrar
                años = perfil.antiguedad_anos
                meses = (hoy.year - fecha_contratacion.year) * 12 + (hoy.month - fecha_contratacion.month)
                
                print(f'✓ Usuario creado: {username}')
                print(f'  - Nombre: {first_name} {last_name}')
                print(f'  - Email: {email}')
                print(f'  - Password: {password}')
                print(f'  - Departamento: {departamento_ventas.nombre}')
                print(f'  - Fecha contratación: {fecha_contratacion.strftime("%d/%m/%Y")}')
                print(f'  - Antigüedad: {años} año{"s" if años != 1 else ""} ({meses} meses)')
                print(f'  - Número de empleado: PRUEBA{i:03d}\n')
                usuarios_creados += 1
            else:
                print(f'❌ Error: No se pudo crear el perfil para {username}\n')
        except Exception as e:
            print(f'❌ Error al crear {username}: {str(e)}\n')
    
    print(f'\n{"="*50}')
    print(f'Resumen:')
    print(f'  - Usuarios creados: {usuarios_creados}')
    print(f'  - Usuarios ya existentes: {usuarios_existentes}')
    print(f'{"="*50}')
    
    if usuarios_creados > 0:
        print('\n¡Usuarios de prueba creados exitosamente!')
    else:
        print('\nNo se crearon nuevos usuarios.')

if __name__ == '__main__':
    crear_usuarios_prueba()
