from pathlib import Path
from BD.Queries import Conexion

DB_FILE = str(Path.home()) + '/abs.db'
Conexion.crear_bd_si_no_existe()

EMG = "EMG"
ROW_COLUMNS = Conexion.get_row_columns()
ENCODING = 'cp1252'
FILES_CSV = 'Archivos CSV (*.csv)'
PATH_FONTS = ':/Static/fonts'
ICONO_GRAFICAS = ':/Static/img/line-graph.svg'
ICONO_CARPETAS = ':/Static/img/folder.svg'
ICONO_VISTA = ':/Static/img/view.svg'
LIMITE_GRAFICAS_POR_VISTA = Conexion.get_limite_graficas()



