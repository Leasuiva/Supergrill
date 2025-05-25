class ModeloDB:
    def __init__(self, conexion):
        self.conn = conexion
        

#                              ------- CREACIONES DE TABLAS -------

# # --- TABLA DIRECCIONES ---
    def crear_tabla_direcciones(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS direcciones (
                id_direccion INT AUTO_INCREMENT PRIMARY KEY,
                direccion VARCHAR(150) NOT NULL
            );
        """)
        self.conn.commit()
        cursor.close()
        print("Tabla 'direcciones' creada o ya existía.")

# --- TABLA EMPRESA ---
    def crear_tabla_empresa(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empresas (
                id_empresa INT AUTO_INCREMENT PRIMARY KEY,
                empresa VARCHAR(150) NOT NULL
            );
        """)
        self.conn.commit()
        cursor.close()
        print("Tabla 'empresas' creada o ya existía.")

# --- TABLA NOMBRES --
    def crear_tabla_nombres(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nombres (
                id_nombre INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(30) NOT NULL
            );
        """)
        self.conn.commit()
        cursor.close()
        print("Tabla 'nombres' creada o ya existía.")

# ------------------------------------------------   
# --- TABLA CADETES ---
    def crear_tabla_cadetes(self):  
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cadetes (
                id_cadete INT AUTO_INCREMENT PRIMARY KEY,
                cadete VARCHAR(30) NOT NULL
            );
        """)
        self.conn.commit()
        cursor.close()
        print("Tabla 'cadetes' creada o ya existía.")

# ------------------------------------------------
# --- TABLA TIPO MENU ---
    def crear_tabla_tipo_menu(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tipo_menu (
                id_tipoMenu INT AUTO_INCREMENT PRIMARY KEY,
                tipoMenu VARCHAR(30) NOT NULL
            );
        """)
        self.conn.commit()
        cursor.close()
        print("Tabla 'tipoMenu' creada o ya existía.")

# -----------------------------------------------    
# --- TABLA MENUS ---
    def crear_tabla_menus(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menus (
                id_menu INT AUTO_INCREMENT PRIMARY KEY,
                nombre_menu VARCHAR(100) NOT NULL,
                id_tipoMenu INT NOT NULL,
                id_guarnicion INT,
                FOREIGN KEY (id_tipoMenu) REFERENCES tipo_menu(id_tipoMenu) ON DELETE CASCADE,
                FOREIGN KEY (id_guarnicion) REFERENCES guarniciones(id_guarnicion) ON DELETE SET NULL
            );
        """)
        self.conn.commit()
        cursor.close()
        print("Tabla 'menus' creada o ya existía.")

    def obtener_menus_por_tipo(self, tipo_nombre):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT m.nombre_menu 
            FROM menus m
            JOIN tipo_menu t ON m.id_tipoMenu = t.id_tipoMenu
            WHERE t.tipoMenu = %s
        """, (tipo_nombre,))
        menus = [fila[0] for fila in cursor.fetchall()]
        cursor.close()
        return menus
    
    def insertar_tipo_menu(self, nombre_tipo):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tipo_menu (tipoMenu)
            SELECT %s FROM DUAL WHERE NOT EXISTS (
                SELECT 1 FROM tipo_menu WHERE tipoMenu = %s
            )
        """, (nombre_tipo, nombre_tipo))
        self.conn.commit()
        cursor.close()

    def insertar_menu(self, tipo_nombre, nombre_menu, nombre_guarnicion=None):
        with self.conn.cursor(buffered=True) as cursor:
            cursor.execute("SELECT id_tipoMenu FROM tipo_menu WHERE tipoMenu = %s", (tipo_nombre,))
            fila_tipo = cursor.fetchone()
            if not fila_tipo:
                raise ValueError(f"Tipo de menú '{tipo_nombre}' no existe.")
            id_tipo = fila_tipo[0]

            id_guarnicion = None
            if nombre_guarnicion:
                cursor.execute("SELECT id_guarnicion FROM guarniciones WHERE guarnicion = %s", (nombre_guarnicion,))
                fila_guarnicion = cursor.fetchone()
                if fila_guarnicion:
                    id_guarnicion = fila_guarnicion[0]
                else:
                    # Crear guarnición si no existe
                    cursor.execute("INSERT INTO guarniciones (guarnicion) VALUES (%s)", (nombre_guarnicion,))
                    self.conn.commit()
                    id_guarnicion = cursor.lastrowid

            if id_guarnicion is not None:
                cursor.execute("""
                    INSERT INTO menus (id_tipoMenu, nombre_menu, id_guarnicion)
                    SELECT %s, %s, %s FROM DUAL WHERE NOT EXISTS (
                        SELECT 1 FROM menus WHERE id_tipoMenu = %s AND nombre_menu = %s AND id_guarnicion = %s
                    )
                """, (id_tipo, nombre_menu, id_guarnicion, id_tipo, nombre_menu, id_guarnicion))
            else:
                cursor.execute("""
                    INSERT INTO menus (id_tipoMenu, nombre_menu)
                    SELECT %s, %s FROM DUAL WHERE NOT EXISTS (
                        SELECT 1 FROM menus WHERE id_tipoMenu = %s AND nombre_menu = %s AND id_guarnicion IS NULL
                    )
                """, (id_tipo, nombre_menu, id_tipo, nombre_menu))

            self.conn.commit()
            print(f"Menú '{nombre_menu}' insertado correctamente.")
            # Se puede usar para insertar un menú en la tabla menus 

