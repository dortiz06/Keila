from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import Perfil, Departamento, SolicitudVacaciones, ConfiguracionSistema, Ticket, Equipo, AsignacionEquipo
from .forms import (
    UsuarioConPerfilForm, SolicitudVacacionesForm, 
    AprobacionJefeForm, AprobacionRHForm, EditarPerfilForm, ConfigurarDepartamentoForm
)
from datetime import date, timedelta


def get_user_profile(user):
    """Obtener perfil del usuario actual"""
    try:
        return user.perfil
    except Perfil.DoesNotExist:
        return None


@login_required
def dashboard(request):
    """Dashboard principal redirigido según tipo de perfil"""
    perfil = get_user_profile(request.user)
    
    if not perfil:
        messages.error(request, 'No tienes un perfil asignado. Contacta al administrador.')
        return redirect('empleados:logout')
    
    # Redirigir según tipo de perfil
    if perfil.es_admin():
        return redirect('empleados:admin_dashboard')
    elif perfil.es_rh():
        return redirect('empleados:rh_dashboard')
    elif perfil.es_jefe_area():
        return redirect('empleados:jefe_dashboard')
    elif perfil.es_sistemas():
        return redirect('empleados:sistemas_dashboard')
    else:
        return redirect('empleados:empleado_dashboard')


@login_required
def admin_dashboard(request):
    """Dashboard para administradores con vista completa del sistema"""
    perfil = get_user_profile(request.user)
    if not perfil or not perfil.es_admin():
        raise PermissionDenied
    
    # === ESTADÍSTICAS DE EMPLEADOS Y DEPARTAMENTOS ===
    total_empleados = Perfil.objects.filter(activo=True).count()
    total_departamentos = Departamento.objects.filter(activo=True).count()
    empleados_por_tipo = {
        'empleados': Perfil.objects.filter(tipo_perfil='EMPLEADO', activo=True).count(),
        'jefes': Perfil.objects.filter(tipo_perfil='JEFE_AREA', activo=True).count(),
        'rh': Perfil.objects.filter(tipo_perfil='RH', activo=True).count(),
        'sistemas': Perfil.objects.filter(tipo_perfil='SISTEMAS', activo=True).count(),
    }
    
    # === ESTADÍSTICAS DE VACACIONES ===
    solicitudes_pendientes_jefe = SolicitudVacaciones.objects.filter(estado='PENDIENTE_JEFE').count()
    solicitudes_pendientes_rh = SolicitudVacaciones.objects.filter(estado='PENDIENTE_RH').count()
    solicitudes_aprobadas_mes = SolicitudVacaciones.objects.filter(
        estado='APROBADO_RH',
        fecha_aprobacion_rh__month=timezone.now().month
    ).count()
    solicitudes_rechazadas_mes = SolicitudVacaciones.objects.filter(
        estado__in=['RECHAZADO_JEFE', 'RECHAZADO_RH'],
        fecha_solicitud__month=timezone.now().month
    ).count()
    
    # === ESTADÍSTICAS DE TICKETS IT ===
    tickets_pendientes = Ticket.objects.filter(estado='PENDIENTE').count()
    tickets_en_proceso = Ticket.objects.filter(estado='EN_PROCESO').count()
    tickets_resueltos_hoy = Ticket.objects.filter(
        estado='RESUELTO',
        fecha_resolucion__date=timezone.now().date()
    ).count()
    tickets_cancelados_hoy = Ticket.objects.filter(
        estado='CANCELADO',
        fecha_actualizacion__date=timezone.now().date()
    ).count()
    
    # === ESTADÍSTICAS DE EQUIPOS ===
    equipos_disponibles = Equipo.objects.filter(estado='DISPONIBLE').count()
    equipos_asignados = Equipo.objects.filter(estado='ASIGNADO').count()
    equipos_en_reparacion = Equipo.objects.filter(estado='EN_REPARACION').count()
    equipos_baja = Equipo.objects.filter(estado='BAJA').count()
    total_equipos = Equipo.objects.count()
    
    # === SOLICITUDES RECIENTES DE VACACIONES ===
    solicitudes_recientes = SolicitudVacaciones.objects.filter(
        estado__in=['PENDIENTE_JEFE', 'PENDIENTE_RH']
    ).select_related('empleado', 'empleado__departamento').order_by('-fecha_solicitud')[:8]
    
    # === TICKETS RECIENTES ===
    tickets_recientes = Ticket.objects.all().select_related('empleado', 'asignado_a').order_by('-fecha_creacion')[:8]
    
    # === EQUIPOS RECIÉN ASIGNADOS ===
    asignaciones_recientes = AsignacionEquipo.objects.filter(
        fecha_devolucion__isnull=True
    ).select_related('equipo', 'equipo__categoria', 'empleado').order_by('-fecha_asignacion')[:5]
    
    context = {
        'perfil': perfil,
        'stats': {
            'total_empleados': total_empleados,
            'total_departamentos': total_departamentos,
            'empleados_por_tipo': empleados_por_tipo,
            'solicitudes_pendientes_jefe': solicitudes_pendientes_jefe,
            'solicitudes_pendientes_rh': solicitudes_pendientes_rh,
            'solicitudes_aprobadas_mes': solicitudes_aprobadas_mes,
            'solicitudes_rechazadas_mes': solicitudes_rechazadas_mes,
            'tickets_pendientes': tickets_pendientes,
            'tickets_en_proceso': tickets_en_proceso,
            'tickets_resueltos_hoy': tickets_resueltos_hoy,
            'tickets_cancelados_hoy': tickets_cancelados_hoy,
            'equipos_disponibles': equipos_disponibles,
            'equipos_asignados': equipos_asignados,
            'equipos_en_reparacion': equipos_en_reparacion,
            'equipos_baja': equipos_baja,
            'total_equipos': total_equipos,
        },
        'solicitudes_recientes': solicitudes_recientes,
        'tickets_recientes': tickets_recientes,
        'asignaciones_recientes': asignaciones_recientes,
    }
    return render(request, 'empleados/admin/dashboard.html', context)

