from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Vacacion, Empleado, Departamento


class SolicitudVacacionForm(forms.ModelForm):
    class Meta:
        model = Vacacion
        fields = ['fecha_inicio', 'fecha_fin', 'motivo', 'motivo_extraordinario']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'motivo': forms.Textarea(attrs={'rows': 3}),
            'motivo_extraordinario': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get('fecha_inicio')
        fin = cleaned.get('fecha_fin')
        if inicio and fin and fin < inicio:
            self.add_error('fecha_fin', 'La fecha fin debe ser mayor o igual a la fecha inicio')
        if inicio and inicio < timezone.now().date():
            self.add_error('fecha_inicio', 'La fecha inicio no puede ser en el pasado')
        return cleaned


class AprobacionJefeForm(forms.Form):
    aprobar = forms.BooleanField(initial=True, required=False, label='Aprobar solicitud')
    comentario = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))


class AprobacionRHForm(forms.Form):
    aprobar = forms.BooleanField(initial=True, required=False, label='Aprobar solicitud')
    comentario = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))


class CrearUsuarioForm(forms.Form):
    """Formulario para crear usuarios con roles"""
    ROL_CHOICES = [
        ('', 'Seleccionar rol...'),
        ('RH', 'Recursos Humanos'),
        ('JEFES', 'Jefe de Área'),
        ('EMPLEADOS', 'Empleado'),
    ]
    
    # Información de usuario
    username = forms.CharField(max_length=150, label='Nombre de usuario')
    email = forms.EmailField(label='Correo electrónico')
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellidos')
    password1 = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirmar contraseña')
    rol = forms.ChoiceField(choices=ROL_CHOICES, required=False, label='Rol')
    
    # Información de empleado (opcional)
    crear_empleado = forms.BooleanField(required=False, label='Crear perfil de empleado')
    numero_empleado = forms.CharField(max_length=20, required=False, label='Número de empleado')
    nombre = forms.CharField(max_length=100, required=False, label='Nombre completo')
    apellido_paterno = forms.CharField(max_length=100, required=False, label='Apellido paterno')
    apellido_materno = forms.CharField(max_length=100, required=False, label='Apellido materno')
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False, label='Departamento')
    puesto = forms.CharField(max_length=100, required=False, label='Puesto')
    fecha_ingreso = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False, label='Fecha de ingreso')
    salario = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Salario')
    supervisor = forms.ModelChoiceField(queryset=Empleado.objects.filter(activo=True), required=False, label='Supervisor')
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        crear_empleado = cleaned_data.get('crear_empleado')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        
        if crear_empleado:
            campos_requeridos = ['numero_empleado', 'nombre', 'apellido_paterno', 'apellido_materno', 
                               'departamento', 'puesto', 'fecha_ingreso', 'salario']
            for campo in campos_requeridos:
                if not cleaned_data.get(campo):
                    raise forms.ValidationError(f'El campo {self.fields[campo].label} es requerido cuando se crea un perfil de empleado.')
        
        return cleaned_data
    
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
    
    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )
        return user


class PerfilEmpleadoForm(forms.ModelForm):
    """Formulario para actualizar perfil de empleado"""
    class Meta:
        model = Empleado
        fields = ['telefono', 'email', 'direccion', 'fecha_nacimiento', 'genero', 'estado_civil']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'telefono': forms.TextInput(attrs={'placeholder': '+52 55 1234 5678'}),
            'email': forms.EmailInput(attrs={'placeholder': 'correo@empresa.com'}),
            'direccion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Calle, número, colonia, ciudad, estado'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos opcionales más visibles
        self.fields['telefono'].required = False
        self.fields['email'].required = False
        self.fields['direccion'].required = False

