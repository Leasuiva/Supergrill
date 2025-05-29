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

        self.opcion_seleccionada = IntVar(value=1)

        self.mostrar_usuario(self.frame_pedidos)
        self.crear_seccion_direccion(self.frame_pedidos)
        self.crear_seccion_empresa(self.frame_pedidos)
        self.crear_seccion_cadete(self.frame_pedidos)
        self.crear_boton_agregar_y_cargar(self.frame_pedidos)
        

        self.fila_base = 4
        self.agregar_fila_pedido()

        self.ventana_pedidos()
        self.crear_buscador()

# --------------------------------- PARTE SUPERIOR -------------------------------

## -------- CAMPO MOSTRAR USUARIO
    def mostrar_usuario(self, frame):
        usuario = self.modelo.obtener_lista("usuarios", "nombre_usuario")
        Label(frame, text="Usuario:", font=("Arial", 10)).grid(row=0, column=11, sticky='nw')
        Label(frame, text=usuario[0], font=("Arial", 10, "bold")).grid(row=0, column=12, sticky='nw')
# ------------------------------------------------------------------

## -------- CAMPO DIRECCION
    def crear_seccion_direccion(self, frame, fila=1):
        Label(frame, text="Dirección:", font=("Arial", 14)).grid(row=fila, column=0, sticky='e', padx=5, pady=2)

        self.entrada_direccion = AutocompleteCombobox(frame, font=("Arial", 14), width=15)
        self.entrada_direccion.grid(row=fila, column=1, padx=5)
        self.entrada_direccion.bind("<FocusIn>", lambda event: self.cargar_direcciones())
        self.cargar_direcciones()

        rb_direccion = Radiobutton(
            frame, variable=self.opcion_seleccionada, value=1,
            command=self.actualizar_estado_comboboxes
        )
        rb_direccion.grid(row=fila, column=2, padx=5)
        rb_direccion.configure(takefocus=0)

    def cargar_direcciones(self):
        if self.conn:
            try:
                direcciones = self.modelo.obtener_lista("direcciones", "direccion")
                self.entrada_direccion.set_completion_list(direcciones)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar las direcciones:\n{e}")
# ------------------------------------------------------------------

## -------- CAMPO EMPRESA
    def crear_seccion_empresa(self, frame, fila=2):
        Label(frame, text="Empresa:", font=("Arial", 14)).grid(row=fila, column=0, sticky='e', padx=5, pady=2)

        self.entrada_empresa = AutocompleteCombobox(frame, font=("Arial", 14), width=15, state='disabled')
        self.entrada_empresa.grid(row=fila, column=1, padx=5)
        self.entrada_empresa.bind("<Button-1>", lambda event, combo=self.entrada_empresa: self.cargar_empresas(combo))

        rb_empresa = Radiobutton(
            frame, variable=self.opcion_seleccionada, value=2,
            command=self.actualizar_estado_comboboxes
        )
        rb_empresa.grid(row=fila, column=2, padx=5)
        rb_empresa.configure(takefocus=0)

    def cargar_empresas(self, combobox):
        if self.conn:
            try:
                empresas = self.modelo.obtener_lista("empresas", "empresa")
                combobox.set_completion_list(empresas)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar los nombres de empresas:\n{e}")
# ------------------------------------------------------------------

## -------- ACTUALIZAR ESTADO DE COMBOBOXES PARA EMPRESA Y DIRECCION
    def actualizar_estado_comboboxes(self):
        ''' Actualiza el estado de los campos de dirección y empresa según la opción seleccionada. '''
        opcion = self.opcion_seleccionada.get()

        if opcion == 1:  # Dirección seleccionada
            self.entrada_direccion.config(state='normal')
            self.entrada_empresa.set('')  # Limpiar contenido
            self.entrada_empresa.config(state='disabled')
        elif opcion == 2:  # Empresa seleccionada
            self.entrada_empresa.config(state='normal')
            self.entrada_direccion.set('')  # Limpiar contenido
            self.entrada_direccion.config(state='disabled')
