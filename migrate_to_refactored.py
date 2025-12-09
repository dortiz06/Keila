#!/usr/bin/env python
"""
Script de migración para refactorizar el sistema de RH
Ejecutar: python manage.py shell < migrate_to_refactored.py
"""

import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rh_project.settings')
django.setup()

from django.contrib.auth.models import User
from empleados.models import Empleado, Departamento, Vacacion
from empleados.models_refactored import Perfil, SolicitudVacaciones

def migrar_datos():
    """Migrar datos del sistema anterior al nuevo"""
    print("🚀 Iniciando migración del sistema...")
    print("=" * 50)
    
    # 1. Migrar Departamentos
    print("📁 Migrando departamentos...")
    departamentos_antiguos = Departamento.objects.all()
    for dept in departamentos_antiguos:
        print(f"  ✓ {dept.nombre}")
    print(f"  Total: {departamentos_antiguos.count()} departamentos")
    
    # 2. Migrar Empleados a Perfiles
    print("\n👥 Migrando empleados a perfiles...")
    empleados_antiguos = Empleado.objects.all()
    
    for empleado in empleados_antiguos:
        if empleado.user:
            # Determinar tipo de perfil según grupos
            tipo_perfil = 'EMPLEADO'  # Default
            
            if empleado.user.groups.filter(name='RH').exists():
                tipo_perfil = 'RH'
            elif empleado.user.groups.filter(name='JEFES').exists():
                tipo_perfil = 'JEFE_AREA'
            elif empleado.user.is_superuser:
                tipo_perfil = 'ADMIN'
            
            # Crear perfil
            perfil, created = Perfil.objects.get_or_create(
                usuario=empleado.user,
                defaults={
                    'tipo_perfil': tipo_perfil,
                    'departamento': empleado.departamento,
                    'fecha_contratacion': empleado.fecha_ingreso,
                    'numero_empleado': empleado.numero_empleado,
                    'puesto': empleado.puesto,
                    'salario': empleado.salario,
                    'telefono': empleado.telefono,
                    'direccion': empleado.direccion,
                    'fecha_nacimiento': empleado.fecha_nacimiento,
                    'dias_vacaciones_anuales': empleado.dias_vacaciones_anuales,
                    'dias_vacaciones_usados': empleado.dias_vacaciones_usados,
                    'activo': empleado.activo,
                }
            )
            
            if created:
                print(f"  ✓ Creado perfil para {empleado.nombre_completo} ({tipo_perfil})")
            else:
                print(f"  - Perfil ya existe para {empleado.nombre_completo}")
    
    print(f"  Total: {empleados_antiguos.count()} empleados procesados")
    
    # 3. Migrar Vacaciones a SolicitudVacaciones
    print("\n🏖️ Migrando solicitudes de vacaciones...")
    vacaciones_antiguas = Vacacion.objects.all()
    
    for vacacion in vacaciones_antiguas:
        # Obtener perfil del empleado
        try:
            perfil_empleado = Perfil.objects.get(usuario=vacacion.empleado.user)
        except Perfil.DoesNotExist:
            print(f"  ⚠️ No se encontró perfil para {vacacion.empleado.nombre_completo}")
            continue
        
        # Mapear estados
        estado_mapping = {
            'P': 'PENDIENTE_JEFE',
            'A': 'APROBADO_RH',
            'R': 'RECHAZADO_JEFE',
            'C': 'CANCELADO',
        }
        
        # Determinar estado final
        if vacacion.aprobado_rh:
            estado_final = 'APROBADO_RH'
        elif vacacion.aprobado_jefe:
            estado_final = 'PENDIENTE_RH'
        elif vacacion.estado == 'R':
            estado_final = 'RECHAZADO_JEFE'
        elif vacacion.estado == 'C':
            estado_final = 'CANCELADO'
        else:
            estado_final = 'PENDIENTE_JEFE'
        
        # Crear solicitud
        solicitud = SolicitudVacaciones.objects.create(
            empleado=perfil_empleado,
            fecha_inicio=vacacion.fecha_inicio,
            fecha_fin=vacacion.fecha_fin,
            dias_solicitados=vacacion.dias_solicitados,
            tipo='NORMAL' if vacacion.tipo == 'N' else 'EXTRAORDINARIA',
            motivo=vacacion.motivo,
            estado=estado_final,
            comentarios_jefe=vacacion.comentarios_rh if vacacion.aprobado_jefe else '',
            comentarios_rh=vacacion.comentarios_rh if vacacion.aprobado_rh else '',
            fecha_solicitud=vacacion.fecha_solicitud,
            fecha_aprobacion_jefe=vacacion.fecha_aprobacion if vacacion.aprobado_jefe else None,
            fecha_aprobacion_rh=vacacion.fecha_aprobacion if vacacion.aprobado_rh else None,
        )
        
        print(f"  ✓ Migrada solicitud de {perfil_empleado.nombre_completo}")
    
    print(f"  Total: {vacaciones_antiguas.count()} solicitudes migradas")
    
    # 4. Estadísticas finales
    print("\n📊 Estadísticas del sistema migrado:")
    print(f"  - Perfiles creados: {Perfil.objects.count()}")
    print(f"  - Departamentos: {Departamento.objects.count()}")
    print(f"  - Solicitudes de vacaciones: {SolicitudVacaciones.objects.count()}")
    
    print("\n✅ Migración completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. Actualizar las URLs en rh_project/urls.py")
    print("2. Renombrar los archivos refactorizados")
    print("3. Actualizar los templates")
    print("4. Probar el sistema")


def crear_grupos_permisos():
    """Crear grupos y permisos para el nuevo sistema"""
    print("\n🔐 Configurando grupos y permisos...")
    
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    
    # Crear grupos
    grupos = ['RH', 'JEFES', 'EMPLEADOS']
    for nombre_grupo in grupos:
        grupo, created = Group.objects.get_or_create(name=nombre_grupo)
        if created:
            print(f"  ✓ Grupo '{nombre_grupo}' creado")
        else:
            print(f"  - Grupo '{nombre_grupo}' ya existe")
    
    print("✅ Grupos configurados")


if __name__ == '__main__':
    try:
        crear_grupos_permisos()
        migrar_datos()
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
