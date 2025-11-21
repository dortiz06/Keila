"""
Script para migrar datos de SQLite a MariaDB/MySQL
Ejecutar después de configurar MariaDB en producción
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rh_project.settings')
django.setup()

from django.core.management import call_command
from django.db import connections
from django.conf import settings

def migrate_database():
    """
    Migra datos de SQLite a MariaDB/MySQL
    """
    print("=" * 60)
    print("MIGRACIÓN DE SQLITE A MARIADB/MYSQL")
    print("=" * 60)
    
    # Verificar que existe la base de datos SQLite
    sqlite_db = settings.DATABASES['default']['NAME']
    if not os.path.exists(sqlite_db):
        print(f"❌ Error: No se encuentra la base de datos SQLite en {sqlite_db}")
        sys.exit(1)
    
    print(f"✓ Base de datos SQLite encontrada: {sqlite_db}")
    
    # Exportar datos de SQLite
    print("\n1. Exportando datos de SQLite...")
    try:
        call_command('dumpdata', 
                    exclude=['auth.permission', 'contenttypes'],
                    output='backup_sqlite.json',
                    indent=2)
        print("✓ Datos exportados a backup_sqlite.json")
    except Exception as e:
        print(f"❌ Error al exportar datos: {e}")
        sys.exit(1)
    
    # Cambiar a configuración de producción (MariaDB)
    print("\n2. Cambiando a configuración de MariaDB...")
    os.environ['DJANGO_SETTINGS_MODULE'] = 'rh_project.settings_production'
    django.setup()
    
    # Verificar conexión a MariaDB
    print("\n3. Verificando conexión a MariaDB...")
    try:
        db_conn = connections['default']
        db_conn.ensure_connection()
        print("✓ Conexión a MariaDB exitosa")
    except Exception as e:
        print(f"❌ Error al conectar a MariaDB: {e}")
        print("\nAsegúrate de que:")
        print("  - MariaDB esté instalado y corriendo")
        print("  - La base de datos y usuario estén creados")
        print("  - Las variables de entorno estén configuradas en .env")
        print("  - PyMySQL esté instalado: pip install PyMySQL")
        sys.exit(1)
    
    # Ejecutar migraciones en MariaDB
    print("\n4. Ejecutando migraciones en MariaDB...")
    try:
        call_command('migrate', verbosity=1)
        print("✓ Migraciones ejecutadas")
    except Exception as e:
        print(f"❌ Error al ejecutar migraciones: {e}")
        sys.exit(1)
    
    # Importar datos a MariaDB
    print("\n5. Importando datos a MariaDB...")
    try:
        call_command('loaddata', 'backup_sqlite.json', verbosity=1)
        print("✓ Datos importados exitosamente")
    except Exception as e:
        print(f"❌ Error al importar datos: {e}")
        print("\nNota: Algunos errores pueden ser normales si hay datos duplicados")
        print("Revisa los logs para más detalles")
    
    print("\n" + "=" * 60)
    print("MIGRACIÓN COMPLETADA")
    print("=" * 60)
    print("\nPróximos pasos:")
    print("1. Verificar que todos los datos se importaron correctamente")
    print("2. Probar el sistema en producción")
    print("3. Hacer backup de MariaDB")
    print("4. Guardar backup_sqlite.json como respaldo")
    print("\n⚠️  IMPORTANTE: No elimines la base de datos SQLite hasta verificar todo")

if __name__ == '__main__':
    migrate_database()

