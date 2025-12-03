from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
from django.contrib.auth import get_user_model


class Departamento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('S', 'Soltero(a)'),
        ('C', 'Casado(a)'),
        ('D', 'Divorciado(a)'),
        ('V', 'Viudo(a)'),
        ('U', 'Unión libre'),
    ]
    
    # Información personal
    numero_empleado = models.CharField(max_length=20, unique=True, verbose_name="Número de Empleado")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido_paterno = models.CharField(max_length=100, verbose_name="Apellido Paterno")
    apellido_materno = models.CharField(max_length=100, verbose_name="Apellido Materno")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, verbose_name="Género")
    estado_civil = models.CharField(max_length=1, choices=ESTADO_CIVIL_CHOICES, verbose_name="Estado Civil")
    
    # Cuenta de usuario (para inicio de sesión y permisos)
    user = models.OneToOneField(
        get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Usuario"
    )

    # Información de contacto
    telefono = models.CharField(max_length=15, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Correo Electrónico")
    direccion = models.TextField(blank=True, verbose_name="Dirección")
    
    # Información laboral
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, verbose_name="Departamento")
    puesto = models.CharField(max_length=100, verbose_name="Puesto")
    fecha_ingreso = models.DateField(verbose_name="Fecha de Ingreso")
    salario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salario")
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Supervisor")
    
    # Información de vacaciones
    dias_vacaciones_anuales = models.PositiveIntegerField(default=20, verbose_name="Días de Vacaciones Anuales")
    dias_vacaciones_usados = models.PositiveIntegerField(default=0, verbose_name="Días de Vacaciones Usados")
    
    # Estado
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ['apellido_paterno', 'apellido_materno', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"
    
    @property
    def dias_vacaciones_disponibles(self):
        return self.dias_vacaciones_anuales - self.dias_vacaciones_usados
    
    @property
    def antiguedad_anos(self):
        today = date.today()
        return today.year - self.fecha_ingreso.year - ((today.month, today.day) < (self.fecha_ingreso.month, self.fecha_ingreso.day))


class Vacacion(models.Model):
    ESTADO_CHOICES = [
        ('P', 'Pendiente'),
        ('A', 'Aprobada'),
        ('R', 'Rechazada'),
        ('C', 'Cancelada'),
    ]

    TIPO_CHOICES = [
        ('N', 'Normal'),          # Cumple antigüedad (>= 1 año)
        ('E', 'Extraordinaria'),  # No cumple antigüedad
    ]

    ETAPA_CHOICES = [
        ('EMP', 'Solicitada por Empleado'),
        ('JEF', 'Revisión de Jefe'),
        ('RH', 'Revisión de RH'),
        ('FIN', 'Finalizada'),
    ]
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='vacaciones', verbose_name="Empleado")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")
    dias_solicitados = models.PositiveIntegerField(verbose_name="Días Solicitados")
    motivo = models.TextField(blank=True, verbose_name="Motivo")
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, default='N', verbose_name="Tipo")
    etapa = models.CharField(max_length=3, choices=ETAPA_CHOICES, default='EMP', verbose_name="Etapa")
    
    # Campos de aprobación por etapas
    aprobado_jefe = models.BooleanField(default=False, verbose_name="Aprobado por Jefe")
    aprobado_rh = models.BooleanField(default=False, verbose_name="Aprobado por RH")
    motivo_extraordinario = models.TextField(blank=True, verbose_name="Motivo Extraordinario")
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P', verbose_name="Estado")
    comentarios_rh = models.TextField(blank=True, verbose_name="Comentarios de RH")
    
    # Auditoría
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Solicitud")
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Aprobación")
    aprobado_por = models.CharField(max_length=100, blank=True, verbose_name="Aprobado por")
    
    class Meta:
        verbose_name = "Vacación"
        verbose_name_plural = "Vacaciones"
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.fecha_inicio} a {self.fecha_fin}"
    
    def save(self, *args, **kwargs):
        # Calcular días solicitados automáticamente
        if self.fecha_inicio and self.fecha_fin:
            delta = self.fecha_fin - self.fecha_inicio
            self.dias_solicitados = delta.days + 1
        # Determinar tipo según antigüedad
        if self.empleado:
            self.tipo = 'N' if self.empleado.antiguedad_anos >= 1 else 'E'
        super().save(*args, **kwargs)

    # Utilidades de negocio
    @property
    def es_normal(self) -> bool:
        return self.tipo == 'N'

    @property
    def es_extraordinaria(self) -> bool:
        return self.tipo == 'E'

    def puede_ser_normal(self) -> bool:
        return self.empleado and self.empleado.antiguedad_anos >= 1

    def marcar_aprobacion_jefe(self, aprobada: bool, comentario: str = ""):
        self.aprobado_jefe = aprobada
        if not aprobada:
            self.estado = 'R'
            self.etapa = 'FIN'
        else:
            self.etapa = 'RH'
        if comentario:
            self.comentarios_rh = (self.comentarios_rh + "\n" if self.comentarios_rh else "") + f"Jefe: {comentario}"
        self.save()

    def marcar_aprobacion_rh(self, aprobada: bool, comentario: str = ""):
        self.aprobado_rh = aprobada
        if aprobada and (self.aprobado_jefe or self.es_normal):
            self.estado = 'A'
        else:
            if not aprobada:
                self.estado = 'R'
        self.etapa = 'FIN'
        if comentario:
            self.comentarios_rh = (self.comentarios_rh + "\n" if self.comentarios_rh else "") + f"RH: {comentario}"
        self.save()
