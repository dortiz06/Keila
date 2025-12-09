from django.core.management.base import BaseCommand
from empleados.models import Perfil

class Command(BaseCommand):
    help = 'Procesa la acumulación mensual de vacaciones para todos los empleados'

    def handle(self, *args, **options):
        perfiles = Perfil.objects.filter(activo=True, antiguedad_anos__gte=1)
        acumulados = 0
        
        self.stdout.write("Procesando acumulación mensual de vacaciones...")
        
        for perfil in perfiles:
            dias_anteriores = perfil.dias_vacaciones_acumulados
            dias_por_mes = perfil.calcular_acumulacion_mensual()
            
            if perfil.procesar_acumulacion_mensual():
                acumulados += 1
                self.stdout.write(
                    f'{perfil.nombre_completo}: +{dias_por_mes:.4f} días '
                    f'({dias_anteriores:.4f} → {perfil.dias_vacaciones_acumulados:.4f})'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Se procesó acumulación mensual para {acumulados} empleados')
        )
