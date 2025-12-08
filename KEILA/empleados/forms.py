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
                ]
                meses_trabajados = ((timezone.now().date() - self.empleado.fecha_contratacion).days) / 30.44
                self.fields['tipo'].help_text = (
                    f'Tienes {antiguedad} año(s) de antigüedad ({meses_trabajados:.1f} meses). '
                    f'Días acumulados: {dias_calculados:.2f}. '
                    f'Días disponibles: {dias_disponibles}'
                )
            else:
                # Para empleados con antigüedad >= 1, mostrar solo TIPOS (sin legacy) para evitar duplicados
                self.fields['tipo'].choices = [
                    ('NORMAL', 'Vacación Normal'),
                    ('EXTRAORDINARIA', 'Vacación Extraordinaria'),
                ]
                self.fields['tipo'].help_text = f'Antigüedad: {antiguedad} años. Días disponibles: {dias_disponibles}'
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            # Validar que la fecha fin sea posterior a la fecha inicio
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
            
            # Validar que no sea más de una semana en el pasado
            # Permitir solicitar vacaciones hasta 7 días antes (para cambiar faltas por días de vacaciones)
            from datetime import date
            hoy = timezone.now().date()
            fecha_limite = hoy - timedelta(days=7)  # Permite hasta una semana antes
            
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
            
            if fecha_inicio_date < fecha_limite:
                raise forms.ValidationError('No puedes solicitar vacaciones para fechas anteriores a hace una semana. Solo se permite retroceder hasta 7 días para cambiar faltas por días de vacaciones.')
            
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


class AprobacionAdminForm(forms.Form):
    """Formulario para aprobar/rechazar solicitudes por administrador"""
    accion = forms.ChoiceField(
        choices=[('aprobar', 'Aprobar'), ('rechazar', 'Rechazar')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Decisión'
    )
    comentario = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Comentarios sobre la decisión (opcional)'
        }),
        label='Comentarios'
    )
    
    def __init__(self, *args, **kwargs):
        solicitud = kwargs.pop('solicitud', None)
        super().__init__(*args, **kwargs)
        
        self.fields['accion'].required = True


class AprobacionRHForm(forms.Form):
    """Formulario para aprobación por RH"""
    accion = forms.ChoiceField(
        choices=[
            ('aprobar', 'Aprobar Solicitud'),
            ('rechazar', 'Rechazar Solicitud'),
        ],
        widget=forms.RadioSelect,  # Mantener RadioSelect pero usar inputs personalizados en template
        label='Acción',
        required=True
    )
    comentario = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comentarios sobre la decisión...', 'class': 'form-control'}),
        label='Comentarios',
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        self.solicitud = kwargs.pop('solicitud', None)
        super().__init__(*args, **kwargs)
        # Hacer accion no requerido en el widget pero requerido en validación
        self.fields['accion'].required = True


