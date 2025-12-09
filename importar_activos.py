import csv
from inventario.models import Activo   # <-- CAMBIA si tu app/modelo tiene otro nombre

def run():
    with open('activos.csv', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            Activo.objects.create(
                categoria=row['Categoria'],          # columna del CSV
                marca=row['Marca'],                  # columna del CSV
                modelo=row['Modelo'],                # columna del CSV
                numero_serie=row['Numero de Serie'], # columna del CSV
                codigo_inventario=row['ID'],         # ID del Excel -> código interno
                estado="Disponible",                 # todos disponibles
            )

    print("Importación completada")
