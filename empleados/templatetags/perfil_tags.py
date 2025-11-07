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