class EditarPerfilForm(forms.ModelForm):
    """Formulario para editar perfil de usuario"""
    
    def __init__(self, *args, **kwargs):
        es_admin = kwargs.pop('es_admin', False)
        super().__init__(*args, **kwargs)
        
        # Si es admin, incluir todos los campos editables
        if es_admin:
            # Agregar campos adicionales si no están ya incluidos
            admin_fields = ['tipo_perfil', 'departamento', 'puesto', 'direccion', 'numero_empleado', 'fecha_contratacion', 'activo']
            for field_name in admin_fields:
                if field_name not in self.fields:
                    # Agregar el campo del modelo
                    self.fields[field_name] = self._meta.model._meta.get_field(field_name).formfield()
                    # Inicializar el valor del campo con el valor de la instancia si existe
                    if self.instance and self.instance.pk:
                        try:
                            field_value = getattr(self.instance, field_name)
                            if field_value is not None:
                                self.initial[field_name] = field_value
                        except AttributeError:
                            pass
        
        # Configurar widgets y estilos para todos los campos
        if 'telefono' in self.fields:
            self.fields['telefono'].widget.attrs.update({
                'class': 'form-control editar-perfil-input',
                'placeholder': 'Ingrese el teléfono'
            })
        
        if 'fecha_nacimiento' in self.fields:
            self.fields['fecha_nacimiento'].widget.attrs.update({
                'class': 'form-control editar-perfil-input datepicker-fecha-nacimiento',
                'placeholder': 'DD/MM/YYYY',
                'type': 'text'
            })
        
        # Si es admin, configurar campos adicionales
        if es_admin:
            if 'tipo_perfil' in self.fields:
                self.fields['tipo_perfil'].widget.attrs.update({
                    'class': 'form-select editar-perfil-select'
                })
            
            if 'departamento' in self.fields:
                self.fields['departamento'].widget.attrs.update({
                    'class': 'form-select editar-perfil-select'
                })
                self.fields['departamento'].queryset = Departamento.objects.filter(activo=True).order_by('nombre')
            
            if 'puesto' in self.fields:
                self.fields['puesto'].widget.attrs.update({
                    'class': 'form-control editar-perfil-input',
                    'placeholder': 'Ingrese el puesto'
                })
            
            if 'direccion' in self.fields:
                self.fields['direccion'].widget.attrs.update({
                    'class': 'form-control editar-perfil-input',
                    'placeholder': 'Ingrese la dirección'
                })
            
            if 'numero_empleado' in self.fields:
                self.fields['numero_empleado'].widget.attrs.update({
                    'class': 'form-control editar-perfil-input',
                    'placeholder': 'Ingrese el número de empleado'
                })
            
            if 'fecha_contratacion' in self.fields:
                self.fields['fecha_contratacion'].widget.attrs.update({
                    'class': 'form-control editar-perfil-input datepicker-fecha-contratacion',
                    'placeholder': 'DD/MM/YYYY',
                    'type': 'text'
                })
            
            if 'activo' in self.fields:
                self.fields['activo'].widget.attrs.update({
                    'class': 'form-check-input editar-perfil-checkbox'
                })
    
    class Meta:
        model = Perfil
        fields = ['telefono', 'fecha_nacimiento']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'text'}),
        }
        labels = {
            'telefono': 'Teléfono',
            'fecha_nacimiento': 'Fecha de Nacimiento',
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


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
    
    # Campo opcional para asignar el equipo al crearlo
    asignar_a_empleado = forms.ModelChoiceField(
        queryset=Perfil.objects.filter(activo=True),
        required=False,
        label='Asignar a Empleado (Opcional)',
        help_text='Si selecciona un empleado, el equipo se asignará automáticamente',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; color: #ffffff !important; border-radius: 10px;'
        })
    )
    condicion_entrega = forms.CharField(
        required=False,
        max_length=200,
        label='Condición al Entregar',
        help_text='Ej: Nuevo, Usado - Buen estado, etc.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Nuevo, Usado - Buen estado, etc.',
            'style': 'background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; color: #ffffff !important; border-radius: 10px;'
        })
    )
    
    class Meta:
        model = Equipo
        fields = [
            'categoria', 'marca', 'modelo', 'numero_serie', 
            'codigo_inventario', 'estado', 'fecha_adquisicion', 'observaciones'
        ]
        widgets = {
            'categoria': forms.Select(attrs={
                'class': 'form-control',
                'style': 'background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; color: #ffffff !important; border-radius: 10px;'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: HP, Apple, Dell',
                'style': 'background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; color: #ffffff !important; border-radius: 10px;'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: EliteBook 840',
                'style': 'background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; color: #ffffff !important; border-radius: 10px;'
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Número de serie único',
                'style': 'background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; color: #ffffff !important; border-radius: 10px;'
            }),
            'codigo_inventario': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Código interno de inventario',
                'style': 'background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; color: #ffffff !important; border-radius: 10px;'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control',
                'style': 'background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; color: #ffffff !important; border-radius: 10px;'
            }),
            'fecha_adquisicion': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'style': 'background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; color: #ffffff !important; border-radius: 10px;'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'style': 'background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; color: #ffffff !important; border-radius: 10px;'
            }),
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar empleados por nombre
        self.fields['asignar_a_empleado'].queryset = Perfil.objects.filter(activo=True).order_by('usuario__first_name', 'usuario__last_name')


