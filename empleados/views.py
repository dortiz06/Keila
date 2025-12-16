from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.db import models
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.urls import reverse
from django import forms
from .models import Perfil, Departamento, SolicitudVacaciones, ConfiguracionSistema, Ticket, Equipo, AsignacionEquipo, HistorialVacaciones
from .forms import (
    UsuarioConPerfilForm, SolicitudVacacionesForm, 
    AprobacionJefeForm, AprobacionAdminForm, AprobacionRHForm, EditarPerfilForm, ConfigurarDepartamentoForm
)
from datetime import date, timedelta, datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.conf import settings
import os


def calcular_fecha_presentarse(fecha_fin):
    """
    Calcula la fecha de presentación después de las vacaciones.
    El domingo es día obligatorio de descanso, por lo que:
    - Si las vacaciones terminan en sábado, se presenta el lunes (saltando domingo)
    - Si el día siguiente es domingo, se salta al lunes
    - En cualquier otro caso, se presenta el día siguiente
    """
    # Calcular el día siguiente
    fecha_siguiente = fecha_fin + timedelta(days=1)
    
    # weekday() retorna: 0=Lunes, 1=Martes, 2=Miércoles, 3=Jueves, 4=Viernes, 5=Sábado, 6=Domingo
    dia_semana = fecha_siguiente.weekday()
    
    # Si el día siguiente es domingo (6), saltar al lunes
    if dia_semana == 6:  # Domingo
        # Agregar un día más para llegar al lunes
        fecha_siguiente = fecha_siguiente + timedelta(days=1)
    
    # Si las vacaciones terminan en sábado, el día siguiente es domingo, 
    # pero ya lo manejamos arriba, así que esto está cubierto
    
    return fecha_siguiente


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
    solicitudes_pendientes_admin = SolicitudVacaciones.objects.filter(estado='PENDIENTE_ADMIN').count()
    solicitudes_pendientes_rh = SolicitudVacaciones.objects.filter(estado='PENDIENTE_RH').count()
    solicitudes_aprobadas_mes = SolicitudVacaciones.objects.filter(
        estado='APROBADO_RH',
        fecha_aprobacion_rh__month=timezone.now().month
    ).count()
    solicitudes_rechazadas_mes = SolicitudVacaciones.objects.filter(
        estado__in=['RECHAZADO_JEFE', 'RECHAZADO_ADMIN', 'RECHAZADO_RH'],
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
        estado__in=['PENDIENTE_JEFE', 'PENDIENTE_ADMIN', 'PENDIENTE_RH']
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
            'solicitudes_pendientes_admin': solicitudes_pendientes_admin,
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
    
    # Solicitudes de empleados asignados directamente al jefe como supervisor
    # Excluir las propias solicitudes del jefe (esas van a admin)
    empleados_asignados = Perfil.objects.filter(
        supervisor=perfil,
        activo=True
    )
    solicitudes_pendientes = SolicitudVacaciones.objects.filter(
        estado='PENDIENTE_JEFE',
        empleado__in=empleados_asignados
    ).exclude(empleado=perfil).order_by('-fecha_solicitud')
    
    # Estadísticas de empleados asignados directamente al jefe
    empleados_departamento = empleados_asignados
    
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
    """Dashboard para Empleados (no Sistemas)"""
    perfil = get_user_profile(request.user)
    if not perfil or not perfil.es_empleado():
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
    """Gestión de usuarios - Redirige a lista_empleados (vista unificada)"""
    # Redirigir a la vista unificada de lista de empleados
    return redirect('empleados:lista_empleados')


@login_required
def crear_usuario(request):
    """Crear nuevo usuario con perfil - Solo Sistemas y Admin"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_sistemas() or perfil.es_admin()):
        raise PermissionDenied
    
    if request.method == 'POST':
        form = UsuarioConPerfilForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario {user.username} creado exitosamente.')
            # Redirigir según el origen
            origen = request.POST.get('origen', 'gestion')
            if origen == 'dashboard':
                if perfil.es_sistemas():
                    return redirect('empleados:sistemas_dashboard')
                elif perfil.es_admin():
                    return redirect('empleados:admin_dashboard')
                else:
                    return redirect('empleados:gestion_usuarios')
            else:
                return redirect('empleados:gestion_usuarios')
    else:
        form = UsuarioConPerfilForm()
    
    # Detectar de dónde viene el usuario
    referer = request.META.get('HTTP_REFERER', '')
    viene_del_dashboard = False
    url_volver = 'empleados:gestion_usuarios'
    texto_volver = 'Volver a Gestión'
    
    if referer:
        # Verificar si viene del dashboard
        if '/sistemas/' in referer or '/administrador/' in referer or '/dashboard/' in referer:
            viene_del_dashboard = True
            if perfil.es_sistemas():
                url_volver = 'empleados:sistemas_dashboard'
                texto_volver = 'Volver a Panel Principal'
            elif perfil.es_admin():
                url_volver = 'empleados:admin_dashboard'
                texto_volver = 'Volver a Panel Principal'
    
    context = {
        'form': form,
        'perfil': perfil,
        'viene_del_dashboard': viene_del_dashboard,
        'url_volver': url_volver,
        'texto_volver': texto_volver,
    }
    return render(request, 'empleados/rh/crear_usuario.html', context)


@login_required
def lista_empleados(request):
    """Lista de empleados - Vista de solo lectura con permisos según rol"""
    perfil = get_user_profile(request.user)
    if not perfil:
        raise PermissionDenied
    
    # Empleados normales no pueden ver la lista
    if perfil.es_empleado() and not perfil.es_jefe_area():
        raise PermissionDenied
    
    # Obtener empleados según permisos
    if perfil.es_sistemas() or perfil.es_admin() or perfil.es_rh():
        # Sistemas, Admin, RH: pueden ver todos los empleados
        empleados = Perfil.objects.filter(activo=True)
    elif perfil.es_jefe_area():
        # Jefes de área: solo pueden ver empleados asignados directamente a ellos como supervisor
        empleados = Perfil.objects.filter(
            activo=True,
            supervisor=perfil
        )
    else:
        raise PermissionDenied
    
    # Filtros
    tipo_perfil = request.GET.get('tipo_perfil')
    departamento_id = request.GET.get('departamento')
    busqueda = request.GET.get('busqueda')
    
    if tipo_perfil:
        empleados = empleados.filter(tipo_perfil=tipo_perfil)
    
    if departamento_id:
        empleados = empleados.filter(departamento_id=departamento_id)
    
    if busqueda:
        from django.db.models import Q
        empleados = empleados.filter(
            Q(usuario__username__icontains=busqueda) |
            Q(usuario__first_name__icontains=busqueda) |
            Q(usuario__last_name__icontains=busqueda) |
            Q(numero_empleado__icontains=busqueda)
        )
    
    departamentos = Departamento.objects.filter(activo=True)
    
    # Determinar permisos
    puede_editar = perfil.es_sistemas() or perfil.es_admin()
    puede_crear = perfil.es_sistemas() or perfil.es_admin()  # Solo Sistemas y Admin pueden crear
    es_gestion_completa = perfil.es_sistemas() or perfil.es_admin()  # Para mostrar columnas adicionales
    
    context = {
        'empleados': empleados.order_by('usuario__first_name', 'usuario__last_name'),
        'departamentos': departamentos,
        'tipo_actual': tipo_perfil,
        'departamento_actual': departamento_id,
        'busqueda_actual': busqueda,
        'perfil': perfil,
        'puede_editar': puede_editar,
        'puede_crear': puede_crear,
        'es_gestion_completa': es_gestion_completa,
    }
    return render(request, 'empleados/lista_empleados.html', context)


@login_required
def editar_perfil(request, perfil_id):
    """Editar perfil de usuario - Solo Sistemas y Admin pueden editar"""
    perfil = get_user_profile(request.user)
    perfil_editado = get_object_or_404(Perfil, id=perfil_id)
    
    # Verificar permisos: Solo Sistemas y Admin pueden editar
    if not (perfil.es_sistemas() or perfil.es_admin()):
        raise PermissionDenied
    
    # Determinar si el usuario actual es admin o sistemas (puede editar todos los campos)
    es_admin_editor = perfil.es_admin() or perfil.es_sistemas()
    
    # Detectar de dónde viene el usuario para redirigir correctamente
    referer = request.META.get('HTTP_REFERER', '')
    viene_de_lista = 'empleados/' in referer or 'lista_empleados' in referer
    viene_de_gestion = 'gestion_usuarios' in referer or 'usuarios/' in referer
    
    # Determinar URL de retorno
    if perfil.es_admin() and (viene_de_gestion or not viene_de_lista):
        url_volver = 'empleados:gestion_usuarios'
        texto_volver = 'Volver a Gestión'
    else:
        url_volver = 'empleados:lista_empleados'
        texto_volver = 'Volver a Lista'
    
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=perfil_editado, es_admin=es_admin_editor)
        if form.is_valid():
            perfil_actualizado = form.save(commit=False)
            # Si es admin, actualizar también los campos adicionales
            if es_admin_editor:
                if 'tipo_perfil' in form.cleaned_data:
                    perfil_actualizado.tipo_perfil = form.cleaned_data['tipo_perfil']
                if 'departamento' in form.cleaned_data:
                    perfil_actualizado.departamento = form.cleaned_data['departamento']
                if 'puesto' in form.cleaned_data:
                    perfil_actualizado.puesto = form.cleaned_data['puesto']
                if 'supervisor' in form.cleaned_data:
                    perfil_actualizado.supervisor = form.cleaned_data['supervisor']
                if 'numero_empleado' in form.cleaned_data:
                    perfil_actualizado.numero_empleado = form.cleaned_data['numero_empleado']
                if 'fecha_contratacion' in form.cleaned_data:
                    perfil_actualizado.fecha_contratacion = form.cleaned_data['fecha_contratacion']
                if 'activo' in form.cleaned_data:
                    perfil_actualizado.activo = form.cleaned_data['activo']
            perfil_actualizado.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            # Redirigir según el origen
            return redirect(url_volver)
    else:
        form = EditarPerfilForm(instance=perfil_editado, es_admin=es_admin_editor)
    
    # Obtener departamentos para el dropdown
    departamentos = Departamento.objects.filter(activo=True).order_by('nombre')
    
    context = {
        'form': form,
        'perfil_editado': perfil_editado,
        'perfil': perfil,
        'es_admin_editor': es_admin_editor,
        'departamentos': departamentos,
        'url_volver': url_volver,
        'texto_volver': texto_volver,
    }
    return render(request, 'empleados/rh/editar_perfil.html', context)


# === GESTIÓN DE VACACIONES ===

@login_required
def mis_vacaciones(request):
    """Vista para ver todas las solicitudes de vacaciones del empleado"""
    perfil = get_user_profile(request.user)
    if not perfil:
        raise PermissionDenied
    
    # Obtener todas las solicitudes del empleado
    solicitudes = SolicitudVacaciones.objects.filter(
        empleado=perfil
    ).order_by('-fecha_solicitud')
    
    # Verificar si puede solicitar vacaciones normales
    puede_normal = perfil.antiguedad_anos >= 1
    
    context = {
        'solicitudes': solicitudes,
        'perfil': perfil,
        'puede_normal': puede_normal,
    }
    return render(request, 'empleados/mis_vacaciones.html', context)


@login_required
def solicitar_vacaciones(request):
    """Solicitar vacaciones - Solo Empleados y Jefes de Área (no RH, no Sistemas, no Admin)"""
    perfil = get_user_profile(request.user)
    if not perfil:
        raise PermissionDenied
    
    # Permitir solo a empleados y jefes de área (excluir RH, Sistemas y Admin)
    if not (perfil.es_empleado() or perfil.es_jefe_area()):
        raise PermissionDenied
    
    if request.method == 'POST':
        form = SolicitudVacacionesForm(request.POST, empleado=perfil)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.empleado = perfil
            solicitud.save()
            messages.success(request, 'Solicitud de vacaciones enviada exitosamente.')
            # Redirigir a la misma página para mostrar el modal con el mensaje de Django
            return redirect('empleados:solicitar_vacaciones')
    else:
        form = SolicitudVacacionesForm(empleado=perfil)
    
    # Obtener solicitudes recientes del empleado
    solicitudes_recientes = SolicitudVacaciones.objects.filter(
        empleado=perfil
    ).order_by('-fecha_solicitud')[:5]
    
    # Verificar si puede solicitar vacaciones extraordinarias
    # Las vacaciones extraordinarias solo se pueden tomar cuando el saldo es 0 o negativo
    saldo_total = perfil.calcular_total_disponible_proyectado()
    puede_solicitar_extraordinarias = saldo_total <= 0
    
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
    
    # Los jefes NO pueden aprobar sus propias solicitudes
    if solicitud.empleado == perfil:
        raise PermissionDenied("No puedes aprobar tu propia solicitud de vacaciones.")
    
    # Los jefes solo pueden aprobar solicitudes de empleados asignados directamente a ellos
    empleados_asignados = Perfil.objects.filter(supervisor=perfil, activo=True)
    if solicitud.empleado not in empleados_asignados:
        raise PermissionDenied("Solo puedes aprobar solicitudes de empleados asignados a tu área.")
    
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
    
    # Obtener solo las solicitudes de empleados asignados directamente al jefe como supervisor
    empleados_asignados = Perfil.objects.filter(
        supervisor=perfil,
        activo=True
    )
    solicitudes = SolicitudVacaciones.objects.filter(
        empleado__in=empleados_asignados
    ).select_related(
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
    elif estado_actual == 'A' or estado_actual == 'APROBADO_RH':
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
def aprobar_admin(request, solicitud_id):
    """Aprobar/rechazar solicitud por administrador (para solicitudes de jefes de área)"""
    perfil = get_user_profile(request.user)
    if not perfil or not perfil.es_admin():
        raise PermissionDenied
    
    solicitud = get_object_or_404(SolicitudVacaciones, id=solicitud_id)
    
    # Solo se pueden aprobar solicitudes de jefes de área que estén pendientes de admin
    if not solicitud.empleado.es_jefe_area():
        raise PermissionDenied("Esta solicitud no requiere aprobación de administrador.")
    
    if not solicitud.estado == 'PENDIENTE_ADMIN':
        raise PermissionDenied("Esta solicitud no está pendiente de aprobación de administrador.")
    
    if request.method == 'POST':
        form = AprobacionAdminForm(request.POST, solicitud=solicitud)
        if form.is_valid():
            accion = form.cleaned_data['accion']
            comentario = form.cleaned_data['comentario']
            
            if accion == 'aprobar':
                if solicitud.aprobar_por_admin(perfil, comentario):
                    messages.success(request, 'Solicitud aprobada exitosamente. Ahora pasará a RH para aprobación final.')
                else:
                    messages.error(request, 'No se pudo aprobar la solicitud.')
            else:
                if solicitud.rechazar_por_admin(perfil, comentario):
                    messages.success(request, 'Solicitud rechazada.')
                else:
                    messages.error(request, 'No se pudo rechazar la solicitud.')
            
            return redirect('empleados:admin_dashboard')
    else:
        form = AprobacionAdminForm(solicitud=solicitud)
    
    context = {
        'form': form,
        'solicitud': solicitud,
        'perfil': perfil,
    }
    return render(request, 'empleados/admin/aprobar_solicitud.html', context)


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
                    messages.success(request, f'Solicitud aprobada exitosamente. <a href="{reverse("empleados:generar_pdf_vacaciones", args=[solicitud.id])}" class="alert-link" target="_blank">Descargar Formulario de Vacaciones</a>', extra_tags='safe')
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


@login_required
def generar_pdf_vacaciones(request, solicitud_id):
    """Vista previa del formulario de vacaciones - Solo RH y Admin"""
    solicitud = get_object_or_404(SolicitudVacaciones, id=solicitud_id)
    perfil = get_user_profile(request.user)
    
    # Solo RH y admin pueden ver la vista previa
    if not perfil:
        raise PermissionDenied
    
    if not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    # Solo mostrar vista previa si está aprobada por RH
    if solicitud.estado != 'APROBADO_RH':
        if perfil.es_rh() or perfil.es_admin():
            messages.error(request, 'Solo se puede generar el formulario de solicitudes aprobadas por RH.')
            return redirect('empleados:rh_dashboard')
        else:
            raise PermissionDenied
    
    # Calcular datos necesarios
    empleado = solicitud.empleado
    fecha_presentarse = calcular_fecha_presentarse(solicitud.fecha_fin)
    ano_vacaciones = solicitud.fecha_fin.year
    dias_usados_antes = empleado.dias_vacaciones_usados - solicitud.dias_solicitados
    dias_pendientes = max(0, empleado.dias_vacaciones_anuales - dias_usados_antes)
    
    context = {
        'solicitud': solicitud,
        'fecha_actual': timezone.now(),
        'fecha_presentarse': fecha_presentarse,
        'ano_vacaciones': ano_vacaciones,
        'dias_pendientes': dias_pendientes,
        'perfil': perfil,
    }
    
    return render(request, 'empleados/rh/vista_previa_vacaciones.html', context)


# === GESTIÓN DE DEPARTAMENTOS ===

@login_required
def gestion_departamentos(request):
    """Gestión de departamentos - Solo RH y Admin"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    departamentos = Departamento.objects.filter(activo=True)
    
    # Determinar el dashboard correcto según el perfil
    if perfil.es_admin():
        url_dashboard = 'empleados:admin_dashboard'
        texto_dashboard = 'Volver al Panel'
    elif perfil.es_rh():
        url_dashboard = 'empleados:rh_dashboard'
        texto_dashboard = 'Volver al Panel'
    else:
        url_dashboard = 'empleados:rh_dashboard'
        texto_dashboard = 'Volver al Panel'
    
    context = {
        'departamentos': departamentos,
        'perfil': perfil,
        'url_dashboard': url_dashboard,
        'texto_dashboard': texto_dashboard,
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


@login_required
def editar_departamento(request, departamento_id):
    """Editar departamento existente"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    departamento = get_object_or_404(Departamento, id=departamento_id)
    
    if request.method == 'POST':
        form = ConfigurarDepartamentoForm(request.POST, instance=departamento)
        if form.is_valid():
            form.save()
            messages.success(request, f'Departamento {departamento.nombre} actualizado exitosamente.')
            return redirect('empleados:gestion_departamentos')
    else:
        form = ConfigurarDepartamentoForm(instance=departamento)
    
    context = {
        'form': form,
        'departamento': departamento,
        'perfil': perfil,
    }
    return render(request, 'empleados/rh/crear_departamento.html', context)


@login_required
def ver_departamento(request, departamento_id):
    """Ver detalles de un departamento"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    departamento = get_object_or_404(Departamento, id=departamento_id)
    empleados = departamento.perfil_set.filter(activo=True)
    
    context = {
        'departamento': departamento,
        'empleados': empleados,
        'perfil': perfil,
    }
    return render(request, 'empleados/rh/ver_departamento.html', context)


@login_required
def toggle_departamento(request, departamento_id):
    """Activar o desactivar un departamento"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    departamento = get_object_or_404(Departamento, id=departamento_id)
    
    if departamento.activo:
        departamento.activo = False
        messages.success(request, f'Departamento {departamento.nombre} desactivado exitosamente.')
    else:
        departamento.activo = True
        messages.success(request, f'Departamento {departamento.nombre} activado exitosamente.')
    
    departamento.save()
    return redirect('empleados:gestion_departamentos')


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
    from django.http import HttpRequest
    
    perfil = get_object_or_404(Perfil, usuario=request.user)
    
    # Obtener la URL de referencia (página anterior)
    referer = request.META.get('HTTP_REFERER', '')
    url_volver = referer if referer and 'crear-ticket' not in referer else None
    
    # Si no hay referer válido, usar el dashboard según el perfil
    if not url_volver:
        if perfil.es_sistemas():
            url_volver = reverse('empleados:sistemas_dashboard')
        elif perfil.es_admin():
            url_volver = reverse('empleados:admin_dashboard')
        elif perfil.es_rh():
            url_volver = reverse('empleados:rh_dashboard')
        elif perfil.es_jefe_area():
            url_volver = reverse('empleados:jefe_dashboard')
        else:
            url_volver = reverse('empleados:empleado_dashboard')
    
    if request.method == 'POST':
        form = TicketForm(request.POST, empleado=perfil)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.empleado = perfil
            ticket.save()
            messages.success(request, f'Ticket {ticket.codigo} creado exitosamente.')
            # Renderizar la misma página con el ticket creado para mostrar el modal
            context = {
                'perfil': perfil,
                'form': TicketForm(empleado=perfil),  # Formulario vacío
                'ticket_creado': ticket,
                'mostrar_modal': True,
                'url_volver': url_volver,
            }
            return render(request, 'empleados/tickets/crear_ticket.html', context)
    else:
        form = TicketForm(empleado=perfil)
    
    context = {
        'perfil': perfil,
        'form': form,
        'mostrar_modal': False,
        'url_volver': url_volver,
    }
    return render(request, 'empleados/tickets/crear_ticket.html', context)


@login_required
def detalle_ticket(request, ticket_id):
    """Vista para ver el detalle de un ticket"""
    perfil = get_object_or_404(Perfil, usuario=request.user)
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Verificar permisos
    if perfil.es_sistemas() or perfil.es_admin() or perfil.es_rh() or ticket.empleado == perfil:
        # Detectar desde dónde viene el usuario para redirigir correctamente
        referer = request.META.get('HTTP_REFERER', '')
        url_volver = 'empleados:mis_tickets'  # Por defecto
        texto_volver = 'Volver'
        
        if referer:
            # Si viene de gestión de tickets (sistemas/admin)
            if '/sistemas/tickets/' in referer:
                if perfil.es_admin():
                    url_volver = 'empleados:admin_dashboard'
                    texto_volver = 'Volver al Panel'
                else:
                    url_volver = 'empleados:gestionar_tickets'
                    texto_volver = 'Volver a Tickets'
            # Si viene del dashboard de sistemas
            elif '/sistemas/' in referer and '/tickets/' not in referer:
                url_volver = 'empleados:sistemas_dashboard'
                texto_volver = 'Volver al Panel'
            # Si viene del dashboard de admin
            elif '/administrador/' in referer:
                url_volver = 'empleados:admin_dashboard'
                texto_volver = 'Volver al Panel'
            # Si viene de mis_tickets (usuarios normales)
            elif '/tickets/' in referer and '/sistemas/' not in referer:
                url_volver = 'empleados:mis_tickets'
                texto_volver = 'Volver'
        else:
            # Si no hay referer, determinar según el tipo de perfil
            if perfil.es_sistemas() or perfil.es_admin():
                if perfil.es_admin():
                    url_volver = 'empleados:admin_dashboard'
                else:
                    url_volver = 'empleados:gestionar_tickets'
                texto_volver = 'Volver al Panel' if perfil.es_admin() else 'Volver a Tickets'
        
        context = {
            'perfil': perfil,
            'ticket': ticket,
            'url_volver': url_volver,
            'texto_volver': texto_volver,
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
            # Recargar el ticket desde la base de datos para obtener los datos actualizados
            ticket.refresh_from_db()
            # Recrear el formulario con el ticket actualizado
            form = TicketResolucionForm(instance=ticket)
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
    
    # Optimizar consultas con prefetch para asignaciones y departamentos
    equipos = Equipo.objects.all().select_related('categoria').prefetch_related(
        'asignaciones__empleado__departamento'
    ).order_by('-fecha_adquisicion')
    
    # Filtros
    estado_filtro = request.GET.get('estado', '')
    if estado_filtro:
        equipos = equipos.filter(estado=estado_filtro)
    
    # Detectar de dónde viene el usuario
    referer = request.META.get('HTTP_REFERER', '')
    url_volver = 'empleados:sistemas_dashboard'
    texto_volver = 'Volver al Panel'
    
    if referer:
        # Verificar si viene del dashboard de sistemas
        if '/sistemas/' in referer and '/equipos/' not in referer:
            url_volver = 'empleados:sistemas_dashboard'
            texto_volver = 'Volver al Panel'
        # Verificar si viene del dashboard de admin
        elif '/administrador/' in referer:
            url_volver = 'empleados:admin_dashboard'
            texto_volver = 'Volver al Panel'
        # Verificar si viene del dashboard de RH
        elif '/rh/' in referer:
            url_volver = 'empleados:rh_dashboard'
            texto_volver = 'Volver al Panel'
        # Verificar si viene de gestión de usuarios
        elif '/usuarios/' in referer:
            url_volver = 'empleados:gestion_usuarios'
            texto_volver = 'Volver a Gestión'
        # Si es admin o RH pero no viene de ningún lugar específico, usar su dashboard
        elif perfil.es_admin():
            url_volver = 'empleados:admin_dashboard'
            texto_volver = 'Volver al Panel'
        elif perfil.es_rh():
            url_volver = 'empleados:rh_dashboard'
            texto_volver = 'Volver al Panel'
    
    context = {
        'perfil': perfil,
        'equipos': equipos,
        'estado_filtro': estado_filtro,
        'url_volver': url_volver,
        'texto_volver': texto_volver,
    }
    return render(request, 'empleados/sistemas/inventario.html', context)


@login_required
def inventario_jefe(request):
    """Vista de inventario para jefes de área - Solo lectura"""
    perfil = get_object_or_404(Perfil, usuario=request.user)
    
    # Verificar permisos - Solo jefes de área
    if not perfil.es_jefe_area():
        messages.error(request, 'No tienes permiso para acceder a esta sección.')
        return redirect('empleados:empleado_dashboard')
    
    # Obtener empleados asignados directamente al jefe como supervisor
    empleados_asignados = Perfil.objects.filter(
        supervisor=perfil,
        activo=True
    )
    
    # Obtener IDs de empleados asignados (incluyendo al jefe mismo)
    empleados_ids = list(empleados_asignados.values_list('id', flat=True))
    empleados_ids.append(perfil.id)  # Incluir al jefe mismo
    
    # Obtener equipos asignados activamente al jefe o a sus empleados
    from django.db.models import Q
    equipos_asignados = Equipo.objects.filter(
        asignaciones__empleado__in=empleados_ids,
        asignaciones__fecha_devolucion__isnull=True
    ).distinct()
    
    # También incluir equipos que estén en el área del jefe (departamento)
    # aunque no estén asignados a nadie específico, pero que estén en el departamento
    if perfil.departamento:
        # Obtener todos los empleados del departamento del jefe
        empleados_departamento = Perfil.objects.filter(
            departamento=perfil.departamento,
            activo=True
        ).values_list('id', flat=True)
        
        # Equipos asignados a cualquier empleado del departamento (incluyendo el jefe)
        equipos_departamento = Equipo.objects.filter(
            asignaciones__empleado__in=empleados_departamento,
            asignaciones__fecha_devolucion__isnull=True
        ).distinct()
        
        # Combinar: equipos asignados al jefe/sus empleados + equipos del departamento
        equipos = (equipos_asignados | equipos_departamento).distinct()
    else:
        # Si el jefe no tiene departamento, solo mostrar equipos asignados directamente
        equipos = equipos_asignados
    
    # Optimizar consultas
    equipos = equipos.select_related('categoria').prefetch_related(
        'asignaciones__empleado__departamento'
    ).order_by('-fecha_adquisicion')
    
    # Filtros
    estado_filtro = request.GET.get('estado', '')
    if estado_filtro:
        equipos = equipos.filter(estado=estado_filtro)
    
    context = {
        'perfil': perfil,
        'equipos': equipos,
        'estado_filtro': estado_filtro,
        'url_volver': 'empleados:jefe_dashboard',
        'texto_volver': 'Volver al Panel',
        'es_jefe': True,  # Flag para indicar que es vista de solo lectura
    }
    return render(request, 'empleados/jefe/inventario.html', context)


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
            
            # Si se seleccionó un empleado para asignar
            empleado_asignar = form.cleaned_data.get('asignar_a_empleado')
            condicion_entrega = form.cleaned_data.get('condicion_entrega', '')
            
            if empleado_asignar:
                # Cerrar cualquier asignación activa previa antes de crear la nueva
                asignacion_anterior = equipo.asignacion_actual
                if asignacion_anterior:
                    asignacion_anterior.fecha_devolucion = timezone.now().date()
                    asignacion_anterior.save()
                
                # Crear la asignación
                from .models import AsignacionEquipo
                asignacion = AsignacionEquipo.objects.create(
                    equipo=equipo,
                    empleado=empleado_asignar,
                    asignado_por=perfil,
                    fecha_asignacion=timezone.now().date(),
                    condicion_entrega=condicion_entrega
                )
                # Actualizar estado del equipo solo si no está en reparación
                # Si está en reparación, mantener ese estado aunque se asigne
                if equipo.estado != 'EN_REPARACION' and equipo.estado != 'DADO_DE_BAJA':
                    equipo.estado = 'ASIGNADO'
                    equipo.save()
                messages.success(request, f'Equipo {equipo.codigo_inventario} agregado y asignado a {empleado_asignar.nombre_completo} exitosamente.')
            else:
                messages.success(request, f'Equipo {equipo.codigo_inventario} agregado exitosamente al inventario.')
            
            # Redirigir a la misma página para mostrar el modal
            return redirect('empleados:agregar_equipo')
    else:
        form = EquipoForm()
    
    context = {
        'perfil': perfil,
        'form': form,
    }
    return render(request, 'empleados/sistemas/agregar_equipo.html', context)


@login_required
def gestionar_asignacion_equipo(request, equipo_id):
    """Vista unificada para crear o editar una asignación de equipo desde el inventario"""
    from .forms import AsignacionEquipoForm
    perfil = get_object_or_404(Perfil, usuario=request.user)
    
    # Verificar permisos
    if not (perfil.es_sistemas() or perfil.es_admin() or perfil.es_rh()):
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('empleados:empleado_dashboard')
    
    equipo = get_object_or_404(Equipo, id=equipo_id)
    asignacion_activa = equipo.asignacion_actual
    asignacion = asignacion_activa if asignacion_activa else None
    es_edicion = asignacion is not None  # Si hay asignación activa, es edición; si no, es creación
    
    # Verificar que el equipo esté disponible o en reparación para nuevas asignaciones
    if not asignacion and equipo.estado not in ['DISPONIBLE', 'EN_REPARACION']:
        messages.error(request, f'El equipo {equipo.codigo_inventario} no está disponible para asignar.')
        return redirect('empleados:inventario_equipos')
    
    equipo_en_reparacion = equipo.estado == 'EN_REPARACION'
    
    if request.method == 'POST':
        form = AsignacionEquipoForm(
            request.POST, 
            instance=asignacion,
            equipo_en_reparacion=equipo_en_reparacion,
            estado_actual=equipo.estado,
            es_edicion=es_edicion
        )
        # Asegurar que el queryset incluya este equipo específico
        form.fields['equipo'].queryset = Equipo.objects.filter(id=equipo.id)
        form.fields['equipo'].required = False
        
        if form.is_valid():
            if es_edicion:
                # Modo edición: actualizar asignación existente
                asignacion = form.save()
            else:
                # Modo creación: cerrar asignación anterior si existe y crear nueva
                asignacion_anterior = equipo.asignacion_actual
                if asignacion_anterior:
                    asignacion_anterior.fecha_devolucion = timezone.now().date()
                    asignacion_anterior.save()
                
                asignacion = form.save(commit=False)
                asignacion.equipo = equipo
                asignacion.asignado_por = perfil
                asignacion.fecha_asignacion = timezone.now().date()
                asignacion.save()
            
            # Actualizar estado del equipo según el formulario
            nuevo_estado = form.cleaned_data.get('nuevo_estado')
            if nuevo_estado:
                equipo.estado = nuevo_estado
                equipo.save()
            elif asignacion.fecha_devolucion:
                # Si se devuelve y no se especificó nuevo estado, cambiar a disponible solo si no está en reparación o dado de baja
                if equipo.estado != 'EN_REPARACION' and equipo.estado != 'DADO_DE_BAJA':
                    equipo.estado = 'DISPONIBLE'
                    equipo.save()
            elif not es_edicion:
                # Si es creación y no se especificó nuevo estado, cambiar a ASIGNADO (excepto si está en reparación o dado de baja)
                if equipo.estado != 'EN_REPARACION' and equipo.estado != 'DADO_DE_BAJA':
                    equipo.estado = 'ASIGNADO'
                    equipo.save()
            # Si es edición y no se especificó nuevo estado, mantener el estado actual
            
            if es_edicion:
                messages.success(request, f'Asignación del equipo {equipo.codigo_inventario} actualizada exitosamente.')
            else:
                messages.success(request, f'Equipo {equipo.codigo_inventario} asignado a {asignacion.empleado.nombre_completo} exitosamente.')
            return redirect('empleados:inventario_equipos')
    else:
        form = AsignacionEquipoForm(
            instance=asignacion,
            equipo_en_reparacion=equipo_en_reparacion,
            estado_actual=equipo.estado,
            es_edicion=es_edicion
        )
        # Ocultar el campo de equipo ya que no se puede cambiar
        form.fields['equipo'].widget = forms.HiddenInput()
        # Asegurar que el equipo esté en el queryset
        form.fields['equipo'].queryset = Equipo.objects.filter(id=equipo.id)
        form.fields['equipo'].required = False
    
    context = {
        'perfil': perfil,
        'form': form,
        'asignacion': asignacion,
        'equipo': equipo,
        'es_edicion': es_edicion,
    }
    return render(request, 'empleados/sistemas/editar_asignacion_equipo.html', context)


@login_required
def editar_asignacion_equipo(request, asignacion_id):
    """Vista para editar una asignación de equipo existente (por ID de asignación)"""
    from .forms import AsignacionEquipoForm
    perfil = get_object_or_404(Perfil, usuario=request.user)
    
    # Verificar permisos
    if not (perfil.es_sistemas() or perfil.es_admin() or perfil.es_rh()):
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('empleados:empleado_dashboard')
    
    asignacion = get_object_or_404(AsignacionEquipo, id=asignacion_id)
    equipo = asignacion.equipo
    es_edicion = True
    equipo_en_reparacion = equipo.estado == 'EN_REPARACION'
    
    if request.method == 'POST':
        form = AsignacionEquipoForm(
            request.POST, 
            instance=asignacion,
            equipo_en_reparacion=equipo_en_reparacion,
            estado_actual=equipo.estado,
            es_edicion=True
        )
        # Asegurar que el queryset incluya este equipo específico
        form.fields['equipo'].queryset = Equipo.objects.filter(id=equipo.id)
        form.fields['equipo'].required = False
        
        if form.is_valid():
            asignacion = form.save()
            
            # Actualizar estado del equipo según el formulario
            nuevo_estado = form.cleaned_data.get('nuevo_estado')
            if nuevo_estado:
                equipo.estado = nuevo_estado
                equipo.save()
            elif asignacion.fecha_devolucion:
                # Si se devuelve y no se especificó nuevo estado, cambiar a disponible solo si no está en reparación o dado de baja
                if equipo.estado != 'EN_REPARACION' and equipo.estado != 'DADO_DE_BAJA':
                    equipo.estado = 'DISPONIBLE'
                    equipo.save()
            else:
                # Si se asigna y no se especificó nuevo estado, mantener EN_REPARACION o DADO_DE_BAJA si ya lo está
                if equipo.estado != 'EN_REPARACION' and equipo.estado != 'DADO_DE_BAJA':
                    equipo.estado = 'ASIGNADO'
                    equipo.save()
            
            messages.success(request, f'Asignación del equipo {equipo.codigo_inventario} actualizada exitosamente.')
            return redirect('empleados:inventario_equipos')
    else:
        form = AsignacionEquipoForm(
            instance=asignacion,
            equipo_en_reparacion=equipo_en_reparacion,
            estado_actual=equipo.estado,
            es_edicion=True
        )
        # Ocultar el campo de equipo ya que no se puede cambiar
        form.fields['equipo'].widget = forms.HiddenInput()
        # Asegurar que el equipo esté en el queryset
        form.fields['equipo'].queryset = Equipo.objects.filter(id=equipo.id)
        form.fields['equipo'].required = False
    
    context = {
        'perfil': perfil,
        'form': form,
        'asignacion': asignacion,
        'equipo': equipo,
        'es_edicion': es_edicion,
    }
    return render(request, 'empleados/sistemas/editar_asignacion_equipo.html', context)


@login_required
def quitar_asignacion_equipo(request, equipo_id):
    """Vista para quitar/remover una asignación de equipo (marcar como devuelto)"""
    from .forms import AsignacionEquipoForm
    perfil = get_object_or_404(Perfil, usuario=request.user)
    
    # Verificar permisos
    if not (perfil.es_sistemas() or perfil.es_admin() or perfil.es_rh()):
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('empleados:empleado_dashboard')
    
    equipo = get_object_or_404(Equipo, id=equipo_id)
    asignacion_activa = equipo.asignacion_actual
    
    if not asignacion_activa:
        messages.error(request, f'El equipo {equipo.codigo_inventario} no tiene una asignación activa.')
        return redirect('empleados:inventario_equipos')
    
    if request.method == 'POST':
        accion = request.POST.get('accion', 'quitar')
        
        if accion == 'quitar':
            # Opción 1: Solo quitar la asignación
            nuevo_estado = request.POST.get('nuevo_estado', '')
            
            # Marcar la asignación como devuelta
            asignacion_activa.fecha_devolucion = timezone.now().date()
            asignacion_activa.save()
            
            # Actualizar estado del equipo según lo seleccionado
            if nuevo_estado:
                equipo.estado = nuevo_estado
            else:
                # Si no se especificó, cambiar a disponible solo si no está en reparación o dado de baja
                if equipo.estado != 'EN_REPARACION' and equipo.estado != 'DADO_DE_BAJA':
                    equipo.estado = 'DISPONIBLE'
            equipo.save()
            
            messages.success(request, f'Asignación del equipo {equipo.codigo_inventario} removida exitosamente.')
            return redirect('empleados:inventario_equipos')
        
        elif accion == 'reasignar':
            # Opción 2: Reasignar a otro empleado/área
            form = AsignacionEquipoForm(request.POST)
            form.fields['equipo'].queryset = Equipo.objects.filter(id=equipo.id)
            form.fields['equipo'].required = False
            
            if form.is_valid():
                # Cerrar la asignación anterior
                asignacion_activa.fecha_devolucion = timezone.now().date()
                asignacion_activa.save()
                
                # Crear nueva asignación
                nueva_asignacion = form.save(commit=False)
                nueva_asignacion.equipo = equipo
                nueva_asignacion.asignado_por = perfil
                nueva_asignacion.fecha_asignacion = timezone.now().date()
                nueva_asignacion.save()
                
                # Actualizar estado del equipo
                nuevo_estado = form.cleaned_data.get('nuevo_estado')
                if nuevo_estado:
                    equipo.estado = nuevo_estado
                elif equipo.estado != 'EN_REPARACION' and equipo.estado != 'DADO_DE_BAJA':
                    equipo.estado = 'ASIGNADO'
                equipo.save()
                
                messages.success(request, f'Equipo {equipo.codigo_inventario} reasignado a {nueva_asignacion.empleado.nombre_completo} exitosamente.')
                return redirect('empleados:inventario_equipos')
            else:
                # Si hay errores en el formulario, mostrar el formulario con errores
                context = {
                    'perfil': perfil,
                    'equipo': equipo,
                    'asignacion': asignacion_activa,
                    'form': form,
                    'mostrar_formulario_reasignacion': True,
                }
                return render(request, 'empleados/sistemas/quitar_asignacion_equipo.html', context)
    
    # GET: Mostrar formulario
    form = AsignacionEquipoForm(
        initial={'equipo': equipo},
        equipo_en_reparacion=False,
        estado_actual=equipo.estado,
        es_edicion=False
    )
    form.fields['equipo'].widget = forms.HiddenInput()
    form.fields['equipo'].queryset = Equipo.objects.filter(id=equipo.id)
    form.fields['equipo'].required = False
    
    context = {
        'perfil': perfil,
        'equipo': equipo,
        'asignacion': asignacion_activa,
        'form': form,
        'mostrar_formulario_reasignacion': False,
    }
    return render(request, 'empleados/sistemas/quitar_asignacion_equipo.html', context)


@login_required
def marcar_equipo_disponible(request, equipo_id):
    """Vista para marcar un equipo como disponible después de reparación"""
    perfil = get_object_or_404(Perfil, usuario=request.user)
    
    # Verificar permisos
    if not (perfil.es_sistemas() or perfil.es_admin() or perfil.es_rh()):
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('empleados:empleado_dashboard')
    
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    # Verificar que el equipo esté en reparación
    if equipo.estado != 'EN_REPARACION':
        messages.error(request, f'El equipo {equipo.codigo_inventario} no está en reparación.')
        return redirect('empleados:inventario_equipos')
    
    if request.method == 'POST':
        # Cambiar estado a disponible
        equipo.estado = 'DISPONIBLE'
        equipo.save()
        
        messages.success(request, f'Equipo {equipo.codigo_inventario} marcado como disponible. El equipo está listo para ser asignado.')
        return redirect('empleados:inventario_equipos')
    
    context = {
        'perfil': perfil,
        'equipo': equipo,
    }
    return render(request, 'empleados/sistemas/marcar_equipo_disponible.html', context)


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


# === KARDEX DE VACACIONES ===

@login_required
def kardex_vacaciones(request):
    """Kardex de vacaciones - Lista de todos los empleados con sus vacaciones acumuladas"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    # Obtener parámetro de ordenamiento (por defecto: alfabetico)
    orden = request.GET.get('orden', 'alfabetico')
    
    # Obtener todos los empleados activos, excluyendo ADMIN, RH y SISTEMAS
    from django.db.models import Case, When, Value, IntegerField
    
    empleados = Perfil.objects.filter(
        activo=True
    ).exclude(
        tipo_perfil__in=['ADMIN', 'RH', 'SISTEMAS']
    ).select_related(
        'usuario', 'departamento'
    )
    
    # Aplicar ordenamiento según el parámetro
    if orden == 'area':
        # Ordenar por área/departamento, luego alfabéticamente
        empleados = empleados.annotate(
        orden_departamento=Case(
            When(departamento__nombre__iexact='Ventas', then=Value(1)),
            When(departamento__nombre__iexact='Conta', then=Value(2)),
            When(departamento__isnull=True, then=Value(999)),
            default=Value(3),
            output_field=IntegerField()
        )
        ).order_by('orden_departamento', 'departamento__nombre', 'usuario__first_name', 'usuario__last_name')
    elif orden == 'antiguedad':
        # Ordenar por antigüedad (más antiguos primero), luego alfabéticamente
        empleados = empleados.order_by('fecha_contratacion', 'usuario__first_name', 'usuario__last_name')
    else:  # alfabetico (por defecto)
        # Ordenar alfabéticamente por nombre primero, luego apellido
        empleados = empleados.order_by('usuario__first_name', 'usuario__last_name')
    
    # Preparar datos de vacaciones para cada empleado
    from empleados.models import HistorialVacaciones
    from decimal import Decimal
    
    empleados_data = []
    for empleado in empleados:
        # Vacaciones del año actual
        dias_anuales = empleado.dias_vacaciones_anuales
        saldo = float(empleado.saldo_vacaciones)  # Saldo de años anteriores (puede ser negativo)
        dias_acumulados_ano_actual = empleado.calcular_dias_acumulados_hasta_hoy()
        
        # Calcular total disponible: Saldo + Días acumulados año actual
        total_disponible = empleado.calcular_total_disponible_proyectado()
        
        # Obtener historial de deducciones (registros donde se restaron días)
        historial_deducciones = HistorialVacaciones.objects.filter(
            empleado=empleado,
            tomadas__gt=0  # Solo registros donde se restaron días
        ).order_by('-fecha_registro', '-fecha_creacion')[:10]  # Últimas 10 deducciones
        
        # Preparar lista de deducciones para mostrar
        deducciones_lista = []
        for registro in historial_deducciones:
            deducciones_lista.append({
                'fecha': registro.fecha_registro,
                'concepto': registro.concepto,
                'dias': float(registro.tomadas),
                'tipo': registro.tipo_movimiento,
                'saldo_despues': float(registro.saldo) if registro.saldo else None,
            })
        
        empleados_data.append({
            'empleado': empleado,
            'dias_anuales': dias_anuales,
            'saldo': round(saldo, 2),
            'dias_acumulados_ano_actual': round(dias_acumulados_ano_actual, 2),
            'total_disponible': round(total_disponible, 2),
            'antiguedad': empleado.antiguedad_detallada,
            'deducciones': deducciones_lista,
            'total_deducciones': len(deducciones_lista),
        })
    
    context = {
        'perfil': perfil,
        'empleados_data': empleados_data,
        'total_empleados': len(empleados_data),
        'orden_actual': orden,
    }
    return render(request, 'empleados/rh/kardex_vacaciones.html', context)


@login_required
def generar_excel_kardex(request):
    """Generar Excel del kardex de vacaciones - Cada empleado con su propio cuadro en la misma hoja"""
    try:
        perfil = get_user_profile(request.user)
        if not perfil or not (perfil.es_rh() or perfil.es_admin()):
            raise PermissionDenied
        
        # Verificar que openpyxl esté instalado
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from openpyxl.utils import get_column_letter
        except ImportError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error importando openpyxl: {e}')
            return HttpResponse(
                'Error: openpyxl no está instalado. Por favor, instálelo con: pip install openpyxl',
                status=500,
                content_type='text/plain'
            )
        
        # Obtener todos los empleados activos, excluyendo ADMIN, RH y SISTEMAS
        from django.db.models import Case, When, Value, IntegerField
        
        empleados = Perfil.objects.filter(
            activo=True
        ).exclude(
            tipo_perfil__in=['ADMIN', 'RH', 'SISTEMAS']
        ).select_related(
            'usuario', 'departamento'
        ).annotate(
            # Ordenar por departamento: Ventas primero, Conta segundo, sin departamento al final
            orden_departamento=Case(
                When(departamento__nombre__iexact='Ventas', then=Value(1)),
                When(departamento__nombre__iexact='Conta', then=Value(2)),
                When(departamento__isnull=True, then=Value(999)),
                default=Value(3),
                output_field=IntegerField()
            )
        ).order_by('orden_departamento', 'departamento__nombre', 'usuario__last_name', 'usuario__first_name')
        
        # Crear respuesta HTTP con Excel
        from datetime import date as date_module
        fecha_actual = date_module.today()
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="kardex_vacaciones_{fecha_actual.strftime("%Y%m%d")}.xlsx"'
        
        # Crear workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Kardex Vacaciones"
        
        # Estilos - Crear una vez y reutilizar
        header_fill = PatternFill(start_color="F97316", end_color="EA580C", fill_type="solid")  # Naranja como en la imagen
        header_font = Font(bold=True, color="FFFFFF", size=11, name="Arial")
        title_font = Font(bold=True, size=12, name="Arial")
        value_font = Font(size=11, name="Arial")
        value_font_bold = Font(bold=True, size=11, name="Arial")
        value_font_bold_red = Font(bold=True, size=11, name="Arial", color="DC2626")
        value_font_bold_green = Font(bold=True, size=11, name="Arial", color="059669")
        border_style = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        center_alignment = Alignment(horizontal='center', vertical='center')
        left_alignment = Alignment(horizontal='left', vertical='center')
        
        # Patrones de relleno reutilizables
        fill_azul_claro = PatternFill(start_color="DBEAFE", end_color="BFDBFE", fill_type="solid")
        fill_naranja_claro = PatternFill(start_color="FED7AA", end_color="FDBA74", fill_type="solid")
        fill_verde_claro = PatternFill(start_color="D1FAE5", end_color="A7F3D0", fill_type="solid")
        fill_rojo_claro = PatternFill(start_color="FEE2E2", end_color="FECACA", fill_type="solid")
        header_fill_blue = PatternFill(start_color="3B82F6", end_color="2563EB", fill_type="solid")
        
        # Título general del documento
        row = 1
        ws.merge_cells(f'A{row}:D{row}')
        cell = ws[f'A{row}']
        cell.value = f'Kárdex de vacaciones del empleado al {fecha_actual.strftime("%d/%m/%Y")}'
        cell.font = Font(bold=True, size=14, name="Arial")
        cell.alignment = center_alignment
        ws.row_dimensions[row].height = 30
        row += 1
        
        # Nota informativa
        ws.merge_cells(f'A{row}:D{row}')
        cell = ws[f'A{row}']
        cell.value = '**Este reporte realiza cálculos tomando en cuenta si el empleado está finiquitado a la fecha de referencia'
        cell.font = Font(size=9, italic=True, name="Arial")
        cell.alignment = center_alignment
        row += 2  # Espacio antes del primer empleado
        
        # Crear sección para cada empleado
        for idx, empleado in enumerate(empleados):
            # Espacio entre empleados (excepto el primero)
            if idx > 0:
                row += 2
            
            # Calcular datos de vacaciones
            dias_anuales = empleado.dias_vacaciones_anuales
            saldo = float(empleado.saldo_vacaciones)  # Saldo de años anteriores
            dias_acumulados_ano_actual = round(empleado.calcular_dias_acumulados_hasta_hoy(), 2)
            total_disponible = round(empleado.calcular_total_disponible_proyectado(), 2)
            
            # Verificar si ha cumplido un año completo (usar la propiedad del modelo)
            ha_cumplido_ano = empleado.antiguedad_anos >= 1
            
            # Usar la propiedad antiguedad_detallada del modelo (ya optimizada)
            antiguedad = empleado.antiguedad_detallada
            
            # Título del empleado (número, nombre, área y antigüedad)
            area_nombre = empleado.departamento.nombre if empleado.departamento else "Sin área asignada"
            empleado_titulo = f'{empleado.numero_empleado}.{empleado.nombre_completo.upper()} - {area_nombre} - Antigüedad: {antiguedad}'
            ws.merge_cells(f'A{row}:D{row}')
            cell = ws[f'A{row}']
            cell.value = empleado_titulo
            cell.font = title_font
            cell.alignment = left_alignment
            ws.row_dimensions[row].height = 20
            row += 1
            
            # Encabezado de la tabla (azul como en la imagen)
            headers_tabla = ['Con Derecho', 'Saldo', 'Acumulado Año Actual', 'Total Disponible']
            for col_num, header in enumerate(headers_tabla, 1):
                cell = ws.cell(row=row, column=col_num)
                cell.value = header
                cell.font = header_font
                cell.fill = header_fill_blue
                cell.alignment = center_alignment
                cell.border = border_style
            ws.row_dimensions[row].height = 25
            row += 1
            
            # Fila de datos (total_disponible ya fue calculado arriba)
            # Columna 1: Con Derecho (azul) - Mostrar 0 si no ha cumplido un año
            dias_anuales_display = 0 if not ha_cumplido_ano else dias_anuales
            cell = ws.cell(row=row, column=1)
            cell.value = f'{dias_anuales_display} días'
            cell.font = value_font_bold
            cell.border = border_style
            cell.alignment = center_alignment
            cell.fill = fill_azul_claro
            
            # Columna 2: Saldo (naranja) - puede ser negativo o positivo
            cell = ws.cell(row=row, column=2)
            saldo_str = f'{saldo:.2f} días' if saldo != 0 else '0.00 días'
            cell.value = saldo_str
            cell.font = value_font_bold_red if saldo < 0 else value_font_bold_green
            cell.border = border_style
            cell.alignment = center_alignment
            cell.fill = fill_naranja_claro
            
            # Columna 3: Acumulado Año Actual (naranja)
            cell = ws.cell(row=row, column=3)
            acumulado_str = f'{dias_acumulados_ano_actual:.2f} días' if dias_acumulados_ano_actual != 0 else '0.00 días'
            cell.value = acumulado_str
            cell.font = value_font_bold
            cell.border = border_style
            cell.alignment = center_alignment
            cell.fill = fill_naranja_claro
            
            # Columna 4: Total Disponible (verde o rojo)
            cell = ws.cell(row=row, column=4)
            total_str = f'{total_disponible:.2f} días'
            cell.value = total_str
            cell.font = value_font_bold
            cell.border = border_style
            cell.alignment = center_alignment
            # Verde claro para positivo, rojo si negativo
            cell.fill = fill_verde_claro if total_disponible > 0 else fill_rojo_claro
            row += 1
        
        # Ajustar ancho de columnas
        column_widths = [20, 18, 25, 20]
        for col_num, width in enumerate(column_widths, 1):
            ws.column_dimensions[get_column_letter(col_num)].width = width
        
        # Guardar workbook
        try:
            wb.save(response)
        except Exception as save_error:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f'Error guardando Excel: {str(save_error)}')
            logger.error(traceback.format_exc())
            return HttpResponse(
                f'Error al guardar el archivo Excel: {str(save_error)}',
                status=500,
                content_type='text/plain'
            )
        
        return response
    
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f'Error generando Excel kardex: {str(e)}')
        logger.error(traceback.format_exc())
        
        # En producción, devolver un error más amigable
        return HttpResponse(
            f'Error al generar el archivo Excel. Por favor, contacte al administrador. Error: {str(e)}',
            status=500,
            content_type='text/plain'
        )


