from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from empleados.models import Perfil, Departamento

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea usuarios de prueba (Usuario10 a Usuario15) con departamento Ventas y antigüedad mínima de 1 año'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creando usuarios de prueba...'))
        
        # Obtener o crear el departamento "Ventas"
        try:
            departamento_ventas = Departamento.objects.get(nombre__iexact='Ventas', activo=True)
            self.stdout.write(f'Departamento "Ventas" encontrado: {departamento_ventas.nombre}')
        except Departamento.DoesNotExist:
            # Crear el departamento si no existe
            departamento_ventas = Departamento.objects.create(
                nombre='Ventas',
                descripcion='Departamento de Ventas',
                activo=True
            )
            self.stdout.write(self.style.SUCCESS('Departamento "Ventas" creado'))
        
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
                self.stdout.write(self.style.WARNING(f'El usuario {username} ya existe. Omitiendo...'))
                continue
            
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
                
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Usuario creado: {username} ({first_name} {last_name})'
                ))
                self.stdout.write(f'  - Password: {password}')
                self.stdout.write(f'  - Departamento: {departamento_ventas.nombre}')
                self.stdout.write(f'  - Fecha contratación: {fecha_contratacion.strftime("%d/%m/%Y")}')
                self.stdout.write(f'  - Antigüedad: {años} año{"s" if años != 1 else ""} ({meses} meses)')
            else:
                self.stdout.write(self.style.ERROR(f'Error: No se pudo crear el perfil para {username}'))
        
        self.stdout.write(self.style.SUCCESS('\n¡Usuarios de prueba creados exitosamente!'))
