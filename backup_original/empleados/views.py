from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Empleado, Vacacion, Departamento
from datetime import date, timedelta
from .forms import SolicitudVacacionForm, AprobacionJefeForm, AprobacionRHForm, CrearUsuarioForm


@login_required
def index(request):
    """Página principal del sistema de RH - Redirige según rol"""
    # Verificar si tiene perfil de empleado
    try:
        empleado = Empleado.objects.get(user=request.user)
        tiene_perfil = True
    except Empleado.DoesNotExist:
        empleado = None
        tiene_perfil = False
    
    # Redirigir según el rol
    if request.user.groups.filter(name='RH').exists():
        return redirect('gestion_usuarios')
    elif request.user.groups.filter(name='JEFES').exists():
        return redirect('panel_jefe')
    elif request.user.groups.filter(name='EMPLEADOS').exists():
        return redirect('mis_vacaciones')
    else:
        # Usuario sin rol específico - mostrar dashboard básico
        context = {
            'tiene_perfil': tiene_perfil,
            'empleado': empleado,
        }
        return render(request, 'empleados/index.html', context)


@login_required
@permission_required('empleados.view_empleado', raise_exception=True)
def lista_empleados(request):
    """Lista todos los empleados con filtros - Solo RH"""
    empleados = Empleado.objects.filter(activo=True)
    departamentos = Departamento.objects.all()
    
    # Filtros
    departamento_id = request.GET.get('departamento')
    busqueda = request.GET.get('busqueda')
    
    if departamento_id:
        empleados = empleados.filter(departamento_id=departamento_id)
    
    if busqueda:
        empleados = empleados.filter(
            Q(nombre__icontains=busqueda) |
            Q(apellido_paterno__icontains=busqueda) |
            Q(apellido_materno__icontains=busqueda) |
            Q(numero_empleado__icontains=busqueda)
        )
    
    # Ordenamiento
    orden = request.GET.get('orden', 'apellido_paterno')
    empleados = empleados.order_by(orden)
    
    context = {
        'empleados': empleados,
        'departamentos': departamentos,
        'departamento_actual': int(departamento_id) if departamento_id else None,
        'busqueda_actual': busqueda,
        'orden_actual': orden,
    }
    
    return render(request, 'empleados/lista_empleados.html', context)


def detalle_empleado(request, empleado_id):
    """Detalle completo de un empleado"""
    empleado = get_object_or_404(Empleado, id=empleado_id)
    vacaciones = Vacacion.objects.filter(empleado=empleado).order_by('-fecha_solicitud')
    
    # Estadísticas de vacaciones
    vacaciones_aprobadas = vacaciones.filter(estado='A').count()
    vacaciones_pendientes = vacaciones.filter(estado='P').count()
    vacaciones_rechazadas = vacaciones.filter(estado='R').count()
    
    context = {
        'empleado': empleado,
        'vacaciones': vacaciones,
        'vacaciones_aprobadas': vacaciones_aprobadas,
        'vacaciones_pendientes': vacaciones_pendientes,
        'vacaciones_rechazadas': vacaciones_rechazadas,
    }
    
    return render(request, 'empleados/detalle_empleado.html', context)


@login_required
@permission_required('empleados.view_vacacion', raise_exception=True)
def vacaciones(request):
    """Lista todas las vacaciones con filtros - Solo RH"""
    vacaciones = Vacacion.objects.all()
    
    # Filtros
    estado = request.GET.get('estado')
    departamento_id = request.GET.get('departamento')
    busqueda = request.GET.get('busqueda')
    
    if estado:
        vacaciones = vacaciones.filter(estado=estado)
    
    if departamento_id:
        vacaciones = vacaciones.filter(empleado__departamento_id=departamento_id)
    
    if busqueda:
        vacaciones = vacaciones.filter(
            Q(empleado__nombre__icontains=busqueda) |
            Q(empleado__apellido_paterno__icontains=busqueda) |
            Q(empleado__apellido_materno__icontains=busqueda)
        )
    
    # Ordenamiento
    orden = request.GET.get('orden', '-fecha_solicitud')
    vacaciones = vacaciones.order_by(orden)
    
    departamentos = Departamento.objects.all()
    
    context = {
        'vacaciones': vacaciones,
        'departamentos': departamentos,
        'estado_actual': estado,
        'departamento_actual': int(departamento_id) if departamento_id else None,
        'busqueda_actual': busqueda,
        'orden_actual': orden,
    }
    
    return render(request, 'empleados/vacaciones.html', context)


