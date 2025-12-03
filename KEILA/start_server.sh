#!/bin/bash

# Script para iniciar el servidor del Sistema de Recursos Humanos
echo "🚀 Iniciando Sistema de Recursos Humanos..."
echo "============================================="

# Activar entorno virtual
echo "📦 Activando entorno virtual..."
source venv/bin/activate

# Verificar que Django esté instalado
echo "🔍 Verificando instalación..."
python -c "import django; print(f'Django {django.get_version()} instalado correctamente')"

# Ejecutar migraciones (por si acaso)
echo "🗄️  Verificando base de datos..."
python manage.py migrate

# Iniciar servidor
echo "🌐 Iniciando servidor de desarrollo..."
echo ""

# Obtener IP local
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

echo "✅ El sistema estará disponible en:"
echo "   📱 Local: http://127.0.0.1:8000/"
echo "   🌐 Red Local: http://${LOCAL_IP}:8000/"
echo "   ⚙️  Panel Admin: http://${LOCAL_IP}:8000/admin/"
echo ""
echo "📋 Comparte este enlace con otros usuarios en tu red:"
echo "   🔗 http://${LOCAL_IP}:8000/"
echo ""
echo "⚠️  IMPORTANTE: Asegúrate de que el firewall permita conexiones en el puerto 8000"
echo ""
echo "🔧 Si el puerto 8000 está ocupado, usa: python manage.py runserver 0.0.0.0:8001"
echo ""
echo "👤 Credenciales de administración:"
echo "   Usuario: admin"
echo "   Contraseña: admin123"
echo ""
echo "🛑 Para detener el servidor presiona Ctrl+C"
echo "============================================="

python manage.py runserver 0.0.0.0:8000
