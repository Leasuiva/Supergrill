import mysql.connector

print("🔌 Conectando al servidor MariaDB de Django...")
try:
    conn = mysql.connector.connect(
        host="127.0.0.1",
        port=3307,  # Confirmamos que ataca al nuevo
        user="root",
        password="", 
        autocommit=True
    )
    cursor = conn.cursor()

    print("✨ Creando una base de datos limpia...")
    cursor.execute("CREATE DATABASE supergrill_django;")

    cursor.close()
    conn.close()
    print("✅ ¡Éxito! La base de datos está vacía y lista para Django.")

except Exception as e:
    print(f"❌ Error: {e}")