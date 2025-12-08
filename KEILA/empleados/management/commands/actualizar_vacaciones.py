from django.core.management.base import BaseCommand
from empleados.models import Perfil

class Command(BaseCommand):
    help = 'Actualiza los días de vacaciones de todos los empleados según su antigüedad y procesa acumulación anual'

    def add_arguments(self, parser):
        parser.add_argument(
            '--acumulacion-anual',
            action='store_true',
            help='Procesar acumulación anual de vacaciones no usadas',
        )
        parser.add_argument(
            '--acumulacion-mensual',
            action='store_true',
            help='Procesar acumulación mensual proporcional de vacaciones',
        )

    def handle(self, *args, **options):
        perfiles = Perfil.objects.filter(activo=True)
        actualizados = 0
        acumulados_anual = 0
        acumulados_mensual = 0
        
        for perfil in perfiles:
            # Actualizar días según antigüedad
            dias_anteriores = perfil.dias_vacaciones_anuales
            perfil.actualizar_dias_vacaciones()
            dias_nuevos = perfil.dias_vacaciones_anuales
            
            if dias_anteriores != dias_nuevos:
                actualizados += 1
                self.stdout.write(
                    f'{perfil.nombre_completo}: {dias_anteriores} → {dias_nuevos} días anuales'
                )
            
            # Procesar acumulación anual si se solicita
            if options['acumulacion_anual']:
                if perfil.procesar_acumulacion_anual():
                    acumulados_anual += 1
                    self.stdout.write(
                        f'{perfil.nombre_completo}: Acumuló {perfil.dias_vacaciones_acumulados} días del año anterior'
                    )
            
            # Procesar acumulación mensual si se solicita
            if options['acumulacion_mensual']:
                if perfil.procesar_acumulacion_mensual():
                    acumulados_mensual += 1
                    dias_por_mes = perfil.calcular_acumulacion_mensual()
                    self.stdout.write(
                        f'{perfil.nombre_completo}: +{dias_por_mes:.4f} días mensuales '
                        f'(Total acumulado: {perfil.dias_vacaciones_acumulados:.4f})'
                    )
        
        # Mostrar resumen
        if options['acumulacion_anual'] and options['acumulacion_mensual']:
            self.stdout.write(
                self.style.SUCCESS(f'Se actualizaron {actualizados} perfiles, '
                                 f'acumulación anual para {acumulados_anual} empleados, '
                                 f'y acumulación mensual para {acumulados_mensual} empleados')
            )
        elif options['acumulacion_anual']:
            self.stdout.write(
                self.style.SUCCESS(f'Se actualizaron {actualizados} perfiles y se procesó acumulación anual para {acumulados_anual} empleados')
            )
        elif options['acumulacion_mensual']:
            self.stdout.write(
                self.style.SUCCESS(f'Se actualizaron {actualizados} perfiles y se procesó acumulación mensual para {acumulados_mensual} empleados')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Se actualizaron {actualizados} perfiles')
            )
            self.stdout.write(
                self.style.WARNING('Usa --acumulacion-anual para procesar días acumulados del año anterior')
            )
            self.stdout.write(
                self.style.WARNING('Usa --acumulacion-mensual para procesar acumulación mensual proporcional')
            )
