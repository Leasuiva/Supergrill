import json
import sys
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User

from gestion.models import (
    Cadete, Menu, Pedido, DetallePedido,
    Direccion, Empresa, Nombre,
    TipoMenu, Guarnicion, FormaPago,
    Estado, Registro
)

class Command(BaseCommand):
    help = '🔥 Migración NIVEL DIOS Flask → Django (ETL Interactivo Completo)'

    def handle(self, *args, **kwargs):
        self.datos_crudos = None
        self.stats = {
            "usuarios": 0,  # <-- Agregamos usuarios a las estadísticas
            "cadetes": 0,
            "base": 0,
            "menus": 0,
            "pedidos": 0,
            "detalles": 0
        }
        self.cache = {}

        self.stdout.write(self.style.SUCCESS("🚀 SISTEMA ETL INICIADO - MIGRACIÓN NIVEL DIOS"))

        while True:
            print("\n" + "=" * 55)
            print(" 🚀 CONSOLA DE MIGRACIÓN SUPERGRILL (DJANGO) ")
            print("=" * 55)
            print("1. Ejecutar Extracción (Leer JSON) 📄")
            print("2. Ver tablas extraídas (Explorar) 🔍")
            print("3. Ver registros de una tabla 📋")
            print("4. Cargar datos a la Base de Datos (L) 💾")
            print("5. Ver Reporte de Carga 📊")
            print("6. Salir 👋")
            print("=" * 55)

            opcion = input("Elige una opción (1-6): ").strip()

            if opcion == '1':
                self.extraer_datos()
            elif opcion == '2':
                self.ver_tablas()
            elif opcion == '3':
                self.ver_registros()
            elif opcion == '4':
                self.menu_carga()
            elif opcion == '5':
                self.reporte()
            elif opcion == '6':
                self.stdout.write(self.style.SUCCESS("👋 Saliendo de la consola de migración..."))
                sys.exit()
            else:
                self.stdout.write(self.style.ERROR("❌ Opción no válida. Intenta de nuevo."))

    # =========================
    # FASE E: EXTRACCIÓN
    # =========================
    def extraer_datos(self):
        try:
            with open('backup_flask.json', 'r', encoding='utf-8') as f:
                self.datos_crudos = json.load(f)
            self.stdout.write(self.style.SUCCESS("✅ Extracción exitosa. El JSON está en memoria."))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("❌ Archivo 'backup_flask.json' no encontrado."))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("❌ Error al leer el JSON. Archivo corrupto."))

    def ver_tablas(self):
        if not self.datos_crudos:
            self.stdout.write(self.style.WARNING("⚠️ Primero debes ejecutar la Extracción (Opción 1)."))
            return
        
        print("\n📂 TABLAS EXTRAÍDAS DEL JSON:")
        for tabla, registros in self.datos_crudos.items():
            cantidad = len(registros) if isinstance(registros, list) else 'N/A'
            print(f"  • {tabla}: {cantidad} registros")

    def ver_registros(self):
        if not self.datos_crudos:
            self.stdout.write(self.style.WARNING("⚠️ Primero debes ejecutar la Extracción (Opción 1)."))
            return
        
        nombre_tabla = input("\nEscribe el nombre de la tabla que quieres ver: ").strip()
        if nombre_tabla in self.datos_crudos and isinstance(self.datos_crudos[nombre_tabla], list):
            print(json.dumps(self.datos_crudos[nombre_tabla][:5], indent=4, ensure_ascii=False))
            print(f"\n... (Mostrando los primeros 5 de {len(self.datos_crudos[nombre_tabla])})")
        else:
            self.stdout.write(self.style.ERROR("❌ Tabla no encontrada o no es una lista de registros."))

    # =========================
    # FASE L: MENÚ DE CARGA
    # =========================
    def menu_carga(self):
        if not self.datos_crudos:
            self.stdout.write(self.style.WARNING("⚠️ ¡Alto ahí! Primero debes cargar el JSON en memoria (Opción 1)."))
            return

        print("\n" + "-" * 40)
        print(" 💾 MENÚ DE CARGA (DJANGO ORM)")
        print("-" * 40)
        print("1. Cargar Usuarios 👤")  # <-- NUEVA OPCIÓN
        print("2. Cargar Cadetes 🛵")
        print("3. Cargar Tablas Base (Direcciones, Empresas, etc.) 🏗️")
        print("4. Cargar Menús 🍔")
        print("5. Cargar Pedidos 📝")
        print("6. Cargar Detalles de Pedidos 🔍")
        print("7. Volver al menú principal 🔙")
        
        # OJO: Aquí debes escribir el NÚMERO, no el nombre de la tabla
        sub_opcion = input("Escribe el NÚMERO del módulo a migrar (1-7): ").strip()

        try:
            if sub_opcion == '1':
                with transaction.atomic():
                    self.cargar_usuarios(self.datos_crudos)
            elif sub_opcion == '2':
                with transaction.atomic():
                    self.cargar_cadetes(self.datos_crudos)
            elif sub_opcion == '3':
                with transaction.atomic():
                    self.cargar_base(self.datos_crudos)
            elif sub_opcion == '4':
                with transaction.atomic():
                    self.cargar_menus(self.datos_crudos)
            elif sub_opcion == '5':
                with transaction.atomic():
                    self.cargar_pedidos(self.datos_crudos)
            elif sub_opcion == '6':
                with transaction.atomic():
                    self.cargar_detalles(self.datos_crudos)
            elif sub_opcion == '7':
                return
            else:
                self.stdout.write(self.style.ERROR("❌ Opción inválida. Debes ingresar un número del 1 al 7."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error crítico durante la carga: {e}"))

    # =========================
    # CACHE
    # =========================
    def build_cache(self):
        self.cache["pedidos"] = {p.id: p for p in Pedido.objects.all()}
        self.cache["menus"] = {m.id: m for m in Menu.objects.all()}

    # =========================
    # FUNCIONES DE CARGA A BD
    # =========================
    def cargar_usuarios(self, data):
        self.stdout.write("Procesando Usuarios...")
        for u in data.get("usuarios", []):
            # Como el modelo de Usuario de Django es estricto, le inventamos un username seguro
            # basándonos en el ID si no viene la clave "username"
            username_seguro = u.get("username", f"usuario_{u.get('id_usuario', 'x')}")
            
            user, created = User.objects.get_or_create(
                id=u.get("id_usuario"),
                defaults={
                    "username": username_seguro,
                    "is_staff": True,      # Le damos acceso al admin por defecto
                    "is_superuser": True   # Puedes cambiar esto a False si no quieres que sean superusuarios
                }
            )
            if created:
                # Si el usuario es nuevo, le seteamos una contraseña por defecto (o la que venga en el JSON)
                password = u.get("password", "supergrill123")
                user.set_password(password)
                user.save()
                self.stats["usuarios"] += 1
                
        self.stdout.write(self.style.SUCCESS("✔ Usuarios cargados exitosamente."))

    def cargar_cadetes(self, data):
        self.stdout.write("Procesando Cadetes...")
        for c in data.get("cadetes", []):
            _, created = Cadete.objects.update_or_create(
                id=c["id_cadete"],
                defaults={"cadete": c["cadete"], "activo": bool(c["activo"])}
            )
            if created:
                self.stats["cadetes"] += 1
        self.stdout.write(self.style.SUCCESS("✔ Cadetes cargados exitosamente."))

    def cargar_base(self, data):
        self.stdout.write("Procesando Tablas Base...")
        for d in data.get("direcciones", []):
            Direccion.objects.update_or_create(id=d["id_direccion"], defaults={"direccion": d["direccion"], "es_frecuente": d.get("es_frecuente", False)})
        for e in data.get("empresas", []):
            Empresa.objects.update_or_create(id=e["id_empresa"], defaults={"empresa": e["empresa"], "es_frecuente": e.get("es_frecuente", False)})
        for n in data.get("nombres", []):
            Nombre.objects.update_or_create(id=n["id_nombre"], defaults={"nombre": n["nombre"]})
        for tm in data.get("tipo_menu", []):
            TipoMenu.objects.update_or_create(id=tm["id_tipoMenu"], defaults={"tipoMenu": tm["tipoMenu"], "activo": True})
        for g in data.get("guarniciones", []):
            Guarnicion.objects.update_or_create(id=g["id_guarnicion"], defaults={"guarnicion": g["guarnicion"], "activo": True})
        for fp in data.get("forma_pago", []):
            FormaPago.objects.update_or_create(id=fp["id_forma_pago"], defaults={"forma_pago": fp["forma_pago"], "activo": bool(fp.get("activo", 1))})
        for est in data.get("estados", []):
            Estado.objects.update_or_create(id=est["id_estado"], defaults={"estado": est["estado"]})
        for r in data.get("registros", []):
            Registro.objects.update_or_create(id=r["id_registro"], defaults={"registro": r["registro"]})
            
        self.stats["base"] += 1
        self.stdout.write(self.style.SUCCESS("✔ Tablas Base completadas."))

    def cargar_menus(self, data):
        self.stdout.write("Procesando Menús...")
        for m in data.get("menus", []):
            tipo_menu, _ = TipoMenu.objects.get_or_create(id=m.get("id_tipoMenu", 1), defaults={"tipoMenu": "AUTO"})
            guarnicion = Guarnicion.objects.filter(id=m.get("id_guarnicion")).first()
            _, created = Menu.objects.update_or_create(
                id=m["id_menu"],
                defaults={"nombre_menu": m.get("nombre_menu", "AUTO"), "tipo_menu": tipo_menu, "guarnicion": guarnicion, "activo": True}
            )
            if created:
                self.stats["menus"] += 1
        self.stdout.write(self.style.SUCCESS("✔ Menus cargados exitosamente."))

    def cargar_pedidos(self, data):
        self.stdout.write("Procesando Pedidos...")
        
        for p in data.get("pedidos", []):
            # Ahora busca al usuario exacto que hizo el pedido si existe el campo id_usuario
            usuario = User.objects.filter(id=p.get("id_usuario")).first() 
            if not usuario:
                usuario = User.objects.first() # Respaldo por si el id_usuario no viene
                
            _, created = Pedido.objects.update_or_create(
                id=p["id_pedido"],
                defaults={
                    "direccion": Direccion.objects.filter(id=p.get("id_direccion")).first(),
                    "empresa": Empresa.objects.filter(id=p.get("id_empresa")).first(),
                    "cadete": Cadete.objects.filter(id=p.get("id_cadete")).first(),
                    "usuario": usuario,
                    "forma_pago": FormaPago.objects.filter(id=p.get("id_formaPago")).first(),
                    "estado": Estado.objects.filter(id=p.get("id_estado")).first(),
                    "registro": Registro.objects.filter(id=p.get("id_registro")).first(),
                    "nombre": Nombre.objects.filter(id=p.get("id_nombre")).first()
                }
            )
            if created:
                self.stats["pedidos"] += 1
        self.build_cache()
        self.stdout.write(self.style.SUCCESS("✔ Pedidos cargados exitosamente."))

    def cargar_detalles(self, data):
        self.stdout.write("Procesando Detalles de Pedidos...")
        if not self.cache:
            self.build_cache()
        for d in data.get("detalle_pedido", []):
            pedido = self.cache["pedidos"].get(d["id_pedido"])
            if not pedido:
                pedido = Pedido.objects.create(id=d["id_pedido"])
                self.cache["pedidos"][pedido.id] = pedido

            menu = self.cache["menus"].get(d["id_menu"])
            if not menu:
                menu = Menu.objects.create(id=d["id_menu"], nombre_menu="AUTO", tipo_menu=TipoMenu.objects.first())
                self.cache["menus"][menu.id] = menu

            _, created = DetallePedido.objects.update_or_create(
                id=d["id_detallePedido"],
                defaults={"pedido": pedido, "menu": menu, "cantidad": d["cantidad"], "descripcion": d["descripcion"]}
            )
            if created:
                self.stats["detalles"] += 1
        self.stdout.write(self.style.SUCCESS("✔ Detalles de Pedidos cargados exitosamente."))

    # =========================
    # REPORTE FINAL
    # =========================
    def reporte(self):
        self.stdout.write(self.style.WARNING("\n📊 REPORTE DE CARGA (Nuevos Registros)"))
        for k, v in self.stats.items():
            self.stdout.write(f"  • {k.upper()}: {v}")