@login_required
def generar_pdf_kardex(request):
    """Generar PDF del kardex de vacaciones"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    # Obtener todos los empleados activos, excluyendo ADMIN, RH y SISTEMAS
    from django.db.models import Case, When, Value, IntegerField
    
    empleados = Perfil.objects.filter(
        activo=True
    ).exclude(
        tipo_perfil__in=['ADMIN', 'RH', 'SISTEMAS']
    ).select_related(
        'usuario', 'departamento'
    ).annotate(
        # Ordenar por departamento: Ventas primero, Conta segundo, sin departamento al final
        orden_departamento=Case(
            When(departamento__nombre__iexact='Ventas', then=Value(1)),
            When(departamento__nombre__iexact='Conta', then=Value(2)),
            When(departamento__isnull=True, then=Value(999)),
            default=Value(3),
            output_field=IntegerField()
        )
    ).order_by('orden_departamento', 'departamento__nombre', 'usuario__last_name', 'usuario__first_name')
    
    # Crear respuesta HTTP con PDF
    response = HttpResponse(content_type='application/pdf')
    fecha_actual = timezone.now().date()
    
    if request.GET.get('imprimir'):
        response['Content-Disposition'] = f'inline; filename="kardex_vacaciones_{fecha_actual.strftime("%Y%m%d")}.pdf"'
    else:
        response['Content-Disposition'] = f'attachment; filename="kardex_vacaciones_{fecha_actual.strftime("%Y%m%d")}.pdf"'
    
    # Crear documento PDF
    doc = SimpleDocTemplate(response, pagesize=A4, 
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph('<b>KARDEX DE VACACIONES</b>', title_style))
    elements.append(Paragraph(f'<i>Generado el: {fecha_actual.strftime("%d/%m/%Y")}</i>', styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))
    
    # Preparar datos para la tabla
    data = [['Empleado', 'Depto', 'Antigüedad', 'Con Derecho', 'Saldo', 'Acum. Año Actual', 'Total Disponible']]
    
    for empleado in empleados:
        dias_anuales = empleado.dias_vacaciones_anuales
        saldo = float(empleado.saldo_vacaciones)  # Saldo de años anteriores
        dias_acumulados_ano_actual = round(empleado.calcular_dias_acumulados_hasta_hoy(), 2)
        total_disponible = round(empleado.calcular_total_disponible_proyectado(), 2)
        
        depto = empleado.departamento.nombre if empleado.departamento else "Sin depto"
        depto = depto[:15] if len(depto) > 15 else depto
        
        data.append([
            empleado.nombre_completo[:25],
            depto,
            empleado.antiguedad_detallada[:12],
            str(dias_anuales),
            f'{saldo:.2f}',
            str(dias_acumulados_ano_actual),
            str(total_disponible),
        ])
    
    # Crear tabla
    table = Table(data, colWidths=[4*cm, 2.5*cm, 2*cm, 2*cm, 2*cm, 2.5*cm, 2.5*cm])
    
    # Estilo de la tabla
    table_style = TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Filas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        
        # Alineación de datos
        ('ALIGN', (0, 1), (1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ])
    
    table.setStyle(table_style)
    elements.append(table)
    
    # Construir PDF
    doc.build(elements)
    return response


# === REPORTE DE VACACIONES ===

@login_required
def reporte_vacaciones_mes(request):
    """Reporte de vacaciones por mes y año - Solo RH y Admin"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    # Obtener mes y año de los parámetros GET, o usar el mes actual por defecto
    hoy = timezone.now().date()
    mes_seleccionado = request.GET.get('mes', hoy.month)
    año_seleccionado = request.GET.get('año', hoy.year)
    
    try:
        mes_seleccionado = int(mes_seleccionado)
        año_seleccionado = int(año_seleccionado)
        
        # Validar rango de mes y año
        if mes_seleccionado < 1 or mes_seleccionado > 12:
            mes_seleccionado = hoy.month
        if año_seleccionado < 2000 or año_seleccionado > 2100:
            año_seleccionado = hoy.year
            
        # Calcular rango del mes seleccionado
        primer_dia_mes = date(año_seleccionado, mes_seleccionado, 1)
        
        # Calcular último día del mes
        if mes_seleccionado == 12:
            ultimo_dia_mes = date(año_seleccionado + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia_mes = date(año_seleccionado, mes_seleccionado + 1, 1) - timedelta(days=1)
            
    except (ValueError, TypeError):
        # Si hay error, usar el mes actual
        primer_dia_mes = hoy.replace(day=1)
        if primer_dia_mes.month == 12:
            ultimo_dia_mes = date(primer_dia_mes.year + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia_mes = date(primer_dia_mes.year, primer_dia_mes.month + 1, 1) - timedelta(days=1)
        mes_seleccionado = primer_dia_mes.month
        año_seleccionado = primer_dia_mes.year
    
    # Obtener todas las solicitudes del mes seleccionado
    solicitudes = SolicitudVacaciones.objects.filter(
        fecha_solicitud__gte=primer_dia_mes,
        fecha_solicitud__lte=ultimo_dia_mes
    ).select_related(
        'empleado', 'empleado__departamento', 'aprobado_por_jefe', 'aprobado_por_rh'
    ).order_by('-fecha_solicitud')
    
    # Estadísticas
    total_solicitudes = solicitudes.count()
    aprobadas = solicitudes.filter(estado='APROBADO_RH').count()
    rechazadas = solicitudes.filter(estado__in=['RECHAZADO_JEFE', 'RECHAZADO_RH', 'RECHAZADO_ADMIN']).count()
    pendientes = solicitudes.filter(estado__in=['PENDIENTE_JEFE', 'PENDIENTE_RH', 'PENDIENTE_ADMIN']).count()
    total_dias = solicitudes.filter(estado='APROBADO_RH').aggregate(
        total=Sum('dias_solicitados')
    )['total'] or 0
    
    # Nombres de meses en español
    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    context = {
        'solicitudes': solicitudes,
        'perfil': perfil,
        'mes': f"{meses.get(mes_seleccionado, '')} {año_seleccionado}",
        'mes_numero': mes_seleccionado,
        'año': año_seleccionado,
        'fecha_inicio': primer_dia_mes,
        'fecha_fin': ultimo_dia_mes,
        'total_solicitudes': total_solicitudes,
        'aprobadas': aprobadas,
        'rechazadas': rechazadas,
        'pendientes': pendientes,
        'total_dias': total_dias,
        'meses': meses,
        'años_disponibles': range(2020, hoy.year + 2),  # Desde 2020 hasta el año siguiente
    }
    return render(request, 'empleados/rh/reporte_vacaciones.html', context)


@login_required
def generar_pdf_reporte_vacaciones(request):
    """Generar PDF del reporte de vacaciones por mes y año"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    # Obtener mes y año de los parámetros GET, o usar el mes actual por defecto
    hoy = timezone.now().date()
    mes_seleccionado = request.GET.get('mes', hoy.month)
    año_seleccionado = request.GET.get('año', hoy.year)
    
    try:
        mes_seleccionado = int(mes_seleccionado)
        año_seleccionado = int(año_seleccionado)
        
        if mes_seleccionado < 1 or mes_seleccionado > 12:
            mes_seleccionado = hoy.month
        if año_seleccionado < 2000 or año_seleccionado > 2100:
            año_seleccionado = hoy.year
            
        primer_dia_mes = date(año_seleccionado, mes_seleccionado, 1)
        if mes_seleccionado == 12:
            ultimo_dia_mes = date(año_seleccionado + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia_mes = date(año_seleccionado, mes_seleccionado + 1, 1) - timedelta(days=1)
    except (ValueError, TypeError):
        primer_dia_mes = hoy.replace(day=1)
        if primer_dia_mes.month == 12:
            ultimo_dia_mes = date(primer_dia_mes.year + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia_mes = date(primer_dia_mes.year, primer_dia_mes.month + 1, 1) - timedelta(days=1)
        mes_seleccionado = primer_dia_mes.month
        año_seleccionado = primer_dia_mes.year
    
    # Obtener todas las solicitudes del mes seleccionado
    solicitudes = SolicitudVacaciones.objects.filter(
        fecha_solicitud__gte=primer_dia_mes,
        fecha_solicitud__lte=ultimo_dia_mes
    ).select_related(
        'empleado', 'empleado__departamento', 'aprobado_por_jefe', 'aprobado_por_rh'
    ).order_by('-fecha_solicitud')
    
    # Crear respuesta HTTP con PDF
    response = HttpResponse(content_type='application/pdf')
    
    # Si es para imprimir, usar 'inline' para abrir en el navegador
    # Si es para descargar, usar 'attachment'
    if request.GET.get('imprimir'):
        response['Content-Disposition'] = f'inline; filename="reporte_vacaciones_{año_seleccionado}_{mes_seleccionado:02d}.pdf"'
    else:
        response['Content-Disposition'] = f'attachment; filename="reporte_vacaciones_{año_seleccionado}_{mes_seleccionado:02d}.pdf"'
    
    # Crear documento PDF con formato APA 7
    doc = SimpleDocTemplate(response, pagesize=A4, 
                            rightMargin=2.54*cm, leftMargin=2.54*cm,
                            topMargin=2.54*cm, bottomMargin=2.54*cm)
    elements = []
    
    # Estilos APA 7
    styles = getSampleStyleSheet()
    
    # Título principal - Times New Roman 12pt, negrita, centrado
    title_style = ParagraphStyle(
        'APATitle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        textColor=colors.black,
        spaceAfter=12,
        alignment=TA_CENTER,
        leading=14.4,  # 1.2 line spacing
    )
    
    # Subtítulo - Times New Roman 12pt, centrado
    subtitle_style = ParagraphStyle(
        'APASubtitle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        textColor=colors.black,
        spaceAfter=18,
        alignment=TA_CENTER,
        leading=14.4,
    )
    
    # Encabezado de sección - Times New Roman 12pt, negrita, alineado izquierda
    heading_style = ParagraphStyle(
        'APAHeading',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        textColor=colors.black,
        spaceAfter=12,
        spaceBefore=12,
        alignment=TA_LEFT,
        leading=14.4,
    )
    
    # Texto normal - Times New Roman 12pt
    normal_style = ParagraphStyle(
        'APANormal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        textColor=colors.black,
        spaceAfter=6,
        alignment=TA_LEFT,
        leading=14.4,
    )
    
    # Título del documento
    elements.append(Paragraph('<b>Reporte de Vacaciones</b>', title_style))
    
    # Información del período
    meses_esp = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
        7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    periodo_texto = f"Período: {meses_esp.get(mes_seleccionado, '')} {año_seleccionado}"
    elements.append(Paragraph(periodo_texto, subtitle_style))
    elements.append(Spacer(1, 24))
    
    # Estadísticas resumidas (texto, no tabla)
    aprobadas = solicitudes.filter(estado='APROBADO_RH').count()
    rechazadas = solicitudes.filter(estado__in=['RECHAZADO_JEFE', 'RECHAZADO_RH', 'RECHAZADO_ADMIN']).count()
    pendientes = solicitudes.filter(estado__in=['PENDIENTE_JEFE', 'PENDIENTE_RH', 'PENDIENTE_ADMIN']).count()
    total_dias = solicitudes.filter(estado='APROBADO_RH').aggregate(
        total=Sum('dias_solicitados')
    )['total'] or 0
    
    stats_text = (
        f"<b>Resumen:</b> Se registraron {solicitudes.count()} solicitudes de vacaciones. "
        f"De estas, {aprobadas} fueron aprobadas ({total_dias} días en total), "
        f"{rechazadas} fueron rechazadas y {pendientes} permanecen pendientes."
    )
    elements.append(Paragraph(stats_text, normal_style))
    elements.append(Spacer(1, 18))
    
    # Tabla de solicitudes
    if solicitudes.exists():
        elements.append(Paragraph('<b>Detalle de Solicitudes</b>', heading_style))
        
        # Encabezados
        data = [['Empleado', 'Departamento', 'Período', 'Días', 'Estado', 'Fecha Solicitud']]
        
        # Estilo para celdas de tabla
        cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=10,
            textColor=colors.black,
            leading=12,
            alignment=TA_LEFT,
        )
        
        cell_style_center = ParagraphStyle(
            'TableCellCenter',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=10,
            textColor=colors.black,
            leading=12,
            alignment=TA_CENTER,
        )
        
        # Encabezados con Paragraph para mejor control
        header_data = [
            Paragraph('<b>Empleado</b>', cell_style),
            Paragraph('<b>Departamento</b>', cell_style),
            Paragraph('<b>Período</b>', cell_style),
            Paragraph('<b>Días</b>', cell_style_center),
            Paragraph('<b>Estado</b>', cell_style),
            Paragraph('<b>Fecha Solicitud</b>', cell_style),
        ]
        data = [header_data]
        
        # Datos con Paragraph para permitir word wrap
        for solicitud in solicitudes:
            periodo = f"{solicitud.fecha_inicio.strftime('%d/%m/%Y')} - {solicitud.fecha_fin.strftime('%d/%m/%Y')}"
            estado_display = solicitud.get_estado_display()
            fecha_solicitud = solicitud.fecha_solicitud.strftime('%d/%m/%Y')
            
            # Truncar nombres muy largos para evitar desbordamiento
            nombre_empleado = solicitud.empleado.nombre_completo
            if len(nombre_empleado) > 30:
                nombre_empleado = nombre_empleado[:27] + '...'
            
            depto = solicitud.empleado.departamento.nombre if solicitud.empleado.departamento else 'N/A'
            if len(depto) > 25:
                depto = depto[:22] + '...'
            
            # Truncar estado si es muy largo
            if len(estado_display) > 25:
                estado_display = estado_display[:22] + '...'
            
            data.append([
                Paragraph(nombre_empleado, cell_style),
                Paragraph(depto, cell_style),
                Paragraph(periodo, cell_style),
                Paragraph(str(solicitud.dias_solicitados), cell_style_center),
                Paragraph(estado_display, cell_style),
                Paragraph(fecha_solicitud, cell_style),
            ])
        
        # Crear tabla con estilo profesional y sencillo - ajustar anchos para que quepa todo
        # Ancho total disponible: A4 - márgenes = 21cm - 5.08cm = 15.92cm
        # Distribución optimizada: 3.5 + 2.5 + 3 + 1.2 + 3 + 2.72 = 15.92cm
        table = Table(data, colWidths=[3.5*cm, 2.5*cm, 3*cm, 1.2*cm, 3*cm, 2.72*cm])
        table.setStyle(TableStyle([
            # Encabezado - fondo gris oscuro profesional con texto blanco bien visible
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),  # Gris oscuro profesional
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Texto blanco para máximo contraste
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),  # Tamaño ligeramente mayor para mejor legibilidad
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('LEFTPADDING', (0, 0), (-1, 0), 6),
            ('RIGHTPADDING', (0, 0), (-1, 0), 6),
            # Cuerpo de la tabla
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Columna de Días centrada
            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # Texto negro en el cuerpo
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),  # Bordes grises claros
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#2d3748')),  # Línea más gruesa bajo encabezado
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación vertical centrada
            ('LEFTPADDING', (0, 1), (-1, -1), 6),
            ('RIGHTPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            # Filas alternadas para mejor legibilidad
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph('No se registraron solicitudes de vacaciones en este período.', normal_style))
    
    # Pie de página con fecha de generación
    elements.append(Spacer(1, 24))
    meses_esp_footer = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
        7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    fecha_actual = timezone.now()
    fecha_generacion = f"{fecha_actual.day} de {meses_esp_footer.get(fecha_actual.month, '')} de {fecha_actual.year}, {fecha_actual.strftime('%H:%M')}"
    footer_text = f"<i>Documento generado el {fecha_generacion}</i>"
    footer_style = ParagraphStyle(
        'APAFooter',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceBefore=12,
    )
    elements.append(Paragraph(footer_text, footer_style))
    
    # Construir PDF
    doc.build(elements)
    return response


@login_required
def generar_excel_reporte_vacaciones(request):
    """Generar Excel del reporte de vacaciones por mes y año con formato profesional"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
    except ImportError:
        # Si openpyxl no está instalado, generar CSV como fallback
        return generar_excel_reporte_vacaciones_csv(request)
    
    # Obtener mes y año de los parámetros GET, o usar el mes actual por defecto
    hoy = timezone.now().date()
    mes_seleccionado = request.GET.get('mes', hoy.month)
    año_seleccionado = request.GET.get('año', hoy.year)
    
    try:
        mes_seleccionado = int(mes_seleccionado)
        año_seleccionado = int(año_seleccionado)
        
        if mes_seleccionado < 1 or mes_seleccionado > 12:
            mes_seleccionado = hoy.month
        if año_seleccionado < 2000 or año_seleccionado > 2100:
            año_seleccionado = hoy.year
            
        primer_dia_mes = date(año_seleccionado, mes_seleccionado, 1)
        if mes_seleccionado == 12:
            ultimo_dia_mes = date(año_seleccionado + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia_mes = date(año_seleccionado, mes_seleccionado + 1, 1) - timedelta(days=1)
    except (ValueError, TypeError):
        primer_dia_mes = hoy.replace(day=1)
        if primer_dia_mes.month == 12:
            ultimo_dia_mes = date(primer_dia_mes.year + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia_mes = date(primer_dia_mes.year, primer_dia_mes.month + 1, 1) - timedelta(days=1)
        mes_seleccionado = primer_dia_mes.month
        año_seleccionado = primer_dia_mes.year
    
    # Obtener todas las solicitudes del mes seleccionado
    solicitudes = SolicitudVacaciones.objects.filter(
        fecha_solicitud__gte=primer_dia_mes,
        fecha_solicitud__lte=ultimo_dia_mes
    ).select_related(
        'empleado', 'empleado__departamento', 'aprobado_por_jefe', 'aprobado_por_rh'
    ).order_by('-fecha_solicitud')
    
    # Crear libro de trabajo Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte de Vacaciones"
    
    # Estilos
    title_font = Font(name='Calibri', size=16, bold=True, color='FFFFFF')
    subtitle_font = Font(name='Calibri', size=12, bold=False, color='000000')
    header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
    normal_font = Font(name='Calibri', size=10, color='000000')
    summary_label_font = Font(name='Calibri', size=11, bold=True, color='000000')
    
    title_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
    header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    summary_fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
    
    center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
    left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)
    
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Encabezado del documento
    meses_esp = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
        7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    
    row = 1
    # Título principal
    ws.merge_cells(f'A{row}:O{row}')
    cell = ws[f'A{row}']
    cell.value = 'Reporte de Vacaciones'
    cell.font = title_font
    cell.fill = title_fill
    cell.alignment = center_align
    cell.border = thin_border
    ws.row_dimensions[row].height = 25
    
    row += 1
    # Período
    ws.merge_cells(f'A{row}:O{row}')
    cell = ws[f'A{row}']
    cell.value = f'Período: {meses_esp.get(mes_seleccionado, "")} {año_seleccionado}'
    cell.font = subtitle_font
    cell.alignment = center_align
    
    row += 1
    # Fecha de generación
    ws.merge_cells(f'A{row}:O{row}')
    cell = ws[f'A{row}']
    fecha_actual = timezone.now()
    cell.value = f'Fecha de generación: {fecha_actual.strftime("%d/%m/%Y %H:%M")}'
    cell.font = subtitle_font
    cell.alignment = center_align
    
    row += 2  # Línea en blanco
    
    # Estadísticas resumidas
    aprobadas = solicitudes.filter(estado='APROBADO_RH').count()
    rechazadas = solicitudes.filter(estado__in=['RECHAZADO_JEFE', 'RECHAZADO_RH', 'RECHAZADO_ADMIN']).count()
    pendientes = solicitudes.filter(estado__in=['PENDIENTE_JEFE', 'PENDIENTE_RH', 'PENDIENTE_ADMIN']).count()
    total_dias = solicitudes.filter(estado='APROBADO_RH').aggregate(
        total=Sum('dias_solicitados')
    )['total'] or 0
    
    # Título de resumen
    ws.merge_cells(f'A{row}:B{row}')
    cell = ws[f'A{row}']
    cell.value = 'Resumen'
    cell.font = summary_label_font
    cell.fill = summary_fill
    cell.alignment = left_align
    cell.border = thin_border
    
    row += 1
    # Estadísticas
    stats = [
        ['Total de Solicitudes', solicitudes.count()],
        ['Aprobadas', aprobadas],
        ['Días Aprobados (Total)', total_dias],
        ['Rechazadas', rechazadas],
        ['Pendientes', pendientes],
    ]
    
    for stat_label, stat_value in stats:
        ws[f'A{row}'] = stat_label
        ws[f'A{row}'].font = summary_label_font
        ws[f'A{row}'].alignment = left_align
        ws[f'A{row}'].border = thin_border
        
        ws[f'B{row}'] = stat_value
        ws[f'B{row}'].font = normal_font
        ws[f'B{row}'].alignment = left_align
        ws[f'B{row}'].border = thin_border
        row += 1
    
    row += 1  # Línea en blanco
    
    # Encabezados de la tabla (en negritas)
    headers = [
        'Empleado', 'Número de Empleado', 'Departamento', 'Puesto',
        'Fecha Inicio', 'Fecha Fin', 'Días Solicitados', 'Tipo de Vacación',
        'Estado', 'Fecha Solicitud', 'Aprobado por Jefe', 'Fecha Aprobación Jefe',
        'Aprobado por RH', 'Fecha Aprobación RH', 'Motivo'
    ]
    
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col_idx)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border
    
    ws.row_dimensions[row].height = 20
    
    row += 1
    
    # Escribir datos
    for solicitud in solicitudes:
        data_row = [
            solicitud.empleado.nombre_completo,
            solicitud.empleado.numero_empleado or 'N/A',
            solicitud.empleado.departamento.nombre if solicitud.empleado.departamento else 'N/A',
            solicitud.empleado.puesto or 'N/A',
            solicitud.fecha_inicio.strftime('%d/%m/%Y'),
            solicitud.fecha_fin.strftime('%d/%m/%Y'),
            solicitud.dias_solicitados,
            solicitud.get_tipo_display(),
            solicitud.get_estado_display(),
            solicitud.fecha_solicitud.strftime('%d/%m/%Y %H:%M'),
            solicitud.aprobado_por_jefe.nombre_completo if solicitud.aprobado_por_jefe else 'N/A',
            solicitud.fecha_aprobacion_jefe.strftime('%d/%m/%Y %H:%M') if solicitud.fecha_aprobacion_jefe else 'N/A',
            solicitud.aprobado_por_rh.nombre_completo if solicitud.aprobado_por_rh else 'N/A',
            solicitud.fecha_aprobacion_rh.strftime('%d/%m/%Y %H:%M') if solicitud.fecha_aprobacion_rh else 'N/A',
            solicitud.motivo.replace('\n', ' ').replace('\r', ' ') if solicitud.motivo else 'N/A',
        ]
        
        for col_idx, value in enumerate(data_row, start=1):
            cell = ws.cell(row=row, column=col_idx)
            cell.value = value
            cell.font = normal_font
            cell.alignment = left_align if col_idx != 7 else center_align  # Días centrado
            cell.border = thin_border
        
        row += 1
    
    # Ajustar ancho de columnas
    column_widths = [20, 15, 18, 15, 12, 12, 10, 15, 20, 18, 20, 18, 20, 18, 30]
    for col_idx, width in enumerate(column_widths, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width
    
    # Crear respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="reporte_vacaciones_{año_seleccionado}_{mes_seleccionado:02d}.xlsx"'
    
    wb.save(response)
    return response


def generar_excel_reporte_vacaciones_csv(request):
    """Fallback: Generar CSV si openpyxl no está disponible"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    # Obtener mes y año de los parámetros GET, o usar el mes actual por defecto
    hoy = timezone.now().date()
    mes_seleccionado = request.GET.get('mes', hoy.month)
    año_seleccionado = request.GET.get('año', hoy.year)
    
    try:
        mes_seleccionado = int(mes_seleccionado)
        año_seleccionado = int(año_seleccionado)
        
        if mes_seleccionado < 1 or mes_seleccionado > 12:
            mes_seleccionado = hoy.month
        if año_seleccionado < 2000 or año_seleccionado > 2100:
            año_seleccionado = hoy.year
            
        primer_dia_mes = date(año_seleccionado, mes_seleccionado, 1)
        if mes_seleccionado == 12:
            ultimo_dia_mes = date(año_seleccionado + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia_mes = date(año_seleccionado, mes_seleccionado + 1, 1) - timedelta(days=1)
    except (ValueError, TypeError):
        primer_dia_mes = hoy.replace(day=1)
        if primer_dia_mes.month == 12:
            ultimo_dia_mes = date(primer_dia_mes.year + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia_mes = date(primer_dia_mes.year, primer_dia_mes.month + 1, 1) - timedelta(days=1)
        mes_seleccionado = primer_dia_mes.month
        año_seleccionado = primer_dia_mes.year
    
    # Obtener todas las solicitudes del mes seleccionado
    solicitudes = SolicitudVacaciones.objects.filter(
        fecha_solicitud__gte=primer_dia_mes,
        fecha_solicitud__lte=ultimo_dia_mes
    ).select_related(
        'empleado', 'empleado__departamento', 'aprobado_por_jefe', 'aprobado_por_rh'
    ).order_by('-fecha_solicitud')
    
    # Crear respuesta HTTP con CSV (compatible con Excel)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="reporte_vacaciones_{año_seleccionado}_{mes_seleccionado:02d}.csv"'
    
    # Agregar BOM para Excel (UTF-8 con BOM)
    response.write('\ufeff')
    
    # Escribir encabezados con formato profesional
    import csv
    writer = csv.writer(response)
    
    # Encabezado del documento
    meses_esp = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
        7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    writer.writerow(['Reporte de Vacaciones'])
    writer.writerow([f'Período: {meses_esp.get(mes_seleccionado, "")} {año_seleccionado}'])
    writer.writerow([f'Fecha de generación: {timezone.now().strftime("%d/%m/%Y %H:%M")}'])
    writer.writerow([])  # Línea en blanco
    
    # Estadísticas resumidas
    aprobadas = solicitudes.filter(estado='APROBADO_RH').count()
    rechazadas = solicitudes.filter(estado__in=['RECHAZADO_JEFE', 'RECHAZADO_RH', 'RECHAZADO_ADMIN']).count()
    pendientes = solicitudes.filter(estado__in=['PENDIENTE_JEFE', 'PENDIENTE_RH', 'PENDIENTE_ADMIN']).count()
    total_dias = solicitudes.filter(estado='APROBADO_RH').aggregate(
        total=Sum('dias_solicitados')
    )['total'] or 0
    
    writer.writerow(['Resumen'])
    writer.writerow(['Total de Solicitudes', solicitudes.count()])
    writer.writerow(['Aprobadas', aprobadas])
    writer.writerow(['Días Aprobados (Total)', total_dias])
    writer.writerow(['Rechazadas', rechazadas])
    writer.writerow(['Pendientes', pendientes])
    writer.writerow([])  # Línea en blanco
    
    # Encabezados de la tabla
    writer.writerow([
        'Empleado', 'Número de Empleado', 'Departamento', 'Puesto',
        'Fecha Inicio', 'Fecha Fin', 'Días Solicitados', 'Tipo de Vacación',
        'Estado', 'Fecha Solicitud', 'Aprobado por Jefe', 'Fecha Aprobación Jefe',
        'Aprobado por RH', 'Fecha Aprobación RH', 'Motivo'
    ])
    
    # Escribir datos
    for solicitud in solicitudes:
        writer.writerow([
            solicitud.empleado.nombre_completo,
            solicitud.empleado.numero_empleado or 'N/A',
            solicitud.empleado.departamento.nombre if solicitud.empleado.departamento else 'N/A',
            solicitud.empleado.puesto or 'N/A',
            solicitud.fecha_inicio.strftime('%d/%m/%Y'),
            solicitud.fecha_fin.strftime('%d/%m/%Y'),
            solicitud.dias_solicitados,
            solicitud.get_tipo_display(),
            solicitud.get_estado_display(),
            solicitud.fecha_solicitud.strftime('%d/%m/%Y %H:%M'),
            solicitud.aprobado_por_jefe.nombre_completo if solicitud.aprobado_por_jefe else 'N/A',
            solicitud.fecha_aprobacion_jefe.strftime('%d/%m/%Y %H:%M') if solicitud.fecha_aprobacion_jefe else 'N/A',
            solicitud.aprobado_por_rh.nombre_completo if solicitud.aprobado_por_rh else 'N/A',
            solicitud.fecha_aprobacion_rh.strftime('%d/%m/%Y %H:%M') if solicitud.fecha_aprobacion_rh else 'N/A',
            solicitud.motivo.replace('\n', ' ').replace('\r', ' ') if solicitud.motivo else 'N/A',
        ])
    
    return response


# === GESTIÓN DE HISTORIAL DE VACACIONES (RH Y ADMIN) ===

@login_required
def historial_vacaciones_lista(request):
    """Lista de empleados para ver su historial de vacaciones"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin() or perfil.es_jefe_area()):
        raise PermissionDenied
    
    # RH y Admin: ven a todos los empleados activos
    empleados = Perfil.objects.filter(activo=True)

    # Jefe de área: solo ve empleados que tiene asignados como supervisor
    if perfil.es_jefe_area():
        empleados = empleados.filter(supervisor=perfil)

    empleados = empleados.order_by('usuario__last_name', 'usuario__first_name')
    
    # Buscar si hay un parámetro de búsqueda
    query = request.GET.get('q', '')
    if query:
        empleados = empleados.filter(
            Q(usuario__first_name__icontains=query) |
            Q(usuario__last_name__icontains=query) |
            Q(numero_empleado__icontains=query)
        )
    
    context = {
        'empleados': empleados,
        'perfil': perfil,
        'query': query,
    }
    return render(request, 'empleados/rh/historial_vacaciones_lista.html', context)


@login_required
def historial_vacaciones_empleado(request, empleado_id):
    """Ver historial de vacaciones de un empleado específico, agrupado por años"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin() or perfil.es_jefe_area()):
        raise PermissionDenied
    
    empleado = get_object_or_404(Perfil, pk=empleado_id)

    # Si es jefe de área, solo puede ver historial de empleados que supervisa
    if perfil.es_jefe_area() and empleado.supervisor_id != perfil.id:
        raise PermissionDenied
    from datetime import date
    from collections import defaultdict
    
    # Obtener todo el historial ordenado
    historial_completo = HistorialVacaciones.objects.filter(empleado=empleado).order_by('fecha_registro', 'fecha_creacion')
    
    # Obtener año seleccionado (si existe)
    año_seleccionado = request.GET.get('año', None)
    if año_seleccionado:
        try:
            año_seleccionado = int(año_seleccionado)
            historial = historial_completo.filter(fecha_registro__year=año_seleccionado)
        except (ValueError, TypeError):
            año_seleccionado = None
            historial = historial_completo
    else:
        historial = historial_completo
    
    # Agrupar historial por años
    historial_por_ano = defaultdict(list)
    años_disponibles = set()
    
    for registro in historial_completo:
        año = registro.fecha_registro.year
        años_disponibles.add(año)
        historial_por_ano[año].append(registro)
    
    # Calcular totales por año (vacaciones normales y extraordinarias)
    from decimal import Decimal
    resumen_por_ano = {}
    
    for año, registros in historial_por_ano.items():
        total_normales = Decimal('0')
        total_extraordinarias = Decimal('0')
        
        for r in registros:
            # Incluir ajustes manuales
            if r.tipo_movimiento == 'AJUSTE_MANUAL':
                if 'normales' in r.concepto.lower():
                    total_normales += r.tomadas
                elif 'extraordinarias' in r.concepto.lower():
                    total_extraordinarias += r.tomadas
            # Vacaciones normales: tipo VACACIONES_TOMADAS que no sean extraordinarias
            elif r.tipo_movimiento == 'VACACIONES_TOMADAS' and 'EXTRAORDINARIA' not in r.concepto.upper():
                total_normales += r.tomadas
            # Vacaciones extraordinarias
            elif ('EXTRAORDINARIA' in r.concepto.upper() or 
                  r.tipo_movimiento == 'VACACIONES_ANTES_REGISTRO' or
                  'EMERGENCIA' in r.concepto.upper()):
                total_extraordinarias += r.tomadas
        
        total_con_derecho = sum(r.con_derecho for r in registros)
        
        # Obtener el último saldo del año
        ultimo_registro = max(registros, key=lambda r: (r.fecha_registro, r.fecha_creacion))
        saldo_final_ano = ultimo_registro.saldo
        
        resumen_por_ano[año] = {
            'total_normales': total_normales,
            'total_extraordinarias': total_extraordinarias,
            'total_con_derecho': total_con_derecho,
            'saldo_final': saldo_final_ano,
            'cantidad_registros': len(registros)
        }
    
    # Obtener solicitudes de vacaciones extraordinarias aprobadas este año
    solicitudes_extraordinarias_ano = SolicitudVacaciones.objects.filter(
        empleado=empleado,
        tipo__in=['EXTRAORDINARIA', 'EMERGENCIA'],
        estado='APROBADO_RH',
        fecha_aprobacion_rh__year=date.today().year
    ).order_by('-fecha_aprobacion_rh')
    
    total_extraordinarias_ano = sum(s.dias_solicitados for s in solicitudes_extraordinarias_ano)
    
    context = {
        'empleado': empleado,
        'historial': historial,
        'historial_completo': historial_completo,
        'historial_por_ano': dict(sorted(historial_por_ano.items())),
        'resumen_por_ano': dict(sorted(resumen_por_ano.items())),
        'años_disponibles': sorted(años_disponibles, reverse=True),
        'año_seleccionado': año_seleccionado,
        'perfil': perfil,
        'solicitudes_extraordinarias_ano': solicitudes_extraordinarias_ano,
        'total_extraordinarias_ano': total_extraordinarias_ano,
    }
    return render(request, 'empleados/rh/historial_vacaciones_empleado.html', context)


@login_required
def crear_historial_vacaciones(request, empleado_id):
    """Crear un nuevo registro en el historial de vacaciones"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    empleado = get_object_or_404(Perfil, pk=empleado_id)
    
    if request.method == 'POST':
        concepto = request.POST.get('concepto', '')
        tipo_movimiento = request.POST.get('tipo_movimiento', 'VACACIONES_TOMADAS')
        fecha_registro = request.POST.get('fecha_registro', '')
        fecha_inicial = request.POST.get('fecha_inicial', '') or None
        fecha_final = request.POST.get('fecha_final', '') or None
        tomadas = request.POST.get('tomadas', '0') or '0'
        con_derecho = request.POST.get('con_derecho', '0') or '0'
        observaciones = request.POST.get('observaciones', '')
        
        try:
            from decimal import Decimal
            historial = HistorialVacaciones.objects.create(
                empleado=empleado,
                concepto=concepto,
                tipo_movimiento=tipo_movimiento,
                fecha_registro=datetime.strptime(fecha_registro, '%Y-%m-%d').date() if fecha_registro else date.today(),
                fecha_inicial=datetime.strptime(fecha_inicial, '%Y-%m-%d').date() if fecha_inicial else None,
                fecha_final=datetime.strptime(fecha_final, '%Y-%m-%d').date() if fecha_final else None,
                tomadas=Decimal(tomadas),
                con_derecho=Decimal(con_derecho),
                observaciones=observaciones,
                creado_por=perfil,
            )
            messages.success(request, 'Registro de historial creado exitosamente.')
            return redirect('empleados:historial_vacaciones_empleado', empleado_id=empleado_id)
        except Exception as e:
            messages.error(request, f'Error al crear el registro: {str(e)}')
    
    context = {
        'empleado': empleado,
        'perfil': perfil,
        'tipos_movimiento': HistorialVacaciones.TIPOS_MOVIMIENTO,
    }
    return render(request, 'empleados/rh/crear_historial_vacaciones.html', context)


@login_required
def editar_historial_vacaciones(request, historial_id):
    """Editar un registro del historial de vacaciones"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    historial = get_object_or_404(HistorialVacaciones, pk=historial_id)
    
    if request.method == 'POST':
        historial.concepto = request.POST.get('concepto', '')
        historial.tipo_movimiento = request.POST.get('tipo_movimiento', 'VACACIONES_TOMADAS')
        fecha_registro = request.POST.get('fecha_registro', '')
        fecha_inicial = request.POST.get('fecha_inicial', '') or None
        fecha_final = request.POST.get('fecha_final', '') or None
        tomadas = request.POST.get('tomadas', '0') or '0'
        con_derecho = request.POST.get('con_derecho', '0') or '0'
        historial.observaciones = request.POST.get('observaciones', '')
        
        try:
            from decimal import Decimal
            if fecha_registro:
                historial.fecha_registro = datetime.strptime(fecha_registro, '%Y-%m-%d').date()
            if fecha_inicial:
                historial.fecha_inicial = datetime.strptime(fecha_inicial, '%Y-%m-%d').date()
            else:
                historial.fecha_inicial = None
            if fecha_final:
                historial.fecha_final = datetime.strptime(fecha_final, '%Y-%m-%d').date()
            else:
                historial.fecha_final = None
            historial.tomadas = Decimal(tomadas)
            historial.con_derecho = Decimal(con_derecho)
            historial.save()
            messages.success(request, 'Registro de historial actualizado exitosamente.')
            return redirect('empleados:historial_vacaciones_empleado', empleado_id=historial.empleado.id)
        except Exception as e:
            messages.error(request, f'Error al actualizar el registro: {str(e)}')
    
    context = {
        'historial': historial,
        'perfil': perfil,
        'tipos_movimiento': HistorialVacaciones.TIPOS_MOVIMIENTO,
    }
    return render(request, 'empleados/rh/editar_historial_vacaciones.html', context)


@login_required
def eliminar_historial_vacaciones(request, historial_id):
    """Eliminar un registro del historial de vacaciones"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    historial = get_object_or_404(HistorialVacaciones, pk=historial_id)
    empleado_id = historial.empleado.id
    
    if request.method == 'POST':
        historial.delete()
        messages.success(request, 'Registro de historial eliminado exitosamente.')
        return redirect('empleados:historial_vacaciones_empleado', empleado_id=empleado_id)
    
    context = {
        'historial': historial,
        'perfil': perfil,
    }
    return render(request, 'empleados/rh/eliminar_historial_vacaciones.html', context)


# === EDICIÓN DE VACACIONES DE EMPLEADOS (RH Y ADMIN) ===

@login_required
def editar_vacaciones_empleado(request, empleado_id):
    """Editar vacaciones de un empleado específico"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    empleado = get_object_or_404(Perfil, pk=empleado_id)
    
    if request.method == 'POST':
        try:
            # Obtener valores del formulario
            dias_usados = int(request.POST.get('dias_vacaciones_usados', 0) or 0)
            dias_extraordinarios = int(request.POST.get('dias_vacaciones_extraordinarios', 0) or 0)
            dias_acumulados = int(request.POST.get('dias_vacaciones_acumulados', 0) or 0)
            dias_extraordinarios_ano_anterior = int(request.POST.get('dias_vacaciones_extraordinarios_ano_anterior', 0) or 0)
            dias_anuales = int(request.POST.get('dias_vacaciones_anuales', 0) or 0)
            
            # Actualizar campos
            empleado.dias_vacaciones_usados = max(0, dias_usados)
            empleado.dias_vacaciones_extraordinarios = max(0, dias_extraordinarios)
            empleado.dias_vacaciones_acumulados = max(0, dias_acumulados)
            empleado.dias_vacaciones_extraordinarios_ano_anterior = max(0, dias_extraordinarios_ano_anterior)
            
            # Si se especificaron días anuales, actualizarlos
            if dias_anuales > 0:
                empleado.dias_vacaciones_anuales = dias_anuales
            
            empleado.save(update_fields=[
                'dias_vacaciones_usados',
                'dias_vacaciones_extraordinarios',
                'dias_vacaciones_acumulados',
                'dias_vacaciones_extraordinarios_ano_anterior',
                'dias_vacaciones_anuales'
            ])
            
            messages.success(request, f'Vacaciones de {empleado.nombre_completo} actualizadas exitosamente.')
            return redirect('empleados:editar_vacaciones_empleado', empleado_id=empleado_id)
        except Exception as e:
            messages.error(request, f'Error al actualizar las vacaciones: {str(e)}')
    
    # Calcular información para mostrar
    antiguedad_anos = empleado.antiguedad_anos
    dias_anuales_calculados = empleado.dias_vacaciones_segun_antiguedad
    dias_disponibles = empleado.dias_vacaciones_disponibles
    total_disponible_proyectado = empleado.calcular_total_disponible_proyectado()
    
    # Obtener solicitudes de vacaciones extraordinarias aprobadas este año
    from datetime import date
    solicitudes_extraordinarias_ano = SolicitudVacaciones.objects.filter(
        empleado=empleado,
        tipo__in=['EXTRAORDINARIA', 'EMERGENCIA'],
        estado='APROBADO_RH',
        fecha_aprobacion_rh__year=date.today().year
    ).order_by('-fecha_aprobacion_rh')
    
    total_extraordinarias_ano = sum(s.dias_solicitados for s in solicitudes_extraordinarias_ano)
    
    # Calcular historial según LFT 2023
    historial_lft, saldo_final_lft = empleado.calcular_vacaciones_lft()
    
    # Verificar si el empleado tiene menos de 1 año (año 0)
    fecha_ingreso = empleado.fecha_contratacion
    tiene_ano_0 = False
    aniversario_ano = None
    if fecha_ingreso:
        años_completos = empleado.calcular_antiguedad_actual(date.today())
        tiene_ano_0 = años_completos == 0
        aniversario_ano = fecha_ingreso.year + 1
    
    context = {
        'empleado': empleado,
        'perfil': perfil,
        'antiguedad_anos': antiguedad_anos,
        'dias_anuales_calculados': dias_anuales_calculados,
        'dias_disponibles': dias_disponibles,
        'total_disponible_proyectado': total_disponible_proyectado,
        'solicitudes_extraordinarias_ano': solicitudes_extraordinarias_ano,
        'total_extraordinarias_ano': total_extraordinarias_ano,
        'historial_lft': historial_lft,
        'saldo_final_lft': saldo_final_lft,
        'tiene_ano_0': tiene_ano_0,
        'fecha_ingreso': fecha_ingreso,
        'aniversario_ano': aniversario_ano,
    }
    return render(request, 'empleados/rh/editar_vacaciones_empleado.html', context)


@login_required
def editar_vacaciones_por_ano(request, empleado_id, año):
    """Editar vacaciones normales y extraordinarias de un año específico"""
    perfil = get_user_profile(request.user)
    if not perfil or not (perfil.es_rh() or perfil.es_admin()):
        raise PermissionDenied
    
    empleado = get_object_or_404(Perfil, pk=empleado_id)
    
    try:
        año = int(año)
    except (ValueError, TypeError):
        messages.error(request, 'Año inválido.')
        return redirect('empleados:historial_vacaciones_empleado', empleado_id=empleado_id)
    
    from datetime import date
    from collections import defaultdict
    from decimal import Decimal
    
    # Obtener parámetros de filtro por período (mes y año)
    mes_filtro = request.GET.get('mes', None)
    año_filtro = request.GET.get('año_filtro', año)
    
    try:
        if mes_filtro:
            mes_filtro = int(mes_filtro)
        if año_filtro:
            año_filtro = int(año_filtro)
    except (ValueError, TypeError):
        mes_filtro = None
        año_filtro = año
    
    # Obtener todos los registros del año seleccionado
    registros_ano_completo = HistorialVacaciones.objects.filter(
        empleado=empleado,
        fecha_registro__year=año
    ).order_by('fecha_registro', 'fecha_creacion')
    
    # Filtrar por período si se especificó
    if mes_filtro and año_filtro:
        registros_ano = registros_ano_completo.filter(
            fecha_registro__year=año_filtro,
            fecha_registro__month=mes_filtro
        )
    else:
        registros_ano = registros_ano_completo
    
    # Calcular totales actuales del año completo (incluyendo ajustes manuales)
    total_normales_actual = Decimal('0')
    total_extraordinarias_actual = Decimal('0')
    
    for r in registros_ano_completo:
        # Excluir ajustes manuales del cálculo base (se sumarán después si es necesario)
        if r.tipo_movimiento == 'AJUSTE_MANUAL':
            if 'normales' in r.concepto.lower():
                # Los ajustes de normales ya están incluidos en el total si son positivos
                # Si son negativos, restan del total
                total_normales_actual += r.tomadas
            elif 'extraordinarias' in r.concepto.lower():
                total_extraordinarias_actual += r.tomadas
        elif r.tipo_movimiento == 'VACACIONES_TOMADAS' and 'EXTRAORDINARIA' not in r.concepto.upper():
            total_normales_actual += r.tomadas
        elif ('EXTRAORDINARIA' in r.concepto.upper() or 
              r.tipo_movimiento == 'VACACIONES_ANTES_REGISTRO' or
              'EMERGENCIA' in r.concepto.upper()):
            total_extraordinarias_actual += r.tomadas
    
    # Calcular totales del período filtrado (si hay filtro)
    total_normales_periodo = Decimal('0')
    total_extraordinarias_periodo = Decimal('0')
    
    if mes_filtro and año_filtro:
        for r in registros_ano:
            if r.tipo_movimiento == 'AJUSTE_MANUAL':
                if 'normales' in r.concepto.lower():
                    total_normales_periodo += r.tomadas
                elif 'extraordinarias' in r.concepto.lower():
                    total_extraordinarias_periodo += r.tomadas
            elif r.tipo_movimiento == 'VACACIONES_TOMADAS' and 'EXTRAORDINARIA' not in r.concepto.upper():
                total_normales_periodo += r.tomadas
            elif ('EXTRAORDINARIA' in r.concepto.upper() or 
                  r.tipo_movimiento == 'VACACIONES_ANTES_REGISTRO' or
                  'EMERGENCIA' in r.concepto.upper()):
                total_extraordinarias_periodo += r.tomadas
    
    if request.method == 'POST':
        try:
            dias_normales = Decimal(request.POST.get('dias_normales', '0') or '0')
            dias_extraordinarias = Decimal(request.POST.get('dias_extraordinarias', '0') or '0')
            observaciones = request.POST.get('observaciones', '').strip()
            
            # Calcular diferencias
            diferencia_normales = dias_normales - total_normales_actual
            diferencia_extraordinarias = dias_extraordinarias - total_extraordinarias_actual
            
            # Si hay diferencia, crear o actualizar registros de ajuste
            if diferencia_normales != 0 or diferencia_extraordinarias != 0:
                # Si hay diferencia en normales, crear un registro de ajuste
                if diferencia_normales != 0:
                    # Buscar si hay un registro de ajuste para este año
                    ajuste_normales = HistorialVacaciones.objects.filter(
                        empleado=empleado,
                        fecha_registro__year=año,
                        concepto__icontains=f'Ajuste vacaciones normales {año}',
                        tipo_movimiento='AJUSTE_MANUAL'
                    ).first()
                    
                    if ajuste_normales:
                        # Actualizar registro existente
                        ajuste_normales.tomadas = diferencia_normales
                        ajuste_normales.observaciones = observaciones or f'Ajuste manual de vacaciones normales para el año {año}. Diferencia: {diferencia_normales:+.3f} días'
                        ajuste_normales.save()
                    else:
                        # Crear nuevo registro de ajuste
                        # Si la diferencia es positiva, significa que se agregaron días (tomadas aumentan)
                        # Si la diferencia es negativa, significa que se quitaron días (tomadas disminuyen)
                        fecha_ajuste = date(año, 12, 31)  # Fecha al final del año
                        HistorialVacaciones.objects.create(
                            empleado=empleado,
                            concepto=f'Ajuste vacaciones normales {año}',
                            tipo_movimiento='AJUSTE_MANUAL',
                            fecha_registro=fecha_ajuste,
                            tomadas=diferencia_normales,  # Puede ser positivo o negativo
                            con_derecho=Decimal('0'),
                            observaciones=observaciones or f'Ajuste manual de vacaciones normales para el año {año}. Total ajustado: {dias_normales} días (diferencia: {diferencia_normales:+.3f} días)',
                            creado_por=perfil
                        )
                
                # Si hay diferencia en extraordinarias, crear un registro de ajuste
                if diferencia_extraordinarias != 0:
                    ajuste_extraordinarias = HistorialVacaciones.objects.filter(
                        empleado=empleado,
                        fecha_registro__year=año,
                        concepto__icontains=f'Ajuste vacaciones extraordinarias {año}',
                        tipo_movimiento='AJUSTE_MANUAL'
                    ).first()
                    
                    if ajuste_extraordinarias:
                        # Actualizar registro existente
                        ajuste_extraordinarias.tomadas = diferencia_extraordinarias
                        ajuste_extraordinarias.observaciones = observaciones or f'Ajuste manual de vacaciones extraordinarias para el año {año}. Diferencia: {diferencia_extraordinarias:+.3f} días'
                        ajuste_extraordinarias.save()
                    else:
                        # Crear nuevo registro de ajuste
                        fecha_ajuste = date(año, 12, 31)  # Fecha al final del año
                        HistorialVacaciones.objects.create(
                            empleado=empleado,
                            concepto=f'Ajuste vacaciones extraordinarias {año}',
                            tipo_movimiento='AJUSTE_MANUAL',
                            fecha_registro=fecha_ajuste,
                            tomadas=diferencia_extraordinarias,  # Puede ser positivo o negativo
                            con_derecho=Decimal('0'),
                            observaciones=observaciones or f'Ajuste manual de vacaciones extraordinarias para el año {año}. Total ajustado: {dias_extraordinarias} días (diferencia: {diferencia_extraordinarias:+.3f} días)',
                            creado_por=perfil
                        )
                
                messages.success(request, f'Vacaciones del año {año} actualizadas exitosamente.')
            else:
                messages.info(request, 'No se realizaron cambios.')
            
            return redirect('empleados:historial_vacaciones_empleado', empleado_id=empleado_id)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar las vacaciones: {str(e)}')
    
    # Obtener años disponibles para el selector
    años_disponibles = HistorialVacaciones.objects.filter(
        empleado=empleado
    ).values_list('fecha_registro__year', flat=True).distinct().order_by('-fecha_registro__year')
    
    # Verificar si el empleado tiene menos de 1 año (año 0)
    from datetime import date
    fecha_ingreso = empleado.fecha_contratacion
    tiene_ano_0 = False
    if fecha_ingreso:
        años_completos = empleado.calcular_antiguedad_actual(date.today())
        tiene_ano_0 = años_completos == 0
    
    # Obtener meses disponibles para el año seleccionado
    meses_disponibles = HistorialVacaciones.objects.filter(
        empleado=empleado,
        fecha_registro__year=año
    ).values_list('fecha_registro__month', flat=True).distinct().order_by('fecha_registro__month')
    
    # Nombres de meses en español
    nombres_meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    # Obtener nombre del mes filtrado si existe
    nombre_mes_filtro = nombres_meses.get(mes_filtro, '') if mes_filtro else ''
    
    # Calcular historial según LFT 2023
    historial_lft, saldo_final_lft = empleado.calcular_vacaciones_lft()
    
    context = {
        'empleado': empleado,
        'año': año,
        'perfil': perfil,
        'registros_ano': registros_ano,
        'registros_ano_completo': registros_ano_completo,
        'total_normales_actual': total_normales_actual,
        'total_extraordinarias_actual': total_extraordinarias_actual,
        'total_normales_periodo': total_normales_periodo,
        'total_extraordinarias_periodo': total_extraordinarias_periodo,
        'años_disponibles': años_disponibles,
        'meses_disponibles': meses_disponibles,
        'nombres_meses': nombres_meses,
        'mes_filtro': mes_filtro,
        'año_filtro': año_filtro,
        'nombre_mes_filtro': nombre_mes_filtro,
        'historial_lft': historial_lft,
        'saldo_final_lft': saldo_final_lft,
        'tiene_ano_0': tiene_ano_0,
        'fecha_ingreso': fecha_ingreso,
    }
    return render(request, 'empleados/rh/editar_vacaciones_por_ano.html', context)


# === VISTAS DE ERROR ===


@login_required
def manual_agregar_equipo(request):
    """Vista para mostrar el manual de usuario sobre cómo agregar equipos"""
    perfil = get_user_profile(request.user)
    
    # Verificar que el usuario tenga permisos de sistemas o admin
    if not perfil or not (perfil.es_sistemas() or perfil.es_admin()):
        messages.error(request, 'No tienes permiso para acceder a esta sección del manual.')
        return redirect('empleados:dashboard')
    
    return render(request, 'empleados/manual/agregar_equipo.html', {
        'perfil': perfil
    })


@login_required
def manual_errores(request):
    """Vista para mostrar el manual de errores comunes y contacto de soporte"""
    perfil = get_user_profile(request.user)
    
    return render(request, 'empleados/manual/errores_soporte.html', {
        'perfil': perfil
    })


def error_403(request, exception=None):
    return render(request, 'empleados/errors/403.html', status=403)

def error_404(request, exception=None):
    return render(request, 'empleados/errors/404.html', status=404)

def error_500(request):
    return render(request, 'empleados/errors/500.html', status=500)