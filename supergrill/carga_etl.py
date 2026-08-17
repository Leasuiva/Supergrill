import os
import django
import json

# 1. Despertar el motor de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supergrill.settings')
django.setup()

# 2. Importar tus modelos exactos
from gestion.models import (
    Direccion, Empresa, Nombre, Cadete, TipoMenu, Guarnicion, 
    Estado, FormaPago, Registro, Menu, Pedido, DetallePedido
)

def cargar_datos():
    print("🚀 Iniciando carga ETL hacia Django...")
    print("-" * 40)

    # --- NIVEL 1: Tablas independientes (Catálogos) ---
    
    print("📥 Cargando Direcciones...")
    for d in json.load(open('direcciones.json', encoding='utf-8')):
        Direccion.objects.update_or_create(
            id=d['id_direccion'], 
            defaults={'direccion': d['direccion'], 'es_frecuente': bool(d.get('es_frecuente', 0))}
        )

    print("📥 Cargando Empresas...")
    for e in json.load(open('empresas.json', encoding='utf-8')):
        Empresa.objects.update_or_create(
            id=e['id_empresa'], 
            defaults={'empresa': e['empresa'], 'es_frecuente': bool(e.get('es_frecuente', 0))}
        )

    print("📥 Cargando Nombres...")
    for n in json.load(open('nombres.json', encoding='utf-8')):
        Nombre.objects.update_or_create(
            id=n['id_nombre'], 
            defaults={'nombre': n['nombre']}
        )

    print("📥 Cargando Cadetes...")
    for c in json.load(open('cadetes.json', encoding='utf-8')):
        Cadete.objects.update_or_create(
            id=c['id_cadete'], 
            defaults={'cadete': c['cadete'], 'activo': bool(c.get('activo', 1))}
        )

    print("📥 Cargando TipoMenu...")
    for tm in json.load(open('tipo_menu.json', encoding='utf-8')):
        TipoMenu.objects.update_or_create(
            id=tm['id_tipoMenu'], 
            defaults={'tipoMenu': tm['tipoMenu'], 'activo': bool(tm.get('activo', 1))}
        )

    print("📥 Cargando Guarniciones...")
    for g in json.load(open('guarniciones.json', encoding='utf-8')):
        Guarnicion.objects.update_or_create(
            id=g['id_guarnicion'], 
            defaults={'guarnicion': g['guarnicion'], 'activo': bool(g.get('activo', 1))}
        )

    print("📥 Cargando Estados...")
    for est in json.load(open('estados.json', encoding='utf-8')):
        Estado.objects.update_or_create(
            id=est['id_estado'], 
            defaults={'estado': est['estado']}
        )

    print("📥 Cargando Formas de Pago...")
    for fp in json.load(open('forma_pago.json', encoding='utf-8')):
        FormaPago.objects.update_or_create(
            id=fp['id_forma_pago'], 
            defaults={'forma_pago': fp['forma_pago'], 'activo': bool(fp.get('activo', 1))}
        )

    print("📥 Cargando Registros...")
    for r in json.load(open('registros.json', encoding='utf-8')):
        Registro.objects.update_or_create(
            id=r['id_registro'], 
            defaults={'registro': r['registro']}
        )

    # --- NIVEL 2: Menús (Dependen de TipoMenu y Guarnicion) ---
    print("📥 Cargando Menús...")
    for m in json.load(open('menus.json', encoding='utf-8')):
        Menu.objects.update_or_create(
            id=m['id_menu'],
            defaults={
                'nombre_menu': m['nombre_menu'],
                'tipo_menu_id': m['id_tipoMenu'],
                'guarnicion_id': m['id_guarnicion'], # Django maneja los None automáticamente
                'activo': bool(m.get('activo', 1))
            }
        )

    # --- NIVEL 3: Pedidos (El núcleo central) ---
    print("📥 Cargando Pedidos (Esto puede demorar unos segundos)...")
    for p in json.load(open('pedidos.json', encoding='utf-8')):
        pedido, creado = Pedido.objects.update_or_create(
            id=p['id_pedido'],
            defaults={
                'direccion_id': p['id_direccion'],
                'empresa_id': p['id_empresa'],
                'cadete_id': p['id_cadete'],
                'usuario_id': 1, # Se lo asignamos al superusuario de Django directamente
                'forma_pago_id': p['id_forma_pago'],
                'nombre_id': p['id_nombre'],
                'estado_id': p['id_estado'],
                'registro_id': p['id_registro']
            }
        )
        # Truco para sobreescribir la fecha (saltándonos el auto_now_add=True)
        if p.get('fecha'):
            Pedido.objects.filter(id=pedido.id).update(fecha=p['fecha'])

    # --- NIVEL 4: Detalles de los Pedidos ---
    print("📥 Cargando Detalles de Pedidos...")
    for dp in json.load(open('detalle_pedido.json', encoding='utf-8')):
        DetallePedido.objects.update_or_create(
            id=dp['id_detallePedido'],
            defaults={
                'pedido_id': dp['id_pedido'],
                'menu_id': dp['id_menu'],
                'cantidad': dp['cantidad'],
                'descripcion': dp['descripcion']
            }
        )

    print("-" * 40)
    print("🎉 ¡MIGRACIÓN FINALIZADA CON ÉXITO! Tu base de datos SQLite ahora tiene todo el historial.")

if __name__ == '__main__':
    cargar_datos()