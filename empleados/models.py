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
    dias_vacaciones_extraordinarios_ano_anterior = models.PositiveIntegerField(default=0, verbose_name="Días Extraordinarios del Año Anterior (para restar del año actual)")
    dias_vacaciones_acumulados = models.PositiveIntegerField(default=0, verbose_name="Días de Vacaciones Acumulados del Año Anterior")
    saldo_vacaciones = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Saldo de Vacaciones (Años Anteriores - Gastado)", help_text="Saldo resultante de años anteriores (acumulado - gastado). Puede ser negativo o positivo.")
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
        else:
            # A partir del año 6 aumentan 2 días cada 5 años (LFT 2023)
            # 6–10 → 22, 11–15 → 24, 16–20 → 26, 21–25 → 28, etc.
            bloques = (anos - 6) // 5
            return 22 + (bloques * 2)
    
    def calcular_antiguedad_actual(self, fecha_evento=None):
        """
        Años completos trabajados hasta la fecha del movimiento.
        Si no se proporciona fecha_evento, usa la fecha actual.
        """
        if not self.fecha_contratacion:
            return 0
        
        if fecha_evento is None:
            fecha_evento = date.today()
        
        return (
            fecha_evento.year - self.fecha_contratacion.year
            - ((fecha_evento.month, fecha_evento.day) < 
               (self.fecha_contratacion.month, self.fecha_contratacion.day))
        )
    
    def dias_trabajados_en_anio(self, fecha_evento=None):
        """
        Días desde el último aniversario laboral hasta la fecha indicada.
        Si no se proporciona fecha_evento, usa la fecha actual.
        """
        if not self.fecha_contratacion:
            return 0
        
        if fecha_evento is None:
            fecha_evento = date.today()
        
        # Calcular el último aniversario laboral
        ultimo_aniv = self.fecha_contratacion.replace(year=fecha_evento.year)
        if fecha_evento < ultimo_aniv:
            ultimo_aniv = ultimo_aniv.replace(year=fecha_evento.year - 1)
        
        return (fecha_evento - ultimo_aniv).days + 1
    
    def calcular_vacaciones_lft(self, fecha_corte=None):
        """
        Calcula el historial de vacaciones según la LFT 2023.
        Retorna un DataFrame con el historial y el saldo final.
        Similar al código Python proporcionado.
        """
        from decimal import Decimal
        
        if fecha_corte is None:
            fecha_corte = date.today()
        
        # Obtener todos los registros del historial ordenados por fecha
        registros = self.historial_vacaciones.all().order_by('fecha_registro', 'fecha_creacion')
        
        saldo = Decimal('0.0')
        historial = []
        ultimo_anio = -1
        extraordinarios_acumulados = Decimal('0.0')
        
        for registro in registros:
            fecha = registro.fecha_registro
            concepto = registro.concepto.lower()
            tomadas = Decimal(str(registro.tomadas))
            con_derecho = Decimal(str(registro.con_derecho))
            
            # Calcular antigüedad en la fecha del movimiento
            anio_actual = self.calcular_antiguedad_actual(fecha)
            
            # Si cambia al siguiente año laboral → otorgar días
            # anio_actual = 0 significa antes del primer aniversario
            # anio_actual = 1 significa que cumplió 1 año, etc.
            if anio_actual != ultimo_anio:
                if anio_actual == 1:
                    # Cambió del año 0 al año 1: otorgar días del año 1 menos extraordinarias del año 0
                    dias_oficiales = 12
                    # Restar extraordinarios acumulados del año 0 (permitir saldo negativo)
                    dias_netos = Decimal(str(dias_oficiales)) - extraordinarios_acumulados
                    saldo += dias_netos
                    
                    historial.append({
                        'fecha': fecha,
                        'concepto': f'Inicio Año {anio_actual}',
                        'dias_otorgados': float(dias_netos),
                        'extraordinarios_arrastrados': float(extraordinarios_acumulados),
                        'saldo_resultante': float(saldo),
                        'tipo': 'ANIVERSARIO'
                    })
                    
                    extraordinarios_acumulados = Decimal('0.0')
                    ultimo_anio = anio_actual
                elif anio_actual > 1:
                    # Cambió a un año mayor: otorgar días según LFT
                    if anio_actual == 2:
                        dias_oficiales = 14
                    elif anio_actual == 3:
                        dias_oficiales = 16
                    elif anio_actual == 4:
                        dias_oficiales = 18
                    elif anio_actual == 5:
                        dias_oficiales = 20
                    else:
                        bloques = (anio_actual - 6) // 5
                        dias_oficiales = 22 + (bloques * 2)
                    
                    # Restar extraordinarios pendientes del año anterior (permitir saldo negativo)
                    dias_netos = Decimal(str(dias_oficiales)) - extraordinarios_acumulados
                    saldo += dias_netos
                    
                    historial.append({
                        'fecha': fecha,
                        'concepto': f'Inicio Año {anio_actual}',
                        'dias_otorgados': float(dias_netos),
                        'extraordinarios_arrastrados': float(extraordinarios_acumulados),
                        'saldo_resultante': float(saldo),
                        'tipo': 'ANIVERSARIO'
                    })
                    
                    extraordinarios_acumulados = Decimal('0.0')
                    ultimo_anio = anio_actual
                elif anio_actual == 0:
                    # Está en el año 0, solo actualizar el último año
                    ultimo_anio = 0
            
            # Procesar movimientos de vacaciones tomadas (después de procesar cambio de año)
            # Solo procesar si hay tomadas > 0 y no es un registro de aniversario que ya se procesó arriba
            if tomadas > 0:
                # Verificar si es vacaciones normales o extraordinarias
                es_extraordinaria = (
                    'extraordinaria' in concepto or 
                    'emergencia' in concepto or 
                    registro.tipo_movimiento == 'VACACIONES_ANTES_REGISTRO'
                )
                
                if es_extraordinaria:
                    # Vacaciones extraordinarias
                    saldo -= tomadas
                    extraordinarios_acumulados += tomadas
                    historial.append({
                        'fecha': fecha,
                        'concepto': registro.concepto,
                        'tomadas': float(tomadas),
                        'saldo_resultante': float(saldo),
                        'tipo': 'EXTRAORDINARIA'
                    })
                elif 'vacaciones' in concepto or registro.tipo_movimiento == 'VACACIONES_TOMADAS':
                    # Vacaciones normales
                    saldo -= tomadas
                    historial.append({
                        'fecha': fecha,
                        'concepto': registro.concepto,
                        'tomadas': float(tomadas),
                        'saldo_resultante': float(saldo),
                        'tipo': 'NORMAL'
                    })
                elif registro.tipo_movimiento == 'AJUSTE_MANUAL':
                    # Ajustes manuales: si tomadas es negativo, resta; si es positivo, suma
                    saldo += tomadas  # tomadas puede ser negativo para ajustes
                    historial.append({
                        'fecha': fecha,
                        'concepto': registro.concepto,
                        'tomadas': float(tomadas),
                        'saldo_resultante': float(saldo),
                        'tipo': 'AJUSTE'
                    })
            
            # Procesar días con derecho (aniversarios, ajustes, etc.)
            # Solo si no es un aniversario que ya se procesó arriba cuando cambió el año
            if con_derecho > 0:
                # Si es un aniversario que ya se procesó arriba, no procesarlo de nuevo
                es_aniversario_procesado = (
                    anio_actual != ultimo_anio and 
                    anio_actual >= 1 and 
                    ('aniversario' in concepto or registro.tipo_movimiento == 'ANIVERSARIO_LABORAL')
                )
                
                if not es_aniversario_procesado:
                    saldo += con_derecho
                    historial.append({
                        'fecha': fecha,
                        'concepto': registro.concepto,
                        'dias_otorgados': float(con_derecho),
                        'saldo_resultante': float(saldo),
                        'tipo': 'CON_DERECHO'
                    })
        
        # Cálculo de prorrateo (hasta hoy)
        if ultimo_anio >= 1:
            # Calcular días correspondientes al año actual (el año que está cumpliendo)
            if ultimo_anio == 1:
                dias_corresponde_ano_actual = 12
            elif ultimo_anio == 2:
                dias_corresponde_ano_actual = 14
            elif ultimo_anio == 3:
                dias_corresponde_ano_actual = 16
            elif ultimo_anio == 4:
                dias_corresponde_ano_actual = 18
            elif ultimo_anio == 5:
                dias_corresponde_ano_actual = 20
            else:
                bloques = (ultimo_anio - 6) // 5
                dias_corresponde_ano_actual = 22 + (bloques * 2)
            
            dias_trab = self.dias_trabajados_en_anio(fecha_corte)
            prorrateo = Decimal(str(dias_corresponde_ano_actual)) * Decimal(str(dias_trab)) / Decimal('365')
            saldo_final = saldo + prorrateo
            
            historial.append({
                'fecha': fecha_corte,
                'concepto': f'Prorrateo acumulado (año {ultimo_anio}, {dias_trab} días trabajados)',
                'dias_acumulados': float(prorrateo),
                'saldo_resultante': float(saldo_final),
                'tipo': 'PRORRATEO'
            })
        elif ultimo_anio == 0:
            # Empleado con menos de 1 año, calcular prorrateo del primer año
            dias_trab = self.dias_trabajados_en_anio(fecha_corte)
            prorrateo = Decimal('12') * Decimal(str(dias_trab)) / Decimal('365')
            saldo_final = saldo + prorrateo
            
            historial.append({
                'fecha': fecha_corte,
                'concepto': f'Prorrateo acumulado (año 0, {dias_trab} días trabajados)',
                'dias_acumulados': float(prorrateo),
                'saldo_resultante': float(saldo_final),
                'tipo': 'PRORRATEO'
            })
        else:
            saldo_final = saldo
        
        return historial, float(saldo_final)


    @property
    def dias_vacaciones_disponibles(self):
        # Actualizar automáticamente los días anuales según antigüedad
        dias_anuales_calculados = int(self.dias_vacaciones_segun_antiguedad)
        if self.dias_vacaciones_anuales != dias_anuales_calculados:
            self.dias_vacaciones_anuales = dias_anuales_calculados
            self.save(update_fields=['dias_vacaciones_anuales'])
        
        # Incluir días acumulados del año anterior
        # Restar días usados normales Y días extraordinarios usados
        total_disponible = (self.dias_vacaciones_anuales + self.dias_vacaciones_acumulados) - self.dias_vacaciones_usados - self.dias_vacaciones_extraordinarios
        return max(0, total_disponible)  # No permitir valores negativos
    
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
        """Retorna antigüedad en formato: X años, Y meses y Z días"""
        if not self.fecha_contratacion:
            return "Sin fecha de contratación"
        
        from datetime import date
        
        today = date.today()
        fecha_inicio = self.fecha_contratacion
        
        # Calcular años completos
        years = today.year - fecha_inicio.year
        if today.month < fecha_inicio.month or (today.month == fecha_inicio.month and today.day < fecha_inicio.day):
            years -= 1
        
        # Calcular la fecha del último aniversario (o fecha_inicio si tiene menos de 1 año)
        if years >= 1:
            if today.month < fecha_inicio.month or (today.month == fecha_inicio.month and today.day < fecha_inicio.day):
                ultimo_aniversario = date(today.year - 1, fecha_inicio.month, fecha_inicio.day)
            else:
                ultimo_aniversario = date(today.year, fecha_inicio.month, fecha_inicio.day)
        else:
            ultimo_aniversario = fecha_inicio
        
        # Calcular meses desde el último aniversario
        months = 0
        fecha_temp = ultimo_aniversario
        
        # Avanzar mes por mes hasta llegar al mes actual
        # Contar meses completos: desde el mes siguiente al último aniversario hasta el mes actual
        while True:
            # Avanzar al siguiente mes
            if fecha_temp.month == 12:
                fecha_temp_siguiente = date(fecha_temp.year + 1, 1, fecha_temp.day)
            else:
                fecha_temp_siguiente = date(fecha_temp.year, fecha_temp.month + 1, fecha_temp.day)
            
            # Si el siguiente mes ya pasó la fecha actual, detener
            if fecha_temp_siguiente.year > today.year or (fecha_temp_siguiente.year == today.year and fecha_temp_siguiente.month > today.month):
                break
            # Si el siguiente mes es el mes actual y el día ya pasó, detener
            if fecha_temp_siguiente.year == today.year and fecha_temp_siguiente.month == today.month:
                if fecha_temp_siguiente.day > today.day:
                    break
            
            # Contar este mes como completo
            months += 1
            fecha_temp = fecha_temp_siguiente
        
        # Calcular días desde la última fecha calculada hasta today (inclusive)
        if fecha_temp.year == today.year and fecha_temp.month == today.month:
            # Estamos en el mismo mes, calcular días desde fecha_temp hasta today (inclusive)
            days = (today - fecha_temp).days
        elif fecha_temp.year < today.year or (fecha_temp.year == today.year and fecha_temp.month < today.month):
            # Ya pasamos meses completos, calcular días del mes actual
            # Días desde el día 1 del mes actual hasta today (inclusive)
            days = today.day
        else:
            # No debería pasar, pero por seguridad
            days = 0
        
        # Asegurar que los valores sean positivos
        if years < 0:
            years = 0
        if months < 0:
            months = 0
        if days < 0:
            days = 0
        
        # Calcular total de días exactos
        total_dias = (today - fecha_inicio).days
        
        # Formatear salida
        partes = []
        
        if years > 0:
            if years == 1:
                partes.append("1 año")
            else:
                partes.append(f"{years} años")
        
        if months > 0:
            if months == 1:
                partes.append("1 mes")
            else:
                partes.append(f"{months} meses")
        
        if days > 0:
            if days == 1:
                partes.append("1 día")
        else:
                partes.append(f"{days} días")
        
        # Si no hay nada, significa que es menos de 1 día
        if not partes:
            return f"Menos de 1 día ({total_dias} días)"
        
        # Formatear según cantidad de partes
        if len(partes) == 1:
            resultado = partes[0]
        elif len(partes) == 2:
            resultado = f"{partes[0]} y {partes[1]}"
        else:
            resultado = f"{partes[0]}, {partes[1]} y {partes[2]}"
        
        # Agregar total de días entre paréntesis
        return f"{resultado} ({total_dias} días)"
    
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
        """
        Calcula cuántos días ha acumulado hasta el día de hoy en el año actual (cálculo diario con decimales).
        
        IMPORTANTE: Si ya pasó el aniversario y se procesó la acumulación anual, el saldo ya incluye
        los días completos del nuevo año. En este caso, este método calcula solo los días proporcionales
        adicionales desde el aniversario hasta hoy.
        """
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
        
        # Si el aniversario ya pasó este año
        if hoy >= fecha_aniversario:
            # Verificar si ya se procesó la acumulación anual este año
            # Si se procesó, el saldo ya incluye los días completos del nuevo año
            # Entonces calculamos los días proporcionales adicionales desde el aniversario hasta hoy
            # Estos días adicionales se suman al saldo para obtener el total disponible
            dias_transcurridos = (hoy - fecha_aniversario).days
            dias_anuales_actuales = self.calcular_dias_segun_ano_laboral(ano_laboral_actual)
            dias_por_dia = dias_anuales_actuales / 365
            dias_acumulados = dias_por_dia * dias_transcurridos
            return round(dias_acumulados, 4)
        else:
            # El aniversario aún no llega, seguimos en el año laboral anterior
            ano_laboral_actual = self.antiguedad_anos
            # Calcular días desde inicio del año
            inicio_ano = date(hoy.year, 1, 1)
            dias_transcurridos = (hoy - inicio_ano).days
        dias_anuales_actuales = self.calcular_dias_segun_ano_laboral(ano_laboral_actual)
        dias_por_dia = dias_anuales_actuales / 365
        dias_acumulados = dias_por_dia * dias_transcurridos
        return round(dias_acumulados, 4)
    
    def calcular_total_disponible_proyectado(self):
        """
        Calcula total de días disponibles día con día.
        Fórmula simplificada: Saldo + Días acumulados (hasta hoy)
        
        - El saldo incluye: saldo de años anteriores + días con derecho del nuevo año (cuando cumple años)
        - Los días acumulados son proporcionales desde el aniversario (si ya pasó) o desde inicio del año
        - Total disponible = Saldo + Días acumulados del año en curso
        """
        from datetime import date
        from decimal import Decimal
        
        if not self.fecha_contratacion:
            return Decimal('0')
        
        # Verificar si el empleado cumplió años y procesar acumulación anual automáticamente
        hoy = date.today()
        
        # Calcular el aniversario de este año
        try:
            aniversario_este_ano = date(hoy.year, self.fecha_contratacion.month, self.fecha_contratacion.day)
        except ValueError:
            # Si el día no existe en este año (ej: 29 de febrero), usar el último día del mes
            from calendar import monthrange
            ultimo_dia = monthrange(hoy.year, self.fecha_contratacion.month)[1]
            aniversario_este_ano = date(hoy.year, self.fecha_contratacion.month, min(self.fecha_contratacion.day, ultimo_dia))
        
        # Verificar si ya pasó el aniversario este año
        # Y si no se ha procesado este año (verificar por fecha, no solo por año)
        if hoy >= aniversario_este_ano:
            # Verificar si no se ha procesado después del aniversario de este año
            if not self.ultimo_reset_vacaciones or self.ultimo_reset_vacaciones < aniversario_este_ano:
                # Procesar acumulación anual automáticamente
                # Esto sumará al saldo: saldo_año_anterior + días_con_derecho_nuevo_año
                self.procesar_acumulacion_anual()
        
        # Saldo actual (incluye saldo de años anteriores + días con derecho del nuevo año cuando cumple años)
        # Ejemplo: si tiene 2 días de saldo del año anterior y cumple años con 32 días, el saldo será 34 días
        saldo = Decimal(str(self.saldo_vacaciones))
        
        # Días acumulados hasta hoy en el año actual (proporcional, se actualiza día con día)
        # Si ya pasó el aniversario: calcula días proporcionales desde el aniversario
        # Si aún no ha cumplido años: calcula días proporcionales desde el inicio del año
        dias_acumulados_hasta_hoy = Decimal(str(self.calcular_dias_acumulados_hasta_hoy()))
        
        # Total disponible = Saldo + Días acumulados del año actual
        # Fórmula simple: el saldo ya incluye los días completos del nuevo año (si ya cumplió años),
        # y los días acumulados son los proporcionales adicionales desde el aniversario
        total = saldo + dias_acumulados_hasta_hoy
        
        return round(total, 4)  # Permitir valores negativos
    
    @property
    def mostrar_seccion_ano_anterior(self):
        """Determina si mostrar la sección de año anterior en el dashboard"""
        # Mostrar si tiene 1+ años de antigüedad (para mostrar año completado)
        return self.antiguedad_anos >= 1
    
    @property
    def dias_ano_anterior_completado(self):
        """Retorna los días del año laboral anterior completado, restando las extraordinarias del año anterior"""
        if self.antiguedad_anos < 1:
            return 0
        
        # Año laboral anterior = antiguedad actual
        # Ejemplo: si tiene 1 año, el año anterior fue el año 1 = 12 días
        ano_laboral_anterior = self.antiguedad_anos
        dias_ano_anterior = self.calcular_dias_segun_ano_laboral(ano_laboral_anterior)
        
        # Restar las vacaciones extraordinarias que se tomaron en el año anterior
        # Estas se restan de las vacaciones que le corresponden este año
        dias_netos = dias_ano_anterior - self.dias_vacaciones_extraordinarios_ano_anterior
        
        return max(0, dias_netos)  # No permitir valores negativos
    
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
        """Procesa la acumulación de vacaciones cuando el empleado cumple un año más"""
        from datetime import date
        from calendar import monthrange
        
        if not self.fecha_contratacion:
            return False
        
        hoy = date.today()
        
        # Calcular el aniversario de este año
        try:
            aniversario_este_ano = date(hoy.year, self.fecha_contratacion.month, self.fecha_contratacion.day)
        except ValueError:
            # Si el día no existe en este año (ej: 29 de febrero), usar el último día del mes
            ultimo_dia = monthrange(hoy.year, self.fecha_contratacion.month)[1]
            aniversario_este_ano = date(hoy.year, self.fecha_contratacion.month, min(self.fecha_contratacion.day, ultimo_dia))
        
        # Verificar si ya pasó el aniversario este año
        if hoy < aniversario_este_ano:
            return False  # Aún no ha cumplido años este año
        
        # Verificar si ya se procesó después del aniversario de este año
        if self.ultimo_reset_vacaciones and self.ultimo_reset_vacaciones >= aniversario_este_ano:
            return False  # Ya se procesó después del aniversario
        
        # Guardar valores del año anterior ANTES de resetear
        extraordinarias_ano_anterior = self.dias_vacaciones_extraordinarios
        dias_con_derecho_ano_anterior = self.dias_vacaciones_anuales  # Días que tenía derecho el año anterior
        dias_usados_ano_anterior = self.dias_vacaciones_usados  # Días normales usados
        dias_extraordinarios_ano_anterior = self.dias_vacaciones_extraordinarios  # Días extraordinarios usados
        
        # Calcular el saldo del año anterior (puede ser negativo)
        # Saldo = días con derecho - días usados (normales + extraordinarios)
        dias_gastados_ano_anterior = dias_usados_ano_anterior + dias_extraordinarios_ano_anterior
        saldo_ano_anterior = dias_con_derecho_ano_anterior - dias_gastados_ano_anterior
        
        # Calcular días no usados del año anterior (solo para compatibilidad)
        dias_no_usados = max(0, dias_con_derecho_ano_anterior - dias_usados_ano_anterior)
        dias_a_acumular = dias_no_usados
        
        # Actualizar días anuales según nueva antigüedad
        nuevos_dias_anuales_base = int(self.dias_vacaciones_segun_antiguedad)
        
        # Restar las vacaciones extraordinarias del año anterior de los nuevos días anuales
        # Las extraordinarias se restan de las vacaciones que le corresponden este año
        nuevos_dias_anuales = max(0, nuevos_dias_anuales_base - extraordinarias_ano_anterior)
        
        # Resetear contadores del año
        self.dias_vacaciones_usados = 0
        self.ultimo_reset_vacaciones = date.today()
        self.dias_vacaciones_anuales = nuevos_dias_anuales
        
        # Guardar las extraordinarias del año anterior para referencia
        self.dias_vacaciones_extraordinarios_ano_anterior = extraordinarias_ano_anterior
        
        # Resetear el contador de extraordinarias del año actual
        self.dias_vacaciones_extraordinarios = 0
        
        # Sumar el saldo del año anterior al saldo total (acumulativo)
        self.saldo_vacaciones += saldo_ano_anterior
        
        # Sumar los días con derecho del nuevo año al saldo
        # Los días con derecho que le corresponden por cumplir el año se suman automáticamente al saldo
        nuevos_dias_con_derecho = nuevos_dias_anuales
        self.saldo_vacaciones += nuevos_dias_con_derecho
        
        # Acumular días no usados del año anterior (para compatibilidad)
        if dias_a_acumular > 0:
            self.dias_vacaciones_acumulados = dias_a_acumular
        
        # Nota: El registro en historial se hará después de guardar para evitar import circular
        
        self.save(update_fields=[
            'dias_vacaciones_acumulados', 
            'dias_vacaciones_usados', 
            'ultimo_reset_vacaciones',
            'dias_vacaciones_anuales',
            'dias_vacaciones_extraordinarios',
            'dias_vacaciones_extraordinarios_ano_anterior',
            'saldo_vacaciones'
        ])
        
        # Registrar en el historial el cambio de saldo por aniversario (después de guardar)
        try:
            from decimal import Decimal
            # Importar aquí para evitar import circular
            from empleados.models import HistorialVacaciones
            HistorialVacaciones.objects.create(
                empleado=self,
                concepto=f'Aniversario laboral - Año {self.antiguedad_anos} completado',
                tipo_movimiento='DIAS_CON_DERECHO',
                fecha_registro=date.today(),
                con_derecho=Decimal(str(dias_con_derecho_ano_anterior + nuevos_dias_con_derecho)),
                tomadas=Decimal(str(dias_gastados_ano_anterior)),
                observaciones=f'Saldo del año anterior: {saldo_ano_anterior:.2f} días. Días con derecho nuevo año: {nuevos_dias_con_derecho:.2f} días. Nuevo saldo acumulado: {self.saldo_vacaciones:.2f} días.'
            )
        except Exception:
            # Si falla el registro en historial, no es crítico
            pass
        
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
        ('PENDIENTE_ADMIN', 'Pendiente Administrador'),
        ('APROBADO_JEFE', 'Aprobado por Jefe'),
        ('APROBADO_ADMIN', 'Aprobado por Administrador'),
        ('RECHAZADO_JEFE', 'Rechazado por Jefe'),
        ('RECHAZADO_ADMIN', 'Rechazado por Administrador'),
        ('PENDIENTE_RH', 'Pendiente RH'),
        ('APROBADO_RH', 'Aprobado por RH'),
        ('RECHAZADO_RH', 'Rechazado por RH'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    TIPOS = [
        ('NORMAL', 'Vacación Normal'),
        ('EXTRAORDINARIA', 'Vacación Extraordinaria'),
    ]
    
    # Mantener EMERGENCIA temporalmente para compatibilidad con datos existentes
    TIPOS_CON_LEGACY = TIPOS + [('EMERGENCIA', 'Vacación Extraordinaria')]
    
    empleado = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='solicitudes_vacaciones', 
                                verbose_name="Empleado")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")
    dias_solicitados = models.PositiveIntegerField(verbose_name="Días Solicitados")
    tipo = models.CharField(max_length=20, choices=TIPOS_CON_LEGACY, default='NORMAL', verbose_name="Tipo")
    motivo = models.TextField(verbose_name="Motivo")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE_JEFE', verbose_name="Estado")
    
    # Campos de aprobación
    aprobado_por_jefe = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='vacaciones_aprobadas_jefe', verbose_name="Aprobado por Jefe")
    aprobado_por_admin = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='vacaciones_aprobadas_admin', verbose_name="Aprobado por Administrador")
    aprobado_por_rh = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='vacaciones_aprobadas_rh', verbose_name="Aprobado por RH")
    
    comentarios_jefe = models.TextField(blank=True, verbose_name="Comentarios del Jefe")
    comentarios_admin = models.TextField(blank=True, verbose_name="Comentarios del Administrador")
    comentarios_rh = models.TextField(blank=True, verbose_name="Comentarios de RH")
    
    # Auditoría
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Solicitud")
    fecha_aprobacion_jefe = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Aprobación Jefe")
    fecha_aprobacion_admin = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Aprobación Administrador")
    fecha_aprobacion_rh = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Aprobación RH")
    
    class Meta:
        verbose_name = "Solicitud de Vacaciones"
        verbose_name_plural = "Solicitudes de Vacaciones"
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.fecha_inicio} a {self.fecha_fin}"
    
    def get_tipo_display(self):
        """Override para manejar valores antiguos de EMERGENCIA"""
        tipo_value = self.tipo
        if tipo_value == 'EMERGENCIA':
            return 'Vacación Extraordinaria'  # Convertir emergencia a extraordinaria para display
        # Usar el método original de Django
        for choice_value, choice_label in self.TIPOS:
            if choice_value == tipo_value:
                return choice_label
        return tipo_value  # Si no encuentra, devolver el valor original
    
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
        
        # Si es una nueva solicitud (sin pk) y el empleado es jefe de área, establecer estado PENDIENTE_ADMIN
        if not self.pk and self.empleado and self.empleado.es_jefe_area():
            if self.estado == 'PENDIENTE_JEFE':  # Solo si es el estado por defecto
                self.estado = 'PENDIENTE_ADMIN'
        
        super().save(*args, **kwargs)
    
    def puede_ser_aprobada_por_jefe(self):
        """Verifica si puede ser aprobada por jefe"""
        return self.estado == 'PENDIENTE_JEFE'
    
    def puede_ser_aprobada_por_admin(self):
        """Verifica si puede ser aprobada por administrador"""
        return self.estado == 'PENDIENTE_ADMIN'
    
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
    
    def aprobar_por_admin(self, admin_user, comentario=""):
        """Aprobar solicitud por administrador"""
        from django.utils import timezone
        
        if not self.puede_ser_aprobada_por_admin():
            return False
        
        self.estado = 'APROBADO_ADMIN'
        self.aprobado_por_admin = admin_user
        self.comentarios_admin = comentario
        self.fecha_aprobacion_admin = timezone.now()
        
        # Después de aprobar por admin, va a RH
        self.estado = 'PENDIENTE_RH'
        
        self.save()
        return True
    
    def rechazar_por_admin(self, admin_user, comentario=""):
        """Rechazar solicitud por administrador"""
        from django.utils import timezone
        
        if not self.puede_ser_aprobada_por_admin():
            return False
        
        self.estado = 'RECHAZADO_ADMIN'
        self.aprobado_por_admin = admin_user
        self.comentarios_admin = comentario
        self.fecha_aprobacion_admin = timezone.now()
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
        
        # Actualizar días usados del empleado según el tipo de vacación
        if self.tipo == 'EXTRAORDINARIA' or self.tipo == 'EMERGENCIA':
            # Las vacaciones extraordinarias se restan directamente del saldo
            # Solo se pueden tomar cuando el saldo es 0 o negativo
            from decimal import Decimal
            self.empleado.dias_vacaciones_extraordinarios += self.dias_solicitados
            # Restar del saldo (el saldo puede ser negativo)
            self.empleado.saldo_vacaciones -= Decimal(str(self.dias_solicitados))
        else:
            # Vacaciones normales: se restan de los días usados del año
            self.empleado.dias_vacaciones_usados += self.dias_solicitados
            # También se restan del saldo
            from decimal import Decimal
            self.empleado.saldo_vacaciones -= Decimal(str(self.dias_solicitados))
        
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


