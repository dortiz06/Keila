from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Perfil
from .csrf_utils import csrf_exempt_for_development, ensure_csrf_cookie_for_development


@ensure_csrf_cookie
@csrf_exempt_for_development
def login_view(request):
    """Vista de login personalizada"""
    if request.user.is_authenticated:
        return redirect('empleados:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'¡Bienvenido, {user.first_name or user.username}!')
                    
                    # Redirigir según el perfil del usuario
                    next_url = request.GET.get('next', 'empleados:dashboard')
                    if next_url == 'empleados:dashboard':
                        # Verificar si tiene perfil
                        try:
                            perfil = Perfil.objects.get(usuario=user)
                            if perfil.es_admin():
                                next_url = 'empleados:admin_dashboard'
                            elif perfil.es_rh():
                                next_url = 'empleados:rh_dashboard'
                            elif perfil.es_jefe_area():
                                next_url = 'empleados:jefe_dashboard'
                            elif perfil.es_sistemas():
                                next_url = 'empleados:sistemas_dashboard'
                            else:
                                next_url = 'empleados:empleado_dashboard'
                        except Perfil.DoesNotExist:
                            # No tiene perfil
                            next_url = 'empleados:dashboard'
                    
                    return redirect(next_url)
                else:
                    messages.error(request, 'Tu cuenta está desactivada.')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    return render(request, 'empleados/login.html')


@login_required
def logout_view(request):
    """Vista de logout personalizada"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('empleados:login')




@login_required
def perfil_usuario(request):
    """Vista del perfil del usuario actual o de otro usuario si se especifica perfil_id"""
    from .models import AsignacionEquipo
    from django.shortcuts import get_object_or_404
    from django.core.exceptions import PermissionDenied
    
    # Obtener perfil del usuario actual
    try:
        perfil_actual = Perfil.objects.get(usuario=request.user)
        tiene_perfil = True
    except Perfil.DoesNotExist:
        perfil_actual = None
        tiene_perfil = False
    
    # Verificar si se solicita ver el perfil de otro usuario
    perfil_id = request.GET.get('perfil_id')
    viene_de_lista = False
    if perfil_id:
        # Verificar permisos para ver otros perfiles
        if not perfil_actual:
            raise PermissionDenied
        
        # Verificar si tiene permiso para ver otros perfiles
        puede_ver_otros = (
            perfil_actual.es_sistemas() or 
            perfil_actual.es_admin() or 
            perfil_actual.es_rh() or 
            perfil_actual.es_jefe_area()
        )
        
        if not puede_ver_otros:
            raise PermissionDenied
        
        # Obtener el perfil solicitado
        perfil_ver = get_object_or_404(Perfil, id=perfil_id)
        
        # Si es jefe de área, solo puede ver empleados de su departamento
        if perfil_actual.es_jefe_area():
            if not perfil_ver.departamento or perfil_ver.departamento != perfil_actual.departamento:
                raise PermissionDenied
        
        perfil = perfil_ver
        es_propio_perfil = (perfil == perfil_actual)
        viene_de_lista = True  # Si hay perfil_id, viene de la lista
    else:
        # Mostrar perfil del usuario actual
        perfil = perfil_actual
        es_propio_perfil = True
        # Verificar si viene de lista usando referer
        referer = request.META.get('HTTP_REFERER', '')
        viene_de_lista = 'lista_empleados' in referer or 'empleados/' in referer
    
    # Obtener grupos del usuario para mostrar roles
    grupos = perfil.usuario.groups.all() if perfil else request.user.groups.all()
    
    # Equipos asignados
    equipos_asignados = None
    if perfil:
        equipos_asignados = AsignacionEquipo.objects.filter(
            empleado=perfil,
            fecha_devolucion__isnull=True
        ).select_related('equipo', 'equipo__categoria')
    
    # Variables para el template
    es_rh = perfil.es_rh() if perfil else False
    es_jefe = perfil.es_jefe_area() if perfil else False
    es_empleado = perfil.es_empleado() if perfil else False
    
    context = {
        'user': perfil.usuario if perfil else request.user,
        'perfil': perfil,
        'tiene_perfil': tiene_perfil,
        'grupos': grupos,
        'es_rh': es_rh,
        'es_jefe': es_jefe,
        'es_empleado': es_empleado,
        'equipos_asignados': equipos_asignados,
        'es_propio_perfil': es_propio_perfil,
        'perfil_actual': perfil_actual,  # Para verificar permisos de edición
        'viene_de_lista': viene_de_lista,  # Para mostrar botón de volver
    }
    
    return render(request, 'empleados/perfil_usuario.html', context)
