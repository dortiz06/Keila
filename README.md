# Sistema de Recursos Humanos

Un sistema web completo para la gestión de empleados y vacaciones desarrollado con Django, HTML, CSS y Bootstrap.

## Características

- **Gestión de Empleados**: Registro completo de información personal y laboral
- **Control de Vacaciones**: Solicitudes, aprobaciones y seguimiento de vacaciones
- **Panel de Administración**: Interfaz administrativa completa con Django Admin
- **Dashboard Interactivo**: Estadísticas y resúmenes visuales
- **Diseño Responsivo**: Interfaz moderna y adaptable a diferentes dispositivos
- **Filtros y Búsquedas**: Herramientas avanzadas para encontrar información rápidamente

## Requisitos del Sistema

- Python 3.8 o superior
- Django 4.2.7
- Navegador web moderno

## Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   cd "Proyecto RH"
   ```

2. **Crear un entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la base de datos**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Crear un superusuario para acceder al admin**
   ```bash
   python manage.py createsuperuser
   ```

6. **Ejecutar el servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

7. **Acceder a la aplicación**
   - Aplicación principal: http://127.0.0.1:8000/
   - Panel de administración: http://127.0.0.1:8000/admin/

## Uso del Sistema

### Panel Principal
- **Dashboard**: Vista general con estadísticas de empleados y vacaciones
- **Empleados**: Lista completa de empleados con filtros y búsquedas
- **Vacaciones**: Gestión de solicitudes de vacaciones

### Gestión de Empleados
1. Acceder a "Empleados" en el menú principal
2. Usar filtros para encontrar empleados específicos
3. Hacer clic en "Ver Detalles" para información completa
4. Usar el panel de administración para editar o agregar empleados

### Gestión de Vacaciones
1. Acceder a "Vacaciones" en el menú principal
2. Ver todas las solicitudes con sus estados
3. Usar filtros para encontrar solicitudes específicas
4. Hacer clic en "Editar" para aprobar o rechazar solicitudes

### Panel de Administración
1. Acceder a http://127.0.0.1:8000/admin/
2. Iniciar sesión con las credenciales del superusuario
3. Gestionar empleados, departamentos y vacaciones
4. Configurar usuarios y permisos

## Estructura del Proyecto

```
Proyecto RH/
├── manage.py                 # Script de gestión de Django
├── requirements.txt          # Dependencias del proyecto
├── rh_project/              # Configuración principal
│   ├── __init__.py
│   ├── settings.py          # Configuración del proyecto
│   ├── urls.py              # URLs principales
│   ├── wsgi.py              # Configuración WSGI
│   └── asgi.py              # Configuración ASGI
├── empleados/               # Aplicación de empleados
│   ├── __init__.py
│   ├── models.py            # Modelos de datos
│   ├── views.py             # Vistas de la aplicación
│   ├── urls.py              # URLs de la aplicación
│   └── admin.py             # Configuración del admin
└── templates/               # Plantillas HTML
    ├── base.html            # Plantilla base
    └── empleados/           # Plantillas específicas
        ├── index.html       # Página principal
        ├── lista_empleados.html
        ├── detalle_empleado.html
        └── vacaciones.html
```

## Modelos de Datos

### Empleado
- Información personal (nombre, fecha de nacimiento, género, etc.)
- Información laboral (departamento, puesto, salario, etc.)
- Control de vacaciones (días anuales, usados, disponibles)

### Vacación
- Solicitudes de vacaciones con fechas y motivos
- Estados: Pendiente, Aprobada, Rechazada, Cancelada
- Seguimiento de aprobaciones y comentarios

### Departamento
- Organización de empleados por departamentos
- Descripción y gestión de áreas de trabajo

## Personalización

### Agregar Nuevos Campos
1. Modificar los modelos en `empleados/models.py`
2. Ejecutar `python manage.py makemigrations`
3. Ejecutar `python manage.py migrate`
4. Actualizar las plantillas HTML según sea necesario

### Cambiar el Diseño
- Modificar `templates/base.html` para cambios globales
- Editar archivos CSS en la sección `<style>` de `base.html`
- Personalizar plantillas específicas en `templates/empleados/`

## Soporte

Para soporte técnico o preguntas sobre el sistema, contactar al equipo de desarrollo.

## Licencia

Este proyecto está desarrollado para uso interno de la empresa.