# --- Flujo de auto-servicio de empleado ---
@login_required
def mis_vacaciones(request):
    empleado = get_object_or_404(Empleado, user=request.user)
    solicitudes = Vacacion.objects.filter(empleado=empleado).order_by('-fecha_solicitud')
    puede_normal = empleado.antiguedad_anos >= 1
    return render(request, 'empleados/mis_vacaciones.html', {
        'empleado': empleado,
        'solicitudes': solicitudes,
        'puede_normal': puede_normal,
    })


@login_required
def solicitar_vacaciones(request):
    empleado = get_object_or_404(Empleado, user=request.user)
    if request.method == 'POST':
        form = SolicitudVacacionForm(request.POST)
        if form.is_valid():
            vac = form.save(commit=False)
            vac.empleado = empleado
            vac.etapa = 'JEF' if empleado.supervisor else 'RH'
            vac.save()
            return redirect('mis_vacaciones')
    else:
        form = SolicitudVacacionForm()
    return render(request, 'empleados/solicitar_vacaciones.html', {
        'form': form,
        'empleado': empleado,
    })


# --- Aprobación por Jefe Directo ---
@login_required
def aprobar_jefe(request, vacacion_id):
    vac = get_object_or_404(Vacacion, id=vacacion_id)
    # Solo el supervisor asignado puede aprobar
    empleado_actual = get_object_or_404(Empleado, user=request.user)
    if vac.empleado.supervisor_id != empleado_actual.id:
        return redirect('index')
    if request.method == 'POST':
        form = AprobacionJefeForm(request.POST)
        if form.is_valid():
            vac.marcar_aprobacion_jefe(form.cleaned_data['aprobar'], form.cleaned_data.get('comentario') or '')
            return redirect('vacaciones')
    else:
        form = AprobacionJefeForm(initial={'aprobar': True})
    return render(request, 'empleados/aprobar_jefe.html', {'vacacion': vac, 'form': form})


# --- Aprobación RH ---
@login_required
@permission_required('empleados.change_vacacion', raise_exception=True)
def aprobar_rh(request, vacacion_id):
    vac = get_object_or_404(Vacacion, id=vacacion_id)
    if request.method == 'POST':
        form = AprobacionRHForm(request.POST)
        if form.is_valid():
            vac.marcar_aprobacion_rh(form.cleaned_data['aprobar'], form.cleaned_data.get('comentario') or '')
            return redirect('vacaciones')
    else:
        form = AprobacionRHForm(initial={'aprobar': True})
    return render(request, 'empleados/aprobar_rh.html', {'vacacion': vac, 'form': form})


# --- Vistas para Jefes de Área ---
@login_required
def panel_jefe(request):
    """Panel principal para jefes de área"""
    try:
        empleado_actual = get_object_or_404(Empleado, user=request.user)
    except:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('index')
    
    # Obtener empleados bajo su supervisión
    empleados_supervisados = Empleado.objects.filter(supervisor=empleado_actual, activo=True)
    
    # Solicitudes pendientes de aprobación
    solicitudes_pendientes = Vacacion.objects.filter(
        empleado__supervisor=empleado_actual,
        etapa='JEF',
        estado='P'
    ).order_by('-fecha_solicitud')
    
    # Estadísticas
    total_empleados = empleados_supervisados.count()
    solicitudes_pendientes_count = solicitudes_pendientes.count()
    
    # Próximas vacaciones aprobadas de sus empleados
    proximas_vacaciones = Vacacion.objects.filter(
        empleado__supervisor=empleado_actual,
        estado='A',
        fecha_inicio__gte=date.today()
    ).order_by('fecha_inicio')[:5]
    
    context = {
        'empleado_actual': empleado_actual,
        'empleados_supervisados': empleados_supervisados,
        'solicitudes_pendientes': solicitudes_pendientes,
        'total_empleados': total_empleados,
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'proximas_vacaciones': proximas_vacaciones,
    }
    
    return render(request, 'empleados/panel_jefe.html', context)