# ------------------------------------------------------------------

## -------- CAMPO CADETE
    def crear_seccion_cadete(self, frame, fila=3):
        Label(frame, text="Cadete:", font=("Arial", 14)).grid(row=fila, column=0, sticky='e')

        self.entrada_cadetes = AutocompleteCombobox(frame, font=("Arial", 14), width=15)
        self.entrada_cadetes.grid(row=fila, column=1)
        self.entrada_cadetes.bind("<Button-1>", lambda event, combo=self.entrada_cadetes: self.cargar_cadetes(combo))

    def cargar_cadetes(self, combobox):
        if self.conn:
            try:
                cadetes = self.modelo.obtener_lista("cadetes", "cadete")
                combobox.set_completion_list(cadetes)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar los cadetes:\n{e}")
# ------------------------------------------------------------------

## -------- CAMPO NOMBRE
    def crear_campo_nombre(self, frame, fila):
        widgets = []

        l_nombre = Label(frame, text="Nombre:", font=("Arial", 14))
        l_nombre.grid(row=fila, column=0, sticky='e', padx=5, pady=5)

        e_nombre = AutocompleteCombobox(frame, font=("Arial", 14), width=15)
        e_nombre.grid(row=fila, column=1, padx=5)

        # Pasamos la referencia del combobox como argumento para actualizarlo
        e_nombre.bind("<Button-1>", lambda event, combo=e_nombre: self.cargar_nombres(combo))

        widgets.extend([l_nombre, e_nombre])
        return widgets, e_nombre
    # Método para cargar nombres en el combobox
    def cargar_nombres(self, combobox):
        if self.conn:
            try:
                nombres = self.modelo.obtener_lista("nombres", "nombre")
                combobox.set_completion_list(nombres)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar los nombres:\n{e}")

# ------------------------------------------------------------------

