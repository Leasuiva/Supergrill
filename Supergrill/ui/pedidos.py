from tkinter import *
from tkinter import ttk, messagebox, simpledialog
from ttkwidgets.autocomplete import AutocompleteCombobox
from datetime import date
from services.pedidosDB import ModeloDB
from services.conexionDB import Conexiones


class ViandasUi(Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.conn = Conexiones.conexion_local()
        self.modelo = ModeloDB(self.conn)

        self.grid(row=0, column=0)
        self.filas = []

        self.frame_pedidos = Frame(self)
        self.frame_pedidos.grid(row=0, column=0, padx=10, pady=10)

        self.mostrar_usuario(self.frame_pedidos)
        self.crear_interfaz(self.frame_pedidos)
        self.ventana_pedidos()

# ---------------------------------------------------------------------------------------------        
    def mostrar_usuario(self, frame):
        usuario = self.modelo.obtener_lista("usuarios", "nombre_usuario")
        Label(frame, text="Usuario:", font=("Arial", 10)).grid(row=0, column=11, sticky='nw')
        Label(frame, text=usuario[0], font=("Arial", 10, "bold")).grid(row=0, column=12, sticky='nw')

    def crear_interfaz(self, frame):
        # Variable para los Radiobuttons (1: Dirección, 2: Empresa)
        self.opcion_seleccionada = IntVar(value=1)  # Dirección por defecto

# -------------------
        # Label Dirección
        Label(frame, text="Dirección:", font=("Arial", 14)).grid(row=1, column=0, sticky='e', padx=5, pady=2)

        self.entrada_direccion = AutocompleteCombobox(frame, font=("Arial", 14), width=15)
        self.entrada_direccion.grid(row=1, column=1, padx=5)

        # Llamo cargar direcciones antes de hacer click
        self.cargar_direcciones()

        # Actualizar al hacer clic
        self.entrada_direccion.bind("<FocusIn>", lambda event: self.cargar_direcciones())

        rb_direccion = Radiobutton(frame, variable=self.opcion_seleccionada, value=1,
                                command=self.actualizar_estado_comboboxes)
        rb_direccion.grid(row=1, column=2, padx=5)
        rb_direccion.configure(takefocus=0)

# ---------------
        # Empresa
        Label(frame, text="Empresa:", font=("Arial", 14)).grid(row=2, column=0, sticky='e', padx=5, pady=2)

        self.entrada_empresa = AutocompleteCombobox(frame, font=("Arial", 14), width=15)
        self.entrada_empresa.config(state='disabled')
        self.entrada_empresa.grid(row=2, column=1, padx=5)

        self.entrada_empresa.bind("<Button-1>", lambda event: self.cargar_empresas())

        rb_empresa = Radiobutton(frame, variable=self.opcion_seleccionada, value=2,
                                command=self.actualizar_estado_comboboxes)
        rb_empresa.grid(row=2, column=2, padx=5)
        rb_empresa.configure(takefocus=0)

        self.fila_base = 3  # Fila donde empiezan los campos de pedidos
        self.filas = []
        self.agregar_fila_pedido()

# ---------------
        # Cadetes
        Label(frame, text="Cadete:", font=("Arial", 14)).grid(row=102, column=0, sticky='e')
        self.entrada_cadetes = AutocompleteCombobox(frame, font=("Arial", 14), width=15)
        self.entrada_cadetes.grid(row=102, column=1)
        self.entrada_cadetes.bind("<Button-1>", lambda event: self.cargar_cadetes())


        #Agregar pedido
        self.btn_agregar = Button(self.frame_pedidos, text="Agregar pedido", font=("Arial", 14), command=self.agregar_fila_pedido)
        self.btn_agregar.grid(row=103, column=2, padx=5)

        # Cargar pedido boton
        self.btn_cargar = Button(frame, text="Cargar pedido", font=("Arial", 14), command=self.cargar_pedido).grid(row=103, column=1, pady=20)

    def agregar_fila_pedido(self):
        fila = self.fila_base + len(self.filas)

        if len(self.filas) >= 10:
            self.btn_agregar.config(state=DISABLED)
            return

        widgets_fila = []  # Para destruir después
        datos_fila = []    # Para leer datos
        
#--------------------
        # NOMBRE
        l_nombre = Label(self.frame_pedidos, text="Nombre:", font=("Arial", 14))
        l_nombre.grid(row=fila, column=0, sticky='e')

        self.e_nombre = AutocompleteCombobox(self.frame_pedidos, font=("Arial", 14), width=15)
        self.e_nombre.grid(row=fila, column=1)
        self.e_nombre.bind("<Button-1>", lambda event: self.cargar_nombres())

        widgets_fila.extend([l_nombre, self.e_nombre])
        datos_fila.append(self.e_nombre)

# ------TIPO MENU --------------
        # Tipo de menú
        menu_tipo_var = StringVar()
        cb_menu_tipo = ttk.Combobox(self.frame_pedidos, textvariable=menu_tipo_var, font=("Arial", 14), width=12)

        # Cargar tipos de menú + opción especial
        tipos_menu_db = self.modelo.obtener_lista("tipo_menu", "tipoMenu")
        cb_menu_tipo['values'] = tipos_menu_db + ["Agregar menú..."]
        cb_menu_tipo.set("")  # Inicia vacío

        cb_menu_tipo.grid(row=fila, column=3, padx=10, pady=5)

        # Menú específico
        menu_var = StringVar()
        cb_menu = ttk.Combobox(self.frame_pedidos, textvariable=menu_var, font=("Arial", 14), width=15)
        cb_menu.set("")  # Inicia vacío
        cb_menu.grid(row=fila, column=4, padx=10, pady=5)

        # Actualizar menús según tipo
        def actualizar_menu(event=None):
            tipo = menu_tipo_var.get()
            if tipo and tipo != "Agregar menú...":
                menus = self.modelo.obtener_menus_por_tipo(tipo)
                cb_menu['values'] = menus
                cb_menu.set(menus[0] if menus else "")
            else:
                cb_menu['values'] = []
                cb_menu.set("")

        # Crear nuevo menú
        def tipo_menu_seleccionado():
            top = Toplevel(self.frame_pedidos)
            top.title("Agregar nuevo menú")
            top.geometry("300x200")
            top.grab_set()

            def al_cerrar():
                top.destroy()
                menu_tipo_var.set("")
                actualizar_menu()

            top.protocol("WM_DELETE_WINDOW", al_cerrar)
            top.bind("<Escape>", lambda e: al_cerrar())

            frame_contenido = Frame(top)
            frame_contenido.pack(padx=10, pady=10, fill="both", expand=True)

            Label(frame_contenido, text="Tipo base:", font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
            tipo_base_var = StringVar()
            cb_tipo_base = ttk.Combobox(frame_contenido, textvariable=tipo_base_var, font=("Arial", 12), width=25)
            tipos_disponibles = self.modelo.obtener_lista("tipo_menu", "tipoMenu")
            cb_tipo_base['values'] = tipos_disponibles
            cb_tipo_base.pack(pady=(0, 10))
            if tipos_disponibles:
                cb_tipo_base.current(0)

            Label(frame_contenido, text="Nuevo menú:", font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
            entrada_menu = Entry(frame_contenido, font=("Arial", 12), width=25)
            entrada_menu.pack(pady=(0, 10))

            def agregar():
                tipo = tipo_base_var.get().strip()
                nuevo_menu = entrada_menu.get().strip()

                if not tipo or not nuevo_menu:
                    messagebox.showerror("Error", "Debe ingresar tipo y menú.")
                    return

                self.modelo.insertar_tipo_menu(tipo)
                self.modelo.insertar_menu(tipo, nuevo_menu)

                # Actualizar valores en comboboxes
                nuevos_tipos = self.modelo.obtener_lista("tipo_menu", "tipoMenu")
                cb_menu_tipo['values'] = nuevos_tipos + ["Agregar menú..."]
                menu_tipo_var.set(tipo)
                actualizar_menu()
                menu_var.set(nuevo_menu)
                top.destroy()

            Button(frame_contenido, text="Agregar", font=("Arial", 12), command=agregar).pack(pady=10)
            top.bind("<Return>", lambda e: agregar())

        # Combobox seleccionó algo
        def on_tipo_menu_selected(event=None):
            if menu_tipo_var.get() == "Agregar menú...":
                tipo_menu_seleccionado()
            else:
                actualizar_menu()

        # Bind del evento de selección
        cb_menu_tipo.bind("<<ComboboxSelected>>", on_tipo_menu_selected)

        # Guardar widgets y datos
        widgets_fila.extend([cb_menu_tipo, cb_menu])
        datos_fila.extend([menu_tipo_var, menu_var])


# ----------------------------------------------------------------------------------------------------
# GUARNICIÓN
        l_guarnicion = Label(self.frame_pedidos, text="Guarnición", font=("Arial", 14))
        l_guarnicion.grid(row=1, column=6)
        widgets_fila.append(l_guarnicion)

        guarnicion_var = StringVar()
        e_guarnicion = ttk.Combobox(self.frame_pedidos, textvariable=guarnicion_var, font=("Arial", 14), width=12)

        # Obtener guarniciones desde la base usando función genérica
        opciones_guarnicion = self.modelo.obtener_lista("guarniciones", "guarnicion")
        opciones_guarnicion.append("Agregar guarnición...")
        e_guarnicion['values'] = opciones_guarnicion
        guarnicion_var.set("")
        e_guarnicion.grid(row=fila, column=6)
        widgets_fila.append(e_guarnicion)
        datos_fila.append(guarnicion_var)

        def agregar_guarnicion():
            top = Toplevel(self.frame_pedidos)
            top.title("Agregar nueva guarnición")
            top.geometry("300x150")
            top.grab_set()

            Label(top, text="Nueva guarnición:", font=("Arial", 12)).pack(pady=10)
            entrada = Entry(top, font=("Arial", 12), width=25)
            entrada.pack(pady=5)

            def confirmar():
                nueva = entrada.get().strip()
                if not nueva:
                    messagebox.showerror("Error", "Debe ingresar una guarnición.")
                    return

                try:
                    self.modelo.insertar_valores("guarniciones", "guarnicion", nueva)
                    # Recargar desde DB usando función genérica
                    nuevas_opciones = self.modelo.obtener_lista("guarniciones", "guarnicion") + ["Agregar guarnición..."]
                    e_guarnicion['values'] = nuevas_opciones
                    guarnicion_var.set(nueva)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

                top.destroy()

            def al_cerrar():
                guarnicion_var.set("")
                top.destroy()

            top.protocol("WM_DELETE_WINDOW", al_cerrar)
            Button(top, text="Agregar", font=("Arial", 12), command=confirmar).pack(pady=10)
            entrada.bind("<Return>", lambda e: confirmar())

        def on_guarnicion_selected(event=None):
            if guarnicion_var.get() == "Agregar guarnición...":
                agregar_guarnicion()

        e_guarnicion.bind("<<ComboboxSelected>>", on_guarnicion_selected)

 # -------------------------------------------------------------------------------------------------

        # Descripción
        l_desc = Label(self.frame_pedidos, text="Descripción", font=("Arial", 14))
        l_desc.grid(row=1, column=7)
        e_descripcion = Entry(self.frame_pedidos, font=("Arial", 14), width=20)
        e_descripcion.grid(row=fila, column=7, padx=10, pady=5)
        widgets_fila.extend([l_desc, e_descripcion])
        datos_fila.append(e_descripcion)

 # -------------------------------------------------------------------------------------------------

        # Cantidad
        l_cant = Label(self.frame_pedidos, text="Cantidad", font=("Arial", 14))
        l_cant.grid(row=1, column=8, padx=10, pady=5, sticky='e')
        e_cantidad = Spinbox(self.frame_pedidos, from_=1, to=100, width=3, font=("Arial", 14), justify='center')
        e_cantidad.grid(row=fila, column=8, padx=5, pady=5)
        widgets_fila.extend([l_cant, e_cantidad])
        datos_fila.append(e_cantidad)

 # -------------------------------------------------------------------------------------------------

        # Forma de pago
        l_pago = Label(self.frame_pedidos, text="Forma de pago", font=("Arial", 14))
        l_pago.grid(row=1, column=9)

        pago_var = StringVar()
        cb_pago = ttk.Combobox(self.frame_pedidos, textvariable=pago_var, font=("Arial", 14), width=12)

        opciones_pago = self.modelo.obtener_lista("forma_pago", "forma_pago") + ["Agregar forma de pago..."]
        cb_pago['values'] = opciones_pago
        cb_pago.set("")
        cb_pago.grid(row=fila, column=9, padx=10, pady=5)

        def agregar_forma_pago():
            top = Toplevel(self.frame_pedidos)
            top.title("Agregar forma de pago")
            top.geometry("300x150")
            top.grab_set()

            Label(top, text="Nueva forma de pago:", font=("Arial", 12)).pack(pady=10)
            entrada = Entry(top, font=("Arial", 12), width=25)
            entrada.pack(pady=5)

            def confirmar():
                nueva = entrada.get().strip()
                if not nueva:
                    messagebox.showerror("Error", "Debe ingresar una forma de pago.")
                    return
                try:
                    self.modelo.insertar_valores("forma_pago", "forma_pago", nueva)
                    nuevas_opciones = self.modelo.obtener_lista("forma_pago", "forma_pago") + ["Agregar forma de pago..."]
                    cb_pago['values'] = nuevas_opciones
                    pago_var.set(nueva)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
                top.destroy()

            def al_cerrar():
                pago_var.set("")
                top.destroy()

            top.protocol("WM_DELETE_WINDOW", al_cerrar)
            Button(top, text="Agregar", font=("Arial", 12), command=confirmar).pack(pady=10)
            entrada.bind("<Return>", lambda e: confirmar())

        def forma_pago_seleccionada(event=None):
            if pago_var.get() == "Agregar forma de pago...":
                agregar_forma_pago()

        cb_pago.bind("<<ComboboxSelected>>", forma_pago_seleccionada)

        widgets_fila.extend([l_pago, cb_pago])
        datos_fila.append(pago_var)
              
 # -------------------------------------------------------------------------------------------------
        # Estados
        opciones_estado = ["Pendiente", "Pagado"]

        l_estado = Label(self.frame_pedidos, text="Estado", font=("Arial", 14))
        l_estado.grid(row=1, column=10)
        widgets_fila.append(l_estado)

        estado_var = StringVar()
        e_estado = ttk.Combobox(self.frame_pedidos, textvariable=estado_var, font=("Arial", 14), width=12)
        e_estado['values'] = opciones_estado
        e_estado.current(0)
        e_estado.grid(row=fila, column=10)
        widgets_fila.append(e_estado)
        datos_fila.append(estado_var) 

        self.filas.append((widgets_fila, datos_fila))

        # Crear botón borrar si no es la primera fila
        if len(self.filas) > 1:
            self.crear_boton_borrar_fila(widgets_fila)


    def ventana_pedidos(self):
        # Configurar la ventana para que se expanda
        self.rowconfigure(104, weight=1)
        self.columnconfigure(0, weight=1)

        # Contenedor principal
        frame_contenedor = Frame(self)
        frame_contenedor.grid(row=104, column=0, sticky='nsew', padx=10, pady=10)

        # Configurar expansión del contenedor
        frame_contenedor.rowconfigure(0, weight=1)
        frame_contenedor.columnconfigure(0, weight=3)  # Izquierda más grande
        frame_contenedor.columnconfigure(1, weight=1)

        # Frame izquierdo con el Treeview
        frame_izquierdo = Frame(frame_contenedor)
        frame_izquierdo.grid(row=0, column=0, sticky='nsew')

        frame_izquierdo.rowconfigure(0, weight=1)
        frame_izquierdo.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            frame_izquierdo,
            columns=("n", "dirección", "nombre", "menu", "descripcion", "cantidad", "forma de pago", "cadete", "estado"),
            show="headings"
        )

        # Configurar cabeceras y columnas
        self.tree.heading("n", text="N°")
        self.tree.heading("dirección", text="Dirección / Empresa")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("menu", text="Menú")
        self.tree.heading("descripcion", text="Descripción")
        self.tree.heading("cantidad", text="Cantidad")
        self.tree.heading("forma de pago", text="Forma de pago")
        self.tree.heading("cadete", text="Cadete")
        self.tree.heading("estado", text="Estado")

        self.tree.column("n", width=50, anchor='center')
        self.tree.column("dirección", width=200)
        self.tree.column("nombre", width=200)
        self.tree.column("menu", width=230)
        self.tree.column("descripcion", width=300)
        self.tree.column("cantidad", width=80, anchor='center')
        self.tree.column("forma de pago", width=180)
        self.tree.column("cadete", width=180)
        self.tree.column("estado", width=180)

        self.tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        # Frame derecho con botones
        frame_derecho = Frame(frame_contenedor)
        frame_derecho.grid(row=0, column=1, sticky='ns', padx=5)

        Button(frame_derecho, text="Cargar viaje", font=("Arial", 14)).pack(pady=10)
        Button(frame_derecho, text="Ver viajes", font=("Arial", 14)).pack(pady=10)

        # Botones debajo
        botones_frame = Frame(self)
        botones_frame.grid(row=105, column=0, columnspan=2, pady=10)

        Button(botones_frame, text="Ver tabla completa", font=("Arial", 14), command=self.pedidos_tablaCompleta).grid(row=0, column=0, padx=5)
        Button(botones_frame, text="Actualizar", font=("Arial", 14)).grid(row=0, column=1, padx=5)
        Button(botones_frame, text="Modificar", font=("Arial", 14)).grid(row=0, column=2, padx=5)
        Button(botones_frame, text="Eliminar", font=("Arial", 14)).grid(row=0, column=3, padx=5)

        self.cargar_pedidos_desde_db()

# ---------------------------------------------------------------------------------------------  
    def cargar_pedido(self):
        if not self.conn:
            messagebox.showerror("Error", "No se pudo establecer conexión con la base de datos.")
            return

        opcion = self.opcion_seleccionada.get()
        direccion = self.entrada_direccion.get().strip()
        empresa = self.entrada_empresa.get().strip()
        cadete = self.entrada_cadetes.get().strip()

        # Validaciones básicas
        if opcion == 1 and not direccion:
            messagebox.showwarning("Campo vacío", "El campo de dirección no puede estar vacía.")
            return
        elif opcion == 2 and not empresa:
            messagebox.showwarning("Campo vacío", "El campo de empresa no puede estar vacía.")
            return

        try:
            # Tomar datos generales del primer pedido
            nombre_cliente = ""
            estado = ""
            forma_pago = ""

            if self.filas:
                datos_fila = self.filas[0][1]
                nombre_cliente = datos_fila[0].get().strip()
                tipo_menu = datos_fila[1].get().strip()
                forma_pago = datos_fila[6].get().strip()
                estado = datos_fila[7].get().strip()

            # Insertar valores si no existen
            if direccion:
                self.modelo.insertar_valores("direcciones", "direccion", direccion)
            if empresa:
                self.modelo.insertar_valores("empresas", "empresa", empresa)
            if cadete:
                self.modelo.insertar_valores("cadetes", "cadete", cadete)
            if nombre_cliente:
                self.modelo.insertar_valores("nombres", "nombre", nombre_cliente)
            if forma_pago:
                self.modelo.insertar_valores("forma_pago", "forma_pago", forma_pago)

            # Obtener IDs
            id_direccion = self.modelo.obtener_id("direcciones", "direccion", direccion) if direccion else None
            id_empresa = self.modelo.obtener_id("empresas", "empresa", empresa) if empresa else None
            id_cadete = self.modelo.obtener_id("cadetes", "cadete", cadete) if cadete else None
            id_forma_pago = self.modelo.obtener_id("forma_pago", "forma_pago", forma_pago) if forma_pago else None
            id_usuario = 1  # por ahora fijo
            fecha = date.today()

            # Insertar pedido principal
            self.modelo.insertar_pedido(
                id_direccion, id_empresa, id_cadete,
                id_usuario, id_forma_pago, fecha,
                nombre_cliente, estado
            )

            # Obtener último ID del pedido
            with self.conn.cursor(buffered=True) as cursor:
                cursor.execute("SELECT LAST_INSERT_ID()")
                id_pedido = cursor.fetchone()[0]

            # Insertar detalles de cada fila
            for widgets_fila, datos_fila in self.filas:
                nombre = datos_fila[0].get().strip()
                tipo_menu = datos_fila[1].get().strip()
                menu = datos_fila[2].get().strip()
                guarnicion = datos_fila[3].get().strip()
                descripcion = datos_fila[4].get().strip()
                cantidad = datos_fila[5].get().strip()

                if not tipo_menu or not menu or not cantidad.isdigit():
                    continue

                # Insertar menú y tipo
                self.modelo.insertar_tipo_menu(tipo_menu)
                self.modelo.insertar_menu(tipo_menu, menu, guarnicion)
                id_menu = self.modelo.obtener_id("menus", "nombre_menu", menu)

                # Insertar detalle
                self.modelo.insertar_detalle_pedido(id_pedido, id_menu, int(cantidad), descripcion)

            # Éxito
            messagebox.showinfo("Éxito", "Pedido cargado exitosamente.")

            # Refrescar vista
            self.cargar_pedidos_desde_db()

            # Limpiar formulario
            self.entrada_direccion.delete(0, END)
            self.entrada_empresa.delete(0, END)
            self.entrada_cadetes.delete(0, END)

            for widgets_fila, _ in self.filas:
                for widget in widgets_fila:
                    widget.destroy()
            self.filas.clear()
            self.btn_agregar.config(state=NORMAL)
            self.agregar_fila_pedido()

        except Exception as e:
            import traceback
            print("ERROR en cargar_pedido:")
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudo guardar el pedido:\n{e}")

# ------------------------------
    # Cargar pedidos desde la base de datos
    def cargar_pedidos_desde_db(self):
        if not self.conn:
            messagebox.showerror("Error", "No hay conexión a la base de datos.")
            return
        
        try:
            resultados = self.modelo.obtener_pedidos_completos()
            self.tree.delete(*self.tree.get_children())

            for i, fila in enumerate(resultados, start=1):
                (_, direccion, empresa, nombre_cliente, menu, descripcion, cantidad, forma_pago, cadete, estado) = fila

                descripcion = descripcion if descripcion else ""
                cantidad = cantidad if cantidad is not None else 0

                self.tree.insert("", "end", values=(
                    i,
                    f"{direccion}{empresa}",
                    nombre_cliente,
                    menu,
                    descripcion,
                    cantidad,
                    forma_pago,
                    cadete,
                    estado
                ))
        except Exception as e: 
            print("Error al cargar pedidos desde DB:", e)  # Imprime en consola el error completo
            messagebox.showerror("Error al cargar", f"No se pudieron cargar los datos: {e}")
            

# -------------------------------------------
    # Boton ver tabla completa , tabla de pedidos de clientes completa            
    def pedidos_tablaCompleta(self):
        ventana = Toplevel(self)
        ventana.title("Pedidos cargados")

        ventana.state('zoomed')
           
        tree = ttk.Treeview(ventana, columns=("n","dirección", "nombre", "menu", "descripcion", "cantidad", "forma de pago", "cadete", "estado"), show="headings")
        tree.heading("n", text="N°")
        tree.heading("dirección", text="Dirección")
        tree.heading("nombre", text="Nombre")
        tree.heading("menu", text="Menú")
        tree.heading("descripcion", text="Descripción")
        tree.heading("cantidad", text="Cantidad")
        tree.heading("forma de pago", text="Forma de pago")
        tree.heading("cadete", text="Cadete")
        tree.heading("estado", text="Estado")

        tree.column("n", width=50, anchor='center')
        tree.column("dirección", width=150)
        tree.column("nombre", width=150)
        tree.column("menu", width=150)
        tree.column("descripcion", width=200)
        tree.column("cantidad", width=80, anchor='center')
        tree.column("forma de pago", width=150)
        tree.column("cadete", width=150)
        tree.column("estado", width=150)

        tree.pack(padx=10, pady=10, fill='both', expand=True)
# --------------------------------------------------------------

    def actualizar_estado_comboboxes(self):
        opcion = self.opcion_seleccionada.get()

        if opcion == 1:  # Dirección seleccionada
            self.entrada_direccion.config(state='normal')
            self.entrada_empresa.set('')  # Limpiar contenido
            self.entrada_empresa.config(state='disabled')
        elif opcion == 2:  # Empresa seleccionada
            self.entrada_empresa.config(state='normal')
            self.entrada_direccion.set('')  # Limpiar contenido
            self.entrada_direccion.config(state='disabled')

    def crear_boton_borrar_fila(self, fila_widgets):
        # Solo mostrar el botón si hay más de una fila
        if len(self.filas) <= 1:
            return

        btn_borrar = Button(self.frame_pedidos, text="❌", font=("Arial", 12),
                            command=lambda: self.borrar_fila(fila_widgets))
        btn_borrar.grid(row=fila_widgets[0].grid_info()['row'], column=11, padx=5)
        fila_widgets.append(btn_borrar)

    def borrar_fila(self, fila_widgets):
        for widget in fila_widgets:
            widget.destroy()

        # Eliminar la fila de la lista de filas
        self.filas = [fila for fila in self.filas if fila[0] != fila_widgets]

        # Habilitar botón agregar si estaba deshabilitado
        if len(self.filas) < 10:
            self.btn_agregar.config(state=NORMAL)
    


# LABEL DIRECCIONES
    def cargar_direcciones(self):
        if self.conn:
            try:
                direcciones = self.modelo.obtener_lista("direcciones", "direccion")
                self.entrada_direccion.set_completion_list(direcciones)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar las direcciones:\n{e}")

# LABEL EMPRESAS
    def cargar_empresas(self):
        if self.conn:
            try:
                empresas = self.modelo.obtener_lista("empresas", "empresa")
                self.entrada_empresa.set_completion_list(empresas)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar los nombres de empresas:\n{e}")

# LABEL CADETES
    def cargar_cadetes(self):
        if self.conn:
            try:
                cadetes = self.modelo.obtener_lista("cadetes", "cadete")
                self.entrada_cadetes.set_completion_list(cadetes)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar los cadetes:\n{e}")

# LABEL NOMBRES
    def cargar_nombres(self):
        if self.conn:
            try:
                nombres = self.modelo.obtener_lista("nombres", "nombre")
                self.e_nombre.set_completion_list(nombres)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar los nombres:\n{e}")






                 









