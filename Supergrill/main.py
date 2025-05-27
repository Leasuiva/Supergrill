from tkinter import *
from ui.pedidoss import ViandasUi2
import os
from services.conexionDB import Conexiones
from services.migracionesDB import MigracionesDB
from ui.barra_menu import barra_menu


class Ventana(Tk):
    def __init__(self):
        super().__init__()
        self.title('Supergrill')
        self.conexion = Conexiones.conexion_local() # Establecer conexión a la base de datos

        self.barra_menu = barra_menu(self)  # Barra menu principal


        # Ruta absoluta basada en el archivo actual
        base_path = os.path.abspath(os.path.dirname(__file__))
        icon_path = os.path.join(base_path, "assets", "logo_supergrill.ico")

        # Intentar establecer el ícono
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        else:
            print(f"[ERROR] Icono no encontrado en: {icon_path}")

        # Llamada de la función de la ventana de pedidos de client
        self.viandas_ui = ViandasUi2(self)
        self.viandas_ui.pack(side=LEFT, fill=BOTH, expand=True)

        # Iniciar maximizada
        self.state('zoomed')

        # Establecer tamaño mínimo
        self.minsize(800, 600)

        # Registrar evento para cuando cambia el estado de la ventana (minimizar/restaurar/etc.)
        self.bind("<Visibility>", self.al_restaurar)

    def al_restaurar(self, event):
        # Si la ventana no está maximizada al restaurarse, centrarla
        if self.state() == 'normal':
            self.centrar()

    def centrar(self):
        ancho = self.winfo_width()
        alto = self.winfo_height()
        pantalla_ancho = self.winfo_screenwidth()
        pantalla_alto = self.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    # def pedidos_cliente(self):  # Ventana de pedidos de cliente
    #     self.viandas_ui = ViandasUi(self)
    #     self.viandas_ui.pack(side=LEFT, fill=BOTH, expand=True)

def main():
    # Ejecutar migraciones antes de iniciar la ventana
    conexion = Conexiones.conexion_local()
    if conexion:
        migraciones = MigracionesDB(conexion)
        migraciones.crear_todas_las_tablas()
        conexion.close()

    # Luego iniciar la ventana principal
    app = Ventana()
    app.mainloop()

if __name__ == "__main__":
    main()


















