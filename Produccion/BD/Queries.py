import sqlite3
import config


class Conexion:

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
