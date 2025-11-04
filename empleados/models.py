from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from datetime import date, timedelta

User = get_user_model()


class Perfil(models.Model):
    """Modelo unificado para todos los perfiles de usuario"""
    TIPOS_PERFIL = [
        ('EMPLEADO', 'Empleado'),
        ('JEFE_AREA', 'Jefe de Área'), 
        ('RH', 'Recursos Humanos'),
        ('SISTEMAS', 'Sistemas/IT'),
        ('ADMIN', 'Administrador'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario")
    tipo_perfil = models.CharField(max_length=20, choices=TIPOS_PERFIL, verbose_name="Tipo de Perfil")
    departamento = models.ForeignKey('Departamento', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Departamento")
    fecha_contratacion = models.DateField(verbose_name="Fecha de Contratación")
    numero_empleado = models.CharField(max_length=20, unique=True, verbose_name="Número de Empleado")
    puesto = models.CharField(max_length=100, verbose_name="Puesto")
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Supervisor")
    activo = models.BooleanField(default=True, verbose_name="Activo")
     
    # Información personal adicional
    telefono = models.CharField(max_length=15, blank=True, verbose_name="Teléfono")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    salario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Salario")
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    
    # Información de vacaciones
    dias_vacaciones_anuales = models.PositiveIntegerField(default=20, verbose_name="Días de Vacaciones Anuales")
    dias_vacaciones_usados = models.PositiveIntegerField(default=0, verbose_name="Días de Vacaciones Usados")
    dias_vacaciones_extraordinarios = models.PositiveIntegerField(default=0, verbose_name="Días de Vacaciones Extraordinarios Usados")
    dias_vacaciones_acumulados = models.PositiveIntegerField(default=0, verbose_name="Días de Vacaciones Acumulados del Año Anterior")
    ultimo_reset_vacaciones = models.DateField(null=True, blank=True, verbose_name="Último Reset de Vacaciones")
    
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"
        ordering = ['usuario__last_name', 'usuario__first_name']
     
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.get_tipo_perfil_display()}"
    
    @property
    def nombre_completo(self):
        return self.usuario.get_full_name() or self.usuario.username
    
    def calcular_dias_segun_ano_laboral(self, ano_laboral):
        """Calcula días según el año laboral específico (1, 2, 3, etc.)"""
        if ano_laboral < 1:
            return 12  # Año 1 por defecto
        elif ano_laboral == 1:
            return 12
        elif ano_laboral == 2:
            return 14
        elif ano_laboral == 3:
            return 16
        elif ano_laboral == 4:
            return 18
        elif ano_laboral == 5:
            return 20
        elif 6 <= ano_laboral <= 10:
            return 22
        elif 11 <= ano_laboral <= 15:
            return 24
        elif 16 <= ano_laboral <= 20:
            return 26
        elif 21 <= ano_laboral <= 25:
            return 28
        elif 26 <= ano_laboral <= 30:
            return 30
        elif ano_laboral >= 31:
            return 32
        else:
            return 12
    
    @property
    def dias_vacaciones_segun_antiguedad(self):
        """Calcula días de vacaciones según tabla de antigüedad"""
        if not self.fecha_contratacion:
            return 0  # Sin fecha de contratación
        
        anos = self.antiguedad_anos
        
        if anos < 1:
            # Cálculo proporcional para empleados con menos de 1 año
            # 12 días del primer año / 12 meses = 1 día por mes
            dias_trabajados = (date.today() - self.fecha_contratacion).days
            meses_trabajados = dias_trabajados / 30.44  # promedio días por mes
            dias_acumulados = (12 / 12) * meses_trabajados
            return round(dias_acumulados, 2)
        elif anos == 1:
            return 12
        elif anos == 2:
            return 14
        elif anos == 3:
            return 16
        elif anos == 4:
            return 18
        elif anos == 5:
            return 20
        elif 6 <= anos <= 10:
            return 22
        elif 11 <= anos <= 15:
            return 24
        elif 16 <= anos <= 20:
            return 26
        elif 21 <= anos <= 25:
            return 28
        elif 26 <= anos <= 30:
            return 30
        elif anos >= 31:
            return 32
        else:
            return 12  # default


    @property
    def dias_vacaciones_disponibles(self):
        # Actualizar automáticamente los días anuales según antigüedad
        dias_anuales_calculados = int(self.dias_vacaciones_segun_antiguedad)
        if self.dias_vacaciones_anuales != dias_anuales_calculados:
            self.dias_vacaciones_anuales = dias_anuales_calculados
            self.save(update_fields=['dias_vacaciones_anuales'])
        
        # Incluir días acumulados del año anterior
        return (self.dias_vacaciones_anuales + self.dias_vacaciones_acumulados) - self.dias_vacaciones_usados
    
    @property
    def dias_vacaciones_extraordinarios_disponibles(self):
        """Días extraordinarios disponibles (para empleados con menos de 1 año)"""
        if self.antiguedad_anos >= 1:
            return 0
        # Los empleados nuevos pueden tener hasta 5 días extraordinarios
        return max(0, 5 - self.dias_vacaciones_extraordinarios)
    
    @property
    def antiguedad_anos(self):
        if not self.fecha_contratacion:
            return 0
        today = date.today()
        # Calcular años completos trabajados
        years = today.year - self.fecha_contratacion.year
        if today.month < self.fecha_contratacion.month or (today.month == self.fecha_contratacion.month and today.day < self.fecha_contratacion.day):
            years -= 1
        return max(0, years)
    
    @property
    def antiguedad_detallada(self):
        """Retorna antigüedad en formato: X años y Y meses"""
        if not self.fecha_contratacion:
            return "Sin fecha de contratación"
        
        today = date.today()
        
        # Calcular años completos
        years = today.year - self.fecha_contratacion.year
        if today.month < self.fecha_contratacion.month or (today.month == self.fecha_contratacion.month and today.day < self.fecha_contratacion.day):
            years -= 1
        
        # Calcular meses adicionales
        if today.month >= self.fecha_contratacion.month:
            months = today.month - self.fecha_contratacion.month
            if today.day < self.fecha_contratacion.day:
                months -= 1
        else:
            months = 12 + today.month - self.fecha_contratacion.month
            if today.day < self.fecha_contratacion.day:
                months -= 1
        
        # Asegurar que los meses sean positivos
        if months < 0:
            months = 0
        
        # Formatear salida
        if years == 0:
            if months == 0:
                return "Menos de 1 mes"
            elif months == 1:
                return "1 mes"
            else:
                return f"{months} meses"
        elif years == 1:
            if months == 0:
                return "1 año"
            elif months == 1:
                return "1 año y 1 mes"
            else:
                return f"1 año y {months} meses"
        else:
            if months == 0:
                return f"{years} años"
            elif months == 1:
                return f"{years} años y 1 mes"
            else:
                return f"{years} años y {months} meses"
    
    def es_jefe_area(self):
        return self.tipo_perfil == 'JEFE_AREA'
    
    def es_rh(self):
        return self.tipo_perfil == 'RH'
    
    def es_admin(self):
        return self.tipo_perfil == 'ADMIN'
    
    def es_sistemas(self):
        return self.tipo_perfil == 'SISTEMAS'
    
    def es_empleado(self):
        return self.tipo_perfil == 'EMPLEADO'
    
    def actualizar_dias_vacaciones(self):
        """Actualiza los días de vacaciones según antigüedad"""
        self.dias_vacaciones_anuales = int(self.dias_vacaciones_segun_antiguedad)
        self.save(update_fields=['dias_vacaciones_anuales'])
    
    def calcular_acumulacion_mensual(self):
        """Calcula cuántos días acumula por mes según su antigüedad"""
        if self.antiguedad_anos < 1:
            return 1.0  # Primer año: 12/12 = 1 día por mes
        
        # Usar el año laboral actual (antiguedad + 1 porque está en ese año)
        ano_laboral_actual = self.antiguedad_anos + 1
        dias_anuales = self.calcular_dias_segun_ano_laboral(ano_laboral_actual)
        return round(dias_anuales / 12, 2)  # Días por mes redondeado a 2 decimales
    
    def calcular_acumulacion_diaria(self):
        """Calcula cuántos días acumula por día trabajado según su antigüedad"""
        if self.antiguedad_anos < 1:
            return round(12 / 365, 6)  # Primer año: 12/365 días por día
        
        # Usar el año laboral actual (antiguedad + 1 porque está en ese año)
        ano_laboral_actual = self.antiguedad_anos + 1
        dias_anuales = self.calcular_dias_segun_ano_laboral(ano_laboral_actual)
        return round(dias_anuales / 365, 6)  # Días por día con 6 decimales
    
    def calcular_dias_acumulados_hasta_hoy(self):
        """Calcula cuántos días ha acumulado hasta el día de hoy en el año actual (cálculo diario con decimales)"""
        from datetime import date
        
        if not self.fecha_contratacion:
            return 0
        
        # Para empleados con menos de 1 año, calcular proporcionalmente por día
        if self.antiguedad_anos < 1:
            dias_trabajados = (date.today() - self.fecha_contratacion).days
            dias_por_dia = 12 / 365
            return round(dias_por_dia * dias_trabajados, 4)
        
        # Para empleados con 1+ años, calcular desde su aniversario
        hoy = date.today()
        fecha_aniversario = date(hoy.year, self.fecha_contratacion.month, self.fecha_contratacion.day)
        
        # Determinar el año laboral actual (antiguedad + 1)
        ano_laboral_actual = self.antiguedad_anos + 1
        
        # Si el aniversario ya pasó este año, calcular desde el aniversario
        if hoy >= fecha_aniversario:
            # Calcular días transcurridos desde el aniversario
            dias_transcurridos = (hoy - fecha_aniversario).days
        else:
            # El aniversario aún no llega, seguimos en el año laboral anterior
            ano_laboral_actual = self.antiguedad_anos
            # Calcular días desde inicio del año
            inicio_ano = date(hoy.year, 1, 1)
            dias_transcurridos = (hoy - inicio_ano).days
        
        # Calcular días correspondientes al año laboral actual
        dias_anuales_actuales = self.calcular_dias_segun_ano_laboral(ano_laboral_actual)
        dias_por_dia = dias_anuales_actuales / 365
        
        # Días acumulados (proporcional a días transcurridos)
        # Mostrar CON DECIMALES exactos (4 decimales)
        dias_acumulados = dias_por_dia * dias_transcurridos
        
        return round(dias_acumulados, 4)
    
    def calcular_total_disponible_proyectado(self):
        """Calcula total de días disponibles: año anterior completado + acumulado este año - usados (con decimales)"""
        
        if not self.fecha_contratacion:
            return 0
        
        # Para empleados con menos de 1 año
        if self.antiguedad_anos < 1:
            return round(self.dias_vacaciones_segun_antiguedad - self.dias_vacaciones_usados, 4)
        
        # Para empleados con 1+ años:
        # Días del año laboral anterior completado (ej: año 1 = 12 días si está en año 2)
        ano_laboral_anterior = self.antiguedad_anos
        dias_ano_anterior_completado = self.calcular_dias_segun_ano_laboral(ano_laboral_anterior)
        
        # Días acumulados hasta hoy en el año laboral actual (ej: año 2 = 3.51 días de 14)
        dias_acumulados_ano_actual = self.calcular_dias_acumulados_hasta_hoy()
        
        # Días ya usados
        dias_usados = self.dias_vacaciones_usados
        
        # Total = Año anterior completo + Acumulado año actual - Usados
        # Ejemplo: 12 (año 1) + 3.5342 (acumulado año 2) - 8 (usados) = 7.5342 días
        total = dias_ano_anterior_completado + dias_acumulados_ano_actual - dias_usados
        
        return round(total, 4)
    
    @property
    def mostrar_seccion_ano_anterior(self):
        """Determina si mostrar la sección de año anterior en el dashboard"""
        # Mostrar si tiene 1+ años de antigüedad (para mostrar año completado)
        return self.antiguedad_anos >= 1
    
    @property
    def dias_ano_anterior_completado(self):
        """Retorna los días del año laboral anterior completado"""
        if self.antiguedad_anos < 1:
            return 0
        
        # Año laboral anterior = antiguedad actual
        # Ejemplo: si tiene 1 año, el año anterior fue el año 1 = 12 días
        ano_laboral_anterior = self.antiguedad_anos
        return self.calcular_dias_segun_ano_laboral(ano_laboral_anterior)
    
    @property
    def dias_al_finalizar_ano_actual(self):
        """Retorna los días totales que tendrá al finalizar el año laboral actual"""
        if not self.fecha_contratacion:
            return 0
        
        if self.antiguedad_anos < 1:
            # Primer año: 12 días
            return 12
        
        # Año laboral actual = antiguedad + 1
        ano_laboral_actual = self.antiguedad_anos + 1
        return self.calcular_dias_segun_ano_laboral(ano_laboral_actual)
    
    def procesar_acumulacion_mensual(self):
        """Procesa la acumulación mensual de vacaciones"""
        from datetime import date
        
        if self.antiguedad_anos < 1:
            return False  # Los empleados nuevos no acumulan mensualmente
        
        # Calcular días a acumular este mes
        dias_por_mes = self.calcular_acumulacion_mensual()
        
        # Agregar días acumulados
        self.dias_vacaciones_acumulados += dias_por_mes
        
        self.save(update_fields=['dias_vacaciones_acumulados'])
        return True
    
    def procesar_acumulacion_anual(self):
        """Procesa la acumulación de vacaciones al inicio del año"""
        from datetime import date
        
        # Verificar si ya se procesó este año
        if self.ultimo_reset_vacaciones and self.ultimo_reset_vacaciones.year == date.today().year:
            return False
        
        # Calcular días no usados del año anterior
        dias_no_usados = max(0, self.dias_vacaciones_anuales - self.dias_vacaciones_usados)
        
        # Acumular TODOS los días no usados (sin límite)
        dias_a_acumular = dias_no_usados
        
        # Actualizar días anuales según nueva antigüedad ANTES de resetear
        nuevos_dias_anuales = int(self.dias_vacaciones_segun_antiguedad)
        
        # Resetear contadores del año
        self.dias_vacaciones_usados = 0
        self.ultimo_reset_vacaciones = date.today()
        self.dias_vacaciones_anuales = nuevos_dias_anuales
        
        # Acumular días no usados del año anterior
        if dias_a_acumular > 0:
            self.dias_vacaciones_acumulados = dias_a_acumular
        
        self.save(update_fields=[
            'dias_vacaciones_acumulados', 
            'dias_vacaciones_usados', 
            'ultimo_reset_vacaciones',
            'dias_vacaciones_anuales'
        ])
        
        return True


class Departamento(models.Model):
    """Departamentos de la empresa"""
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    jefe = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True, 
                            related_name='departamento_dirigido', verbose_name="Jefe de Departamento")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    @property
    def empleados_count(self):
        return self.perfil_set.filter(activo=True).count()


class SolicitudVacaciones(models.Model):
    """Solicitudes de vacaciones con flujo de aprobación"""
    ESTADOS = [
        ('PENDIENTE_JEFE', 'Pendiente Jefe de Área'),
        ('APROBADO_JEFE', 'Aprobado por Jefe'),
        ('RECHAZADO_JEFE', 'Rechazado por Jefe'),
        ('PENDIENTE_RH', 'Pendiente RH'),
        ('APROBADO_RH', 'Aprobado por RH'),
        ('RECHAZADO_RH', 'Rechazado por RH'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    TIPOS = [
        ('NORMAL', 'Vacación Normal'),
        ('EXTRAORDINARIA', 'Vacación Extraordinaria'),
        ('EMERGENCIA', 'Vacación de Emergencia'),
    ]
    
    empleado = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='solicitudes_vacaciones', 
                                verbose_name="Empleado")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")
    dias_solicitados = models.PositiveIntegerField(verbose_name="Días Solicitados")
    tipo = models.CharField(max_length=20, choices=TIPOS, default='NORMAL', verbose_name="Tipo")
    motivo = models.TextField(verbose_name="Motivo")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE_JEFE', verbose_name="Estado")
    
    # Campos de aprobación
    aprobado_por_jefe = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='vacaciones_aprobadas_jefe', verbose_name="Aprobado por Jefe")
    aprobado_por_rh = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='vacaciones_aprobadas_rh', verbose_name="Aprobado por RH")
    
    comentarios_jefe = models.TextField(blank=True, verbose_name="Comentarios del Jefe")
    comentarios_rh = models.TextField(blank=True, verbose_name="Comentarios de RH")
    
    # Auditoría
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Solicitud")
    fecha_aprobacion_jefe = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Aprobación Jefe")
    fecha_aprobacion_rh = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Aprobación RH")
    
    class Meta:
        verbose_name = "Solicitud de Vacaciones"
        verbose_name_plural = "Solicitudes de Vacaciones"
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.fecha_inicio} a {self.fecha_fin}"
    
    @staticmethod
    def calcular_dias_laborables(fecha_inicio, fecha_fin):
        """Calcula días laborables excluyendo domingos"""
        if not fecha_inicio or not fecha_fin:
            return 0
        
        dias_totales = 0
        fecha_actual = fecha_inicio
        
        while fecha_actual <= fecha_fin:
            # weekday() retorna 0=Lunes, 6=Domingo
            if fecha_actual.weekday() != 6:  # 6 = Domingo
                dias_totales += 1
            fecha_actual += timedelta(days=1)
        
        return dias_totales
    
    def save(self, *args, **kwargs):
        # Calcular días solicitados automáticamente (excluyendo domingos)
        if self.fecha_inicio and self.fecha_fin:
            self.dias_solicitados = self.calcular_dias_laborables(self.fecha_inicio, self.fecha_fin)
        super().save(*args, **kwargs)
    
    def puede_ser_aprobada_por_jefe(self):
        """Verifica si puede ser aprobada por jefe"""
        return self.estado == 'PENDIENTE_JEFE'
    
    def puede_ser_aprobada_por_rh(self):
        """Verifica si puede ser aprobada por RH"""
        return self.estado == 'PENDIENTE_RH'
    
    def aprobar_por_jefe(self, jefe, comentario=""):
        """Aprobar solicitud por jefe de área"""
        from django.utils import timezone
        
        if not self.puede_ser_aprobada_por_jefe():
            return False
        
        self.estado = 'APROBADO_JEFE'
        self.aprobado_por_jefe = jefe
        self.comentarios_jefe = comentario
        self.fecha_aprobacion_jefe = timezone.now()
        
        # Si es empleado normal, va directo a RH
        if self.tipo == 'NORMAL':
            self.estado = 'PENDIENTE_RH'
        
        self.save()
        return True
    
    def rechazar_por_jefe(self, jefe, comentario=""):
        """Rechazar solicitud por jefe de área"""
        from django.utils import timezone
        
        if not self.puede_ser_aprobada_por_jefe():
            return False
        
        self.estado = 'RECHAZADO_JEFE'
        self.aprobado_por_jefe = jefe
        self.comentarios_jefe = comentario
        self.fecha_aprobacion_jefe = timezone.now()
        self.save()
        return True
    
    def aprobar_por_rh(self, rh_user, comentario=""):
        """Aprobar solicitud por RH"""
        from django.utils import timezone
        
        if not self.puede_ser_aprobada_por_rh():
            return False
        
        self.estado = 'APROBADO_RH'
        self.aprobado_por_rh = rh_user
        self.comentarios_rh = comentario
        self.fecha_aprobacion_rh = timezone.now()
        
        # Actualizar días usados del empleado
        self.empleado.dias_vacaciones_usados += self.dias_solicitados
        self.empleado.save()
        
        self.save()
        return True
    
    def rechazar_por_rh(self, rh_user, comentario=""):
        """Rechazar solicitud por RH"""
        from django.utils import timezone
        
        if not self.puede_ser_aprobada_por_rh():
            return False
        
        self.estado = 'RECHAZADO_RH'
        self.aprobado_por_rh = rh_user
        self.comentarios_rh = comentario
        self.fecha_aprobacion_rh = timezone.now()
        self.save()
        return True


