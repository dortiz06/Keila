from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from datetime import timedelta, datetime, date
from .models import Perfil, Departamento, SolicitudVacaciones, Ticket, Equipo, AsignacionEquipo, CategoriaEquipo


class UsuarioConPerfilForm(UserCreationForm):
    """Formulario para crear usuario con perfil"""
    TIPOS_PERFIL = [
        ('EMPLEADO', 'Empleado'),
        ('JEFE_AREA', 'Jefe de Área'),
        ('RH', 'Recursos Humanos'),
        ('SISTEMAS', 'Sistemas/IT'),
        ('ADMIN', 'Administrador'),
    ]
    
    # Campos de usuario
    first_name = forms.CharField(max_length=30, label='Nombre', required=True)
    last_name = forms.CharField(max_length=30, label='Apellidos', required=True)
    email = forms.EmailField(label='Correo electrónico', required=True)
    
    # Campos de perfil
    tipo_perfil = forms.ChoiceField(choices=TIPOS_PERFIL, label='Tipo de Perfil')
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.filter(activo=True),
        label='Departamento',
        required=False
    )
    fecha_contratacion = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha de Contratación',
        initial=timezone.now().date()
    )
    numero_empleado = forms.CharField(max_length=20, label='Número de Empleado')
    puesto = forms.CharField(max_length=100, label='Puesto')
    jefe_area = forms.ModelChoiceField(
        queryset=Perfil.objects.filter(activo=True, tipo_perfil__in=['JEFE_AREA', 'ADMIN']),
        label='Supervisor',
        required=False,
        empty_label='-------',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Información personal adicional
    telefono = forms.CharField(max_length=15, label='Teléfono', required=False)
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha de Nacimiento',
        required=False
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos más amigables
        self.fields['username'].help_text = 'Nombre de usuario único para iniciar sesión'
        self.fields['password1'].help_text = 'Mínimo 8 caracteres'
        # Personalizar cómo se muestran los jefes de área en el dropdown
        if 'jefe_area' in self.fields:
            self.fields['jefe_area'].label_from_instance = lambda obj: f"{obj.nombre_completo} - {obj.get_tipo_perfil_display()}"
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya existe.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def clean_numero_empleado(self):
        numero_empleado = self.cleaned_data.get('numero_empleado')
        if Perfil.objects.filter(numero_empleado=numero_empleado).exists():
            raise forms.ValidationError('Este número de empleado ya existe.')
        return numero_empleado
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # El perfil se crea automáticamente por el signal
            # Solo actualizamos los campos específicos del perfil
            if hasattr(user, 'perfil'):
                perfil = user.perfil
                perfil.tipo_perfil = self.cleaned_data['tipo_perfil']
                perfil.departamento = self.cleaned_data.get('departamento')
                perfil.fecha_contratacion = self.cleaned_data['fecha_contratacion']
                perfil.numero_empleado = self.cleaned_data['numero_empleado']
                perfil.puesto = self.cleaned_data['puesto']
                perfil.supervisor = self.cleaned_data.get('jefe_area')
                perfil.telefono = self.cleaned_data.get('telefono', '')
                perfil.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
                perfil.save()
        
        return user


class SolicitudVacacionesForm(forms.ModelForm):
    """Formulario para solicitar vacaciones"""
    
    class Meta:
        model = SolicitudVacaciones
        fields = ['fecha_inicio', 'fecha_fin', 'tipo', 'motivo']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={
                'type': 'text',
                'class': 'form-control datepicker-ddmm',
                'placeholder': 'DD/MM/YYYY'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'type': 'text',
                'class': 'form-control datepicker-ddmm',
                'placeholder': 'DD/MM/YYYY'
            }),
            'motivo': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe el motivo de tu solicitud de vacaciones...'}),
        }
        labels = {
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin',
            'tipo': 'Tipo de Vacación',
            'motivo': 'Motivo',
        }
    
    def __init__(self, *args, **kwargs):
        self.empleado = kwargs.pop('empleado', None)
        super().__init__(*args, **kwargs)
        
        # Mostrar información de elegibilidad
        if self.empleado:
            antiguedad = self.empleado.antiguedad_anos
            dias_calculados = self.empleado.dias_vacaciones_segun_antiguedad
            dias_disponibles = self.empleado.dias_vacaciones_disponibles
            
            if antiguedad < 1:
                self.fields['tipo'].choices = [
                    ('EXTRAORDINARIA', 'Vacación Extraordinaria'),
                    ('EMERGENCIA', 'Vacación de Emergencia'),
                ]
                meses_trabajados = ((timezone.now().date() - self.empleado.fecha_contratacion).days) / 30.44
                self.fields['tipo'].help_text = (
                    f'Tienes {antiguedad} año(s) de antigüedad ({meses_trabajados:.1f} meses). '
                    f'Días acumulados: {dias_calculados:.2f}. '
                    f'Días disponibles: {dias_disponibles}'
                )
            else:
                self.fields['tipo'].help_text = f'Antigüedad: {antiguedad} años. Días disponibles: {dias_disponibles}'
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            # Validar que la fecha fin sea posterior a la fecha inicio
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
            
            # Validar que no sea en el pasado
            # Usar solo la fecha sin hora para comparar correctamente
            from datetime import date
            hoy = timezone.now().date()
            
            # Asegurar que tenemos un objeto date
            if isinstance(fecha_inicio, date):
                fecha_inicio_date = fecha_inicio
            elif isinstance(fecha_inicio, str):
                try:
                    fecha_inicio_date = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                except ValueError:
                    raise forms.ValidationError('Formato de fecha inválido.')
            else:
                fecha_inicio_date = fecha_inicio
            
            if fecha_inicio_date < hoy:
                raise forms.ValidationError('No puedes solicitar vacaciones para fechas pasadas.')
            
            # Calcular días solicitados (excluyendo domingos)
            dias_solicitados = SolicitudVacaciones.calcular_dias_laborables(fecha_inicio, fecha_fin)
            
            # Contar cuántos domingos hay en el rango
            dias_calendario = (fecha_fin - fecha_inicio).days + 1
            domingos_excluidos = dias_calendario - dias_solicitados
            
            # Validar días disponibles
            if self.empleado and dias_solicitados > self.empleado.dias_vacaciones_disponibles:
                raise forms.ValidationError(
                    f'No tienes suficientes días de vacaciones disponibles. '
                    f'Disponibles: {self.empleado.dias_vacaciones_disponibles} días. '
                    f'Solicitaste: {dias_solicitados} días laborables ({dias_calendario} días totales - {domingos_excluidos} domingos)'
                )
        
        return cleaned_data


