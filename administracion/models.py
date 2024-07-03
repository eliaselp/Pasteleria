from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Usuario(models.Model):
    userid=models.OneToOneField(User,on_delete=models.CASCADE)
    cliente_bool=models.BooleanField(null=False,blank=False)
    nombres=models.CharField(max_length=30,null=False,blank=False)
    apellidos=models.CharField(max_length=30,null=False,blank=False)
    class Meta:
        unique_together = ('nombres', 'apellidos',)



class Categoria(models.Model):
    categoria=models.CharField(max_length=30,null=False,blank=False,unique=True)



class Producto(models.Model):
    nombre=models.CharField(max_length=30,null=False,blank=False)
    categoriaid=models.ForeignKey(Categoria,on_delete=models.CASCADE,null=False)
    cantidad_Almacen=models.IntegerField(null=False,blank=False)
    cantidad_Mostrador=models.IntegerField(null=False,blank=False)
    peso=models.FloatField(null=False,blank=False)
    precio=models.FloatField(null=False,blank=False)
    #imagen=models.ImageField()
    urlimagen=models.CharField(max_length=500)




class Informe_Cierre(models.Model):
    fecha=models.DateField(null=False,auto_now=True)
    usuarioid=models.ForeignKey(Usuario,on_delete=models.SET_NULL,null=True,blank=True)
    estado=models.IntegerField(null=False,blank=False)
    perdida=models.FloatField(null=True,blank=True)




class Detalle_Informe(models.Model):
    informeid=models.ForeignKey(Informe_Cierre,on_delete=models.CASCADE,null=False,blank=False)
    productoid=models.ForeignKey(Producto,on_delete=models.SET_NULL,null=True)
    resto=models.IntegerField(null=False,blank=False)
    diferencia=models.IntegerField(null=False,blank=False)