class ConfiguracionSistema(models.Model):
    """Configuraciones generales del sistema"""
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    valor = models.TextField(verbose_name="Valor")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    
    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuraciones del Sistema"
    
    def __str__(self):
        return f"{self.nombre}: {self.valor}"


# ===================================================================
# MODELOS DE GESTIÓN DE EQUIPOS Y TICKETS IT
# ===================================================================

class CategoriaEquipo(models.Model):
    """Categorías de equipos/dispositivos tecnológicos"""
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Categoría de Equipo"
        verbose_name_plural = "Categorías de Equipos"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Equipo(models.Model):
    """Inventario de equipos tecnológicos"""
    ESTADOS_EQUIPO = [
        ('DISPONIBLE', 'Disponible'),
        ('ASIGNADO', 'Asignado'),
        ('EN_REPARACION', 'En Reparación'),
        ('DADO_DE_BAJA', 'Dado de Baja'),
    ]
    
    categoria = models.ForeignKey(CategoriaEquipo, on_delete=models.PROTECT, verbose_name="Categoría")
    marca = models.CharField(max_length=50, verbose_name="Marca")
    modelo = models.CharField(max_length=100, verbose_name="Modelo")
    numero_serie = models.CharField(max_length=100, unique=True, verbose_name="Número de Serie")
    codigo_inventario = models.CharField(max_length=50, unique=True, verbose_name="Código de Inventario")
    estado = models.CharField(max_length=20, choices=ESTADOS_EQUIPO, default='DISPONIBLE', verbose_name="Estado")
    fecha_adquisicion = models.DateField(verbose_name="Fecha de Adquisición")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ['-fecha_adquisicion']
    
    def __str__(self):
        return f"{self.categoria.nombre} - {self.marca} {self.modelo} ({self.codigo_inventario})"
    
    @property
    def asignacion_actual(self):
        """Retorna la asignación activa si existe"""
        return self.asignaciones.filter(fecha_devolucion__isnull=True).first()
    
    @property
    def empleado_asignado(self):
        """Retorna el empleado al que está asignado actualmente"""
        asignacion = self.asignacion_actual
        return asignacion.empleado if asignacion else None


