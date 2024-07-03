from django.db import models
from administracion import models as admin_models
# Create your models here.

class Cliente(models.Model):
    verificado=models.BooleanField(null=False,blank=False)
    tocken=models.TextField(null=True,blank=True)
    direccion=models.TextField(null=False,blank=False)
    usuarioid=models.OneToOneField(admin_models.Usuario,on_delete=models.CASCADE,null=False,blank=False)



class Carrito(models.Model):
    clienteid=models.ForeignKey(Cliente,on_delete=models.CASCADE,null=False,blank=False)
    productoid=models.ForeignKey(admin_models.Producto,on_delete=models.CASCADE,null=False,blank=False)
    cantidad=models.IntegerField(null=False,blank=False)



class Compra(models.Model):
    clienteid=models.ForeignKey(Cliente,on_delete=models.CASCADE,null=False,blank=False)
    entregado=models.IntegerField(null=False,blank=False)
    fecha=models.DateField(null=False,auto_now=True)
    codigo=models.TextField(null=False,blank=False,unique=True)



class Detalles_Compra(models.Model):
    compraid=models.ForeignKey(Compra,on_delete=models.CASCADE,null=False,blank=False)
    productoid=models.ForeignKey(admin_models.Producto,on_delete=models.CASCADE,null=False,blank=False)
    cantidad=models.IntegerField(null=False,blank=False)
