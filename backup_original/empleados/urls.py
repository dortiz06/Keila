from django.urls import path
from . import views
from . import auth_views

urlpatterns = [
    path('', auth_views.login_view, name='index'),
    path('empleados/', views.lista_empleados, name='lista_empleados'),
    path('empleados/<int:empleado_id>/', views.detalle_empleado, name='detalle_empleado'),
    path('vacaciones/', views.vacaciones, name='vacaciones'),
    
    # Autoservicio empleado
    path('mis-vacaciones/', views.mis_vacaciones, name='mis_vacaciones'),
    path('solicitar-vacaciones/', views.solicitar_vacaciones, name='solicitar_vacaciones'),
    
    # Aprobaciones
    path('aprobar-jefe/<int:vacacion_id>/', views.aprobar_jefe, name='aprobar_jefe'),
    path('aprobar-rh/<int:vacacion_id>/', views.aprobar_rh, name='aprobar_rh'),
    
    # Panel de jefes
    path('panel-jefe/', views.panel_jefe, name='panel_jefe'),
    path('solicitudes-jefe/', views.solicitudes_jefe, name='solicitudes_jefe'),
    
    # Gestión de usuarios y roles
    path('gestion-usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('crear-usuario/', views.crear_usuario, name='crear_usuario'),
    path('asignar-rol/<int:user_id>/', views.asignar_rol, name='asignar_rol'),
    
    # API
    path('api/validar-antiguedad/', views.validar_antiguedad, name='validar_antiguedad'),
    
    # Autenticación personalizada
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('perfil/', auth_views.perfil_usuario, name='perfil_usuario'),
    
    # Dashboard principal (solo para usuarios autenticados)
    path('dashboard/', views.index, name='dashboard'),
]