## -------- CAMPO MENU
    def crear_campo_menu(self, frame, fila):
        widgets = []

        # Etiqueta para el campo de tipo menú
        tipo_menu = Label(frame, text="Tipo de menú", font=("Arial", 14))
        tipo_menu.grid(row=3, column=3, padx=5)
        widgets.append(tipo_menu)

        # Tipo de menú
        tipo_menu_var = StringVar()
        cb_menu_tipo = ttk.Combobox(frame, textvariable=tipo_menu_var, font=("Arial", 14), width=12, state="readonly")
        tipos_menu = self.modelo.obtener_lista("tipo_menu", "tipoMenu") + ["Agregar menú..."]
        cb_menu_tipo['values'] = tipos_menu
        cb_menu_tipo.set("")
        cb_menu_tipo.grid(row=fila, column=3, padx=10, pady=5)

        # Etiqueta para el campo de menú específico
        m_menu = Label(frame, text="Menú", font=("Arial", 14))
        m_menu.grid(row=3, column=4, padx=5)
        widgets.append(m_menu)

        # Menú específico
        menu_var = StringVar()
        cb_menu = ttk.Combobox(frame, textvariable=menu_var, font=("Arial", 14), width=15, state="readonly")
        cb_menu.set("")
        cb_menu.grid(row=fila, column=4, padx=10, pady=5)

        def actualizar_menu():
            tipo = tipo_menu_var.get()
            if tipo and tipo != "Agregar menú...":
                menus = self.modelo.obtener_menus_por_tipo(tipo)
                cb_menu['values'] = menus
                cb_menu.set(menus[0] if menus else "")
            else:
                cb_menu['values'] = []
                cb_menu.set("")

        def agregar_nuevo_menu():
            top = Toplevel(self)
            top.title("Agregar nuevo menú")
            top.geometry("300x200")
            top.grab_set()

            def cerrar():
                top.destroy()
                tipo_menu_var.set("")
                actualizar_menu()

            top.protocol("WM_DELETE_WINDOW", cerrar)
            top.bind("<Escape>", lambda e: cerrar())

            frame_contenido = Frame(top)
            frame_contenido.pack(padx=10, pady=10, fill="both", expand=True)

            Label(frame_contenido, text="Tipo base:", font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
            tipo_base_var = StringVar()
            cb_tipo_base = ttk.Combobox(frame_contenido, textvariable=tipo_base_var, font=("Arial", 12), width=25)
            tipos = self.modelo.obtener_lista("tipo_menu", "tipoMenu")
            cb_tipo_base['values'] = tipos
            cb_tipo_base.pack(pady=(0, 10))
            if tipos:
                cb_tipo_base.current(0)

            Label(frame_contenido, text="Nuevo menú:", font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
            entrada_menu = Entry(frame_contenido, font=("Arial", 12), width=25)
            entrada_menu.pack(pady=(0, 10))

            def confirmar():
                tipo = tipo_base_var.get().strip()
                nuevo_menu = entrada_menu.get().strip()

                if not tipo or not nuevo_menu:
                    messagebox.showerror("Error", "Debe ingresar tipo y menú.")
                    return

                self.modelo.insertar_tipo_menu(tipo)
                self.modelo.insertar_menu(tipo, nuevo_menu)

                nuevos_tipos = self.modelo.obtener_lista("tipo_menu", "tipoMenu") + ["Agregar menú..."]
                cb_menu_tipo['values'] = nuevos_tipos
                tipo_menu_var.set(tipo)
                actualizar_menu()
                menu_var.set(nuevo_menu)
                top.destroy()

            Button(frame_contenido, text="Agregar", font=("Arial", 12), command=confirmar).pack(pady=10)
            top.bind("<Return>", lambda e: confirmar())

        def on_tipo_menu_selected(event=None):
            if tipo_menu_var.get() == "Agregar menú...":
                agregar_nuevo_menu()
            else:
                actualizar_menu()

        cb_menu_tipo.bind("<<ComboboxSelected>>", on_tipo_menu_selected)

        widgets.extend([cb_menu_tipo, cb_menu])
        return widgets, tipo_menu_var, menu_var
# ------------------------------------------------------------------

## -------- CAMPO GUARNICION
    def crear_campo_guarnicion(self, frame, fila):
        widgets = []

        l_guarnicion = Label(frame, text="Guarnición", font=("Arial", 14))
        l_guarnicion.grid(row=3, column=5, padx=5)
        widgets.append(l_guarnicion)

        guarnicion_var = StringVar()
        cb_guarnicion = ttk.Combobox(frame, textvariable=guarnicion_var, font=("Arial", 14), width=12, state="readonly")

        opciones = [" "] + self.modelo.obtener_lista("guarniciones", "guarnicion") + ["Agregar guarnición..."]
        cb_guarnicion['values'] = opciones
        guarnicion_var.set(" ")
        cb_guarnicion.grid(row=fila, column=5, padx=5)
        widgets.append(cb_guarnicion)

        def agregar_nueva_guarnicion():
            top = Toplevel(self)
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
                    nuevas_opciones = self.modelo.obtener_lista("guarniciones", "guarnicion") + ["Agregar guarnición..."]
                    cb_guarnicion['values'] = nuevas_opciones
                    guarnicion_var.set(nueva)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
                top.destroy()

            def cerrar():
                guarnicion_var.set("")
                top.destroy()

            top.protocol("WM_DELETE_WINDOW", cerrar)
            Button(top, text="Agregar", font=("Arial", 12), command=confirmar).pack(pady=10)
            entrada.bind("<Return>", lambda e: confirmar())

        def on_select(event=None):
            if guarnicion_var.get() == "Agregar guarnición...":
                agregar_nueva_guarnicion()

        cb_guarnicion.bind("<<ComboboxSelected>>", on_select)

        return widgets, guarnicion_var
# ------------------------------------------------------------------

## -------- CAMPO DESCRIPCION
    def crear_campo_descripcion(self, frame, fila):
        widgets = []

        l_desc = Label(frame, text="Descripción", font=("Arial", 14))
        l_desc.grid(row=3, column=7, padx=5)
        widgets.append(l_desc)

        e_descripcion = Entry(frame, font=("Arial", 14), width=20)
        e_descripcion.grid(row=fila, column=7, padx=5)
        widgets.append(e_descripcion)

        return widgets, e_descripcion
# ------------------------------------------------------------------

## -------- CAMPO CANTIDAD
    def crear_campo_cantidad(self, frame, fila):
        widgets = []

        l_cant = Label(frame, text="Cantidad:", font=("Arial", 14))
        l_cant.grid(row=3, column=8, padx=10, pady=5, sticky='e')
        widgets.append(l_cant)

        # Función de validación para aceptar solo enteros >= 1
        def validar_cantidad(valor):
            if valor == "":
                return True  # permite borrar temporalmente
            try:
                return int(valor) >= 1
            except ValueError:
                return False

        vcmd = (frame.register(validar_cantidad), '%P')

        e_cantidad = Spinbox(
            frame,
            from_=1,
            to=100,
            width=5,
            font=("Arial", 14),
            justify='center',
            validate='key',
            validatecommand=vcmd
        )
        e_cantidad.grid(row=fila, column=8, padx=5, pady=5)
        widgets.append(e_cantidad)

        return widgets, e_cantidad

# ------------------------------------------------------------------ 
#   
## -------- CAMPO FORMA DE PAGO
    def crear_campo_pago(self, frame, fila):
        widgets = []

        l_pago = Label(frame, text="Forma de pago", font=("Arial", 14))
        l_pago.grid(row=3, column=9, padx=5)
        widgets.append(l_pago)

        pago_var = StringVar()
        cb_pago = ttk.Combobox(frame, textvariable=pago_var, font=("Arial", 14), width=15, state="readonly")

        opciones = self.modelo.obtener_lista("forma_pago", "forma_pago") + ["Agregar forma de pago..."]
        cb_pago['values'] = opciones
        pago_var.set("Sin seleccionar")
        cb_pago.grid(row=fila, column=9, padx=5)
        widgets.append(cb_pago)

        def agregar_forma_pago():
            top = Toplevel(self)
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
                    nuevas = self.modelo.obtener_lista("forma_pago", "forma_pago") + ["Agregar forma de pago..."]
                    cb_pago['values'] = nuevas
                    pago_var.set(nueva)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
                top.destroy()

            def cerrar():
                pago_var.set("")
                top.destroy()

            top.protocol("WM_DELETE_WINDOW", cerrar)
            Button(top, text="Agregar", font=("Arial", 12), command=confirmar).pack(pady=10)
            entrada.bind("<Return>", lambda e: confirmar())

        def on_select(event=None):
            if pago_var.get() == "Agregar forma de pago...":
                agregar_forma_pago()

        cb_pago.bind("<<ComboboxSelected>>", on_select)

        return widgets, pago_var

    
## -------- CAMPO ESTADOS
    def crear_campo_estado(self, frame, fila):
        widgets = []

        l_estado = Label(frame, text="Estado", font=("Arial", 14))
        l_estado.grid(row=3, column=11, padx=5)
        widgets.append(l_estado)

        estado_var = StringVar()
        cb_estado = ttk.Combobox(frame, textvariable=estado_var, font=("Arial", 14), width=12, state="readonly")
        valores_estados = ["Pendiente", "Pagado"]
        cb_estado['values'] = valores_estados
        cb_estado.current(0)
        cb_estado.grid(row=fila, column=11, padx=5)
        widgets.append(cb_estado)

        # Insertar en la tabla 'estados' si no existen
        for estado in valores_estados:
            self.modelo.insertar_valores("estados", "estado", estado)

        return widgets, estado_var
    
# ------------------------------------------------------------------

## -------- CAMPO AGREGAR FILA PARA OTRO PEDIDO MAS, BORRAR FILA 
    def agregar_fila_pedido(self):
        fila = self.fila_base + len(self.filas)
        if len(self.filas) >= 10:
            self.btn_agregar.config(state=DISABLED)
            return

        widgets_fila = []
        datos_fila = []

        # Crear cada campo modularmente
        w, e = self.crear_campo_nombre(self.frame_pedidos, fila); widgets_fila += w; datos_fila.append(e)
        w, tipo_menu, menu = self.crear_campo_menu(self.frame_pedidos, fila); widgets_fila += w; datos_fila += [tipo_menu, menu]
        w, guarnicion = self.crear_campo_guarnicion(self.frame_pedidos, fila); widgets_fila += w; datos_fila.append(guarnicion)
        w, descripcion = self.crear_campo_descripcion(self.frame_pedidos, fila); widgets_fila += w; datos_fila.append(descripcion)
        w, cantidad = self.crear_campo_cantidad(self.frame_pedidos, fila); widgets_fila += w; datos_fila.append(cantidad)
        w, forma_pago = self.crear_campo_pago(self.frame_pedidos, fila); widgets_fila += w; datos_fila.append(forma_pago)
        w, estado = self.crear_campo_estado(self.frame_pedidos, fila); widgets_fila += w; datos_fila.append(estado)

        self.filas.append((widgets_fila, datos_fila))

        if len(self.filas) > 1:
            self.crear_boton_borrar_fila(widgets_fila)
            
#  BOTON BORRAR FILA
    def crear_boton_borrar_fila(self, widgets_fila):
        btn_borrar = Button(
            self.frame_pedidos,
            text="❌",
            font=("Arial", 12),
            command=lambda: self.borrar_fila(widgets_fila)
        )
        # Lo colocamos en la columna siguiente a la última usada (ajustar si cambiás diseño)
        fila = widgets_fila[0].grid_info()['row']
        btn_borrar.grid(row=fila, column=13, padx=5)

        widgets_fila.append(btn_borrar)

    def borrar_fila(self, widgets_fila):
        for widget in widgets_fila:
            widget.destroy()

        self.filas = [fila for fila in self.filas if fila[0] != widgets_fila]

        if len(self.filas) < 10:
            self.btn_agregar.config(state=NORMAL)
# ------------------------------------------------------------------

## -------- CAMPO BOTONES AGREGAR Y CARGAR
    def crear_boton_agregar_y_cargar(self, frame, fila=104):
        # Botón "Agregar pedido"
        self.btn_agregar = Button(
            frame,
            text="Agregar pedido",
            font=("Arial", 14),
            command=self.agregar_fila_pedido
        )
        self.btn_agregar.grid(row=fila, column=2, padx=5, pady=10)

        # Botón "Cargar pedido"
        self.btn_cargar = Button(
            frame,
            text="Cargar pedido",
            font=("Arial", 14),
            command=self.cargar_pedido
        )
        self.btn_cargar.grid(row=fila, column=1, padx=5, pady=10)

    def cargar_pedido(self):
        if not self.conn:
            messagebox.showerror("Error", "No se pudo establecer conexión con la base de datos.")
            return
        
        # DEBUG TEMPORAL
        print("Cantidad de filas:", len(self.filas))
        for i, (_, datos_fila) in enumerate(self.filas):
            print(f"Fila {i+1}:")
            for campo in datos_fila:
                print("  -", campo.get().strip())

        # Determinar si se usó Dirección o Empresa
        opcion = self.opcion_seleccionada.get()
        direccion = self.entrada_direccion.get().strip()
        empresa = self.entrada_empresa.get().strip()
        cadete = self.entrada_cadetes.get().strip()

        # Validaciones básicas
        if opcion == 1 and not direccion:
            messagebox.showwarning("Campo vacío", "El campo de dirección no puede estar vacío.")
            return
        elif opcion == 2 and not empresa:
            messagebox.showwarning("Campo vacío", "El campo de empresa no puede estar vacío.")
            return

        try:
            # Tomar datos generales del primer pedido
            nombre_cliente = ""
            forma_pago = ""
            estado = ""

            if self.filas:
                datos_fila = self.filas[0][1]
                nombre_cliente = datos_fila[0].get().strip()
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
            if estado:
                self.modelo.insertar_valores("estados", "estado", estado)
                

            # Obtener IDs necesarios
            id_direccion = self.modelo.obtener_id("direcciones", "direccion", direccion) if direccion else None
            id_empresa = self.modelo.obtener_id("empresas", "empresa", empresa) if empresa else None
            id_cadete = self.modelo.obtener_id("cadetes", "cadete", cadete) if cadete else None
            id_forma_pago = self.modelo.obtener_id("forma_pago", "forma_pago", forma_pago) if forma_pago else None
            id_estado = self.modelo.obtener_id("estados", "estado", estado) if estado else None
            id_nombre = self.modelo.obtener_id("nombres", "nombre", nombre_cliente) if nombre_cliente else None
            id_usuario = 1  # Por ahora fijo
            fecha = date.today()

            # Insertar pedido principal
            self.modelo.insertar_pedido(
                id_direccion, id_empresa, id_cadete,
                id_usuario, id_forma_pago, fecha,
                id_nombre, id_estado
            )

            # Obtener ID del nuevo pedido
            with self.conn.cursor(buffered=True) as cursor:
                cursor.execute("SELECT LAST_INSERT_ID()")
                id_pedido = cursor.fetchone()[0]

            # Insertar detalles por cada fila
            for _, datos_fila in self.filas:
                nombre_cliente = datos_fila[0].get().strip()
                tipo_menu = datos_fila[1].get().strip()
                menu = datos_fila[2].get().strip()
                guarnicion = datos_fila[3].get().strip()
                descripcion = datos_fila[4].get().strip()
                cantidad = datos_fila[5].get().strip()
                cantidad = "1" if cantidad == "" or not cantidad.isdigit() or int(cantidad) <= 0 else cantidad

                # Insertar menú y tipo
                self.modelo.insertar_tipo_menu(tipo_menu)
                self.modelo.insertar_menu(tipo_menu, menu, guarnicion)
                id_menu = self.modelo.obtener_id_menu(tipo_menu, menu, guarnicion)

                # Insertar detalle
                self.modelo.insertar_detalle_pedido(id_pedido, id_menu, cantidad, descripcion)

            messagebox.showinfo("Éxito", "Pedido cargado exitosamente.")
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

# --------------------------------- PARTE DEL MEDIO --------------------------------

# --------------------------------- TREEVIEW PEDIDOS -------------------------------
    def ventana_pedidos(self):
        self.rowconfigure(104, weight=1)
        self.columnconfigure(0, weight=1)

        frame_contenedor = Frame(self)
        frame_contenedor.grid(row=104, column=0, sticky='nsew', padx=10, pady=10)
        frame_contenedor.rowconfigure(0, weight=1)
        frame_contenedor.columnconfigure(0, weight=3)
        frame_contenedor.columnconfigure(1, weight=1)

        self.crear_treeview(frame_contenedor)

        self.crear_botones_inferiores(self)
        self.crear_botones_viajes(frame_contenedor)

        self.cargar_pedidos_desde_db()

    def crear_treeview(self, parent):
        frame_tree = Frame(parent)
        frame_tree.grid(row=0, column=0, sticky='nsew')

        frame_tree.rowconfigure(0, weight=1)
        frame_tree.columnconfigure(0, weight=1)

        columnas = (
            "n", "dirección", "nombre", "menu", "descripcion",
            "cantidad", "forma de pago", "cadete", "estado"
        )

        self.tree = ttk.Treeview(
            frame_tree,
            columns=columnas,
            show="headings",
            height=10
        )

        encabezados = {
            "n": "N°",
            "dirección": "Dirección / Empresa",
            "nombre": "Nombre",
            "menu": "Menú",
            "descripcion": "Descripción",
            "cantidad": "Cantidad",
            "forma de pago": "Forma de pago",
            "cadete": "Cadete",
            "estado": "Estado"
        }

        anchos = {
            "n": 50,
            "dirección": 200,
            "nombre": 200,
            "menu": 230,
            "descripcion": 300,
            "cantidad": 80,
            "forma de pago": 180,
            "cadete": 180,
            "estado": 180
        }

        for col in columnas:
            self.tree.heading(col, text=encabezados[col])
            self.tree.column(col, width=anchos[col], anchor='center' if col in ["n", "cantidad"] else 'w')

        # Scrollbar tabla si excede los 10
        vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew', padx=(10, 0), pady=10)
        vsb.grid(row=0, column=1, sticky='ns', padx=(0, 10), pady=10)

        return frame_tree
    
    def cargar_pedidos_desde_db(self):
        self.todos_los_pedidos = []
        
        if not self.conn:
            messagebox.showerror("Error", "No hay conexión a la base de datos.")
            return

        try:
            resultados = self.modelo.obtener_pedidos_completos()
            self.tree.delete(*self.tree.get_children())  # Limpiar Treeview

            for i, fila in enumerate(resultados, start=1):
                (
                    _, direccion, empresa, nombre_cliente, menu,
                    guarnicion, descripcion, cantidad, forma_pago, cadete, estado
                ) = fila

                descripcion = descripcion or ""
                cantidad = cantidad if cantidad is not None else 0
                destino = direccion if direccion else empresa

                self.todos_los_pedidos.append((
                    i,
                    destino,
                    nombre_cliente,
                    f"{menu} - {guarnicion}",
                    descripcion,
                    cantidad,
                    forma_pago,
                    cadete,
                    estado
                ))

                self.tree.insert("", "end", values=(
                    i,
                    destino,
                    nombre_cliente,
                    f"{menu} - {guarnicion}",
                    descripcion,
                    cantidad,
                    forma_pago,
                    cadete,
                    estado
                ))

        except Exception as e:
            print("Error al cargar pedidos desde DB:", e)
            messagebox.showerror("Error al cargar", f"No se pudieron cargar los datos: {e}")

# ----------------- BUSCADOR DE DIRECCIONES DE PEDIDOS ----------------------------
    def crear_buscador(self):
        frame_buscador = Frame(self)
        frame_buscador.grid(row=103, column=0, sticky='we')

        label_buscar = Label(frame_buscador, text="Buscar:", font=("Arial", 10))
        label_buscar.grid(row=0, column=0, padx=20, sticky='w')

        self.entry_buscar = Entry(frame_buscador, width=30)
        self.entry_buscar.grid(row=0, column=1, padx=10, sticky='we')
        self.entry_buscar.bind("<KeyRelease>", self.filtrar_treeview)

        return frame_buscador
    
    def filtrar_treeview(self, event=None):
        texto = self.entry_buscar.get().lower()
        self.tree.delete(*self.tree.get_children())

        for fila in self.todos_los_pedidos:
            direccion_o_empresa = str(fila[1]).lower()
            if texto in direccion_o_empresa:
                self.tree.insert("", "end", values=fila)

# -----------------  BOTONES INFERIORES DEL TREEVIEW DE PEDIDOS -------------------
    def crear_botones_inferiores(self, parent):
        frame_botones = Frame(parent)
        frame_botones.grid(row=105, column=0, columnspan=2, pady=10)

        Button(
            frame_botones,
            text="Ver tabla completa",
            font=("Arial", 14),
            #command=self.  
        ).grid(row=0, column=0, padx=5)

        Button(
            frame_botones,
            text="Actualizar",
            font=("Arial", 14)
        ).grid(row=0, column=1, padx=5)

        Button(
            frame_botones,
            text="Modificar",
            font=("Arial", 14)
        ).grid(row=0, column=2, padx=5)

        Button(
            frame_botones,
            text="Eliminar",
            font=("Arial", 14)
        ).grid(row=0, column=3, padx=5)

# -----------------  PARTE DERECHA DEL TREVIEW DE PEDIDOS -------------------------
# BOTONES VIAJES
    def crear_botones_viajes(self, parent):
        frame_derecho = Frame(parent)
        frame_derecho.grid(row=0, column=1, sticky='ns', padx=5)

        Button(frame_derecho, text="Cargar viaje", font=("Arial", 14)).pack(pady=10)
        Button(frame_derecho, text="Ver viajes", font=("Arial", 14)).pack(pady=10)

        return frame_derecho

# -------------------------------------------------------------------------------------
# FUNCIONES DE VALIDACION

# ✅ Lista de mejoras y optimizaciones futuras
# 🧠 Código y arquitectura
#  Centralizar estilos (fuente, tamaño, colores) en constantes globales o archivo de configuración.

#  Separar aún más la lógica de interfaz de la lógica de negocio (ej. crear clases controladoras o services).

#  Modularizar la lógica de validación por campo (por ejemplo, cantidad, menú, dirección).

# 📦 Funcionalidades nuevas
#  Implementar lógica para el botón "Ver viajes".

#  Implementar lógica para el botón "Cargar viaje".

#  Conectar los botones "Modificar", "Actualizar" y "Eliminar" con la base de datos.

#  Agregar filtros de búsqueda en el Treeview.

#  Permitir exportar pedidos a PDF o Excel.

# 🔎 Experiencia de usuario
#  Agregar confirmación antes de eliminar pedidos.

#  Autocompletar campos relacionados (por ejemplo, cargar descripción según menú).

#  Añadir colores o iconos al Treeview para destacar estados (Pendiente, Pagado).

#  Agregar un contador visual de filas/pedidos.

# 📁 Organización
#  Crear una carpeta /widgets/ para mover los métodos de interfaz_utils.py.

#  Dividir aún más ModeloDB si empieza a crecer demasiado (por módulo: menú, pedidos, etc.).

#  Crear tests unitarios para verificar la inserción de datos.


# -------------------------------------------------------------------------------------
    # # Boton ver tabla completa , tabla de pedidos de clientes completa            
    # def pedidos_tablaCompleta(self):
    #     ventana = Toplevel(self)
    #     ventana.title("Pedidos cargados")

    #     ventana.state('zoomed')
           
    #     tree = ttk.Treeview(ventana, columns=("n","dirección", "nombre", "menu", "descripcion", "cantidad", "forma de pago", "cadete", "estado"), show="headings")
    #     tree.heading("n", text="N°")
    #     tree.heading("dirección", text="Dirección")
    #     tree.heading("nombre", text="Nombre")
    #     tree.heading("menu", text="Menú")
    #     tree.heading("descripcion", text="Descripción")
    #     tree.heading("cantidad", text="Cantidad")
    #     tree.heading("forma de pago", text="Forma de pago")
    #     tree.heading("cadete", text="Cadete")
    #     tree.heading("estado", text="Estado")

    #     tree.column("n", width=50, anchor='center')
    #     tree.column("dirección", width=150)
    #     tree.column("nombre", width=150)
    #     tree.column("menu", width=150)
    #     tree.column("descripcion", width=200)
    #     tree.column("cantidad", width=80, anchor='center')
    #     tree.column("forma de pago", width=150)
    #     tree.column("cadete", width=150)
    #     tree.column("estado", width=150)

    #     tree.pack(padx=10, pady=10, fill='both', expand=True)