class AprobacionJefeForm(forms.Form):
    """Formulario para aprobación por jefe de área"""
    accion = forms.ChoiceField(
        choices=[
            ('aprobar', 'Aprobar Solicitud'),
            ('rechazar', 'Rechazar Solicitud'),
        ],
        widget=forms.RadioSelect,
        label='Acción'
    )
    comentario = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comentarios sobre la decisión...'}),
        label='Comentarios',
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        self.solicitud = kwargs.pop('solicitud', None)
        super().__init__(*args, **kwargs)


class AprobacionRHForm(forms.Form):
    """Formulario para aprobación por RH"""
    accion = forms.ChoiceField(
        choices=[
            ('aprobar', 'Aprobar Solicitud'),
            ('rechazar', 'Rechazar Solicitud'),
        ],
        widget=forms.RadioSelect,
        label='Acción'
    )
    comentario = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comentarios sobre la decisión...'}),
        label='Comentarios',
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        self.solicitud = kwargs.pop('solicitud', None)
        super().__init__(*args, **kwargs)


class EditarPerfilForm(forms.ModelForm):
    """Formulario para editar perfil de usuario"""
    
    class Meta:
        model = Perfil
        fields = ['telefono', 'fecha_nacimiento']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'telefono': 'Teléfono',
            'fecha_nacimiento': 'Fecha de Nacimiento',
        }


class ConfigurarDepartamentoForm(forms.ModelForm):
    """Formulario para configurar departamentos"""
    
    class Meta:
        model = Departamento
        fields = ['nombre', 'descripcion', 'jefe']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'nombre': 'Nombre del Departamento',
            'descripcion': 'Descripción',
            'jefe': 'Jefe de Departamento',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar jefes de área como opciones para jefe de departamento
        self.fields['jefe'].queryset = Perfil.objects.filter(
            activo=True, 
            tipo_perfil__in=['JEFE_AREA', 'ADMIN']
        )


# ===================================================================
# FORMULARIOS DE TICKETS Y EQUIPOS
# ===================================================================

