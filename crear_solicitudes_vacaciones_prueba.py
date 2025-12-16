#!/usr/bin/env python
"""
Script para crear solicitudes de vacaciones de prueba para los usuarios de prueba
Ejecutar con: python crear_solicitudes_vacaciones_prueba.py
"""
import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rh_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from empleados.models import Perfil, SolicitudVacaciones

User = get_user_model()

def crear_solicitudes_vacaciones():
    """Crea solicitudes de vacaciones diferentes para cada usuario de prueba"""
    print('Creando solicitudes de vacaciones de prueba...\n')
    
    hoy = date.today()
    solicitudes_creadas = 0
    
    # Configuración de solicitudes diferentes para cada usuario
    # Cada una con fechas, estados, tipos y motivos diferentes
    configuraciones = [
        {
            'usuario': 'usuario10',
            'fecha_inicio': hoy + timedelta(days=30),  # Próximo mes
            'dias': 5,
            'tipo': 'NORMAL',
            'estado': 'PENDIENTE_JEFE',
            'motivo': 'Descanso y relajación personal'
        },
        {
            'usuario': 'usuario11',
            'fecha_inicio': hoy + timedelta(days=45),
            'dias': 3,
            'tipo': 'NORMAL',
            'estado': 'PENDIENTE_RH',
            'motivo': 'Viaje familiar programado'
        },
        {
            'usuario': 'usuario12',
            'fecha_inicio': hoy + timedelta(days=60),
            'dias': 7,
            'tipo': 'NORMAL',
            'estado': 'APROBADO_RH',
            'motivo': 'Vacaciones de verano'
        },
        {
            'usuario': 'usuario13',
            'fecha_inicio': hoy + timedelta(days=20),
            'dias': 2,
            'tipo': 'EXTRAORDINARIA',
            'estado': 'PENDIENTE_JEFE',
            'motivo': 'Asunto personal urgente'
        },
        {
            'usuario': 'usuario14',
            'fecha_inicio': hoy + timedelta(days=75),
            'dias': 10,
            'tipo': 'NORMAL',
            'estado': 'RECHAZADO_JEFE',
            'motivo': 'Vacaciones largas para descanso',
            'comentarios_jefe': 'No se puede aprobar por carga de trabajo en esa fecha'
        },
        {
            'usuario': 'usuario15',
            'fecha_inicio': hoy + timedelta(days=15),
            'dias': 4,
            'tipo': 'NORMAL',
            'estado': 'APROBADO_JEFE',
            'motivo': 'Celebración de aniversario'
        }
    ]
    
    for config in configuraciones:
        try:
            # Obtener el usuario
            user = User.objects.get(username=config['usuario'])
            
            if not hasattr(user, 'perfil'):
                print(f'⚠️  Usuario {config["usuario"]} no tiene perfil. Omitiendo...\n')
                continue
            
            perfil = user.perfil
            
            # Calcular fecha fin (excluyendo domingos)
            fecha_inicio = config['fecha_inicio']
            dias_solicitados = config['dias']
            fecha_fin = fecha_inicio
            
            # Calcular fecha fin contando solo días laborables (lunes a sábado)
            dias_agregados = 0
            while dias_agregados < dias_solicitados:
                fecha_fin += timedelta(days=1)
                # Si no es domingo (0 = lunes, 6 = domingo), contar el día
                if fecha_fin.weekday() != 6:  # 6 = domingo
                    dias_agregados += 1
            
            # Verificar si ya existe una solicitud similar
            existe = SolicitudVacaciones.objects.filter(
                empleado=perfil,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            ).exists()
            
            if existe:
                print(f'⚠️  Solicitud similar ya existe para {config["usuario"]}. Omitiendo...\n')
                continue
            
            # Crear la solicitud
            solicitud = SolicitudVacaciones.objects.create(
                empleado=perfil,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                dias_solicitados=dias_solicitados,
                tipo=config['tipo'],
                motivo=config['motivo'],
                estado=config['estado'],
                comentarios_jefe=config.get('comentarios_jefe', '')
            )
            
            # Si está aprobada, establecer fechas de aprobación
            if config['estado'] in ['APROBADO_JEFE', 'APROBADO_RH']:
                if config['estado'] == 'APROBADO_JEFE':
                    solicitud.fecha_aprobacion_jefe = timezone.now()
                if config['estado'] == 'APROBADO_RH':
                    solicitud.fecha_aprobacion_rh = timezone.now()
                solicitud.save()
            
            print(f'✓ Solicitud creada para {config["usuario"]} ({perfil.nombre_completo})')
            print(f'  - Fechas: {fecha_inicio.strftime("%d/%m/%Y")} a {fecha_fin.strftime("%d/%m/%Y")}')
            print(f'  - Días: {dias_solicitados}')
            print(f'  - Tipo: {solicitud.get_tipo_display()}')
            print(f'  - Estado: {solicitud.get_estado_display()}')
            print(f'  - Motivo: {config["motivo"]}\n')
            
            solicitudes_creadas += 1
            
        except User.DoesNotExist:
            print(f'❌ Usuario {config["usuario"]} no existe. Omitiendo...\n')
        except Exception as e:
            print(f'❌ Error al crear solicitud para {config["usuario"]}: {str(e)}\n')
    
    print(f'\n{"="*50}')
    print(f'Resumen:')
    print(f'  - Solicitudes creadas: {solicitudes_creadas}')
    print(f'{"="*50}')
    
    if solicitudes_creadas > 0:
        print('\n¡Solicitudes de vacaciones creadas exitosamente!')
        print('\nEstados de las solicitudes:')
        print('  - PENDIENTE_JEFE: 2 solicitudes')
        print('  - PENDIENTE_RH: 1 solicitud')
        print('  - APROBADO_RH: 1 solicitud')
        print('  - APROBADO_JEFE: 1 solicitud')
        print('  - RECHAZADO_JEFE: 1 solicitud')
    else:
        print('\nNo se crearon nuevas solicitudes.')

if __name__ == '__main__':
    crear_solicitudes_vacaciones()
