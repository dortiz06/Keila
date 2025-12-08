#!/bin/bash
# Script para recopilar archivos estáticos en producción
# Ejecutar este script después de hacer cambios en archivos estáticos

echo "Recopilando archivos estáticos para producción..."

# Activar el entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Ejecutar collectstatic con la configuración de producción
python manage.py collectstatic --noinput --settings=rh_project.settings_production

echo "¡Archivos estáticos recopilados exitosamente!"
echo "Los archivos están en: staticfiles/"
