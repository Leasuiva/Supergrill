from django.db import models
from django.contrib.auth.models import User # El sistema de usuarios oficial de Django
from django.utils import timezone

class Direccion(models.Model):
    direccion = models.CharField(max_length=150)
    es_frecuente = models.BooleanField(default=False)

    def __str__(self):
        return self.direccion

class Empresa(models.Model):
    empresa = models.CharField(max_length=150)
    es_frecuente = models.BooleanField(default=False)

    def __str__(self):
        return self.empresa

class Nombre(models.Model):
    nombre = models.CharField(max_length=30)

    def __str__(self):
        return self.nombre

class Cadete(models.Model):
    cadete = models.CharField(max_length=30)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.cadete

class TipoMenu(models.Model):
    tipoMenu = models.CharField(max_length=30)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.tipoMenu

class Guarnicion(models.Model):
    guarnicion = models.CharField(max_length=30)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.guarnicion

class Estado(models.Model):
    estado = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.estado

class FormaPago(models.Model):
    forma_pago = models.CharField(max_length=30)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.forma_pago

class Registro(models.Model):
    registro = models.CharField(max_length=30)

    def __str__(self):
        return self.registro

class Menu(models.Model):
    nombre_menu = models.CharField(max_length=100)
    # Así se hacen las Foreign Keys en Django. ¡Simple y seguro!
    tipo_menu = models.ForeignKey(TipoMenu, on_delete=models.CASCADE)
    guarnicion = models.ForeignKey(Guarnicion, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre_menu} ({self.tipo_menu.tipoMenu})"

class Pedido(models.Model):
    direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True)
    cadete = models.ForeignKey(Cadete, on_delete=models.SET_NULL, null=True, blank=True)
    # Usamos el usuario que ya trae Django por defecto
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    forma_pago = models.ForeignKey(FormaPago, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateField(auto_now_add=True) # Se pone la fecha de hoy automáticamente
    nombre = models.ForeignKey(Nombre, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True, blank=True)
    registro = models.ForeignKey(Registro, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        destino = self.empresa if self.empresa else self.direccion
        return f"Pedido {self.id} - {destino}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.cantidad}x {self.menu.nombre_menu}"

# Esta parte es para la rendicion de dinero de los cadetes
# Se encuentra en gestor de pedidos > opciones > cadetes.
class RegistroDiarioCadete(models.Model):
    cadete = models.ForeignKey(Cadete, on_delete=models.CASCADE, related_name='registros_diarios')
    fecha = models.DateField(default=timezone.now)
    dinero_sobrante = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    viajes = models.IntegerField(default=0)
    
    # NUEVO: Campo para la descripción del día
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Registro Diario de Cadete"
        verbose_name_plural = "Registros Diarios de Cadetes"
        unique_together = ('cadete', 'fecha')

    def __str__(self):
        return f"{self.cadete.cadete} - {self.fecha} (Viajes: {self.viajes})"
# ----------------------------------------------------------------------------