from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_http_methods
from functools import wraps


def csrf_exempt_for_development(view_func):
    """
    Decorador que desactiva CSRF solo en desarrollo
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # En desarrollo, permitir sin CSRF
        if hasattr(request, 'META') and 'HTTP_HOST' in request.META:
            host = request.META['HTTP_HOST']
            if '127.0.0.1' in host or 'localhost' in host:
                # Marcar la request como exenta de CSRF
                request.csrf_processing_done = True
        return view_func(request, *args, **kwargs)
    return wrapper


def ensure_csrf_cookie_for_development(view_func):
    """
    Decorador que asegura que la cookie CSRF esté disponible
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Asegurar que la cookie CSRF esté disponible
        get_token(request)
        return view_func(request, *args, **kwargs)
    return wrapper


def get_csrf_token(request):
    """
    Función helper para obtener el token CSRF
    """
    return get_token(request)
