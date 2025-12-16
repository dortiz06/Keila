#!/usr/bin/env python
"""
Script para verificar y crear usuarios de prueba si no existen
Ejecutar con: python verificar_usuarios_prueba.py
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

def verificar_y_crear_usuarios():
    """Verifica y crea usuarios de prueba del 10 al 15"""
    print('Verificando usuarios de prueba...\n')
    
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
    usuarios_actualizados = 0
    usuarios_existentes = 0
    
    # Verificar y crear usuarios del 10 al 15 (6 usuarios)
    for idx, i in enumerate(range(10, 16)):
        username = f'usuario{i}'
        first_name = f'Usuario{i}'
        last_name = 'Prueba'
        email = f'usuario{i}@prueba.com'
        password = f'prueba{i}'
        fecha_contratacion = fechas_contratacion[idx]
        
        # Verificar si el usuario ya existe
        try:
            user = User.objects.get(username=username)
            usuarios_existentes += 1
            print(f'⚠️  Usuario {username} ya existe')
            
            # Verificar si tiene perfil
            if hasattr(user, 'perfil'):
                perfil = user.perfil
                # Actualizar perfil si es necesario
                actualizado = False
                if perfil.departamento != departamento_ventas:
                    perfil.departamento = departamento_ventas
                    actualizado = True
                if perfil.fecha_contratacion != fecha_contratacion:
                    perfil.fecha_contratacion = fecha_contratacion
                    actualizado = True
                if perfil.tipo_perfil != 'EMPLEADO':
                    perfil.tipo_perfil = 'EMPLEADO'
                    actualizado = True
                if perfil.puesto != 'Empleado de Prueba':
                    perfil.puesto = 'Empleado de Prueba'
                    actualizado = True
                if not perfil.activo:
                    perfil.activo = True
                    actualizado = True
                
                if actualizado:
                    perfil.save()
                    usuarios_actualizados += 1
                    print(f'  ✓ Perfil actualizado')
                else:
                    print(f'  ✓ Perfil ya está correcto')
                
                # Mostrar información
                años = perfil.antiguedad_anos
                meses = (hoy.year - perfil.fecha_contratacion.year) * 12 + (hoy.month - perfil.fecha_contratacion.month)
                print(f'  - Departamento: {perfil.departamento.nombre if perfil.departamento else "Sin departamento"}')
                print(f'  - Fecha contratación: {perfil.fecha_contratacion.strftime("%d/%m/%Y")}')
                print(f'  - Antigüedad: {años} año{"s" if años != 1 else ""} ({meses} meses)')
                print(f'  - Tipo: {perfil.get_tipo_perfil_display()}')
                print(f'  - Activo: {"Sí" if perfil.activo else "No"}\n')
            else:
                # Crear perfil si no existe
                print(f'  ⚠️  Usuario sin perfil, creando perfil...')
                perfil = Perfil.objects.create(
                    usuario=user,
                    tipo_perfil='EMPLEADO',
                    departamento=departamento_ventas,
                    fecha_contratacion=fecha_contratacion,
                    numero_empleado=f'PRUEBA{i:03d}',
                    puesto='Empleado de Prueba',
                    activo=True
                )
                usuarios_actualizados += 1
                print(f'  ✓ Perfil creado\n')
                
        except User.DoesNotExist:
            # Crear usuario nuevo
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # El perfil debería crearse automáticamente por el signal
                # Pero lo verificamos y actualizamos si es necesario
                if hasattr(user, 'perfil'):
                    perfil = user.perfil
                    perfil.tipo_perfil = 'EMPLEADO'
                    perfil.departamento = departamento_ventas
                    perfil.fecha_contratacion = fecha_contratacion
                    perfil.numero_empleado = f'PRUEBA{i:03d}'
                    perfil.puesto = 'Empleado de Prueba'
                    perfil.activo = True
                    perfil.save()
                else:
                    # Si el signal no funcionó, crear el perfil manualmente
                    perfil = Perfil.objects.create(
                        usuario=user,
                        tipo_perfil='EMPLEADO',
                        departamento=departamento_ventas,
                        fecha_contratacion=fecha_contratacion,
                        numero_empleado=f'PRUEBA{i:03d}',
                        puesto='Empleado de Prueba',
                        activo=True
                    )
                
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
                
            except Exception as e:
                print(f'❌ Error al crear {username}: {str(e)}\n')
    
    print(f'\n{"="*50}')
    print(f'Resumen:')
    print(f'  - Usuarios nuevos creados: {usuarios_creados}')
    print(f'  - Usuarios actualizados: {usuarios_actualizados}')
    print(f'  - Usuarios ya existentes (sin cambios): {usuarios_existentes - usuarios_actualizados}')
    print(f'{"="*50}')
    
    # Verificar que todos los usuarios tengan perfiles
    print(f'\nVerificando que todos los usuarios tengan perfiles...')
    usuarios_sin_perfil = []
    for i in range(10, 16):
        username = f'usuario{i}'
        try:
            user = User.objects.get(username=username)
            if not hasattr(user, 'perfil'):
                usuarios_sin_perfil.append(username)
        except User.DoesNotExist:
            pass
    
    if usuarios_sin_perfil:
        print(f'⚠️  Usuarios sin perfil: {", ".join(usuarios_sin_perfil)}')
    else:
        print(f'✓ Todos los usuarios tienen perfiles')
    
    # Mostrar lista de todos los usuarios de prueba
    print(f'\n{"="*50}')
    print(f'Lista de usuarios de prueba:')
    print(f'{"="*50}')
    for i in range(10, 16):
        username = f'usuario{i}'
        try:
            user = User.objects.get(username=username)
            if hasattr(user, 'perfil'):
                perfil = user.perfil
                print(f'{username}: {perfil.nombre_completo} - {perfil.get_tipo_perfil_display()} - {perfil.departamento.nombre if perfil.departamento else "Sin dept"} - Activo: {"Sí" if perfil.activo else "No"}')
            else:
                print(f'{username}: SIN PERFIL')
        except User.DoesNotExist:
            print(f'{username}: NO EXISTE')

if __name__ == '__main__':
    verificar_y_crear_usuarios()
