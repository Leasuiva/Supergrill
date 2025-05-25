import mysql.connector

class Conexiones:
    @staticmethod
    def conexion_local():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                port=3306,
                user="user",        # Cambiar por tu usuario
                password="clave123",   # Cambiar por tu contraseña
                database="Supergrill"     # Cambiar por tu base de datos
            )
            print("✅ Conexión LOCAL establecida")
            return conn
        except mysql.connector.Error as err:
            print("❌ Error al conectar con la base LOCAL:", err)
            return None

    @staticmethod
    def conexion_remota():
        try:
            conn = mysql.connector.connect(
                host="containers-us-west-123.railway.app",  # Cambiar por tu host real
                port=12345,                                 # Cambiar por tu puerto real
                user="root",                                # Cambiar si usás otro usuario
                password="tu_contraseña",                   # Cambiar por tu contraseña
                database="railway"                          # Cambiar por tu base
            )
            print("✅ Conexión REMOTA establecida")
            return conn
        except mysql.connector.Error as err:
            print("❌ Error al conectar con la base REMOTA:", err)
            return None
