import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supergrill.settings')
django.setup()

from django.contrib.auth.models import User
from gestion.models import (
    Cadete, Direccion, Empresa, Estado, FormaPago, 
    Guarnicion, Nombre, TipoMenu, Menu, Pedido, DetallePedido, Registro
)

# Definir la ruta base absoluta donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def leer_json(nombre_archivo):
    # Posibles rutas donde puede estar la carpeta datos_viejos
    posibles_rutas = [
        os.path.join(BASE_DIR, 'datos_viejos', f'{nombre_archivo}.json'),
        os.path.join(BASE_DIR, 'datos_viejos', nombre_archivo),
        os.path.join(BASE_DIR, '..', 'datos_viejos', f'{nombre_archivo}.json'),
        os.path.join(BASE_DIR, '..', 'datos_viejos', nombre_archivo),
    ]
    
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            with open(ruta, 'r', encoding='utf-8') as f:
                return json.load(f)
                
    raise FileNotFoundError(f"No se encontró el archivo '{nombre_archivo}' ni en supergrill/datos_viejos ni en la raíz.")

def ejecutar_etl():
    print("Iniciando migración ETL de Supergrill Viandas...")

    # --- FASE 1: TABLAS INDEPENDIENTES ---
    print("1/13 - Cargando Usuarios...")
    for f in leer_json('usuarios'):
        # Evita conflictos si ya creaste el superusuario 'admin' con el id 1 por consola
        usuario, created = User.objects.update_or_create(
            id=f['id_usuario'],
            defaults={'username': f['nombre_usuario']}
        )
        if created:
            usuario.set_password(f['contrasena'])
            usuario.save()

    print("2/13 - Cargando Cadetes...")
    for f in leer_json('cadetes'):
        Cadete.objects.create(
            id=f['id_cadete'], 
            cadete=f['cadete'], 
            activo=(f['activo'] == 1)
        )

    print("3/13 - Cargando Direcciones...")
    for f in leer_json('direcciones'):
        Direccion.objects.create(
            id=f['id_direccion'], 
            direccion=f['direccion'], 
            es_frecuente=(f['es_frecuente'] == 1)
        )

    print("4/13 - Cargando Empresas...")
    for f in leer_json('empresas'):
        Empresa.objects.create(
            id=f['id_empresa'], 
            empresa=f['empresa'], 
            es_frecuente=(f['es_frecuente'] == 1)
        )

    print("5/13 - Cargando Estados...")
    for f in leer_json('estados'):
        Estado.objects.create(
            id=f['id_estado'], 
            estado=f['estado']
        )

    print("6/13 - Cargando Formas de Pago...")
    for f in leer_json('forma_pago'):
        FormaPago.objects.create(
            id=f['id_forma_pago'], 
            forma_pago=f['forma_pago'], 
            activo=(f['activo'] == 1)
        )

    print("7/13 - Cargando Guarniciones...")
    for f in leer_json('guarniciones'):
        Guarnicion.objects.create(
            id=f['id_guarnicion'], 
            guarnicion=f['guarnicion'], 
            activo=(f['activo'] == 1)
        )

    print("8/13 - Cargando Nombres...")
    for f in leer_json('nombres'):
        Nombre.objects.create(
            id=f['id_nombre'], 
            nombre=f['nombre']
        )

    print("9/13 - Cargando Registros...")
    for f in leer_json('registros'):
        Registro.objects.create(
            id=f['id_registro'], 
            registro=f['registro']
        )

    print("10/13 - Cargando Tipos de Menú...")
    for f in leer_json('tipo_menu'):
        TipoMenu.objects.create(
            id=f['id_tipoMenu'], 
            tipoMenu=f['tipoMenu'],
            activo=(f['activo'] == 1)
        )


    # --- FASE 2: TABLAS DEPENDIENTES (Catálogo) ---
    print("11/13 - Cargando Menús...")
    for f in leer_json('menus'):
        Menu.objects.create(
            id=f['id_menu'],
            nombre_menu=f['nombre_menu'],
            tipo_menu_id=f['id_tipoMenu'],
            guarnicion_id=f['id_guarnicion'], 
            activo=(f['activo'] == 1)
        )


    # --- FASE 3: TRANSACCIONALES (Historial) ---
    print("12/13 - Cargando Pedidos...")
    for f in leer_json('pedidos'):
        pedido = Pedido.objects.create(
            id=f['id_pedido'], 
            direccion_id=f['id_direccion'], 
            empresa_id=f['id_empresa'], 
            cadete_id=f['id_cadete'], 
            usuario_id=f['id_usuario'], 
            forma_pago_id=f['id_forma_pago'], 
            nombre_id=f['id_nombre'], 
            estado_id=f['id_estado'], 
            registro_id=f['id_registro'] 
        )
        # Forzamos la actualización de la fecha para saltarnos el auto_now_add=True
        Pedido.objects.filter(id=pedido.id).update(fecha=f['fecha'])

    print("13/13 - Cargando Detalles de Pedido...")
    for f in leer_json('detalle_pedido'):
        DetallePedido.objects.create(
            id=f['id_detallePedido'],
            pedido_id=f['id_pedido'],
            menu_id=f['id_menu'],
            cantidad=f['cantidad'],
            descripcion=f['descripcion']
        )

    print("¡Migración masiva completada! Tu sistema en Django está listo.")

if __name__ == '__main__':
    ejecutar_etl()