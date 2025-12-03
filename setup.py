#!/usr/bin/env python
"""
Script de configuración inicial para el Sistema de Recursos Humanos
Ejecutar: python setup.py
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_database():
    """Configura la base de datos inicial"""
    print("🔧 Configurando base de datos...")
    
    # Aplicar migraciones
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("✅ Base de datos configurada correctamente")

def create_sample_data():
    """Crea datos de ejemplo para demostración"""
    print("📊 Creando datos de ejemplo...")
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rh_project.settings')
    django.setup()
    
    from empleados.models import Departamento, Empleado, Vacacion
    from datetime import date, timedelta
    import random
    
    # Crear departamentos
    departamentos_data = [
        {'nombre': 'Recursos Humanos', 'descripcion': 'Gestión del talento humano'},
        {'nombre': 'Tecnología', 'descripcion': 'Desarrollo y soporte técnico'},
        {'nombre': 'Ventas', 'descripcion': 'Equipo comercial y marketing'},
        {'nombre': 'Finanzas', 'descripcion': 'Contabilidad y finanzas'},
        {'nombre': 'Operaciones', 'descripcion': 'Gestión operativa'},
    ]
    
    departamentos = []
    for dept_data in departamentos_data:
        dept, created = Departamento.objects.get_or_create(
            nombre=dept_data['nombre'],
            defaults={'descripcion': dept_data['descripcion']}
        )
        departamentos.append(dept)
        if created:
            print(f"  ✓ Creado departamento: {dept.nombre}")
    
    # Crear empleados de ejemplo
    empleados_data = [
        {
            'numero_empleado': 'EMP001',
            'nombre': 'Ana',
            'apellido_paterno': 'García',
            'apellido_materno': 'López',
            'fecha_nacimiento': date(1985, 5, 15),
            'genero': 'F',
            'estado_civil': 'C',
            'telefono': '555-0101',
            'email': 'ana.garcia@empresa.com',
            'direccion': 'Calle Principal 123, Ciudad',
            'departamento': departamentos[0],  # RH
            'puesto': 'Gerente de RH',
            'fecha_ingreso': date(2020, 1, 15),
            'salario': 25000.00,
            'dias_vacaciones_anuales': 25,
            'dias_vacaciones_usados': 5,
        },
        {
            'numero_empleado': 'EMP002',
            'nombre': 'Carlos',
            'apellido_paterno': 'Rodríguez',
            'apellido_materno': 'Martínez',
            'fecha_nacimiento': date(1990, 8, 22),
            'genero': 'M',
            'estado_civil': 'S',
            'telefono': '555-0102',
            'email': 'carlos.rodriguez@empresa.com',
            'direccion': 'Avenida Central 456, Ciudad',
            'departamento': departamentos[1],  # Tecnología
            'puesto': 'Desarrollador Senior',
            'fecha_ingreso': date(2021, 3, 10),
            'salario': 22000.00,
            'dias_vacaciones_anuales': 20,
            'dias_vacaciones_usados': 8,
        },
        {
            'numero_empleado': 'EMP003',
            'nombre': 'María',
            'apellido_paterno': 'Fernández',
            'apellido_materno': 'Sánchez',
            'fecha_nacimiento': date(1988, 12, 3),
            'genero': 'F',
            'estado_civil': 'C',
            'telefono': '555-0103',
            'email': 'maria.fernandez@empresa.com',
            'direccion': 'Plaza Mayor 789, Ciudad',
            'departamento': departamentos[2],  # Ventas
            'puesto': 'Ejecutiva de Ventas',
            'fecha_ingreso': date(2019, 6, 1),
            'salario': 18000.00,
            'dias_vacaciones_anuales': 20,
            'dias_vacaciones_usados': 12,
        },
        {
            'numero_empleado': 'EMP004',
            'nombre': 'Luis',
            'apellido_paterno': 'Hernández',
            'apellido_materno': 'González',
            'fecha_nacimiento': date(1992, 4, 18),
            'genero': 'M',
            'estado_civil': 'S',
            'telefono': '555-0104',
            'email': 'luis.hernandez@empresa.com',
            'direccion': 'Calle Secundaria 321, Ciudad',
            'departamento': departamentos[3],  # Finanzas
            'puesto': 'Contador',
            'fecha_ingreso': date(2022, 2, 14),
            'salario': 16000.00,
            'dias_vacaciones_anuales': 20,
            'dias_vacaciones_usados': 3,
        },
        {
            'numero_empleado': 'EMP005',
            'nombre': 'Laura',
            'apellido_paterno': 'Morales',
            'apellido_materno': 'Jiménez',
            'fecha_nacimiento': date(1987, 9, 7),
            'genero': 'F',
            'estado_civil': 'D',
            'telefono': '555-0105',
            'email': 'laura.morales@empresa.com',
            'direccion': 'Boulevard Norte 654, Ciudad',
            'departamento': departamentos[4],  # Operaciones
            'puesto': 'Coordinadora de Operaciones',
            'fecha_ingreso': date(2020, 11, 20),
            'salario': 19000.00,
            'dias_vacaciones_anuales': 20,
            'dias_vacaciones_usados': 15,
        },
    ]
    
    empleados = []
    for emp_data in empleados_data:
        emp, created = Empleado.objects.get_or_create(
            numero_empleado=emp_data['numero_empleado'],
            defaults=emp_data
        )
        empleados.append(emp)
        if created:
            print(f"  ✓ Creado empleado: {emp.nombre_completo}")
    
    # Crear vacaciones de ejemplo
    estados = ['P', 'A', 'R']
    motivos = [
        'Vacaciones familiares',
        'Descanso personal',
        'Viaje de negocios',
        'Emergencia familiar',
        'Celebración especial',
    ]
    
    for i, empleado in enumerate(empleados):
        # Crear 2-3 vacaciones por empleado
        num_vacaciones = random.randint(2, 3)
        for j in range(num_vacaciones):
            fecha_inicio = date.today() + timedelta(days=random.randint(-30, 60))
            dias_vacacion = random.randint(3, 10)
            fecha_fin = fecha_inicio + timedelta(days=dias_vacacion - 1)
            
            vacacion, created = Vacacion.objects.get_or_create(
                empleado=empleado,
                fecha_inicio=fecha_inicio,
                defaults={
                    'fecha_fin': fecha_fin,
                    'dias_solicitados': dias_vacacion,
                    'motivo': random.choice(motivos),
                    'estado': random.choice(estados),
                    'comentarios_rh': 'Aprobado por el sistema' if random.choice(estados) == 'A' else '',
                }
            )
            if created:
                print(f"  ✓ Creada vacación para {empleado.nombre_completo}")
    
    print("✅ Datos de ejemplo creados correctamente")

def main():
    """Función principal de configuración"""
    print("🚀 Iniciando configuración del Sistema de Recursos Humanos...")
    print("=" * 60)
    
    try:
        # Configurar base de datos
        setup_database()
        print()
        
        # Crear datos de ejemplo
        create_sample_data()
        print()
        
        print("=" * 60)
        print("🎉 ¡Configuración completada exitosamente!")
        print()
        print("📋 Próximos pasos:")
        print("1. Crear un superusuario: python manage.py createsuperuser")
        print("2. Ejecutar el servidor: python manage.py runserver")
        print("3. Acceder a la aplicación: http://127.0.0.1:8000/")
        print("4. Acceder al admin: http://127.0.0.1:8000/admin/")
        print()
        print("👥 Datos de ejemplo creados:")
        print("- 5 departamentos")
        print("- 5 empleados con información completa")
        print("- Múltiples solicitudes de vacaciones")
        print()
        print("¡El sistema está listo para usar! 🎊")
        
    except Exception as e:
        print(f"❌ Error durante la configuración: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()


