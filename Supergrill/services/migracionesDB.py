from services.pedidosDB import ModeloDB

class MigracionesDB:
    def __init__(self, conexion):
        self.conn = conexion

    def crear_todas_las_tablas(self):
        modelo = ModeloDB(self.conn)

        modelo.crear_tabla_direcciones()
        modelo.crear_tabla_empresa()
        modelo.crear_tabla_cadetes()
        modelo.crear_tabla_tipo_menu()
        modelo.crear_tabla_guarnicion()
        modelo.crear_tabla_menus()
        modelo.crear_tabla_forma_pago()
        modelo.crear_tabla_nombres()
        modelo.crear_tabla_estados()
        modelo.crear_tabla_usuarios()
        modelo.crear_tabla_pedidos()
        modelo.crear_tabla_pedidos_detalle()

        print("✅ Migraciones ejecutadas correctamente.")

