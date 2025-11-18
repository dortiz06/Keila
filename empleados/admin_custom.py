from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Q
from .models import Perfil, Departamento, SolicitudVacaciones, ConfiguracionSistema, Ticket, Equipo, AsignacionEquipo, CategoriaEquipo
from datetime import date, timedelta


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    """Admin personalizado para gestión de perfiles de empleados"""
    
    list_display = [
        'numero_empleado', 'nombre_completo', 'tipo_perfil', 'departamento', 
        'fecha_contratacion', 'antiguedad_display', 'puede_vacaciones', 
        'dias_vacaciones_info', 'activo_status'
    ]
    
    list_filter = [
        'tipo_perfil', 'departamento', 'activo', 'fecha_contratacion',
        ('fecha_contratacion', admin.DateFieldListFilter),
    ]
    
    search_fields = [
        'usuario__username', 'usuario__first_name', 'usuario__last_name',
        'numero_empleado', 'puesto', 'departamento__nombre'
    ]
    
    readonly_fields = [
        'antiguedad_display', 'puede_vacaciones', 'dias_vacaciones_info',
        'fecha_creacion', 'fecha_actualizacion'
    ]
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('usuario', 'numero_empleado', 'tipo_perfil', 'activo')
        }),
        ('Información Laboral', {
            'fields': ('departamento', 'puesto', 'supervisor')
        }),
        ('Fechas Importantes', {
            'fields': ('fecha_contratacion', 'fecha_nacimiento', 'antiguedad_display'),
            'description': 'La fecha de contratación determina los días de vacaciones según antigüedad. Puedes modificarla para hacer pruebas.'
        }),
        ('Control de Vacaciones', {
            'fields': (
                'puede_vacaciones', 
                'dias_vacaciones_anuales', 
                'dias_vacaciones_usados', 
                'dias_vacaciones_acumulados',
                'dias_vacaciones_extraordinarios',
                'ultimo_reset_vacaciones',
                'dias_vacaciones_info'
            ),
            'description': 'Los días anuales se calculan automáticamente según antigüedad. Puedes ajustar manualmente para pruebas.',
            'classes': ('collapse',)
        }),
        ('Información de Contacto', {
            'fields': ('telefono',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['usuario__last_name', 'usuario__first_name']
    
    def antiguedad_display(self, obj):
        """Muestra la antigüedad de forma legible"""
        anos = obj.antiguedad_anos
        if anos == 0:
            return format_html('<span style="color: orange;">Menos de 1 año</span>')
        elif anos == 1:
            return format_html('<span style="color: green;">1 año</span>')
        else:
            return format_html('<span style="color: green;">{} años</span>', anos)
    antiguedad_display.short_description = 'Antigüedad'
    
    def puede_vacaciones(self, obj):
        """Indica si el empleado puede solicitar vacaciones"""
        if not obj.fecha_contratacion:
            return format_html('<span style="color: gray;">Sin fecha</span>')
        
        if obj.antiguedad_anos >= 1:
            return format_html('<span style="color: green;">✓ Puede solicitar</span>')
        else:
            dias_restantes = 365 - (date.today() - obj.fecha_contratacion).days
            return format_html(
                '<span style="color: orange;">✗ Falta {} días</span>', 
                dias_restantes
            )
    puede_vacaciones.short_description = 'Puede Vacaciones'
    
    def dias_vacaciones_info(self, obj):
        """Muestra información detallada de vacaciones"""
        disponibles = obj.dias_vacaciones_disponibles
        usados = obj.dias_vacaciones_usados
        total = obj.dias_vacaciones_anuales
        
        if disponibles > 0:
            color = 'green'
        elif disponibles == 0:
            color = 'orange'
        else:
            color = 'red'
            
        return format_html(
            '<span style="color: {};">{} disponibles / {} usados / {} total</span>',
            color, disponibles, usados, total
        )
    dias_vacaciones_info.short_description = 'Estado Vacaciones'
    
    def activo_status(self, obj):
        """Muestra el estado activo con colores"""
        if obj.activo:
            return format_html('<span style="color: green;">✓ Activo</span>')
        else:
            return format_html('<span style="color: red;">✗ Inactivo</span>')
    activo_status.short_description = 'Estado'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'usuario', 'departamento', 'supervisor'
        )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Personalizar cómo se muestran los campos ForeignKey"""
        if db_field.name == 'supervisor':
            # Filtrar solo jefes de área y administradores
            kwargs['queryset'] = Perfil.objects.filter(
                activo=True, 
                tipo_perfil__in=['JEFE_AREA', 'ADMIN']
            )
            # Personalizar cómo se muestra en el dropdown
            field = super().formfield_for_foreignkey(db_field, request, **kwargs)
            field.label_from_instance = lambda obj: f"{obj.nombre_completo} - {obj.get_tipo_perfil_display()}"
            return field
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    actions = [
        'marcar_como_activos', 'marcar_como_inactivos', 'resetear_vacaciones',
        'simular_1_ano', 'simular_2_anos', 'simular_5_anos', 'actualizar_dias_vacaciones'
    ]
    
    def marcar_como_activos(self, request, queryset):
        """Marcar empleados seleccionados como activos"""
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} empleados marcados como activos.')
    marcar_como_activos.short_description = "Marcar como activos"
    
    def marcar_como_inactivos(self, request, queryset):
        """Marcar empleados seleccionados como inactivos"""
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} empleados marcados como inactivos.')
    marcar_como_inactivos.short_description = "Marcar como inactivos"
    
    def resetear_vacaciones(self, request, queryset):
        """Resetear días de vacaciones usados"""
        updated = queryset.update(dias_vacaciones_usados=0)
        self.message_user(request, f'Vacaciones reseteadas para {updated} empleados.')
    resetear_vacaciones.short_description = "Resetear vacaciones"
    
    def simular_1_ano(self, request, queryset):
        """Simular que el empleado tiene 1 año de antigüedad (para pruebas)"""
        fecha_hace_1_ano = date.today() - timedelta(days=365)
        updated = queryset.update(fecha_contratacion=fecha_hace_1_ano)
        for perfil in queryset:
            perfil.actualizar_dias_vacaciones()
        self.message_user(request, f'{updated} empleados ajustados a 1 año de antigüedad (12 días).')
    simular_1_ano.short_description = "🧪 Simular 1 año de antigüedad"
    
    def simular_2_anos(self, request, queryset):
        """Simular que el empleado tiene 2 años de antigüedad (para pruebas)"""
        fecha_hace_2_anos = date.today() - timedelta(days=730)
        updated = queryset.update(fecha_contratacion=fecha_hace_2_anos)
        for perfil in queryset:
            perfil.actualizar_dias_vacaciones()
        self.message_user(request, f'{updated} empleados ajustados a 2 años de antigüedad (14 días).')
    simular_2_anos.short_description = "🧪 Simular 2 años de antigüedad"
    
    def simular_5_anos(self, request, queryset):
        """Simular que el empleado tiene 5 años de antigüedad (para pruebas)"""
        fecha_hace_5_anos = date.today() - timedelta(days=1825)
        updated = queryset.update(fecha_contratacion=fecha_hace_5_anos)
        for perfil in queryset:
            perfil.actualizar_dias_vacaciones()
        self.message_user(request, f'{updated} empleados ajustados a 5 años de antigüedad (20 días).')
    simular_5_anos.short_description = "🧪 Simular 5 años de antigüedad"
    
    def actualizar_dias_vacaciones(self, request, queryset):
        """Actualizar días de vacaciones según antigüedad actual"""
        for perfil in queryset:
            perfil.actualizar_dias_vacaciones()
        self.message_user(request, f'Días de vacaciones actualizados para {queryset.count()} empleados.')
    actualizar_dias_vacaciones.short_description = "🔄 Actualizar días según antigüedad"


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    """Admin para gestión de departamentos"""
    
    list_display = ['nombre', 'jefe', 'empleados_count', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


@admin.register(SolicitudVacaciones)
class SolicitudVacacionesAdmin(admin.ModelAdmin):
    """Admin para gestión de solicitudes de vacaciones"""
    
    list_display = [
        'empleado', 'fecha_inicio', 'fecha_fin', 'dias_solicitados',
        'tipo', 'estado', 'fecha_solicitud'
    ]
    
    list_filter = [
        'estado', 'tipo', 'fecha_solicitud',
        ('fecha_solicitud', admin.DateFieldListFilter),
    ]
    
    search_fields = [
        'empleado__usuario__username', 'empleado__usuario__first_name',
        'empleado__usuario__last_name', 'empleado__numero_empleado'
    ]
    
    readonly_fields = ['fecha_solicitud', 'dias_solicitados']
    
    fieldsets = (
        ('Información de la Solicitud', {
            'fields': ('empleado', 'fecha_inicio', 'fecha_fin', 'dias_solicitados', 'tipo', 'motivo')
        }),
        ('Estado y Aprobaciones', {
            'fields': ('estado', 'aprobado_por_jefe', 'aprobado_por_rh')
        }),
        ('Comentarios', {
            'fields': ('comentarios_jefe', 'comentarios_rh')
        }),
        ('Fechas', {
            'fields': ('fecha_solicitud', 'fecha_aprobacion_jefe', 'fecha_aprobacion_rh')
        }),
    )
    
    ordering = ['-fecha_solicitud']


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    """Admin para configuraciones del sistema"""
    
    list_display = ['nombre', 'valor', 'descripcion']
    search_fields = ['nombre', 'descripcion']


# ===================================================================
# ADMIN DE TICKETS Y EQUIPOS
# ===================================================================

@admin.register(CategoriaEquipo)
class CategoriaEquipoAdmin(admin.ModelAdmin):
    """Admin para categorías de equipos"""
    
    list_display = ['nombre', 'descripcion', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']


class AsignacionEquipoInline(admin.TabularInline):
    """Inline para gestionar asignaciones de equipos desde el admin de Equipo"""
    model = AsignacionEquipo
    extra = 1
    fields = ('empleado', 'fecha_asignacion', 'fecha_devolucion', 'condicion_entrega', 'condicion_devolucion', 'asignado_por')
    readonly_fields = ('asignado_por',)
    can_delete = True
    
    def get_readonly_fields(self, request, obj=None):
        """Hacer campos editables según el contexto"""
        if obj and obj.pk:  # Si el objeto ya existe
            # Mostrar fecha_asignacion y fecha_devolucion como readonly si ya existen
            return ('asignado_por',)
        return ('asignado_por',)  # Al crear, todos los campos son editables excepto asignado_por


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    """Admin para equipos tecnológicos"""
    
    list_display = [
        'codigo_inventario', 'categoria', 'marca', 'modelo', 
        'numero_serie', 'estado', 'empleado_asignado_display', 'fecha_adquisicion'
    ]
    list_filter = ['estado', 'categoria', 'fecha_adquisicion']
    search_fields = ['codigo_inventario', 'numero_serie', 'marca', 'modelo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'empleado_asignado_display']
    inlines = [AsignacionEquipoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('categoria', 'marca', 'modelo', 'numero_serie', 'codigo_inventario')
        }),
        ('Estado y Fechas', {
            'fields': ('estado', 'fecha_adquisicion')
        }),
        ('Asignación Actual', {
            'fields': ('empleado_asignado_display',),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def empleado_asignado_display(self, obj):
        """Muestra el empleado al que está asignado el equipo"""
        empleado = obj.empleado_asignado
        if empleado:
            return format_html(
                '<span class="badge badge-success">{}</span>',
                empleado.nombre_completo
            )
        return format_html('<span class="badge badge-secondary">No asignado</span>')
    empleado_asignado_display.short_description = 'Asignado A'
    
    def save_model(self, request, obj, form, change):
        """Guardar el equipo"""
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        """Guardar el formset de asignaciones y actualizar estado del equipo"""
        instances = formset.save(commit=False)
        for instance in instances:
            # Si es una nueva asignación, establecer asignado_por
            if not instance.pk or not instance.asignado_por:
                try:
                    instance.asignado_por = request.user.perfil
                except:
                    pass
            # Si no tiene fecha_asignacion, usar la fecha actual
            if not instance.fecha_asignacion:
                from django.utils import timezone
                instance.fecha_asignacion = timezone.now().date()
            instance.save()
        
        # Eliminar asignaciones marcadas para eliminar
        for obj in formset.deleted_objects:
            obj.delete()
        
        # Actualizar estado del equipo según asignaciones activas
        equipo = form.instance
        asignacion_activa = equipo.asignaciones.filter(fecha_devolucion__isnull=True).first()
        if asignacion_activa and equipo.estado != 'ASIGNADO':
            equipo.estado = 'ASIGNADO'
            equipo.save(update_fields=['estado'])
        elif not asignacion_activa and equipo.estado == 'ASIGNADO':
            equipo.estado = 'DISPONIBLE'
            equipo.save(update_fields=['estado'])


@admin.register(AsignacionEquipo)
class AsignacionEquipoAdmin(admin.ModelAdmin):
    """Admin para asignaciones de equipos"""
    
    list_display = [
        'equipo', 'empleado', 'fecha_asignacion', 'fecha_devolucion',
        'estado_asignacion', 'asignado_por'
    ]
    list_filter = ['fecha_asignacion', 'fecha_devolucion']
    search_fields = [
        'equipo__codigo_inventario', 'empleado__usuario__first_name',
        'empleado__usuario__last_name'
    ]
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Asignación', {
            'fields': ('equipo', 'empleado', 'fecha_asignacion', 'fecha_devolucion')
        }),
        ('Condiciones', {
            'fields': ('condicion_entrega', 'condicion_devolucion')
        }),
        ('Información Adicional', {
            'fields': ('observaciones', 'asignado_por')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def estado_asignacion(self, obj):
        """Muestra si la asignación está activa o no"""
        if obj.esta_activa:
            return format_html('<span class="badge badge-success">Activa</span>')
        return format_html('<span class="badge badge-secondary">Devuelto</span>')
    estado_asignacion.short_description = 'Estado'


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Admin para tickets de soporte"""
    
    list_display = [
        'codigo', 'empleado', 'tipo', 'prioridad', 'estado',
        'asignado_a', 'fecha_creacion', 'fecha_resolucion'
    ]
    list_filter = ['estado', 'tipo', 'prioridad', 'fecha_creacion']
    search_fields = ['codigo', 'descripcion', 'empleado__usuario__first_name', 'empleado__usuario__last_name']
    readonly_fields = ['codigo', 'fecha_creacion', 'fecha_actualizacion', 'tiempo_respuesta_display', 'tiempo_resolucion_display']
    
    fieldsets = (
        ('Información del Ticket', {
            'fields': ('codigo', 'empleado', 'tipo', 'prioridad', 'estado')
        }),
        ('Detalles del Problema', {
            'fields': ('area', 'dispositivo', 'descripcion')
        }),
        ('Asignación y Resolución', {
            'fields': ('asignado_a', 'solucion')
        }),
        ('Fechas', {
            'fields': (
                'fecha_creacion', 'fecha_asignacion', 'fecha_resolucion',
                'fecha_actualizacion', 'tiempo_respuesta_display', 'tiempo_resolucion_display'
            )
        }),
    )
    
    def tiempo_respuesta_display(self, obj):
        """Muestra el tiempo de respuesta formateado"""
        tiempo = obj.tiempo_respuesta
        if tiempo:
            horas = tiempo.total_seconds() / 3600
            return f"{horas:.2f} horas"
        return "-"
    tiempo_respuesta_display.short_description = 'Tiempo de Respuesta'
    
    def tiempo_resolucion_display(self, obj):
        """Muestra el tiempo de resolución formateado"""
        tiempo = obj.tiempo_resolucion
        if tiempo:
            horas = tiempo.total_seconds() / 3600
            return f"{horas:.2f} horas"
        return "-"
    tiempo_resolucion_display.short_description = 'Tiempo de Resolución'


# Personalizar el admin de Django
admin.site.site_header = "Sistema de Recursos Humanos - Grupo Keila"
admin.site.site_title = "RH Admin"
admin.site.index_title = "Panel de Administración"