class AsignacionEquipoForm(forms.ModelForm):
    """Formulario para asignar equipos a empleados"""
    
    # Campo adicional para cambiar el estado del equipo (solo cuando está en reparación)
    nuevo_estado = forms.ChoiceField(
        choices=Equipo.ESTADOS_EQUIPO,
        required=False,
        label='Cambiar Estado del Equipo',
        help_text='Seleccione el nuevo estado del equipo después de la asignación',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; color: #ffffff !important; border-radius: 10px;'
        })
    )
    
    class Meta:
        model = AsignacionEquipo
        fields = ['equipo', 'empleado', 'condicion_entrega', 'observaciones']
        widgets = {
            'equipo': forms.Select(attrs={
                'class': 'form-control',
                'style': 'background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; color: #ffffff !important; border-radius: 10px;'
            }),
            'empleado': forms.Select(attrs={
                'class': 'form-control',
                'style': 'background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; color: #ffffff !important; border-radius: 10px;'
            }),
            'condicion_entrega': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Nuevo, Usado - Buen estado, etc.',
                'style': 'background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; color: #ffffff !important; border-radius: 10px;'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'style': 'background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; color: #ffffff !important; border-radius: 10px;'
            }),
        }
        labels = {
            'equipo': 'Equipo',
            'empleado': 'Empleado',
            'condicion_entrega': 'Condición al Entregar',
            'observaciones': 'Observaciones',
        }
    
    def __init__(self, *args, **kwargs):
        equipo_en_reparacion = kwargs.pop('equipo_en_reparacion', False)
        estado_actual = kwargs.pop('estado_actual', None)
        es_edicion = kwargs.pop('es_edicion', False)
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        
        # Si es una edición, permitir cualquier equipo (ya está asignado)
        if instance:
            self.fields['equipo'].queryset = Equipo.objects.all()
        else:
            # Solo mostrar equipos disponibles o en reparación para nuevas asignaciones
            self.fields['equipo'].queryset = Equipo.objects.filter(estado__in=['DISPONIBLE', 'EN_REPARACION'])
        
        # Solo mostrar empleados activos
        self.fields['empleado'].queryset = Perfil.objects.filter(activo=True).order_by('usuario__first_name', 'usuario__last_name')
        # Hacer opcional observaciones y condición
        self.fields['observaciones'].required = False
        self.fields['condicion_entrega'].required = False
        
        # Mostrar campo de estado si el equipo está en reparación, es una edición, o es una nueva asignación
        mostrar_campo_estado = equipo_en_reparacion or es_edicion
        
        # Si es una nueva asignación (no edición), siempre mostrar el campo de estado
        if not instance and not es_edicion:
            mostrar_campo_estado = True
        
        if mostrar_campo_estado:
            self.fields['nuevo_estado'].required = False  # Opcional
            self.fields['nuevo_estado'].initial = estado_actual
            
            # En edición, permitir todos los estados incluyendo mantener el actual
            if es_edicion:
                choices = [('', 'Mantener estado actual')]
                choices.extend(Equipo.ESTADOS_EQUIPO)
                self.fields['nuevo_estado'].choices = choices
                self.fields['nuevo_estado'].help_text = 'Opcional: Cambie el estado si el equipo se descompuso, se dio de baja, o necesita mantenimiento'
            elif equipo_en_reparacion:
                # Si está en reparación y es nueva asignación, no permitir mantener "En Reparación"
                choices = [('', 'Seleccione el nuevo estado...')]
                choices.extend([(estado[0], estado[1]) for estado in Equipo.ESTADOS_EQUIPO if estado[0] != 'EN_REPARACION'])
                self.fields['nuevo_estado'].choices = choices
                self.fields['nuevo_estado'].required = True
                self.fields['nuevo_estado'].help_text = 'Seleccione el nuevo estado del equipo después de la asignación'
            else:
                # Nueva asignación de equipo disponible - permitir todos los estados excepto mantener el actual
                choices = [('', 'Mantener estado actual (se cambiará a Asignado automáticamente)')]
                choices.extend(Equipo.ESTADOS_EQUIPO)
                self.fields['nuevo_estado'].choices = choices
                self.fields['nuevo_estado'].help_text = 'Opcional: Seleccione un estado específico, o deje en blanco para cambiar automáticamente a "Asignado"'
        else:
            # Ocultar el campo si no se debe mostrar
            self.fields['nuevo_estado'].widget = forms.HiddenInput()
            self.fields['nuevo_estado'].required = False


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
