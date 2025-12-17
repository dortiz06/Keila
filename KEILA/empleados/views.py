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
from .models import Perfil, Departamento, SolicitudVacaciones, ConfiguracionSistema, Ticket, Equipo, AsignacionEquipo
from .forms import (
    UsuarioConPerfilForm, SolicitudVacacionesForm, 
    AprobacionJefeForm, AprobacionAdminForm, AprobacionRHForm, EditarPerfilForm, ConfigurarDepartamentoForm
)
from datetime import date, timedelta
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
    
    # Solicitudes de todos los empleados (jefes pueden gestionar cualquier departamento)
    # Excluir las propias solicitudes del jefe (esas van a admin)
    solicitudes_pendientes = SolicitudVacaciones.objects.filter(
        estado='PENDIENTE_JEFE'
    ).exclude(empleado=perfil).order_by('-fecha_solicitud')
    
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
        # Jefes de área: solo pueden ver empleados de su departamento
        if perfil.departamento:
            empleados = Perfil.objects.filter(
                activo=True,
                departamento=perfil.departamento
            )
        else:
            empleados = Perfil.objects.none()
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
    
    # Ordenamiento
    orden_actual = request.GET.get('orden', 'alfabetico')
    if orden_actual == 'alfabetico':
        empleados = empleados.order_by('usuario__first_name', 'usuario__last_name')
    elif orden_actual == 'area':
        empleados = empleados.order_by('departamento__nombre', 'usuario__first_name', 'usuario__last_name')
    elif orden_actual == 'antiguedad':
        empleados = empleados.order_by('-fecha_contratacion')
    else:
        empleados = empleados.order_by('usuario__first_name', 'usuario__last_name')
    
    # Determinar permisos
    puede_editar = perfil.es_sistemas() or perfil.es_admin()
    puede_crear = perfil.es_sistemas() or perfil.es_admin()  # Solo Sistemas y Admin pueden crear
    es_gestion_completa = perfil.es_sistemas() or perfil.es_admin()  # Para mostrar columnas adicionales
    
    context = {
        'empleados': empleados,
        'departamentos': departamentos,
        'tipo_actual': tipo_perfil,
        'departamento_actual': departamento_id,
        'busqueda_actual': busqueda,
        'orden_actual': orden_actual,
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
                if 'direccion' in form.cleaned_data:
                    perfil_actualizado.direccion = form.cleaned_data['direccion']
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
    
    # Los jefes NO pueden aprobar sus propias solicitudes
    if solicitud.empleado == perfil:
        raise PermissionDenied("No puedes aprobar tu propia solicitud de vacaciones.")
    
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


# === VISTAS DE ERROR ===


def error_403(request, exception=None):
    return render(request, 'empleados/errors/403.html', status=403)

def error_404(request, exception=None):
    return render(request, 'empleados/errors/404.html', status=404)

def error_500(request):
    return render(request, 'empleados/errors/500.html', status=500)