@login_required
def rh_dashboard(request):
    """Dashboard para Recursos Humanos"""
    perfil = get_user_profile(request.user)
    if not perfil or not perfil.es_rh():
        raise PermissionDenied
    
    # Solicitudes pendientes de RH
    solicitudes_pendientes = SolicitudVacaciones.objects.filter(
        estado='PENDIENTE_RH'
    ).order_by('-fecha_solicitud')
    
    # Estadísticas
    stats = {
        'solicitudes_pendientes': solicitudes_pendientes.count(),
        'aprobadas_este_mes': SolicitudVacaciones.objects.filter(
            estado='APROBADO_RH',
            fecha_aprobacion_rh__month=timezone.now().month
        ).count(),
        'rechazadas_este_mes': SolicitudVacaciones.objects.filter(
            estado='RECHAZADO_RH',
            fecha_aprobacion_rh__month=timezone.now().month
        ).count(),
    }
    
    context = {
        'solicitudes_pendientes': solicitudes_pendientes,
        'stats': stats,
        'perfil': perfil,
    }
    return render(request, 'empleados/rh/dashboard.html', context)


@login_required
def jefe_dashboard(request):
    """Dashboard para Jefes de Área"""
    perfil = get_user_profile(request.user)
    if not perfil or not perfil.es_jefe_area():
        raise PermissionDenied
    
    # Solicitudes de todos los empleados (jefes pueden gestionar cualquier departamento)
    solicitudes_pendientes = SolicitudVacaciones.objects.filter(
        estado='PENDIENTE_JEFE'
    ).order_by('-fecha_solicitud')
    
    # Estadísticas generales (jefes pueden ver estadísticas de todos los departamentos)
    empleados_departamento = Perfil.objects.filter(
        departamento=perfil.departamento,
        activo=True
    )
    
    stats = {
        'empleados_departamento': empleados_departamento.count(),
        'solicitudes_pendientes': solicitudes_pendientes.count(),
        'aprobadas_este_mes': SolicitudVacaciones.objects.filter(
            estado='APROBADO_JEFE',
            fecha_aprobacion_jefe__month=timezone.now().month
        ).count(),
    }
    
    context = {
        'solicitudes_pendientes': solicitudes_pendientes,
        'stats': stats,
        'perfil': perfil,
        'empleados_departamento': empleados_departamento,
    }
    return render(request, 'empleados/jefe/dashboard.html', context)


