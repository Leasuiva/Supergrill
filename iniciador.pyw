import sys
import os
import tkinter as tk
import socket
import threading
import webbrowser
import subprocess 
import time
import traceback
from tkinter import messagebox

# ==========================================
# CONFIGURACIONES GLOBALES
# ==========================================
PUERTO_DB = 3307
PUERTO_DJANGO = 5002 # Ajustado al puerto que se ve en tu imagen

class LanzadorSupergrill:
    def __init__(self, root):
        self.root = root
        self.proceso_bd = None
        self.proceso_django = None 
        
        self.ip_actual = self.obtener_ip_local()
        self.url_red = f"http://{self.ip_actual}:{PUERTO_DJANGO}"

        self._configurar_ventana()
        self._construir_interfaz()

    # ==========================================
    # INTERFAZ GRÁFICA (UI)
    # ==========================================
    def _configurar_ventana(self):
        self.root.title("Supergrill")
        try:
            self.root.iconbitmap(os.path.join(os.getcwd(), "logo.ico"))
        except Exception:
            pass 
            
        self.root.geometry("480x320")
        self.root.resizable(False, False)
        self.root.configure(bg="#ffffff")
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        self.root.eval('tk::PlaceWindow . center')

    def _construir_interfaz(self):
        frame_header = tk.Frame(self.root, bg="#ea044e", height=60)
        frame_header.pack(fill="x", side="top")
        frame_header.pack_propagate(False)
        tk.Label(frame_header, text="🍔 SUPERGRILL", font=("Segoe UI", 18, "bold"), bg="#ea044e", fg="#ffffff").pack(pady=12)

        frame_body = tk.Frame(self.root, bg="#ffffff")
        frame_body.pack(fill="both", expand=True, pady=15)
        tk.Label(frame_body, text="Copia y pega esta IP en tu navegador favorito:", font=("Segoe UI", 10), bg="#ffffff", fg="#495057").pack(pady=(0, 5))

        frame_ip = tk.Frame(frame_body, bg="#f8f9fa", bd=1, relief="solid")
        frame_ip.pack(pady=5)

        txt_ip = tk.Entry(frame_ip, font=("Consolas", 15, "bold"), justify="center", bg="#f8f9fa", fg="#212529", relief="flat", width=22)
        txt_ip.insert(0, self.url_red)
        txt_ip.configure(state="readonly")
        txt_ip.pack(side="left", padx=(10, 0), ipady=8)

        btn_copiar = tk.Button(frame_ip, text="📋 Copiar", font=("Segoe UI", 9, "bold"), bg="#dee2e6", fg="#495057", 
                               activebackground="#ced4da", relief="flat", cursor="hand2", command=self.copiar_ip)
        btn_copiar.pack(side="right", padx=5, pady=5, ipadx=5, ipady=2)

        self.lbl_aviso_copia = tk.Label(frame_body, text="", font=("Segoe UI", 9, "bold"), bg="#ffffff")
        self.lbl_aviso_copia.pack()

        frame_footer = tk.Frame(self.root, bg="#ffffff")
        frame_footer.pack(side="bottom", fill="x", pady=20)

        self.btn_iniciar = tk.Button(frame_footer, text="🚀 INICIAR SERVIDOR", font=("Segoe UI", 13, "bold"), 
                                     bg="#042505", fg="white", activebackground="#0a4b0d", activeforeground="white",
                                     cursor="hand2", relief="flat", command=self.boton_iniciar_click)
        self.btn_iniciar.pack(ipadx=20, ipady=6)

        frame_estado = tk.Frame(frame_footer, bg="#ffffff")
        frame_estado.pack(pady=(10, 0))

        self.lbl_led = tk.Label(frame_estado, text="🔴", font=("Segoe UI", 10), bg="#ffffff", fg="#dc3545")
        self.lbl_led.pack(side="left")

        self.lbl_estado = tk.Label(frame_estado, text="Servidor apagado.", font=("Segoe UI", 9, "italic"), bg="#ffffff", fg="#6c757d")
        self.lbl_estado.pack(side="left", padx=5)

    # ==========================================
    # LÓGICA DE NEGOCIO Y SERVIDOR
    # ==========================================
    @staticmethod
    def obtener_ip_local():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"

    def arrancar_mariadb(self):
        try:
            # Detecta la carpeta donde está este archivo .pyw
            ruta_base = os.path.dirname(os.path.abspath(__file__))
            ruta_basedir = os.path.join(ruta_base, "mariadb")
            ruta_mysqld = os.path.join(ruta_basedir, "bin", "mysqld.exe")
            ruta_datadir = os.path.join(ruta_basedir, "data")
            
            # EL SECRETO: Constante de Windows para no crear ventana
            CREATE_NO_WINDOW = 0x08000000
            
            self.proceso_bd = subprocess.Popen(
                [ruta_mysqld, f"--basedir={ruta_basedir}", f"--datadir={ruta_datadir}", f"--port={PUERTO_DB}"], 
                creationflags=CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL, # Oculta los mensajes internos
                stderr=subprocess.DEVNULL
            )
            
            for _ in range(10):
                if self._verificar_puerto(PUERTO_DB):
                    return True
                time.sleep(1)
                
            return False
        except Exception as e:
            return False

    def _verificar_puerto(self, puerto):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect(('127.0.0.1', puerto))
            return True
        except Exception:
            return False

    def arrancar_servidor(self):
        # 1. Arrancar BD
        if not self.arrancar_mariadb():
            self.root.after(0, lambda: self.lbl_estado.config(text="Error: La base de datos no inició.", fg="#dc3545"))
            self.root.after(0, lambda: self.lbl_led.config(text="🔴", fg="#dc3545"))
            return
        
        self.root.after(0, lambda: self.lbl_led.config(text="🟢", fg="#28a745"))
        self.root.after(0, lambda: self.lbl_estado.config(text="Servidor corriendo. Minimiza esta ventana.", fg="#28a745"))
        
        # 2. Arrancar Django usando subprocess de forma oculta
        try:
            ruta_base = os.path.dirname(os.path.abspath(__file__))
            
            # Usamos el python.exe de tu entorno virtual directamente
            python_exe = os.path.join(ruta_base, "env", "Scripts", "python.exe")
            ruta_manage = os.path.join(ruta_base, "supergrill", "manage.py")
            
            comando_django = [python_exe, ruta_manage, "runserver", f"0.0.0.0:{PUERTO_DJANGO}"]
            
            CREATE_NO_WINDOW = 0x08000000
            self.proceso_django = subprocess.Popen(
                comando_django, 
                creationflags=CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            
        except Exception as e:
            error_msg = traceback.format_exc()
            self.root.after(0, lambda: messagebox.showerror("Error Crítico", f"Django falló al iniciar:\n\n{error_msg}"))
            self.root.after(0, lambda: self.lbl_estado.config(text="El servidor web falló.", fg="#dc3545"))
            self.root.after(0, lambda: self.lbl_led.config(text="🔴", fg="#dc3545"))

    def boton_iniciar_click(self):
        self.btn_iniciar.config(text="INICIANDO...", bg="#e9ecef", fg="#6c757d", state="disabled", cursor="arrow")
        self.lbl_led.config(text="🟡", fg="#ffc107")
        self.lbl_estado.config(text="Cargando base de datos...", fg="#ffc107")

        threading.Thread(target=self.arrancar_servidor, daemon=True).start()
        
        self.root.after(3500, lambda: webbrowser.open(self.url_red))
        self.root.after(4000, self.root.iconify)

    def copiar_ip(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.url_red)
        self.lbl_aviso_copia.config(text="¡Copiado!", fg="#28a745")
        self.root.after(2000, lambda: self.lbl_aviso_copia.config(text=""))

    def cerrar_aplicacion(self):
        # Cuando cerrás la ventana, matamos los procesos fantasma
        if self.proceso_bd:
            self.proceso_bd.terminate()
        if self.proceso_django:
            self.proceso_django.terminate()
            
        self.root.destroy()
        os._exit(0)

if __name__ == "__main__":
    ventana_principal = tk.Tk()
    app_lanzador = LanzadorSupergrill(ventana_principal)
    ventana_principal.mainloop()