class HistorialVacaciones(models.Model):
    """Historial de vacaciones tomadas en años anteriores - editable por RH y Admin"""
    TIPOS_MOVIMIENTO = [
        ('VACACIONES_TOMADAS', 'Vacaciones tomadas'),
        ('VACACIONES_ANTES_REGISTRO', 'Vac. tomadas antes del registro del empleado'),
        ('ANIVERSARIO_LABORAL', 'Aniversario laboral al finalizar I'),
        ('AJUSTE_MANUAL', 'Ajuste manual'),
        ('OTRO', 'Otro'),
    ]
    
    empleado = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='historial_vacaciones', 
                                verbose_name="Empleado")
    concepto = models.CharField(max_length=200, verbose_name="Concepto")
    tipo_movimiento = models.CharField(max_length=50, choices=TIPOS_MOVIMIENTO, default='VACACIONES_TOMADAS', 
                                      verbose_name="Tipo de Movimiento")
    fecha_registro = models.DateField(verbose_name="Fecha registro")
    fecha_inicial = models.DateField(null=True, blank=True, verbose_name="Fecha inicial")
    fecha_final = models.DateField(null=True, blank=True, verbose_name="Fecha final")
    tomadas = models.DecimalField(max_digits=10, decimal_places=3, default=0, verbose_name="Tomadas")
    con_derecho = models.DecimalField(max_digits=10, decimal_places=3, default=0, verbose_name="Con derecho")
    saldo = models.DecimalField(max_digits=10, decimal_places=3, default=0, verbose_name="Saldo")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    
    # Auditoría
    creado_por = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='historial_vacaciones_creadas', verbose_name="Creado por")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    class Meta:
        verbose_name = "Historial de Vacaciones"
        verbose_name_plural = "Historial de Vacaciones"
        ordering = ['empleado', 'fecha_registro', '-fecha_creacion']
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.concepto} ({self.fecha_registro})"
    
    def save(self, *args, **kwargs):
        # Guardar primero para tener el pk
        super().save(*args, **kwargs)
        
        # Recalcular todos los saldos desde el principio para asegurar consistencia
        # Esto es importante porque el orden cronológico puede afectar el cálculo
        self._recalcular_todos_los_saldos()
    
    def _recalcular_todos_los_saldos(self):
        """Recalcula el saldo de TODOS los registros del empleado desde el principio"""
        # Obtener todos los registros ordenados por fecha_registro y fecha_creacion
        registros = HistorialVacaciones.objects.filter(
            empleado=self.empleado
        ).order_by('fecha_registro', 'fecha_creacion')
        
        # Calcular saldo acumulativo desde el principio
        saldo_actual = 0
        registros_a_actualizar = []
        
        for registro in registros:
            # Calcular: saldo anterior + con derecho - tomadas
            saldo_actual = saldo_actual + registro.con_derecho - registro.tomadas
            registros_a_actualizar.append((registro.pk, saldo_actual))
        
        # Actualizar todos los registros con sus saldos calculados
        for pk, saldo in registros_a_actualizar:
            HistorialVacaciones.objects.filter(pk=pk).update(saldo=saldo)
        
        # Actualizar el saldo del registro actual también
        if self.pk:
            saldo_final = next((saldo for pk_reg, saldo in registros_a_actualizar if pk_reg == self.pk), 0)
            self.saldo = saldo_final
            # Guardar el saldo actualizado
            HistorialVacaciones.objects.filter(pk=self.pk).update(saldo=saldo_final)


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
    
    @property
    def fecha_disponibilidad(self):
        """Retorna la fecha desde la cual el equipo está disponible"""
        # Si hay una asignación con fecha de devolución, usar esa fecha
        ultima_devolucion = self.asignaciones.filter(
            fecha_devolucion__isnull=False
        ).order_by('-fecha_devolucion').first()
        
        if ultima_devolucion:
            return ultima_devolucion.fecha_devolucion
        
        # Si no hay devoluciones, usar la fecha de actualización del equipo
        return self.fecha_actualizacion.date() if self.fecha_actualizacion else self.fecha_creacion.date()


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