@login_required
def empleado_dashboard(request):
    """Dashboard para Empleados y personal de sistemas"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_empleado() or perfil.es_sistemas()):
        raise PermissionDenied
    
    # Solicitudes del empleado
    solicitudes = SolicitudVacaciones.objects.filter(
        empleado=perfil
    ).order_by('-fecha_solicitud')
    
    # Equipos asignados
    equipos_asignados = AsignacionEquipo.objects.filter(
        empleado=perfil,
        fecha_devolucion__isnull=True
    ).select_related('equipo', 'equipo__categoria')[:5]
    
    # Tickets del empleado (sin slice para estadísticas)
    tickets_empleado = Ticket.objects.filter(empleado=perfil)
    
    # Tickets recientes (con slice para mostrar solo 5)
    tickets_recientes = tickets_empleado.order_by('-fecha_creacion')[:5]
    
    # Estadísticas personales
    stats = {
        'dias_disponibles': perfil.dias_vacaciones_disponibles,
        'dias_usados': perfil.dias_vacaciones_usados,
        'solicitudes_pendientes': solicitudes.filter(
            estado__in=['PENDIENTE_JEFE', 'PENDIENTE_RH']
        ).count(),
        'solicitudes_aprobadas': solicitudes.filter(estado='APROBADO_RH').count(),
        'equipos_asignados': equipos_asignados.count(),
        'tickets_pendientes': tickets_empleado.filter(estado__in=['PENDIENTE', 'EN_PROCESO']).count(),
    }
    
    context = {
        'solicitudes': solicitudes,
        'equipos_asignados': equipos_asignados,
        'tickets_recientes': tickets_recientes,
        'stats': stats,
        'perfil': perfil,
    }
    return render(request, 'empleados/empleado/dashboard.html', context)


# === GESTIÓN DE USUARIOS ===

@login_required
def gestion_usuarios(request):
    """Gestión de usuarios - Solo RH y Admin"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    usuarios = Perfil.objects.filter(activo=True)
    
    # Filtros
    tipo_perfil = request.GET.get('tipo_perfil')
    departamento_id = request.GET.get('departamento')
    busqueda = request.GET.get('busqueda')
    
    if tipo_perfil:
        usuarios = usuarios.filter(tipo_perfil=tipo_perfil)
    
    if departamento_id:
        usuarios = usuarios.filter(departamento_id=departamento_id)
    
    if busqueda:
        usuarios = usuarios.filter(
            Q(usuario__username__icontains=busqueda) |
            Q(usuario__first_name__icontains=busqueda) |
            Q(usuario__last_name__icontains=busqueda) |
            Q(numero_empleado__icontains=busqueda)
        )
    
    departamentos = Departamento.objects.filter(activo=True)
    
    context = {
        'usuarios': usuarios,
        'departamentos': departamentos,
        'tipo_actual': tipo_perfil,
        'departamento_actual': departamento_id,
        'busqueda_actual': busqueda,
        'perfil': perfil,
    }
    return render(request, 'empleados/rh/gestion_usuarios.html', context)


@login_required
def crear_usuario(request):
    """Crear nuevo usuario con perfil"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    if request.method == 'POST':
        form = UsuarioConPerfilForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario {user.username} creado exitosamente.')
            return redirect('empleados:gestion_usuarios')
    else:
        form = UsuarioConPerfilForm()
    
    context = {
        'form': form,
        'perfil': perfil,
    }
    return render(request, 'empleados/rh/crear_usuario.html', context)


@login_required
def editar_perfil(request, perfil_id):
    """Editar perfil de usuario"""
    perfil = get_user_profile(request.user)
    perfil_editado = get_object_or_404(Perfil, id=perfil_id)
    
    # Verificar permisos
    if not (perfil.es_rh() or perfil.es_admin() or perfil == perfil_editado):
        raise PermissionDenied
    
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=perfil_editado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('empleados:gestion_usuarios')
    else:
        form = EditarPerfilForm(instance=perfil_editado)
    
    context = {
        'form': form,
        'perfil_editado': perfil_editado,
        'perfil': perfil,
    }
    return render(request, 'empleados/rh/editar_perfil.html', context)


# === GESTIÓN DE VACACIONES ===

@login_required
def solicitar_vacaciones(request):
    """Solicitar vacaciones - Empleados, RH y personal de sistemas"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_empleado() or perfil.es_sistemas() or perfil.es_rh()):
        raise PermissionDenied
    
    if request.method == 'POST':
        form = SolicitudVacacionesForm(request.POST, empleado=perfil)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.empleado = perfil
            solicitud.save()
            messages.success(request, 'Solicitud de vacaciones enviada exitosamente.')
            # Redirigir al panel correspondiente del usuario
            return redirect('empleados:dashboard')
    else:
        form = SolicitudVacacionesForm(empleado=perfil)
    
    # Obtener solicitudes recientes del empleado
    solicitudes_recientes = SolicitudVacaciones.objects.filter(
        empleado=perfil
    ).order_by('-fecha_solicitud')[:5]
    
    # Verificar si puede solicitar vacaciones extraordinarias
    puede_solicitar_extraordinarias = (
        perfil.dias_vacaciones_disponibles >= 1 or 
        perfil.dias_vacaciones_extraordinarios_disponibles >= 1
    )
    
    # Verificar si puede solicitar vacaciones normales (antigüedad >= 1 año y días disponibles)
    puede_solicitar_normales = (
        perfil.antiguedad_anos >= 1 and 
        perfil.dias_vacaciones_disponibles > 0
    )
    
    context = {
        'form': form,
        'perfil': perfil,
        'solicitudes_recientes': solicitudes_recientes,
        'puede_solicitar_extraordinarias': puede_solicitar_extraordinarias,
        'puede_solicitar_normales': puede_solicitar_normales,
        'dias_extraordinarios_disponibles': perfil.dias_vacaciones_extraordinarios_disponibles,
    }
    return render(request, 'empleados/empleado/solicitar_vacaciones.html', context)


