#!/usr/bin/env python
"""
Script de instalación para el sistema refactorizado de RH
Ejecutar: python install_refactored_system.py
"""

import os
import sys
import shutil
from pathlib import Path

def crear_directorio_logs():
    """Crear directorio de logs si no existe"""
    logs_dir = Path('logs')
    if not logs_dir.exists():
        logs_dir.mkdir()
        print("✅ Directorio 'logs' creado")

def backup_archivos_actuales():
    """Hacer backup de archivos actuales"""
    print("📦 Creando backup de archivos actuales...")
    
    archivos_backup = [
        'empleados/models.py',
        'empleados/forms.py', 
        'empleados/views.py',
        'empleados/urls.py',
        'rh_project/settings.py',
        'rh_project/urls.py',
    ]
    
    backup_dir = Path('backup_original')
    backup_dir.mkdir(exist_ok=True)
    
    for archivo in archivos_backup:
        if Path(archivo).exists():
            destino = backup_dir / archivo
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(archivo, destino)
            print(f"  ✓ Backup: {archivo}")

def instalar_sistema_refactorizado():
    """Instalar sistema refactorizado"""
    print("\n🚀 Instalando sistema refactorizado...")
    
    # Renombrar archivos refactorizados
    archivos_refactorizados = {
        'empleados/models_refactored.py': 'empleados/models.py',
        'empleados/forms_refactored.py': 'empleados/forms.py',
        'empleados/views_refactored.py': 'empleados/views.py',
        'empleados/urls_refactored.py': 'empleados/urls.py',
        'rh_project/settings_refactored.py': 'rh_project/settings.py',
        'rh_project/urls_refactored.py': 'rh_project/urls.py',
    }
    
    for origen, destino in archivos_refactorizados.items():
        if Path(origen).exists():
            shutil.move(origen, destino)
            print(f"  ✓ Instalado: {destino}")
        else:
            print(f"  ⚠️ No encontrado: {origen}")

def ejecutar_migraciones():
    """Ejecutar migraciones de Django"""
    print("\n🗄️ Ejecutando migraciones...")
    
    comandos = [
        'python manage.py makemigrations',
        'python manage.py migrate',
    ]
    
    for comando in comandos:
        print(f"  Ejecutando: {comando}")
        resultado = os.system(comando)
        if resultado == 0:
            print(f"  ✓ Completado: {comando}")
        else:
            print(f"  ❌ Error en: {comando}")

def crear_superusuario_admin():
    """Crear superusuario administrador"""
    print("\n👤 Creando superusuario administrador...")
    
    # Verificar si ya existe
    try:
        from django.contrib.auth.models import User
        if User.objects.filter(username='admin').exists():
            print("  - Usuario 'admin' ya existe")
            return
    except:
        pass
    
    # Crear superusuario
    comando = "python manage.py shell -c \"from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@grupokeila.com', 'admin123')\""
    resultado = os.system(comando)
    
    if resultado == 0:
        print("  ✓ Superusuario 'admin' creado (contraseña: admin123)")
    else:
        print("  ❌ Error creando superusuario")

def mostrar_instrucciones_finales():
    """Mostrar instrucciones finales"""
    print("\n" + "="*60)
    print("🎉 ¡SISTEMA REFACTORIZADO INSTALADO EXITOSAMENTE!")
    print("="*60)
    
    print("\n📋 INSTRUCCIONES DE USO:")
    print("1. Iniciar servidor: python manage.py runserver")
    print("2. Acceder a: http://127.0.0.1:8000/")
    print("3. Login con usuario: admin, contraseña: admin123")
    
    print("\n🔧 FUNCIONALIDADES MEJORADAS:")
    print("✅ Sistema de perfiles unificado")
    print("✅ Flujo de aprobación de vacaciones mejorado")
    print("✅ Dashboards específicos por rol")
    print("✅ Manejo de errores robusto")
    print("✅ URLs organizadas y RESTful")
    print("✅ Validaciones mejoradas")
    
    print("\n👥 ROLES DISPONIBLES:")
    print("- ADMIN: Acceso completo al sistema")
    print("- RH: Gestión de empleados y aprobación final de vacaciones")
    print("- JEFE_AREA: Aprobación de vacaciones de su departamento")
    print("- EMPLEADO: Solicitar vacaciones y ver su información")
    
    print("\n📁 ARCHIVOS BACKUP:")
    print("- Los archivos originales están en: ./backup_original/")
    print("- Puedes restaurarlos si es necesario")
    
    print("\n🚀 ¡El sistema está listo para usar!")

def main():
    """Función principal de instalación"""
    print("🔧 INSTALADOR DEL SISTEMA REFACTORIZADO - GRUPO KEILA")
    print("="*60)
    
    try:
        # Verificar que estamos en el directorio correcto
        if not Path('manage.py').exists():
            print("❌ Error: No se encontró manage.py")
            print("   Asegúrate de estar en el directorio del proyecto Django")
            return
        
        # Crear directorio de logs
        crear_directorio_logs()
        
        # Hacer backup
        backup_archivos_actuales()
        
        # Instalar sistema refactorizado
        instalar_sistema_refactorizado()
        
        # Ejecutar migraciones
        ejecutar_migraciones()
        
        # Crear superusuario
        crear_superusuario_admin()
        
        # Mostrar instrucciones
        mostrar_instrucciones_finales()
        
    except Exception as e:
        print(f"\n❌ Error durante la instalación: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Sugerencia: Verifica que todos los archivos refactorizados existan")

if __name__ == '__main__':
    main()
