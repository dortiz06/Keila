#!/bin/bash
# Script de diagnóstico para Gunicorn
# Ejecutar en el servidor: bash diagnostico_gunicorn.sh

echo "=========================================="
echo "DIAGNÓSTICO DE GUNICORN"
echo "=========================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar ruta del proyecto
echo "1. Verificando ruta del proyecto..."
PROJECT_DIR="/home/admin-key/SistemaGK/Keila"
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${GREEN}✓${NC} Proyecto encontrado en: $PROJECT_DIR"
    cd "$PROJECT_DIR"
else
    echo -e "${RED}✗${NC} Proyecto NO encontrado en: $PROJECT_DIR"
    exit 1
fi
echo ""

# 2. Verificar manage.py
echo "2. Verificando manage.py..."
if [ -f "manage.py" ]; then
    echo -e "${GREEN}✓${NC} manage.py existe"
else
    echo -e "${RED}✗${NC} manage.py NO existe"
    exit 1
fi
echo ""

# 3. Verificar rutas del venv
echo "3. Verificando rutas del entorno virtual..."
VENV1="/home/admin-key/SistemaGK/venv/bin/gunicorn"
VENV2="/home/admin-key/SistemaGK/Keila/venv/bin/gunicorn"

if [ -f "$VENV1" ]; then
    echo -e "${GREEN}✓${NC} Gunicorn encontrado en: $VENV1"
    VENV_PATH="/home/admin-key/SistemaGK/venv"
elif [ -f "$VENV2" ]; then
    echo -e "${GREEN}✓${NC} Gunicorn encontrado en: $VENV2"
    VENV_PATH="/home/admin-key/SistemaGK/Keila/venv"
else
    echo -e "${RED}✗${NC} Gunicorn NO encontrado en ninguna ubicación"
    echo "Buscando gunicorn..."
    find /home/admin-key -name gunicorn 2>/dev/null | head -5
    exit 1
fi
echo ""

# 4. Activar venv y verificar gunicorn
echo "4. Verificando instalación de Gunicorn..."
source "$VENV_PATH/bin/activate"
if command -v gunicorn &> /dev/null; then
    GUNICORN_VERSION=$(gunicorn --version)
    echo -e "${GREEN}✓${NC} Gunicorn instalado: $GUNICORN_VERSION"
else
    echo -e "${RED}✗${NC} Gunicorn NO está instalado"
    echo "Instalando gunicorn..."
    pip install gunicorn
fi
echo ""

# 5. Verificar psycopg2
echo "5. Verificando psycopg2..."
python -c "import psycopg2; print('OK')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} psycopg2 instalado"
else
    echo -e "${YELLOW}⚠${NC} psycopg2 NO encontrado, instalando..."
    pip install psycopg2-binary
fi
echo ""

# 6. Verificar Django
echo "6. Verificando Django..."
python manage.py check --deploy 2>&1 | head -20
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Django check pasó"
else
    echo -e "${RED}✗${NC} Django check falló"
fi
echo ""

# 7. Verificar importación WSGI
echo "7. Verificando importación WSGI..."
python -c "
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rh_project.settings_production')
try:
    from rh_project.wsgi import application
    print('OK - WSGI se importa correctamente')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} WSGI se importa correctamente"
else
    echo -e "${RED}✗${NC} Error al importar WSGI"
fi
echo ""

# 8. Verificar settings_production.py
echo "8. Verificando settings_production.py..."
if [ -f "rh_project/settings_production.py" ]; then
    echo -e "${GREEN}✓${NC} settings_production.py existe"
    echo "ALLOWED_HOSTS:"
    grep "ALLOWED_HOSTS" rh_project/settings_production.py | head -10
else
    echo -e "${RED}✗${NC} settings_production.py NO existe"
fi
echo ""

# 9. Verificar socket
echo "9. Verificando socket de Gunicorn..."
SOCKET_PATH="/home/admin-key/SistemaGK/Keila/gunicorn.sock"
if [ -S "$SOCKET_PATH" ]; then
    echo -e "${GREEN}✓${NC} Socket existe: $SOCKET_PATH"
    ls -la "$SOCKET_PATH"
else
    echo -e "${YELLOW}⚠${NC} Socket NO existe (se creará al iniciar Gunicorn)"
fi
echo ""

# 10. Verificar permisos
echo "10. Verificando permisos..."
if [ -w "$PROJECT_DIR" ]; then
    echo -e "${GREEN}✓${NC} Permisos de escritura en el directorio"
else
    echo -e "${RED}✗${NC} Sin permisos de escritura"
fi
echo ""

# 11. Verificar servicio systemd
echo "11. Verificando servicio systemd..."
if systemctl is-active --quiet gunicorn; then
    echo -e "${GREEN}✓${NC} Servicio gunicorn está activo"
else
    echo -e "${YELLOW}⚠${NC} Servicio gunicorn NO está activo"
fi

if systemctl is-enabled --quiet gunicorn; then
    echo -e "${GREEN}✓${NC} Servicio gunicorn está habilitado"
else
    echo -e "${YELLOW}⚠${NC} Servicio gunicorn NO está habilitado"
fi
echo ""

# 12. Mostrar últimas líneas del log
echo "12. Últimas líneas del log de Gunicorn:"
echo "----------------------------------------"
sudo journalctl -u gunicorn -n 20 --no-pager 2>/dev/null | tail -20
echo ""

# 13. Resumen y recomendaciones
echo "=========================================="
echo "RESUMEN Y RECOMENDACIONES"
echo "=========================================="
echo ""
echo "Ruta del venv encontrada: $VENV_PATH"
echo "Ruta del proyecto: $PROJECT_DIR"
echo ""
echo "Para actualizar el servicio systemd, usa:"
echo "sudo nano /etc/systemd/system/gunicorn.service"
echo ""
echo "Y asegúrate de que tenga:"
echo "Environment=\"PATH=$VENV_PATH/bin\""
echo "ExecStart=$VENV_PATH/bin/gunicorn \\"
echo "          --workers 3 \\"
echo "          --bind unix:$SOCKET_PATH \\"
echo "          rh_project.wsgi:application"
echo ""
echo "Luego:"
echo "sudo systemctl daemon-reload"
echo "sudo systemctl restart gunicorn"
echo "sudo systemctl status gunicorn"
echo ""



