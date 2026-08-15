import pymysql
import json
from datetime import date, datetime
from decimal import Decimal

# --- CONEXIÓN AL MOTOR VIEJO DE FLASK (PUERTO 3307) ---
DB_HOST = '127.0.0.1'
DB_PORT = 3307
DB_USER = 'root'
DB_PASS = ''
DB_NAME = 'supergrill'

def serializador_magico(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"El tipo {type(obj)} no se puede serializar")

def extraer_datos():
    print(f"🔌 Conectando al Flask Viejo en el puerto {DB_PORT}...")
    
    try:
        conexion = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"❌ Error al conectar. ¿Está encendido el Flask viejo? Detalles: {e}")
        return

    datos_extraidos = {}

    with conexion.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tablas = [list(t.values())[0] for t in cursor.fetchall()]
        print(f"🔍 Se encontraron {len(tablas)} tablas. Iniciando extracción...")

        for tabla in tablas:
            print(f"📦 Descargando datos de la tabla: {tabla}...")
            cursor.execute(f"SELECT * FROM {tabla}")
            datos_extraidos[tabla] = cursor.fetchall()

    print("\n💾 Guardando los datos en 'backup_flask.json'...")
    with open('backup_flask.json', 'w', encoding='utf-8') as archivo:
        json.dump(datos_extraidos, archivo, default=serializador_magico, indent=4)

    conexion.close()
    print("✅ ¡EXTRACCIÓN EXITOSA! Datos guardados en backup_flask.json")

if __name__ == '__main__':
    extraer_datos()