# -------------------------------------------------
# --- TABLA GUARNICIONES ---
    def crear_tabla_guarnicion(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guarniciones (
                id_guarnicion INT AUTO_INCREMENT PRIMARY KEY,
                guarnicion VARCHAR(30) NOT NULL
            );
        """)
        self.conn.commit()
        cursor.close()
        print("Tabla 'guarnicion' creada o ya existía.")

# -------------------------------------------------
# --- TABLA FORMA DE PAGO ---
    def crear_tabla_forma_pago(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forma_pago (
                id_forma_pago INT AUTO_INCREMENT PRIMARY KEY,
                forma_pago VARCHAR(30) NOT NULL
            );
        """)
        self.conn.commit()
        cursor.close()
        print("Tabla 'forma_pago' creada o ya existía.")

# -------------------------------------------------
# --- TABLA USUARIOS ---
    def crear_tabla_usuarios(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                nombre_usuario VARCHAR(30) NOT NULL,
                contrasena VARCHAR(100) NOT NULL
            );
        """)
        self.conn.commit()
        cursor.close()
        print("Tabla 'usuarios' creada o ya existía.")

# --------------------------------------------------
# --- TABLA PEDIDOS ---

    def crear_tabla_pedidos(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id_pedido INT AUTO_INCREMENT PRIMARY KEY,
                id_direccion INT,
                id_empresa INT,
                id_cadete INT,
                id_usuario INT,
                id_forma_pago INT,
                fecha DATE NOT NULL,
                nombre_cliente VARCHAR(100),
                estado VARCHAR(50),
                FOREIGN KEY (id_direccion) REFERENCES direcciones(id_direccion),
                FOREIGN KEY (id_empresa) REFERENCES empresas(id_empresa),
                FOREIGN KEY (id_cadete) REFERENCES cadetes(id_cadete),
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
                FOREIGN KEY (id_forma_pago) REFERENCES forma_pago(id_forma_pago)
            );
        """)
        self.conn.commit()
        cursor.close()  
        print("Tabla 'pedidos' creada o ya existía.")

    def obtener_pedidos(self):  
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.id_pedido, d.direccion, e.empresa, c.cadete, p.fecha, p.nombre_cliente, p.estado
            FROM pedidos p
            LEFT JOIN direcciones d ON p.id_direccion = d.id_direccion
            LEFT JOIN empresas e ON p.id_empresa = e.id_empresa
            LEFT JOIN cadetes c ON p.id_cadete = c.id_cadete
        """)
        filas = cursor.fetchall()
        cursor.close()
        lista_pedidos = []
        for fila in filas:
            lista_pedidos.append({
                "id_pedido": fila[0],
                "direccion": fila[1],
                "empresa": fila[2],
                "cadete": fila[3],
                "fecha": fila[4],
                "nombre_cliente": fila[5],
                "estado": fila[6]
            })
        return lista_pedidos

    def insertar_pedido(self, id_direccion, id_empresa, id_cadete, id_usuario, id_forma_pago, fecha, nombre_cliente, estado):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO pedidos (id_direccion, id_empresa, id_cadete, id_usuario, id_forma_pago, fecha, nombre_cliente, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (id_direccion, id_empresa, id_cadete, id_usuario, id_forma_pago, fecha, nombre_cliente, estado))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
        print("Pedido insertado correctamente.")
        # Se puede usar para insertar un pedido en la tabla pedidos

    def obtener_pedidos_completos(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                p.id_pedido,
                COALESCE(d.direccion, '') AS direccion,
                COALESCE(e.empresa, '') AS empresa,
                p.nombre_cliente,
                CONCAT(m.nombre_menu, ' - ', COALESCE(g.guarnicion, '')) AS menu,
                dp.descripcion,
                dp.cantidad,
                fp.forma_pago,
                c.cadete,
                p.estado
            FROM pedidos p
            LEFT JOIN direcciones d ON p.id_direccion = d.id_direccion
            LEFT JOIN empresas e ON p.id_empresa = e.id_empresa
            LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
            LEFT JOIN menus m ON dp.id_menu = m.id_menu
            LEFT JOIN guarniciones g ON m.id_guarnicion = g.id_guarnicion
            LEFT JOIN forma_pago fp ON p.id_forma_pago = fp.id_forma_pago
            LEFT JOIN cadetes c ON p.id_cadete = c.id_cadete
            
        """)
        resultados = cursor.fetchall()
        cursor.close()
        return resultados


