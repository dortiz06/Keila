from django.core.management.base import BaseCommand
from django.utils import timezone
from empleados.models import Perfil
from datetime import date


class Command(BaseCommand):
    help = 'Resetea los días de vacaciones usados para todos los empleados activos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué se haría sin ejecutar los cambios',
        )
        parser.add_argument(
            '--empleado-id',
            type=int,
            help='Resetear solo un empleado específico por ID',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        empleado_id = options.get('empleado_id')
        
        # Filtrar empleados
        if empleado_id:
            empleados = Perfil.objects.filter(id=empleado_id, activo=True)
            if not empleados.exists():
                self.stdout.write(
                    self.style.ERROR(f'No se encontró empleado con ID {empleado_id}')
                )
                return
        else:
            empleados = Perfil.objects.filter(activo=True)
        
        total_empleados = empleados.count()
        empleados_con_vacaciones = empleados.filter(dias_vacaciones_usados__gt=0)
        
        self.stdout.write(f'📊 Resumen:')
        self.stdout.write(f'  - Total empleados activos: {total_empleados}')
        self.stdout.write(f'  - Empleados con vacaciones usadas: {empleados_con_vacaciones.count()}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 MODO DRY-RUN - No se realizarán cambios'))
            self.stdout.write('\nEmpleados que serían afectados:')
            for empleado in empleados_con_vacaciones:
                self.stdout.write(
                    f'  - {empleado.nombre_completo} ({empleado.numero_empleado}): '
                    f'{empleado.dias_vacaciones_usados} días usados → 0 días'
                )
        else:
            # Resetear vacaciones
            updated = empleados_con_vacaciones.update(dias_vacaciones_usados=0)
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Reset completado exitosamente')
            )
            self.stdout.write(f'  - Empleados actualizados: {updated}')
            self.stdout.write(f'  - Fecha de reset: {timezone.now().strftime("%d/%m/%Y %H:%M")}')
            
            # Mostrar empleados actualizados
            if updated > 0:
                self.stdout.write('\nEmpleados actualizados:')
                for empleado in empleados_con_vacaciones:
                    self.stdout.write(f'  - {empleado.nombre_completo} ({empleado.numero_empleado})')
        
        # Mostrar estadísticas de antigüedad
        self.stdout.write(f'\n📈 Estadísticas de antigüedad:')
        for anos in range(0, 6):
            count = empleados.filter(
                fecha_contratacion__year=timezone.now().year - anos
            ).count()
            if count > 0:
                self.stdout.write(f'  - {anos} año{"s" if anos != 1 else ""}: {count} empleado{"s" if count != 1 else ""}')
        
        # Mostrar empleados próximos a cumplir 1 año
        hoy = date.today()
        proximos_aniversario = empleados.filter(
            fecha_contratacion__year=hoy.year - 1,
            fecha_contratacion__month=hoy.month,
            fecha_contratacion__day__gte=hoy.day
        ).order_by('fecha_contratacion')
        
        if proximos_aniversario.exists():
            self.stdout.write(f'\n🎉 Próximos aniversarios (cumplirán 1 año):')
            for empleado in proximos_aniversario:
                dias_restantes = (empleado.fecha_contratacion.replace(year=hoy.year) - hoy).days
                self.stdout.write(
                    f'  - {empleado.nombre_completo}: {dias_restantes} días restantes'
                )
