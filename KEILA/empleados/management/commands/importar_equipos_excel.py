"""
Comando de Django para importar equipos desde un archivo Excel
Uso: python manage.py importar_equipos_excel ruta/al/archivo.xlsx
"""
import os
import sys
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from openpyxl import load_workbook
from datetime import datetime
from empleados.models import Equipo, CategoriaEquipo


class Command(BaseCommand):
    help = 'Importa equipos desde un archivo Excel'

    def add_arguments(self, parser):
        parser.add_argument(
            'archivo_excel',
            type=str,
            help='Ruta al archivo Excel (.xlsx)'
        )
        parser.add_argument(
            '--hoja',
            type=str,
            default='Equipos',
            help='Nombre de la hoja a leer (default: "Equipos")'
        )
        parser.add_argument(
            '--fila-inicio',
            type=int,
            default=2,
            help='Fila donde inician los datos (default: 2, asumiendo fila 1 es encabezado)'
        )
        parser.add_argument(
            '--crear-categorias',
            action='store_true',
            help='Crear categorías automáticamente si no existen'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular importación sin guardar en la base de datos'
        )

    def handle(self, *args, **options):
        archivo_excel = options['archivo_excel']
        nombre_hoja = options['hoja']
        fila_inicio = options['fila_inicio']
        crear_categorias = options['crear_categorias']
        dry_run = options['dry_run']

        # Verificar que el archivo existe
        if not os.path.exists(archivo_excel):
            raise CommandError(f'El archivo "{archivo_excel}" no existe.')

        # Verificar extensión
        if not archivo_excel.endswith(('.xlsx', '.xls')):
            raise CommandError('El archivo debe ser .xlsx o .xls')

        self.stdout.write(self.style.SUCCESS(f'📂 Leyendo archivo: {archivo_excel}'))

        try:
            # Cargar el archivo Excel
            workbook = load_workbook(archivo_excel, data_only=True)
            
            # Verificar que la hoja existe
            if nombre_hoja not in workbook.sheetnames:
                raise CommandError(
                    f'La hoja "{nombre_hoja}" no existe. Hojas disponibles: {", ".join(workbook.sheetnames)}'
                )
            
            worksheet = workbook[nombre_hoja]
            self.stdout.write(self.style.SUCCESS(f'📄 Leyendo hoja: {nombre_hoja}'))

            # Leer datos
            equipos_importados = []
            equipos_actualizados = []
            errores = []

            # Mapeo de columnas esperadas (puedes ajustar según tu Excel)
            # Formato esperado:
            # A: Categoría
            # B: Marca
            # C: Modelo
            # D: Número de Serie
            # E: Código de Inventario
            # F: Estado (DISPONIBLE, ASIGNADO, EN_REPARACION, DADO_DE_BAJA)
            # G: Fecha de Adquisición (formato: YYYY-MM-DD o DD/MM/YYYY)
            # H: Observaciones (opcional)

            total_filas = worksheet.max_row
            self.stdout.write(f'📊 Total de filas encontradas: {total_filas}')

            for row_num in range(fila_inicio, total_filas + 1):
                try:
                    # Leer valores de las celdas
                    categoria_nombre = self._get_cell_value(worksheet, row_num, 1)  # Columna A
                    marca = self._get_cell_value(worksheet, row_num, 2)  # Columna B
                    modelo = self._get_cell_value(worksheet, row_num, 3)  # Columna C
                    numero_serie = self._get_cell_value(worksheet, row_num, 4)  # Columna D
                    codigo_inventario = self._get_cell_value(worksheet, row_num, 5)  # Columna E
                    estado = self._get_cell_value(worksheet, row_num, 6)  # Columna F
                    fecha_adquisicion = self._get_cell_value(worksheet, row_num, 7)  # Columna G
                    observaciones = self._get_cell_value(worksheet, row_num, 8)  # Columna H

                    # Validar campos obligatorios
                    if not categoria_nombre or not marca or not modelo or not numero_serie or not codigo_inventario:
                        errores.append({
                            'fila': row_num,
                            'error': 'Campos obligatorios faltantes (Categoría, Marca, Modelo, Serie, Código)'
                        })
                        continue

                    # Obtener o crear categoría
                    categoria, created = CategoriaEquipo.objects.get_or_create(
                        nombre=categoria_nombre.strip(),
                        defaults={'descripcion': f'Categoría importada desde Excel', 'activo': True}
                    )
                    if created and not crear_categorias:
                        # Si no se permite crear categorías y no existe, error
                        errores.append({
                            'fila': row_num,
                            'error': f'Categoría "{categoria_nombre}" no existe. Usa --crear-categorias para crearla automáticamente.'
                        })
                        continue

                    # Normalizar estado
                    estado_normalizado = self._normalizar_estado(estado)

                    # Procesar fecha
                    fecha_adq = self._procesar_fecha(fecha_adquisicion)
                    if not fecha_adq:
                        fecha_adq = datetime.now().date()  # Fecha por defecto: hoy

                    # Verificar si el equipo ya existe (por código de inventario o número de serie)
                    equipo_existente = None
                    if codigo_inventario:
                        try:
                            equipo_existente = Equipo.objects.get(codigo_inventario=codigo_inventario.strip())
                        except Equipo.DoesNotExist:
                            pass
                    
                    if not equipo_existente and numero_serie:
                        try:
                            equipo_existente = Equipo.objects.get(numero_serie=numero_serie.strip())
                        except Equipo.DoesNotExist:
                            pass

                    if not dry_run:
                        with transaction.atomic():
                            if equipo_existente:
                                # Actualizar equipo existente
                                equipo_existente.categoria = categoria
                                equipo_existente.marca = marca.strip()
                                equipo_existente.modelo = modelo.strip()
                                equipo_existente.numero_serie = numero_serie.strip()
                                equipo_existente.codigo_inventario = codigo_inventario.strip()
                                equipo_existente.estado = estado_normalizado
                                equipo_existente.fecha_adquisicion = fecha_adq
                                if observaciones:
                                    equipo_existente.observaciones = str(observaciones).strip()
                                equipo_existente.save()
                                equipos_actualizados.append({
                                    'fila': row_num,
                                    'equipo': equipo_existente
                                })
                            else:
                                # Crear nuevo equipo
                                nuevo_equipo = Equipo.objects.create(
                                    categoria=categoria,
                                    marca=marca.strip(),
                                    modelo=modelo.strip(),
                                    numero_serie=numero_serie.strip(),
                                    codigo_inventario=codigo_inventario.strip(),
                                    estado=estado_normalizado,
                                    fecha_adquisicion=fecha_adq,
                                    observaciones=str(observaciones).strip() if observaciones else ''
                                )
                                equipos_importados.append({
                                    'fila': row_num,
                                    'equipo': nuevo_equipo
                                })
                    else:
                        # Modo dry-run: solo mostrar qué se haría
                        if equipo_existente:
                            equipos_actualizados.append({
                                'fila': row_num,
                                'equipo': f'[ACTUALIZAR] {codigo_inventario}'
                            })
                        else:
                            equipos_importados.append({
                                'fila': row_num,
                                'equipo': f'[CREAR] {codigo_inventario}'
                            })

                except Exception as e:
                    errores.append({
                        'fila': row_num,
                        'error': str(e)
                    })

            # Mostrar resumen
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('📊 RESUMEN DE IMPORTACIÓN'))
            self.stdout.write('='*60)
            
            if dry_run:
                self.stdout.write(self.style.WARNING('⚠️  MODO DRY-RUN: No se guardaron cambios'))
            
            self.stdout.write(self.style.SUCCESS(f'✅ Equipos importados: {len(equipos_importados)}'))
            self.stdout.write(self.style.SUCCESS(f'🔄 Equipos actualizados: {len(equipos_actualizados)}'))
            self.stdout.write(self.style.ERROR(f'❌ Errores: {len(errores)}'))

            if equipos_importados:
                self.stdout.write('\n📦 EQUIPOS IMPORTADOS:')
                for item in equipos_importados[:10]:  # Mostrar primeros 10
                    if isinstance(item['equipo'], Equipo):
                        self.stdout.write(f"  ✓ Fila {item['fila']}: {item['equipo'].codigo_inventario} - {item['equipo'].marca} {item['equipo'].modelo}")
                    else:
                        self.stdout.write(f"  ✓ Fila {item['fila']}: {item['equipo']}")
                if len(equipos_importados) > 10:
                    self.stdout.write(f"  ... y {len(equipos_importados) - 10} más")

            if equipos_actualizados:
                self.stdout.write('\n🔄 EQUIPOS ACTUALIZADOS:')
                for item in equipos_actualizados[:10]:
                    if isinstance(item['equipo'], Equipo):
                        self.stdout.write(f"  ↻ Fila {item['fila']}: {item['equipo'].codigo_inventario} - {item['equipo'].marca} {item['equipo'].modelo}")
                    else:
                        self.stdout.write(f"  ↻ Fila {item['fila']}: {item['equipo']}")
                if len(equipos_actualizados) > 10:
                    self.stdout.write(f"  ... y {len(equipos_actualizados) - 10} más")

            if errores:
                self.stdout.write('\n❌ ERRORES:')
                for error in errores[:20]:  # Mostrar primeros 20 errores
                    self.stdout.write(self.style.ERROR(f"  ✗ Fila {error['fila']}: {error['error']}"))
                if len(errores) > 20:
                    self.stdout.write(f"  ... y {len(errores) - 20} errores más")

            self.stdout.write('\n' + '='*60)

        except Exception as e:
            raise CommandError(f'Error al procesar el archivo: {str(e)}')

    def _get_cell_value(self, worksheet, row, col):
        """Obtiene el valor de una celda de forma segura"""
        try:
            cell = worksheet.cell(row=row, column=col)
            value = cell.value
            if value is None:
                return None
            # Convertir a string y limpiar espacios
            return str(value).strip() if value else None
        except:
            return None

    def _normalizar_estado(self, estado):
        """Normaliza el estado del equipo"""
        if not estado:
            return 'DISPONIBLE'
        
        estado_upper = str(estado).strip().upper()
        
        # Mapeo de estados comunes
        mapeo_estados = {
            'DISPONIBLE': 'DISPONIBLE',
            'DISP': 'DISPONIBLE',
            'ASIGNADO': 'ASIGNADO',
            'ASIG': 'ASIGNADO',
            'EN REPARACION': 'EN_REPARACION',
            'EN_REPARACION': 'EN_REPARACION',
            'REPARACION': 'EN_REPARACION',
            'DADO DE BAJA': 'DADO_DE_BAJA',
            'DADO_DE_BAJA': 'DADO_DE_BAJA',
            'BAJA': 'DADO_DE_BAJA',
        }
        
        return mapeo_estados.get(estado_upper, 'DISPONIBLE')

    def _procesar_fecha(self, fecha_value):
        """Procesa diferentes formatos de fecha"""
        if not fecha_value:
            return None
        
        # Si ya es una fecha de Python
        if isinstance(fecha_value, datetime):
            return fecha_value.date()
        
        # Si es string, intentar parsear
        fecha_str = str(fecha_value).strip()
        
        # Intentar diferentes formatos
        formatos = [
            '%Y-%m-%d',      # 2024-01-15
            '%d/%m/%Y',      # 15/01/2024
            '%m/%d/%Y',      # 01/15/2024
            '%d-%m-%Y',      # 15-01-2024
            '%Y/%m/%d',      # 2024/01/15
        ]
        
        for formato in formatos:
            try:
                return datetime.strptime(fecha_str, formato).date()
            except:
                continue
        
        return None