class AsignacionEquipo(models.Model):
    """Historial de asignaciones de equipos a empleados"""
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='asignaciones', verbose_name="Equipo")
    empleado = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='equipos_asignados', verbose_name="Empleado")
    fecha_asignacion = models.DateField(verbose_name="Fecha de Asignación")
    fecha_devolucion = models.DateField(null=True, blank=True, verbose_name="Fecha de Devolución")
    condicion_entrega = models.CharField(max_length=200, blank=True, verbose_name="Condición al Entregar")
    condicion_devolucion = models.CharField(max_length=200, blank=True, verbose_name="Condición al Devolver")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    asignado_por = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, related_name='asignaciones_realizadas', verbose_name="Asignado Por")
    
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Asignación de Equipo"
        verbose_name_plural = "Asignaciones de Equipos"
        ordering = ['-fecha_asignacion']
    
    def __str__(self):
        estado = "Activa" if not self.fecha_devolucion else f"Devuelto el {self.fecha_devolucion}"
        return f"{self.equipo.codigo_inventario} → {self.empleado.nombre_completo} ({estado})"
    
    @property
    def esta_activa(self):
        """Verifica si la asignación está activa"""
        return self.fecha_devolucion is None


class Ticket(models.Model):
    """Sistema de tickets de soporte técnico"""
    TIPOS_TICKET = [
        ('HARDWARE', 'Hardware'),
        ('SOFTWARE', 'Software'),
        ('RED', 'Red/Conectividad'),
        ('ACCESO', 'Acceso/Permisos'),
        ('OTRO', 'Otro'),
    ]
    
    PRIORIDADES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]
    
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('RESUELTO', 'Resuelto'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    # Información básica
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código", editable=False)
    empleado = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='tickets_creados', verbose_name="Solicitante")
    tipo = models.CharField(max_length=20, choices=TIPOS_TICKET, verbose_name="Tipo")
    area = models.CharField(max_length=100, blank=True, verbose_name="Área")
    dispositivo = models.CharField(max_length=100, blank=True, verbose_name="Dispositivo Afectado")
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default='MEDIA', verbose_name="Prioridad")
    descripcion = models.TextField(verbose_name="Descripción del Problema")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE', verbose_name="Estado")
    
    # Asignación y resolución
    asignado_a = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='tickets_asignados', verbose_name="Asignado A")
    solucion = models.TextField(blank=True, verbose_name="Solución Aplicada")
    
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_asignacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Asignación")
    fecha_resolucion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Resolución")
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.codigo} - {self.empleado.nombre_completo} ({self.get_estado_display()})"
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            # Generar código único TKT-YYYYMMDD-XXX
            from django.utils import timezone
            today = timezone.now().date()
            prefix = f"TKT-{today.strftime('%Y%m%d')}"
            last_ticket = Ticket.objects.filter(codigo__startswith=prefix).order_by('-codigo').first()
            if last_ticket:
                last_num = int(last_ticket.codigo.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.codigo = f"{prefix}-{new_num:03d}"
        super().save(*args, **kwargs)
    
    @property
    def tiempo_respuesta(self):
        """Calcula el tiempo desde creación hasta asignación"""
        if self.fecha_asignacion:
            delta = self.fecha_asignacion - self.fecha_creacion
            return delta
        return None
    
    @property
    def tiempo_resolucion(self):
        """Calcula el tiempo desde creación hasta resolución"""
        if self.fecha_resolucion:
            delta = self.fecha_resolucion - self.fecha_creacion
            return delta
        return None


# ===================================================================
# SEÑALES
# ===================================================================

# Señales para mantener sincronización con User model
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crear perfil automáticamente cuando se crea un usuario"""
    if created:
        # Solo crear perfil si no existe
        if not hasattr(instance, 'perfil'):
            Perfil.objects.create(
                usuario=instance,
                tipo_perfil='EMPLEADO',  # Default
                fecha_contratacion=date.today(),
                numero_empleado=f"EMP{instance.id:04d}",
                puesto="Por definir"
            )