@login_required
def aprobar_jefe(request, solicitud_id):
    """Aprobar/rechazar solicitud por jefe de área"""
    perfil = get_user_profile(request.user)
    if not perfil or not perfil.es_jefe_area():
        raise PermissionDenied
    
    solicitud = get_object_or_404(SolicitudVacaciones, id=solicitud_id)
    
    # Los jefes pueden aprobar solicitudes de cualquier departamento
    
    if request.method == 'POST':
        form = AprobacionJefeForm(request.POST, solicitud=solicitud)
        if form.is_valid():
            accion = form.cleaned_data['accion']
            comentario = form.cleaned_data['comentario']
            
            if accion == 'aprobar':
                if solicitud.aprobar_por_jefe(perfil, comentario):
                    messages.success(request, 'Solicitud aprobada exitosamente.')
                else:
                    messages.error(request, 'No se pudo aprobar la solicitud.')
            else:
                if solicitud.rechazar_por_jefe(perfil, comentario):
                    messages.success(request, 'Solicitud rechazada.')
                else:
                    messages.error(request, 'No se pudo rechazar la solicitud.')
            
            return redirect('empleados:jefe_dashboard')
    else:
        form = AprobacionJefeForm(solicitud=solicitud)
    
    context = {
        'form': form,
        'solicitud': solicitud,
        'perfil': perfil,
    }
    return render(request, 'empleados/jefe/aprobar_solicitud.html', context)


@login_required
def solicitudes_jefe(request):
    """Listar todas las solicitudes de vacaciones para jefe de área"""
    perfil = get_user_profile(request.user)
    if not perfil or not perfil.es_jefe_area():
        raise PermissionDenied
    
    # Obtener todas las solicitudes (jefes pueden ver todas)
    solicitudes = SolicitudVacaciones.objects.all().select_related(
        'empleado', 'empleado__departamento'
    ).order_by('-fecha_solicitud')
    
    # Filtros
    estado_actual = request.GET.get('estado', '')
    busqueda_actual = request.GET.get('busqueda', '')
    
    # Filtrar por estado
    if estado_actual == 'P':
        solicitudes = solicitudes.filter(estado='PENDIENTE_JEFE')
    elif estado_actual == 'A':
        solicitudes = solicitudes.filter(estado__in=['APROBADO_JEFE', 'APROBADO_RH'])
    elif estado_actual == 'R':
        solicitudes = solicitudes.filter(estado__in=['RECHAZADO_JEFE', 'RECHAZADO_RH'])
    
    # Filtrar por búsqueda de empleado
    if busqueda_actual:
        solicitudes = solicitudes.filter(
            empleado__user__first_name__icontains=busqueda_actual
        ) | solicitudes.filter(
            empleado__user__last_name__icontains=busqueda_actual
        ) | solicitudes.filter(
            empleado__nombre_completo__icontains=busqueda_actual
        )
    
    context = {
        'solicitudes': solicitudes,
        'estado_actual': estado_actual,
        'busqueda_actual': busqueda_actual,
        'perfil': perfil,
    }
    return render(request, 'empleados/solicitudes_jefe.html', context)


