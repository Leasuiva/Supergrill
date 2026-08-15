from django.contrib import admin
from .models import (Direccion, Empresa, Nombre, Cadete, TipoMenu, 
                     Guarnicion, Estado, FormaPago, Registro, Menu, 
                     Pedido, DetallePedido)

# Registramos todos los modelos para poder verlos y editarlos
admin.site.register(Direccion)
admin.site.register(Empresa)
admin.site.register(Nombre)
admin.site.register(Cadete)
admin.site.register(TipoMenu)
admin.site.register(Guarnicion)
admin.site.register(Estado)
admin.site.register(FormaPago)
admin.site.register(Registro)
admin.site.register(Menu)
admin.site.register(Pedido)
admin.site.register(DetallePedido)