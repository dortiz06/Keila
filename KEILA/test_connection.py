"""
Script para probar la conexión a MariaDB desde Django
Ejecutar después de configurar phpMyAdmin y el archivo .env
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rh_project.settings_production')
django.setup()

from django.db import connection
from django.conf import settings

def test_connection():
    """
    Prueba la conexión a la base de datos MariaDB
    """
    print("=" * 60)
    print("PRUEBA DE CONEXIÓN A MARIADB")
    print("=" * 60)
    
    # Mostrar configuración (sin mostrar contraseña completa)
    db_config = settings.DATABASES['default']
    print(f"\n📋 Configuración de Base de Datos:")
    print(f"   Motor: {db_config['ENGINE']}")
    print(f"   Nombre: {db_config['NAME']}")
    print(f"   Usuario: {db_config['USER']}")
    print(f"   Host: {db_config['HOST']}")
    print(f"   Puerto: {db_config['PORT']}")
    print(f"   Contraseña: {'*' * len(db_config.get('PASSWORD', ''))}")
    
    # Probar conexión
    print("\n🔌 Probando conexión...")
    try:
        with connection.cursor() as cursor:
            # Prueba simple
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            
            # Obtener versión de MariaDB
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            
            # Obtener nombre de la base de datos actual
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()[0]
            
            print("✅ ¡Conexión exitosa a MariaDB!")
            print(f"✅ Versión de MariaDB/MySQL: {version}")
            print(f"✅ Base de datos actual: {current_db}")
            print(f"✅ Resultado de prueba: {result}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("\n🔍 Posibles causas:")
        print("   1. La base de datos no existe")
        print("   2. El usuario no existe o la contraseña es incorrecta")
        print("   3. El usuario no tiene privilegios en la base de datos")
        print("   4. MariaDB no está corriendo")
        print("   5. El archivo .env no está configurado correctamente")
        print("\n💡 Soluciones:")
        print("   - Verifica la configuración en phpMyAdmin")
        print("   - Verifica el archivo .env")
        print("   - Revisa la guía GUIA_PHPMYADMIN.md")
        sys.exit(1)
    
    # Verificar que la base de datos es la correcta
    print("\n🔍 Verificando base de datos...")
    if current_db != db_config['NAME']:
        print(f"⚠️  Advertencia: Base de datos actual ({current_db}) no coincide con la configurada ({db_config['NAME']})")
    else:
        print(f"✅ Base de datos correcta: {current_db}")
    
    # Probar permisos básicos
    print("\n🔍 Verificando permisos...")
    try:
        with connection.cursor() as cursor:
            # Probar SELECT
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✅ Permiso SELECT: OK (encontradas {len(tables)} tablas)")
            
            # Probar CREATE (crear tabla temporal)
            cursor.execute("""
                CREATE TEMPORARY TABLE test_permissions (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    test VARCHAR(50)
                )
            """)
            print("✅ Permiso CREATE: OK")
            
            # Probar INSERT
            cursor.execute("INSERT INTO test_permissions (test) VALUES ('test')")
            print("✅ Permiso INSERT: OK")
            
            # Probar UPDATE
            cursor.execute("UPDATE test_permissions SET test = 'updated' WHERE id = 1")
            print("✅ Permiso UPDATE: OK")
            
            # Probar DELETE
            cursor.execute("DELETE FROM test_permissions WHERE id = 1")
            print("✅ Permiso DELETE: OK")
            
            # La tabla temporal se elimina automáticamente
            print("✅ Permisos básicos: TODOS OK")
            
    except Exception as e:
        print(f"⚠️  Advertencia al verificar permisos: {e}")
        print("   Algunos permisos pueden estar limitados")
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURACIÓN EXITOSA")
    print("=" * 60)
    print("\n🎉 ¡La configuración de phpMyAdmin fue exitosa!")
    print("\n📝 Próximos pasos:")
    print("   1. Ejecutar migraciones: python manage.py migrate")
    print("   2. Crear superusuario: python manage.py createsuperuser")
    print("   3. Iniciar servidor: python manage.py runserver")
    print("\n💡 Puedes verificar las tablas en phpMyAdmin después de ejecutar las migraciones")

if __name__ == '__main__':
    test_connection()