@login_required
def solicitudes_rh(request):
    """Listar todas las solicitudes de vacaciones para RH"""
    perfil = get_user_profile(request.user)
    if not perfil or not perfil.es_rh():
        raise PermissionDenied
    
    # Obtener todas las solicitudes que han sido aprobadas por jefe y están pendientes de RH
    solicitudes = SolicitudVacaciones.objects.filter(
        estado='PENDIENTE_RH'
    ).select_related(
        'empleado', 'empleado__departamento'
    ).order_by('-fecha_solicitud')
    
    # Filtros
    estado_actual = request.GET.get('estado', '')
    busqueda_actual = request.GET.get('busqueda', '')
    
    # Filtrar por estado (para ver también otras solicitudes si se desea)
    if estado_actual == 'P':
        solicitudes = solicitudes.filter(estado='PENDIENTE_RH')
    elif estado_actual == 'A':
        solicitudes = SolicitudVacaciones.objects.filter(estado='APROBADO_RH').select_related(
            'empleado', 'empleado__departamento'
        ).order_by('-fecha_solicitud')
    elif estado_actual == 'R':
        solicitudes = SolicitudVacaciones.objects.filter(estado='RECHAZADO_RH').select_related(
            'empleado', 'empleado__departamento'
        ).order_by('-fecha_solicitud')
    elif estado_actual == 'TODAS':
        solicitudes = SolicitudVacaciones.objects.all().select_related(
            'empleado', 'empleado__departamento'
        ).order_by('-fecha_solicitud')
    
    # Filtrar por búsqueda de empleado
    if busqueda_actual:
        solicitudes = solicitudes.filter(
            empleado__user__first_name__icontains=busqueda_actual
        ) | solicitudes.filter(
            empleado__user__last_name__icontains=busqueda_actual
        ) | solicitudes.filter(
            empleado__nombre_completo__icontains=busqueda_actual
        )
    
    context = {
        'solicitudes': solicitudes,
        'estado_actual': estado_actual,
        'busqueda_actual': busqueda_actual,
        'perfil': perfil,
    }
    return render(request, 'empleados/rh/solicitudes_rh.html', context)


