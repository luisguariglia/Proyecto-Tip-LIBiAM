import sqlite3
import config


class Conexion:

    @staticmethod
    def crear_bd_si_no_existe():
        db = sqlite3.connect(config.DB_FILE)
        cursor = db.cursor()

        # TABLA DONDE SE GUARDA LA LINEA DEL CSV DONDE EMPIEZAN LOS DATOS
        cursor.execute('CREATE TABLE IF NOT EXISTS FILA_COLUMNAS ("id"	INTEGER,'
                   '"row_column" INTEGER,'
                   ' PRIMARY KEY("id" AUTOINCREMENT));')

        # TABLA DONDE SE GUARDA EL LÍMITE DE GRÁFICAS POR VISTA
        cursor.execute('CREATE TABLE IF NOT EXISTS LIMITE_GRAFICAS ("id"	INTEGER,'
                       '"limite_grafica" INTEGER,'
                       ' PRIMARY KEY("id" AUTOINCREMENT));')

        cursor.execute('SELECT count(row_column) FROM FILA_COLUMNAS')
        datito1 = cursor.fetchone()[0]

        cursor.execute('SELECT count(limite_grafica) FROM LIMITE_GRAFICAS')
        datito2 = cursor.fetchone()[0]


        if int(datito1) == 0:
            cursor.execute('INSERT INTO FILA_COLUMNAS ("id","row_column") values (NULL, 788)')


        if int(datito2) == 0:
            cursor.execute('INSERT INTO LIMITE_GRAFICAS ("id","limite_grafica") values (NULL, 4)')

        db.commit()
        db.close()
    @staticmethod
    def get_limite_graficas():
        mi_conexion = sqlite3.connect(config.DB_FILE)
        cursor = mi_conexion.cursor()
        cursor.execute("SELECT limite_grafica FROM LIMITE_GRAFICAS WHERE id = 1")
        datito = cursor.fetchone()[0]
        mi_conexion.commit()
        mi_conexion.close()
        return datito

    @staticmethod
    def set_limite_graficas(nuevo_limite):
        mi_conexion = sqlite3.connect(config.DB_FILE)
        cursor = mi_conexion.cursor()
        cursor.execute("UPDATE LIMITE_GRAFICAS SET limite_grafica = ? ", [nuevo_limite])
        mi_conexion.commit()
        mi_conexion.close()

    @staticmethod
    def get_row_columns():
        mi_conexion = sqlite3.connect(config.DB_FILE)
        cursor = mi_conexion.cursor()
        cursor.execute("SELECT row_column FROM FILA_COLUMNAS WHERE id = 1")
        datito = cursor.fetchone()[0]
        mi_conexion.commit()
        mi_conexion.close()
        return datito

    @staticmethod
    def set_row_columns(nuevo_row_columns):
        mi_conexion = sqlite3.connect(config.DB_FILE)
        cursor = mi_conexion.cursor()
        cursor.execute("UPDATE FILA_COLUMNAS SET row_column = ? ", [nuevo_row_columns])
        mi_conexion.commit()
        mi_conexion.close()
