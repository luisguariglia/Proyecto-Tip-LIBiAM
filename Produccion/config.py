from BD.Queries import Conexion

EMG = "EMG"
DB_FILE = 'bd_humilde.db'
ROW_COLUMNS = Conexion.get_row_columns()
ENCODING = 'cp1252'
FILES_CSV = 'Archivos CSV (*.csv);'
PATH_FONTS = 'Static/fonts'
ICONO_GRAFICAS = 'Static/img/line-graph.svg'
ICONO_CARPETAS = 'Static/img/folder.svg'
ICONO_VISTA = 'Static/img/view.svg'
LIMITE_GRAFICAS_POR_VISTA = Conexion.get_limite_graficas()