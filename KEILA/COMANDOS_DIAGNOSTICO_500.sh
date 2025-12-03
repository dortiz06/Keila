#!/bin/bash
# Script de diagnóstico para Error 500
# Ejecutar en el servidor: bash COMANDOS_DIAGNOSTICO_500.sh

echo "=========================================="
echo "DIAGNÓSTICO ERROR 500"
echo "=========================================="
echo ""

PROJECT_DIR="/home/admin-key/SistemaGK/Keila"
VENV_PATH="/home/admin-key/SistemaGK/venv"

cd "$PROJECT_DIR"
source "$VENV_PATH/bin/activate"

echo "1. Verificando logs de Gunicorn..."
echo "----------------------------------------"
if [ -f "logs/gunicorn-error.log" ]; then
    echo "Últimas 50 líneas de gunicorn-error.log:"
    tail -50 logs/gunicorn-error.log
else
    echo "⚠️  Archivo logs/gunicorn-error.log NO existe"
fi
echo ""

echo "2. Verificando logs de Django..."
echo "----------------------------------------"
if [ -f "logs/django.log" ]; then
    echo "Últimas 50 líneas de django.log:"
    tail -50 logs/django.log
else
    echo "⚠️  Archivo logs/django.log NO existe"
fi
echo ""

echo "3. Verificando Django check..."
echo "----------------------------------------"
python manage.py check 2>&1
echo ""

echo "4. Verificando conexión a base de datos..."
echo "----------------------------------------"
python manage.py check --database default 2>&1
echo ""

echo "5. Verificando migraciones pendientes..."
echo "----------------------------------------"
python manage.py showmigrations | grep "\[ \]" | head -10
if [ $? -eq 0 ]; then
    echo "⚠️  Hay migraciones pendientes"
else
    echo "✓ Todas las migraciones están aplicadas"
fi
echo ""

echo "6. Verificando archivos estáticos..."
echo "----------------------------------------"
if [ -d "staticfiles" ]; then
    echo "✓ Directorio staticfiles existe"
    ls -la staticfiles | head -5
else
    echo "⚠️  Directorio staticfiles NO existe"
    echo "Ejecutar: python manage.py collectstatic --noinput"
fi
echo ""

echo "7. Verificando SECRET_KEY..."
echo "----------------------------------------"
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rh_project.settings_production')
from django.conf import settings
if settings.SECRET_KEY and settings.SECRET_KEY != 'cambiar-en-produccion':
    print('✓ SECRET_KEY configurado')
else:
    print('⚠️  SECRET_KEY NO está configurado correctamente')
" 2>&1
echo ""

echo "8. Verificando ALLOWED_HOSTS..."
echo "----------------------------------------"
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rh_project.settings_production')
from django.conf import settings
print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)
" 2>&1
echo ""

echo "9. Verificando importación WSGI..."
echo "----------------------------------------"
python -c "
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rh_project.settings_production')
try:
    from rh_project.wsgi import application
    print('✓ WSGI se importa correctamente')
except Exception as e:
    print(f'✗ ERROR al importar WSGI: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
" 2>&1
echo ""

echo "10. Verificando variables de entorno..."
echo "----------------------------------------"
if [ -f ".env" ]; then
    echo "✓ Archivo .env existe"
    echo "Variables configuradas:"
    grep -v "^#" .env | grep -v "^$" | sed 's/=.*/=***/' 
else
    echo "⚠️  Archivo .env NO existe"
fi
echo ""

echo "=========================================="
echo "RESUMEN"
echo "=========================================="
echo ""
echo "Revisa los logs de error arriba para encontrar el problema específico."
echo ""
echo "Comandos útiles:"
echo "  - Ver logs en tiempo real: tail -f logs/gunicorn-error.log"
echo "  - Ver logs del sistema: sudo journalctl -u gunicorn -f"
echo "  - Aplicar migraciones: python manage.py migrate"
echo "  - Recolectar estáticos: python manage.py collectstatic --noinput"
echo ""



