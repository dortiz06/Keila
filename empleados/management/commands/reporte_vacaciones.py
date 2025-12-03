from django.core.management.base import BaseCommand
from django.utils import timezone
from empleados.models import Perfil, SolicitudVacaciones
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Genera reportes de vacaciones y antigüedad de empleados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--formato',
            choices=['texto', 'csv'],
            default='texto',
            help='Formato del reporte (texto o csv)',
        )
        parser.add_argument(
            '--archivo',
            help='Archivo donde guardar el reporte',
        )
        parser.add_argument(
            '--departamento',
            help='Filtrar por departamento específico',
        )

    def handle(self, *args, **options):
        formato = options['formato']
        archivo = options.get('archivo')
        departamento = options.get('departamento')
        
        # Filtrar empleados
        empleados = Perfil.objects.filter(activo=True)
        if departamento:
            empleados = empleados.filter(departamento__nombre__icontains=departamento)
        
        empleados = empleados.select_related('departamento', 'usuario')
        
        # Generar reporte
        if formato == 'csv':
            self.generar_csv(empleados, archivo)
        else:
            self.generar_texto(empleados, archivo)

    def generar_texto(self, empleados, archivo):
        """Generar reporte en formato texto"""
        output = []
        
        output.append("=" * 80)
        output.append("REPORTE DE VACACIONES Y ANTIGÜEDAD - GRUPO KEILA")
        output.append("=" * 80)
        output.append(f"Fecha de generación: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
        output.append(f"Total empleados: {empleados.count()}")
        output.append("")
        
        # Estadísticas generales
        elegibles_vacaciones = empleados.filter(fecha_contratacion__lte=timezone.now().date() - timedelta(days=365))
        empleados_con_dias = sum(1 for emp in empleados if emp.dias_vacaciones_disponibles > 0)
        empleados_sin_dias = sum(1 for emp in empleados if emp.dias_vacaciones_disponibles == 0)
        
        output.append("📊 ESTADÍSTICAS GENERALES")
        output.append("-" * 40)
        output.append(f"Empleados elegibles para vacaciones: {elegibles_vacaciones.count()}")
        output.append(f"Empleados con días disponibles: {empleados_con_dias}")
        output.append(f"Empleados sin días disponibles: {empleados_sin_dias}")
        output.append("")
        
        # Por departamento
        output.append("🏢 POR DEPARTAMENTO")
        output.append("-" * 40)
        departamentos = empleados.values_list('departamento__nombre', flat=True).distinct()
        for dept in departamentos:
            if dept:
                dept_empleados = empleados.filter(departamento__nombre=dept)
                elegibles_dept = dept_empleados.filter(fecha_contratacion__lte=timezone.now().date() - timedelta(days=365))
                output.append(f"{dept}: {dept_empleados.count()} empleados ({elegibles_dept.count()} elegibles)")
        output.append("")
        
        # Lista detallada
        output.append("👥 LISTA DETALLADA DE EMPLEADOS")
        output.append("-" * 80)
        output.append(f"{'Nombre':<25} {'Número':<10} {'Depto':<15} {'Antigüedad':<10} {'Días Disp':<10} {'Elegible'}")
        output.append("-" * 80)
        
        for empleado in empleados.order_by('usuario__last_name', 'usuario__first_name'):
            nombre = empleado.nombre_completo[:24]
            numero = empleado.numero_empleado[:9]
            depto = (empleado.departamento.nombre[:14] if empleado.departamento else 'Sin depto')[:14]
            antiguedad = f"{empleado.antiguedad_anos} años"
            dias_disp = str(empleado.dias_vacaciones_disponibles)
            elegible = "✓" if empleado.antiguedad_anos >= 1 else "✗"
            
            output.append(f"{nombre:<25} {numero:<10} {depto:<15} {antiguedad:<10} {dias_disp:<10} {elegible}")
        
        output.append("")
        output.append("=" * 80)
        
        # Guardar o mostrar
        contenido = "\n".join(output)
        if archivo:
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
            self.stdout.write(self.style.SUCCESS(f'Reporte guardado en: {archivo}'))
        else:
            self.stdout.write(contenido)

    def generar_csv(self, empleados, archivo):
        """Generar reporte en formato CSV"""
        import csv
        
        if not archivo:
            archivo = f"reporte_vacaciones_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(archivo, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Encabezados
            writer.writerow([
                'Nombre', 'Apellidos', 'Número Empleado', 'Departamento', 
                'Puesto', 'Fecha Contratación', 'Antigüedad (años)', 
                'Días Anuales', 'Días Usados', 'Días Disponibles', 
                'Elegible Vacaciones', 'Activo'
            ])
            
            # Datos
            for empleado in empleados.order_by('usuario__last_name', 'usuario__first_name'):
                writer.writerow([
                    empleado.usuario.first_name or '',
                    empleado.usuario.last_name or '',
                    empleado.numero_empleado,
                    empleado.departamento.nombre if empleado.departamento else '',
                    empleado.puesto,
                    empleado.fecha_contratacion.strftime('%d/%m/%Y'),
                    empleado.antiguedad_anos,
                    empleado.dias_vacaciones_anuales,
                    empleado.dias_vacaciones_usados,
                    empleado.dias_vacaciones_disponibles,
                    'Sí' if empleado.antiguedad_anos >= 1 else 'No',
                    'Sí' if empleado.activo else 'No'
                ])
        
        self.stdout.write(self.style.SUCCESS(f'Reporte CSV guardado en: {archivo}'))
