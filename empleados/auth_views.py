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
    """Vista del perfil del usuario actual"""
    from .models import AsignacionEquipo
    
    try:
        perfil = Perfil.objects.get(usuario=request.user)
        tiene_perfil = True
    except Perfil.DoesNotExist:
        perfil = None
        tiene_perfil = False
    
    # Obtener grupos del usuario para mostrar roles
    grupos = request.user.groups.all()
    
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
        'user': request.user,
        'perfil': perfil,
        'tiene_perfil': tiene_perfil,
        'grupos': grupos,
        'es_rh': es_rh,
        'es_jefe': es_jefe,
        'es_empleado': es_empleado,
        'equipos_asignados': equipos_asignados,
    }
    
    return render(request, 'empleados/perfil_usuario.html', context)
