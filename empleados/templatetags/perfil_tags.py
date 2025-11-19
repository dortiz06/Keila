from django import template
from datetime import datetime

register = template.Library()

@register.simple_tag
def saludo_dinamico():
    """
    Retorna un saludo dinámico basado en la hora del sistema:
    - "Buenos días," desde medianoche hasta las 11:59 AM
    - "Buenas tardes," desde las 12:00 PM hasta las 07:59 PM
    - "Buenas noches," desde las 08:00 PM hasta la medianoche
    """
    hora_actual = datetime.now().hour
    
    if 0 <= hora_actual < 12:
        return "Buenos días,"
    elif 12 <= hora_actual < 20:
        return "Buenas tardes,"
    else:  # 20 <= hora_actual < 24
        return "Buenas noches,"

@register.simple_tag
def categoria_icono(nombre_categoria):
    """
    Retorna el icono de Font Awesome correspondiente a una categoría de equipo.
    """
    # Normalizar el nombre de la categoría (minúsculas, sin espacios)
    nombre = nombre_categoria.lower().strip()
    
    # Mapeo de categorías a iconos de Font Awesome
    iconos = {
        'laptop': 'fa-laptop',
        'celular': 'fa-mobile-alt',
        'tablet': 'fa-tablet-alt',
        'teclado': 'fa-keyboard',
        'monitor': 'fa-desktop',
        'mouse': 'fa-mouse',
        'impresora': 'fa-print',
        'router': 'fa-router',
        'switch': 'fa-network-wired',
        'servidor': 'fa-server',
        'disco duro': 'fa-hdd',
        'disco': 'fa-hdd',
        'hdd': 'fa-hdd',
        'ssd': 'fa-hdd',
        'cámara': 'fa-camera',
        'camara': 'fa-camera',
        'auriculares': 'fa-headphones',
        'headphones': 'fa-headphones',
        'micrófono': 'fa-microphone',
        'microfono': 'fa-microphone',
        'microphone': 'fa-microphone',
        'webcam': 'fa-video',
        'cámara web': 'fa-video',
        'camara web': 'fa-video',
        'proyector': 'fa-projector',
        'cable': 'fa-plug',
        'adaptador': 'fa-plug',
        'cargador': 'fa-plug',
        'ups': 'fa-battery-full',
        'regulador': 'fa-bolt',
        'estabilizador': 'fa-bolt',
    }
    
    # Buscar coincidencia exacta o parcial
    for categoria, icono in iconos.items():
        if categoria in nombre or nombre in categoria:
            return icono
    
    # Si no se encuentra, retornar un icono por defecto
    return 'fa-tag'

