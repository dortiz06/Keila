from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from . import auth_views


app_name = 'empleados'

urlpatterns = [
    # === RUTAS PRINCIPALES ===
    path('', auth_views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', auth_views.logout_view, name='logout'),
    
    # === DASHBOARDS POR PERFIL ===
    path('administrador/', views.admin_dashboard, name='admin_dashboard'),
    path('rh/', views.rh_dashboard, name='rh_dashboard'),
    path('jefe/', views.jefe_dashboard, name='jefe_dashboard'),
    path('empleado/', views.empleado_dashboard, name='empleado_dashboard'),
    
    # === GESTIÓN DE USUARIOS ===
    path('usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:perfil_id>/editar/', views.editar_perfil, name='editar_perfil'),
    
    # === GESTIÓN DE VACACIONES ===
    path('vacaciones/', views.mis_vacaciones, name='mis_vacaciones'),
    path('vacaciones/solicitar/', views.solicitar_vacaciones, name='solicitar_vacaciones'),
    path('vacaciones/<int:solicitud_id>/aprobar-jefe/', views.aprobar_jefe, name='aprobar_jefe'),
    path('vacaciones/<int:solicitud_id>/aprobar-rh/', views.aprobar_rh, name='aprobar_rh'),
    path('vacaciones/<int:solicitud_id>/pdf/', views.generar_pdf_vacaciones, name='generar_pdf_vacaciones'),
    path('vacaciones/solicitudes-jefe/', views.solicitudes_jefe, name='solicitudes_jefe'),
    path('vacaciones/solicitudes-rh/', views.solicitudes_rh, name='solicitudes_rh'),
    
    # === GESTIÓN DE DEPARTAMENTOS ===
    path('departamentos/', views.gestion_departamentos, name='gestion_departamentos'),
    path('departamentos/crear/', views.crear_departamento, name='crear_departamento'),
    path('departamentos/<int:departamento_id>/', views.ver_departamento, name='ver_departamento'),
    path('departamentos/<int:departamento_id>/editar/', views.editar_departamento, name='editar_departamento'),
    path('departamentos/<int:departamento_id>/toggle/', views.toggle_departamento, name='toggle_departamento'),
    
    # === TICKETS ===
    path('tickets/', views.mis_tickets, name='mis_tickets'),
    path('tickets/crear/', views.crear_ticket, name='crear_ticket'),
    path('tickets/<int:ticket_id>/', views.detalle_ticket, name='detalle_ticket'),
    
    # === EQUIPOS ===
    path('equipos/', views.mis_equipos, name='mis_equipos'),
    
    # === SISTEMAS/IT DASHBOARD ===
    path('sistemas/', views.dashboard_sistemas, name='sistemas_dashboard'),
    path('sistemas/tickets/', views.gestionar_tickets, name='gestionar_tickets'),
    path('sistemas/tickets/<int:ticket_id>/asignar/', views.asignar_ticket, name='asignar_ticket'),
    path('sistemas/tickets/<int:ticket_id>/resolver/', views.resolver_ticket, name='resolver_ticket'),
    path('sistemas/equipos/', views.inventario_equipos, name='inventario_equipos'),
    path('sistemas/equipos/agregar/', views.agregar_equipo, name='agregar_equipo'),
    path('sistemas/equipos/asignar/', views.asignar_equipo, name='asignar_equipo'),
    path('sistemas/equipos/<int:equipo_id>/asignar/', views.asignar_equipo_desde_inventario, name='asignar_equipo_inventario'),
    path('sistemas/equipos/asignacion/<int:asignacion_id>/editar/', views.editar_asignacion_equipo, name='editar_asignacion_equipo'),
    path('sistemas/equipos/<int:equipo_id>/quitar-asignacion/', views.quitar_asignacion_equipo, name='quitar_asignacion_equipo'),
    path('sistemas/equipos/<int:asignacion_id>/devolver/', views.devolver_equipo, name='devolver_equipo'),
    
    # === API ENDPOINTS ===
    path('api/validar-antiguedad/', views.validar_antiguedad, name='validar_antiguedad'),
    
    # === PERFIL DE USUARIO ===
    path('perfil/', auth_views.perfil_usuario, name='perfil_usuario'),
]

# URLs de error
handler403 = views.error_403
handler404 = views.error_404
handler500 = views.error_500

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
