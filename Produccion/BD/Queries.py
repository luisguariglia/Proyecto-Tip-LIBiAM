import sqlite3
import config


class Conexion:

    @staticmethod
    def get_limite_graficas():
        mi_conexion = sqlite3.connect(config.DB_FILE)
        cursor = mi_conexion.cursor()
        cursor.execute("SELECT limite_vista FROM configuraciones_vista WHERE id = 1")
        datito = cursor.fetchone()[0]
        mi_conexion.commit()
        mi_conexion.close()
        return datito

    @staticmethod
    def set_limite_graficas(nuevo_limite):
        mi_conexion = sqlite3.connect(config.DB_FILE)
        cursor = mi_conexion.cursor()
        cursor.execute("UPDATE configuraciones_vista SET limite_vista = ? ", [nuevo_limite])
        mi_conexion.commit()
        mi_conexion.close()
