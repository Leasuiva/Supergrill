from tkinter import *
from tkinter import messagebox, ttk
import threading
from services.pedidosDB import ModeloDB
from services.conexionDB import Conexiones
from services.migracionesDB import MigracionesDB

class barra_menu(Menu):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.conn = Conexiones.conexion_local()
        self.master.config(menu=self)
        self.loading_window = None
        self.progress_bar = None
        self.create_menu()

    def create_menu(self):
        menu_inicio = Menu(self, tearoff=0)
        self.add_cascade(label="Inicio", menu=menu_inicio)

        menu_inicio.add_command(label="Nuevo", command=lambda: None) 
        menu_inicio.add_command(label="Guardar", command=lambda: None)
        menu_inicio.add_command(label="Exportar a Excel", command=lambda: None)
        menu_inicio.add_separator()
        menu_inicio.add_command(label="Salir", command=self.master.destroy)

#     def confirmar_nuevo(self):
#         respuesta = messagebox.askyesno("Confirmar", "¿Estás seguro de que querés borrar las tablas?")
#         if respuesta:
#             self.mostrar_cargando()
#             threading.Thread(target=self.crear_nuevo).start()

#     def mostrar_cargando(self):
#         self.loading_window = Toplevel(self.master)
#         self.loading_window.title("Procesando...")
#         self.loading_window.geometry("300x100")
#         self.loading_window.resizable(False, False)
#         self.loading_window.transient(self.master)
#         self.loading_window.grab_set()

#         Label(self.loading_window, text="Creando nueva base de datos...").pack(pady=10)

#         self.progress_bar = ttk.Progressbar(self.loading_window, mode='indeterminate')
#         self.progress_bar.pack(padx=20, pady=10, fill='x')
#         self.progress_bar.start(10)  # Velocidad de la animación

#     def cerrar_cargando(self):
#         if self.progress_bar:
#             self.progress_bar.stop()
#         if self.loading_window:
#             self.loading_window.destroy()
#             self.loading_window = None

#     def crear_nuevo(self):
#         if self.conn:
#             try:
#                 modelo = ModeloDB(self.conn)
#                 modelo.borrar_tablas()
#                 migraciones = MigracionesDB(self.conn)
#                 migraciones.crear_todas_las_tablas()
#                 self.master.after(0, self.cerrar_cargando)
#                 self._mostrar_info("Listo", "Se ha creado una nueva base vacía.")
#             except Exception as e:
#                 self.master.after(0, self.cerrar_cargando)
#                 self._mostrar_error("Error", f"No se pudo reiniciar la base de datos:\n{e}")

#     def _mostrar_info(self, titulo, mensaje):
#         self.master.after(0, lambda: messagebox.showinfo(titulo, mensaje))

#     def _mostrar_error(self, titulo, mensaje):
#         self.master.after(0, lambda: messagebox.showerror(titulo, mensaje))