class TicketForm(forms.ModelForm):
    """Formulario para crear/editar tickets de soporte"""
    
    class Meta:
        model = Ticket
        fields = ['tipo', 'area', 'dispositivo', 'prioridad', 'descripcion']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Administración, Ventas, etc.'}),
            'dispositivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Laptop HP, iPhone, etc.'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5,
                'placeholder': 'Describe detalladamente el problema...'
            }),
        }
        labels = {
            'tipo': 'Tipo de Problema',
            'area': 'Área',
            'dispositivo': 'Dispositivo Afectado',
            'prioridad': 'Prioridad',
            'descripcion': 'Descripción del Problema',
        }
    
    def __init__(self, *args, **kwargs):
        self.empleado = kwargs.pop('empleado', None)
        super().__init__(*args, **kwargs)
        # Hacer opcional el campo área y dispositivo
        self.fields['area'].required = False
        self.fields['dispositivo'].required = False


class TicketResolucionForm(forms.ModelForm):
    """Formulario para resolver tickets (usado por Sistemas/IT)"""
    
    class Meta:
        model = Ticket
        fields = ['estado', 'solucion']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'solucion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe la solución aplicada...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limitar las opciones de estado a las relevantes para resolución
        self.fields['estado'].choices = [
            ('EN_PROCESO', 'En Proceso'),
            ('RESUELTO', 'Resuelto'),
            ('CANCELADO', 'Cancelado'),
        ]


class EquipoForm(forms.ModelForm):
    """Formulario para agregar/editar equipos en inventario"""
    
    class Meta:
        model = Equipo
        fields = [
            'categoria', 'marca', 'modelo', 'numero_serie', 
            'codigo_inventario', 'estado', 'fecha_adquisicion', 'observaciones'
        ]
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: HP, Apple, Dell'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: EliteBook 840'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de serie único'}),
            'codigo_inventario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código interno de inventario'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_adquisicion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'categoria': 'Categoría',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'numero_serie': 'Número de Serie',
            'codigo_inventario': 'Código de Inventario',
            'estado': 'Estado',
            'fecha_adquisicion': 'Fecha de Adquisición',
            'observaciones': 'Observaciones',
        }


class AsignacionEquipoForm(forms.ModelForm):
    """Formulario para asignar equipos a empleados"""
    
    class Meta:
        model = AsignacionEquipo
        fields = ['equipo', 'empleado', 'condicion_entrega', 'observaciones']
        widgets = {
            'equipo': forms.Select(attrs={'class': 'form-control'}),
            'empleado': forms.Select(attrs={'class': 'form-control'}),
            'condicion_entrega': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Nuevo, Usado - Buen estado, etc.'
            }),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'equipo': 'Equipo',
            'empleado': 'Empleado',
            'condicion_entrega': 'Condición al Entregar',
            'observaciones': 'Observaciones',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar equipos disponibles
        self.fields['equipo'].queryset = Equipo.objects.filter(estado='DISPONIBLE')
        # Solo mostrar empleados activos
        self.fields['empleado'].queryset = Perfil.objects.filter(activo=True)
        # Hacer opcional observaciones
        self.fields['observaciones'].required = False


class DevolucionEquipoForm(forms.ModelForm):
    """Formulario para registrar devolución de equipos"""
    
    class Meta:
        model = AsignacionEquipo
        fields = ['fecha_devolucion', 'condicion_devolucion', 'observaciones']
        widgets = {
            'fecha_devolucion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'condicion_devolucion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Buen estado, Con daños menores, etc.'
            }),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'fecha_devolucion': 'Fecha de Devolución',
            'condicion_devolucion': 'Condición al Devolver',
            'observaciones': 'Observaciones',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fecha de devolución por defecto hoy
        self.fields['fecha_devolucion'].initial = timezone.now().date()
        # Hacer opcional observaciones
        self.fields['observaciones'].required = False
    
    def clean_fecha_devolucion(self):
        fecha_devolucion = self.cleaned_data.get('fecha_devolucion')
        if self.instance and fecha_devolucion:
            if fecha_devolucion < self.instance.fecha_asignacion:
                raise forms.ValidationError('La fecha de devolución no puede ser anterior a la fecha de asignación.')
        return fecha_devolucion


class CategoriaEquipoForm(forms.ModelForm):
    """Formulario para crear/editar categorías de equipos"""
    
    class Meta:
        model = CategoriaEquipo
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Laptop, Celular, Tablet'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre de la Categoría',
            'descripcion': 'Descripción',
            'activo': 'Activo',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['descripcion'].required = False