@login_required
def solicitudes_jefe(request):
    """Lista de solicitudes para aprobación del jefe"""
    try:
        empleado_actual = get_object_or_404(Empleado, user=request.user)
    except:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('index')
    
    # Filtros
    estado = request.GET.get('estado', 'P')
    busqueda = request.GET.get('busqueda')
    
    solicitudes = Vacacion.objects.filter(
        empleado__supervisor=empleado_actual,
        etapa='JEF'
    )
    
    if estado:
        solicitudes = solicitudes.filter(estado=estado)
    
    if busqueda:
        solicitudes = solicitudes.filter(
            Q(empleado__nombre__icontains=busqueda) |
            Q(empleado__apellido_paterno__icontains=busqueda) |
            Q(empleado__apellido_materno__icontains=busqueda)
        )
    
    solicitudes = solicitudes.order_by('-fecha_solicitud')
    
    context = {
        'solicitudes': solicitudes,
        'estado_actual': estado,
        'busqueda_actual': busqueda,
    }
    
    return render(request, 'empleados/solicitudes_jefe.html', context)


# --- Gestión de Usuarios y Roles ---
@login_required
@permission_required('auth.add_user', raise_exception=True)
def gestion_usuarios(request):
    """Panel de gestión de usuarios y roles"""
    usuarios = User.objects.all().select_related('empleado')
    grupos = Group.objects.all()
    
    # Filtros
    grupo_id = request.GET.get('grupo')
    busqueda = request.GET.get('busqueda')
    
    if grupo_id:
        usuarios = usuarios.filter(groups__id=grupo_id)
    
    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )
    
    context = {
        'usuarios': usuarios,
        'grupos': grupos,
        'grupo_actual': int(grupo_id) if grupo_id else None,
        'busqueda_actual': busqueda,
    }
    
    return render(request, 'empleados/gestion_usuarios.html', context)


@login_required
@permission_required('auth.add_user', raise_exception=True)
def crear_usuario(request):
    """Crear nuevo usuario con rol"""
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Asignar grupo según el rol seleccionado
            rol = form.cleaned_data['rol']
            if rol:
                grupo = Group.objects.get(name=rol)
                user.groups.add(grupo)
            
            # Crear perfil de empleado si se proporciona información
            if form.cleaned_data.get('crear_empleado'):
                empleado = Empleado.objects.create(
                    user=user,
                    numero_empleado=form.cleaned_data['numero_empleado'],
                    nombre=form.cleaned_data['nombre'],
                    apellido_paterno=form.cleaned_data['apellido_paterno'],
                    apellido_materno=form.cleaned_data['apellido_materno'],
                    departamento=form.cleaned_data['departamento'],
                    puesto=form.cleaned_data['puesto'],
                    fecha_ingreso=form.cleaned_data['fecha_ingreso'],
                    salario=form.cleaned_data['salario'],
                    supervisor=form.cleaned_data.get('supervisor'),
                    email=user.email,
                )
            
            messages.success(request, f'Usuario {user.username} creado exitosamente.')
            return redirect('gestion_usuarios')
    else:
        form = CrearUsuarioForm()
    
    return render(request, 'empleados/crear_usuario.html', {'form': form})


@login_required
@permission_required('auth.change_user', raise_exception=True)
def asignar_rol(request, user_id):
    """Asignar o cambiar rol de usuario"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        rol = request.POST.get('rol')
        if rol:
            # Limpiar grupos existentes
            user.groups.clear()
            # Asignar nuevo grupo
            grupo = Group.objects.get(name=rol)
            user.groups.add(grupo)
            messages.success(request, f'Rol asignado exitosamente a {user.username}.')
        else:
            user.groups.clear()
            messages.success(request, f'Roles removidos de {user.username}.')
        
        return redirect('gestion_usuarios')
    
    grupos_actuales = user.groups.all()
    todos_grupos = Group.objects.all()
    
    context = {
        'user': user,
        'grupos_actuales': grupos_actuales,
        'todos_grupos': todos_grupos,
    }
    
    return render(request, 'empleados/asignar_rol.html', context)


# --- API para validaciones AJAX ---
@login_required
def validar_antiguedad(request):
    """Validar si empleado puede solicitar vacaciones normales"""
    empleado_id = request.GET.get('empleado_id')
    try:
        empleado = Empleado.objects.get(id=empleado_id)
        puede_normal = empleado.antiguedad_anos >= 1
        return JsonResponse({
            'puede_normal': puede_normal,
            'antiguedad': empleado.antiguedad_anos,
            'dias_disponibles': empleado.dias_vacaciones_disponibles
        })
    except Empleado.DoesNotExist:
        return JsonResponse({'error': 'Empleado no encontrado'}, status=404)