# --- TABLA PEDIDOS DETALLE ---
    def crear_tabla_pedidos_detalle(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_pedido (
                id_detallePedido INT AUTO_INCREMENT PRIMARY KEY,
                id_pedido INT,
                id_menu INT,
                cantidad INT NOT NULL,
                descripcion TEXT,
                FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido),
                FOREIGN KEY (id_menu) REFERENCES menus(id_menu)
            );
        """)
        self.conn.commit()
        cursor.close()  
        print("Tabla 'pedidos_detalle' creada o ya existía.")

    def obtener_pedidos_detalle(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT d.id_detallePedido, p.id_pedido, m.nombre_menu, d.cantidad, d.descripcion
            FROM detalle_pedido d
            JOIN pedidos p ON d.id_pedido = p.id_pedido
            JOIN menus m ON d.id_menu = m.id_menu
        """)
        filas = cursor.fetchall()
        cursor.close()
        lista_detalle_pedidos = []
        for fila in filas:
            lista_detalle_pedidos.append({
                "id_detallePedido": fila[0],
                "id_pedido": fila[1],
                "nombre_menu": fila[2],
                "cantidad": fila[3],
                "descripcion": fila[4]
            })
        return lista_detalle_pedidos

    def insertar_detalle_pedido(self, id_pedido, id_menu, cantidad, descripcion):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO detalle_pedido (id_pedido, id_menu, cantidad, descripcion)
                VALUES (%s, %s, %s, %s)
            """, (id_pedido, id_menu, cantidad, descripcion))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
        print("Detalle de pedido insertado correctamente.")


# -----------------------------------------------
# --- FUNCIONES GENERALES ---

# Funciones para obtener listas de valores únicos de las tablas

    def obtener_lista(self, tabla, campo):
        query = f"SELECT {campo} FROM {tabla}"
        with self.conn.cursor(buffered=True) as cursor:
            cursor.execute(query)
            return [fila[0] for fila in cursor.fetchall()]
        
# Funcion para insertar valores en la tabla

    def insertar_valores(self, tabla, campo, valor):
        if not valor:
            return
        query_check = f"SELECT COUNT(*) FROM {tabla} WHERE {campo} = %s"
        query_insert = f"INSERT INTO {tabla} ({campo}) VALUES (%s)"
        with self.conn.cursor(buffered=True) as cursor:
            cursor.execute(query_check, (valor,))
            if cursor.fetchone()[0] == 0:
                cursor.execute(query_insert, (valor,))
                self.conn.commit()
                print(f"{campo.capitalize()} '{valor}' insertado en {tabla}.")

# --------------------------------------------------------------
    def obtener_id(self, tabla, campo, valor):
        id_column_map = {
            ("menus", "nombre_menu"): "id_menu",
            ("tipo_menu", "tipoMenu"): "id_tipoMenu",
            ("nombres", "nombre"): "id_nombre",
            ("pedidos", "id_pedido"): "id_pedido",
            ("direcciones", "direccion"): "id_direccion",
            ("empresas", "empresa"): "id_empresa",
            ("cadetes", "cadete"): "id_cadete",
            ("forma_pago", "forma_pago"): "id_forma_pago",
            ("usuarios", "nombre_usuario"): "id_usuario",
        }
        id_columna = id_column_map.get((tabla, campo), f"id_{campo}")
        with self.conn.cursor(buffered=True) as cursor:
            cursor.execute(f"SELECT {id_columna} FROM {tabla} WHERE {campo} = %s", (valor,))
            resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    