@login_required
def aprobar_rh(request, solicitud_id):
    """Aprobar/rechazar solicitud por RH"""
    perfil = get_user_profile(request.user)
    if not perfil or not perfil.es_rh():
        raise PermissionDenied
    
    solicitud = get_object_or_404(SolicitudVacaciones, id=solicitud_id)
    
    if request.method == 'POST':
        form = AprobacionRHForm(request.POST, solicitud=solicitud)
        if form.is_valid():
            accion = form.cleaned_data.get('accion')
            comentario = form.cleaned_data.get('comentario', '')
            
            if accion == 'aprobar':
                if solicitud.aprobar_por_rh(perfil, comentario):
                    messages.success(request, 'Solicitud aprobada exitosamente.')
                else:
                    messages.error(request, 'No se pudo aprobar la solicitud. La solicitud puede que ya haya sido procesada o no esté en estado PENDIENTE_RH.')
            elif accion == 'rechazar':
                if solicitud.rechazar_por_rh(perfil, comentario):
                    messages.success(request, 'Solicitud rechazada.')
                else:
                    messages.error(request, 'No se pudo rechazar la solicitud. La solicitud puede que ya haya sido procesada o no esté en estado PENDIENTE_RH.')
            else:
                messages.error(request, 'Acción no válida. Por favor selecciona aprobar o rechazar.')
            
            return redirect('empleados:rh_dashboard')
        else:
            # Si el formulario no es válido, mostrar errores
            messages.error(request, 'Por favor, completa todos los campos requeridos correctamente.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = AprobacionRHForm(solicitud=solicitud)
    
    context = {
        'form': form,
        'solicitud': solicitud,
        'perfil': perfil,
    }
    return render(request, 'empleados/rh/aprobar_solicitud.html', context)


# === GESTIÓN DE DEPARTAMENTOS ===

@login_required
def gestion_departamentos(request):
    """Gestión de departamentos - Solo RH y Admin"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    departamentos = Departamento.objects.filter(activo=True)
    
    context = {
        'departamentos': departamentos,
        'perfil': perfil,
    }
    return render(request, 'empleados/rh/gestion_departamentos.html', context)


@login_required
def crear_departamento(request):
    """Crear nuevo departamento"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    if request.method == 'POST':
        form = ConfigurarDepartamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Departamento creado exitosamente.')
            return redirect('empleados:gestion_departamentos')
    else:
        form = ConfigurarDepartamentoForm()
    
    context = {
        'form': form,
        'perfil': perfil,
    }
    return render(request, 'empleados/rh/crear_departamento.html', context)


# === API ENDPOINTS ===

@login_required
def validar_antiguedad(request):
    """API para validar antigüedad de empleado"""
    perfil = get_user_profile(request.user)
    if not perfil:
        return JsonResponse({'error': 'Perfil no encontrado'}, status=400)
    
    antiguedad = perfil.antiguedad_anos
    puede_vacaciones_normales = antiguedad >= 1
    
    return JsonResponse({
        'antiguedad_anos': antiguedad,
        'puede_vacaciones_normales': puede_vacaciones_normales,
        'dias_disponibles': perfil.dias_vacaciones_disponibles,
    })


# ===================================================================
# VISTAS DE TICKETS Y EQUIPOS
# ===================================================================

@login_required
def mis_tickets(request):
    """Vista para ver los tickets del empleado"""
    perfil = get_object_or_404(Perfil, usuario=request.user)
    tickets = Ticket.objects.filter(empleado=perfil).order_by('-fecha_creacion')
    
    context = {
        'perfil': perfil,
        'tickets': tickets,
    }
    return render(request, 'empleados/tickets/mis_tickets.html', context)


@login_required
def crear_ticket(request):
    """Vista para crear un nuevo ticket"""
    from .forms import TicketForm
    perfil = get_object_or_404(Perfil, usuario=request.user)
    
    if request.method == 'POST':
        form = TicketForm(request.POST, empleado=perfil)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.empleado = perfil
            ticket.save()
            messages.success(request, f'Ticket {ticket.codigo} creado exitosamente.')
            # Redirección basada en el tipo de perfil
            if perfil.es_sistemas():
                return redirect('empleados:sistemas_dashboard')
            elif perfil.es_admin():
                return redirect('empleados:admin_dashboard')
            elif perfil.es_rh():
                return redirect('empleados:rh_dashboard')
            elif perfil.es_jefe_area():
                return redirect('empleados:jefe_dashboard')
            else:
                return redirect('empleados:mis_tickets')
    else:
        form = TicketForm(empleado=perfil)
    
    context = {
        'perfil': perfil,
        'form': form,
    }
    return render(request, 'empleados/tickets/crear_ticket.html', context)


@login_required
def detalle_ticket(request, ticket_id):
    """Vista para ver el detalle de un ticket"""
    perfil = get_object_or_404(Perfil, usuario=request.user)
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Verificar permisos
    if perfil.es_sistemas() or perfil.es_admin() or perfil.es_rh() or ticket.empleado == perfil:
        context = {
            'perfil': perfil,
            'ticket': ticket,
        }
        return render(request, 'empleados/tickets/detalle_ticket.html', context)
    else:
        messages.error(request, 'No tienes permiso para ver este ticket.')
        return redirect('empleados:empleado_dashboard')


@login_required
def mis_equipos(request):
    """Vista para ver los equipos asignados al empleado"""
    perfil = get_object_or_404(Perfil, usuario=request.user)
    asignaciones_activas = AsignacionEquipo.objects.filter(
        empleado=perfil,
        fecha_devolucion__isnull=True
    ).select_related('equipo', 'equipo__categoria')
    
    historial_asignaciones = AsignacionEquipo.objects.filter(
        empleado=perfil,
        fecha_devolucion__isnull=False
    ).select_related('equipo', 'equipo__categoria').order_by('-fecha_devolucion')[:10]
    
    context = {
        'perfil': perfil,
        'asignaciones_activas': asignaciones_activas,
        'historial_asignaciones': historial_asignaciones,
    }
    return render(request, 'empleados/equipos/mis_equipos.html', context)


# === VISTAS DE SISTEMAS/IT ===

@login_required
def dashboard_sistemas(request):
    """Dashboard para el área de Sistemas/IT"""
    perfil = get_object_or_404(Perfil, usuario=request.user)
    
    # Verificar permisos
    if not (perfil.es_sistemas() or perfil.es_admin()):
        messages.error(request, 'No tienes permiso para acceder a esta sección.')
        return redirect('empleados:empleado_dashboard')
    
    # Estadísticas de tickets
    tickets_pendientes = Ticket.objects.filter(estado='PENDIENTE').count()
    tickets_en_proceso = Ticket.objects.filter(estado='EN_PROCESO').count()
    tickets_resueltos_hoy = Ticket.objects.filter(
        estado='RESUELTO',
        fecha_resolucion__date=timezone.now().date()
    ).count()
    
    # Tickets recientes - Todos los tickets
    tickets_recientes = Ticket.objects.all().order_by('-fecha_creacion')[:10]
    
    # Estadísticas de equipos
    equipos_disponibles = Equipo.objects.filter(estado='DISPONIBLE').count()
    equipos_asignados = Equipo.objects.filter(estado='ASIGNADO').count()
    equipos_en_reparacion = Equipo.objects.filter(estado='EN_REPARACION').count()
    
    context = {
        'perfil': perfil,
        'tickets_pendientes': tickets_pendientes,
        'tickets_en_proceso': tickets_en_proceso,
        'tickets_resueltos_hoy': tickets_resueltos_hoy,
        'tickets_recientes': tickets_recientes,
        'equipos_disponibles': equipos_disponibles,
        'equipos_asignados': equipos_asignados,
        'equipos_en_reparacion': equipos_en_reparacion,
    }
    return render(request, 'empleados/sistemas/dashboard.html', context)


@login_required
def gestionar_tickets(request):
    """Vista para gestionar tickets (Sistemas/IT)"""
    from .forms import TicketResolucionForm
    perfil = get_object_or_404(Perfil, usuario=request.user)
    
    # Verificar permisos
    if not (perfil.es_sistemas() or perfil.es_admin()):
        messages.error(request, 'No tienes permiso para acceder a esta sección.')
        return redirect('empleados:empleado_dashboard')
    
    # Filtros
    estado_filtro = request.GET.get('estado', 'TODOS')
    
    tickets = Ticket.objects.all().order_by('-fecha_creacion')
    if estado_filtro != 'TODOS':
        tickets = tickets.filter(estado=estado_filtro)
    
    context = {
        'perfil': perfil,
        'tickets': tickets,
        'estado_filtro': estado_filtro,
    }
    return render(request, 'empleados/sistemas/gestionar_tickets.html', context)


@login_required
def asignar_ticket(request, ticket_id):
    """Asignar un ticket al usuario de sistemas actual"""
    perfil = get_object_or_404(Perfil, usuario=request.user)
    
    # Verificar permisos
    if not (perfil.es_sistemas() or perfil.es_admin()):
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('empleados:empleado_dashboard')
    
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.asignado_a = perfil
    ticket.estado = 'EN_PROCESO'
    ticket.fecha_asignacion = timezone.now()
    ticket.save()
    
    messages.success(request, f'Ticket {ticket.codigo} asignado correctamente.')
    return redirect('empleados:gestionar_tickets')


@login_required
def resolver_ticket(request, ticket_id):
    """Marcar un ticket como resuelto"""
    from .forms import TicketResolucionForm
    perfil = get_object_or_404(Perfil, usuario=request.user)
    
    # Verificar permisos
    if not (perfil.es_sistemas() or perfil.es_admin()):
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('empleados:empleado_dashboard')
    
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        form = TicketResolucionForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save(commit=False)
            if ticket.estado == 'RESUELTO' and not ticket.fecha_resolucion:
                ticket.fecha_resolucion = timezone.now()
            ticket.save()
            messages.success(request, f'Ticket {ticket.codigo} actualizado correctamente.')
            # Redirección basada en el tipo de perfil
            if perfil.es_sistemas():
                return redirect('empleados:sistemas_dashboard')
            elif perfil.es_admin():
                return redirect('empleados:admin_dashboard')
            elif perfil.es_rh():
                return redirect('empleados:rh_dashboard')
            elif perfil.es_jefe_area():
                return redirect('empleados:jefe_dashboard')
            else:
                return redirect('empleados:gestionar_tickets')
    else:
        form = TicketResolucionForm(instance=ticket)
    
    context = {
        'perfil': perfil,
        'ticket': ticket,
        'form': form,
    }
    return render(request, 'empleados/sistemas/resolver_ticket.html', context)


@login_required
def inventario_equipos(request):
    """Vista para gestionar el inventario de equipos"""
    from .forms import EquipoForm
    perfil = get_object_or_404(Perfil, usuario=request.user)
    
    # Verificar permisos
    if not (perfil.es_sistemas() or perfil.es_admin() or perfil.es_rh()):
        messages.error(request, 'No tienes permiso para acceder a esta sección.')
        return redirect('empleados:empleado_dashboard')
    
    equipos = Equipo.objects.all().select_related('categoria').order_by('-fecha_adquisicion')
    
    # Filtros
    estado_filtro = request.GET.get('estado', 'TODOS')
    if estado_filtro != 'TODOS':
        equipos = equipos.filter(estado=estado_filtro)
    
    context = {
        'perfil': perfil,
        'equipos': equipos,
        'estado_filtro': estado_filtro,
    }
    return render(request, 'empleados/sistemas/inventario.html', context)


@login_required
def agregar_equipo(request):
    """Vista para agregar un nuevo equipo al inventario"""
    from .forms import EquipoForm
    perfil = get_object_or_404(Perfil, usuario=request.user)
    
    # Verificar permisos
    if not (perfil.es_sistemas() or perfil.es_admin()):
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('empleados:empleado_dashboard')
    
    if request.method == 'POST':
        form = EquipoForm(request.POST)
        if form.is_valid():
            equipo = form.save()
            messages.success(request, f'Equipo {equipo.codigo_inventario} agregado exitosamente.')
            # Redirección basada en el tipo de perfil
            if perfil.es_sistemas():
                return redirect('empleados:sistemas_dashboard')
            elif perfil.es_admin():
                return redirect('empleados:admin_dashboard')
            elif perfil.es_rh():
                return redirect('empleados:rh_dashboard')
            elif perfil.es_jefe_area():
                return redirect('empleados:jefe_dashboard')
            else:
                return redirect('empleados:inventario_equipos')
    else:
        form = EquipoForm()
    
    context = {
        'perfil': perfil,
        'form': form,
    }
    return render(request, 'empleados/sistemas/agregar_equipo.html', context)


@login_required
def asignar_equipo(request):
    """Vista para asignar equipos a empleados"""
    from .forms import AsignacionEquipoForm
    perfil = get_object_or_404(Perfil, usuario=request.user)
    
    # Verificar permisos
    if not (perfil.es_sistemas() or perfil.es_admin() or perfil.es_rh()):
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('empleados:empleado_dashboard')
    
    if request.method == 'POST':
        form = AsignacionEquipoForm(request.POST)
        if form.is_valid():
            asignacion = form.save(commit=False)
            asignacion.asignado_por = perfil
            asignacion.fecha_asignacion = timezone.now().date()  # Establecer fecha automáticamente
            asignacion.save()
            
            # Actualizar estado del equipo
            equipo = asignacion.equipo
            equipo.estado = 'ASIGNADO'
            equipo.save()
            
            messages.success(request, f'Equipo {equipo.codigo_inventario} asignado a {asignacion.empleado.nombre_completo}.')
            # Redirección basada en el tipo de perfil
            if perfil.es_sistemas():
                return redirect('empleados:sistemas_dashboard')
            elif perfil.es_admin():
                return redirect('empleados:admin_dashboard')
            elif perfil.es_rh():
                return redirect('empleados:rh_dashboard')
            elif perfil.es_jefe_area():
                return redirect('empleados:jefe_dashboard')
            else:
                return redirect('empleados:inventario_equipos')
    else:
        form = AsignacionEquipoForm()
    
    context = {
        'perfil': perfil,
        'form': form,
    }
    return render(request, 'empleados/sistemas/asignar_equipo.html', context)


@login_required
def devolver_equipo(request, asignacion_id):
    """Vista para registrar la devolución de un equipo"""
    from .forms import DevolucionEquipoForm
    perfil = get_object_or_404(Perfil, usuario=request.user)
    
    # Verificar permisos
    if not (perfil.es_sistemas() or perfil.es_admin() or perfil.es_rh()):
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('empleados:empleado_dashboard')
    
    asignacion = get_object_or_404(AsignacionEquipo, id=asignacion_id)
    
    if request.method == 'POST':
        form = DevolucionEquipoForm(request.POST, instance=asignacion)
        if form.is_valid():
            asignacion = form.save()
            
            # Actualizar estado del equipo
            equipo = asignacion.equipo
            equipo.estado = 'DISPONIBLE'
            equipo.save()
            
            messages.success(request, f'Devolución de equipo {equipo.codigo_inventario} registrada correctamente.')
            # Redirección basada en el tipo de perfil
            if perfil.es_sistemas():
                return redirect('empleados:sistemas_dashboard')
            elif perfil.es_admin():
                return redirect('empleados:admin_dashboard')
            elif perfil.es_rh():
                return redirect('empleados:rh_dashboard')
            elif perfil.es_jefe_area():
                return redirect('empleados:jefe_dashboard')
            else:
                return redirect('empleados:inventario_equipos')
    else:
        form = DevolucionEquipoForm(instance=asignacion)
    
    context = {
        'perfil': perfil,
        'asignacion': asignacion,
        'form': form,
    }
    return render(request, 'empleados/sistemas/devolver_equipo.html', context)


# === VISTAS DE ERROR ===


def error_403(request, exception=None):
    return render(request, 'empleados/errors/403.html', status=403)

def error_404(request, exception=None):
    return render(request, 'empleados/errors/404.html', status=404)

def error_500(request):
    return render(request, 'empleados/errors/500.html', status=500)