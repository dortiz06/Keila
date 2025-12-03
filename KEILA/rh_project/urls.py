"""
URL configuration for rh_project project.
Sistema de Recursos Humanos - Grupo Keila (Refactorizado)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def redirect_to_dashboard(request):
    """Redirigir a dashboard si el usuario está autenticado"""
    if request.user.is_authenticated:
        return redirect('empleados:dashboard')
    return redirect('empleados:login')

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Aplicación principal
    path('', include(('empleados.urls', 'empleados'), namespace='empleados')),
]

# Manejo de errores personalizados
handler403 = 'empleados.views.error_403'
handler404 = 'empleados.views.error_404'
handler500 = 'empleados.views.error_500'

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
