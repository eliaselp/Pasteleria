from django.shortcuts import render,redirect
from django.http import HttpResponse

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
from django.core.validators import validate_image_file_extension
from django.core.exceptions import ValidationError
from django.conf import settings
from Pasteleria import settings as st_py
from django.views import View

import uuid
import re
import os
#from p1.settings import EMAIL_HOST_USER,ENVIO_EMAIL
from . import models
from cliente import models as client_model

# Create your views here.

def validar_username(username):
    users=User.objects.filter(username=username)
    if(users.exists()):
        return False
    else:
        return True
    
def validar_email(email):
    users=User.objects.filter(email=email)
    if(users.exists()):
        return False
    else:
        return True
def validar_password(password1,password2):
    if("" in [password1,password2]):
        return "Todos los campos son obligatorios"
    if(password1!=password2):
        return "Las contraseñas no coinciden"
    if not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$', password1):
        return "La contraseña debe tener al menos 8 caracteres, incluyendo números, letras mayúsculas y minúsculas, y caracteres especiales."
    return "OK"

def Solo_Letras_espacio(string):
    # Expresión regular para verificar que el string solo contiene letras y espacios
    patron = re.compile(r'^[a-zA-Z ]+$')
    return bool(patron.match(string))


def Solo_letras_numeros(string):
    # Expresión regular para verificar que el string solo contiene letras y números
    patron = re.compile(r'^[a-zA-Z0-9]+$')
    return bool(patron.match(string))

def formato_correo(correo):
    # Expresión regular para verificar el formato de un correo electrónico
    patron = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(patron.match(correo))


def validar_imagen(archivo):
    try:
        validate_image_file_extension(archivo)
    except ValidationError:
        return False
    return True


def get_empleados():
    return list(models.Usuario.objects.filter(cliente_bool=False))
def get_categorias():
    return list(models.Categoria.objects.all())
def add_categoria(str_cat):
    try:
        ncat=models.Categoria(categoria=str_cat)
        ncat.save()
        return ncat
    except Exception:
        try:
            ncat = models.Categoria.objects.get(categoria=str_cat)
            return ncat
        except Exception:
            return None
def get_productos(ubicacion):
    if ubicacion=="Almacen":
        return list(models.Producto.objects.all())
    else:
        return list(models.Producto.objects.filter(cantidad_Mostrador__gt=0))

def eliminar_imagen_producto(producto_id):
    # Obtener el objeto Producto por su ID
    producto = models.Producto.objects.get(id=producto_id)
    
    # Obtener la URL de la imagen del objeto Producto
    url_imagen = producto.urlimagen
    
    # Construir la ruta completa del archivo en el servidor
    ruta_imagen=f"{st_py.BASE_DIR}\\{url_imagen[1:]}"
    ruta_imagen=ruta_imagen.replace('/','\\')
    print(ruta_imagen)
    # Verificar si el archivo existe y eliminarlo
    if os.path.isfile(ruta_imagen):
        os.remove(ruta_imagen)
        return True
    else:
        return False



def get_historial_informes(usuario=None):
    historial=None
    contexto=[]
    try:
        if usuario!=None:
            historial=list(models.Informe_Cierre.objects.filter(usuarioid=usuario).order_by('-id'))
        else:
            historial=list(models.Informe_Cierre.objects.all().order_by('-id'))
        for h in historial:
            detalles=list(models.Detalle_Informe.objects.filter(informeid=h))
            det=[]
            for dd in detalles:
                det.append({"detalle":dd,"subtotal":dd.productoid.precio*dd.diferencia})
            contexto.append({"informe":h,"detalles":det,"total":get_total_historial(detalles)})
    except Exception as e:
        print(e)
    if contexto.__len__()==0:
        contexto=None
    return contexto


def get_total_historial(detalles):
    total=0
    try:
        for h in detalles:
            total+=h.diferencia*h.productoid.precio
    except Exception as e:
        print(e)
    return total

################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
################################################################################################
########################



class Login(View):
    def get(self,request):
        if(not request.user.is_authenticated):
            return render(request,'login/login.html')
        else:
            return redirect("../../../admin/index/")
        
    def post(self,request):
        if(not request.user.is_authenticated):
            username=request.POST.get("username")
            password=request.POST.get("password")
            user=User.objects.filter(username=username)
            if(user.exists()):
                user=user.first()
                if(user.check_password(password)):
                    user = authenticate(request,username=user.username, password=password)
                    if user is not None:
                        auth_login(request,user)
                        return redirect("../../../admin/index/")    
            return render(request,'login/login.html',{
                "Alerta":"Nombre de usuario o contraseña incorrecto","back":request.POST
            })
        else:
            return redirect("../../../admin/index/")


class Index(View):
    def get(self,request):
        if request.user.is_authenticated:
            staf=request.user.is_staff
            base=""
            if staf == True:
                base="panel/Almacenero/almacenero.html"
            else:
                u=models.Usuario.objects.filter(userid=request.user)
                u=u.first()
                if u.cliente_bool == False:
                    base="panel/Mostrador/mostrador.html"
                else:
                    return redirect("../../../../../../")
            return render(request,"panel/home.html",{
                "base":base
            })
        else:
            return redirect("../../../../admin/login/")


    def post(self,request):
        if request.user.is_authenticated:
            staf=request.user.is_staff
            base=""
            if staf == True:
                base="panel/Almacenero/almacenero.html"
            else:
                u=models.Usuario.objects.filter(userid=request.user)
                u=u.first()
                if u.cliente_bool == False:
                    base="panel/Mostrador/mostrador.html"
                else:
                    return redirect("../../../../../../")    

            opc=request.POST.get("opc")
            #### TODOS ####
            if opc=="cambiar_contraseña":
                password0=request.POST.get("password0")
                password1=request.POST.get("password1")
                password2=request.POST.get("password2")
                back={
                    "password0":password0,
                    "password1":password1,
                    "password2":password2,
                }
                if "" in [password0,password1,password2]:
                    return render(request,"panel/home.html",{
                        "base":base,"back":back,
                        "Alerta":"Todos los campos son obligatorios"
                    })
                if(not request.user.check_password(password0)):
                    return render(request,"panel/home.html",{
                        "base":base,"back":back,
                        "Alerta":"Contraseña incorrecta"
                    })
                valid=validar_password(password1=password1,password2=password2)
                if valid!="OK":
                    return render(request,"panel/home.html",{
                        "base":base,"back":back,
                        "Alerta":valid
                    })
                request.user.set_password(password1)
                request.user.save()
                user2 = authenticate(request,username=request.user.username, password=password1)
                auth_login(request,user2)
                return render(request,"panel/home.html",{
                    "base":base,
                    "Alerta":"Contraseña actualizada correctamente"
                })
            elif opc=="cerrar_sesion":
                logout(request)
                return redirect("../../../admin/login/")
        #### ADMIN ####
            #### CRUD EMPLEADO #####
            elif opc=="get_empleados":
                return render(request,"panel/Almacenero/empleados.html",{
                    "empleados":get_empleados()
                })
            elif opc=="registrar_empleado":
                nombre=str(request.POST.get("nombre")).strip().title()
                apellidos=str(request.POST.get("apellidos")).strip().title()
                username=str(request.POST.get("username")).strip()
                email=str(request.POST.get("email")).strip()
                password1=request.POST.get("password1")
                password2=request.POST.get("password2")
                back={
                    "nombre":nombre,"apellido":apellidos,"username":username,"email":email,
                    "password1":password1,"password2":password2
                }

                if "" in [nombre,apellidos,username,email,password1,password2]:
                    return render(request,"panel/Almacenero/empleados.html",{
                        "Alerta":"Todos los campos son obligatorios",
                        "back":back,
                        "empleados":get_empleados()
                    })
                
                if not Solo_Letras_espacio(nombre):
                    return render(request,"panel/Almacenero/empleados.html",{
                        "Alerta":"El nombre no admite caracteres especiales ni numeros",
                        "back":back,
                        "empleados":get_empleados()
                    })

                if not Solo_Letras_espacio(apellidos):
                    return render(request,"panel/Almacenero/empleados.html",{
                        "Alerta":"El apellido no admite caracteres especiales ni numeros",
                        "back":back,
                        "empleados":get_empleados()
                    })

                if not Solo_letras_numeros(username):
                    return render(request,"panel/Almacenero/empleados.html",{
                        "Alerta":"El nombre de usuario no admite caracteres especiales",
                        "back":request.POST,
                        "empleados":get_empleados()
                    })

                if not validar_username(username):
                    return render(request,"panel/Almacenero/empleados.html",{
                        "Alerta":"El nombre de usuario esta en uso",
                        "back":back,
                        "empleados":get_empleados()
                    })
                
                
                if not validar_email(email):
                    return render(request,"panel/Almacenero/empleados.html",{
                        "Alerta":"El correo electrónico esta en uso",
                        "back":back,
                        "empleados":get_empleados()
                    })
                
                if not formato_correo(email):
                    return render(request,"panel/Almacenero/empleados.html",{
                        "Alerta":"Fromato de correo electrónico incorrecto",
                        "back":back,
                        "empleados":get_empleados()
                    })

                r=validar_password(password1,password2)
                if r!="OK":
                    return render(request,"panel/Almacenero/empleados.html",{
                        "Alerta":r,
                        "back":back,
                        "empleados":get_empleados()
                    })
                vu=models.Usuario.objects.filter(nombres=nombre,apellidos=apellidos)
                if vu.exists():
                    return render(request,"panel/Almacenero/empleados.html",{
                        "Alerta":"Usuario con nombres y apellidos en uso",
                        "back":back,
                        "empleados":get_empleados()
                    })
                try:
                    new_user=User(email=email,username=username)
                    new_user.set_password(password1)
                    new_user.save()
                    nu=models.Usuario(userid=new_user,cliente_bool=False,nombres=nombre,apellidos=apellidos)
                    nu.save()
                    return render(request,"panel/Almacenero/empleados.html",{
                        "Alerta":"Empleado registrado con éxito",
                        "empleados":get_empleados()
                    })
                except Exception as e:
                    return render(request,"panel/Almacenero/empleados.html",{
                        "Alerta":f"ERROR: {e}",
                        "empleados":get_empleados()
                    })
            elif opc=="eliminar_empleado":
                empleadoid=request.POST.get("id")
                if request.user.is_staff:
                    try:
                        de=models.Usuario.objects.get(id=empleadoid,cliente_bool=False)
                        de.userid.delete()
                        de.delete()
                        return render(request,"panel/Almacenero/empleados.html",{
                            "Alerta":"Empleado eliminado con exito",
                            "empleados":get_empleados()
                        })  
                    except Exception as e:
                        return render(request,"panel/Almacenero/empleados.html",{
                            "Alerta":f"ERROR: {e}",
                            "empleados":get_empleados()
                        })  
                return redirect("../../../../../../../../")
            elif opc=="get_modificar_empleado":
                empleadoid=request.POST.get("id")
                try:
                    me=models.Usuario.objects.get(id=empleadoid,cliente_bool=False)
                    return render(request,"panel/Almacenero/modificar/modificar_empleado.html",{
                        "empleado":me
                    })
                except Exception as e:
                    return render(request,"panel/Almacenero/empleados.html",{
                        "Alerta":f"ERROR: {e}",
                        "empleados":get_empleados()
                    })  
            elif opc=="modificar_empleado":
                id=request.POST.get("id")
                if request.user.is_staff:
                    try:
                        me=models.Usuario.objects.get(cliente_bool=False,id=id)
                        nombre=str(request.POST.get("nombre")).strip().title()
                        apellidos=str(request.POST.get("apellidos")).strip().title()
                        username=str(request.POST.get("username")).strip()
                        if "" in [nombre,apellidos,username]:
                            return render(request,"panel/Almacenero/modificar/modificar_empleado.html",{
                                "empleado":me,
                                "Alerta":"Todos los campos son obligatorios"
                            })
                        if nombre!=me.nombres or apellidos!=me.apellidos:
                            vn=models.Usuario.objects.filter(nombres=nombre,apellidos=apellidos)
                            if not vn.exists():
                                if not Solo_Letras_espacio(nombre):
                                    return render(request,"panel/Almacenero/modificar/modificar_empleado.html",{
                                        "empleado":me,
                                        "Alerta":"El nombre no admite caracteres especiales ni números"
                                    })
                                if not Solo_Letras_espacio(apellidos):
                                    return render(request,"panel/Almacenero/modificar/modificar_empleado.html",{
                                        "empleado":me,
                                        "Alerta":"El apellido no admite caracteres especiales ni números"
                                    })
                                me.nombres=nombre
                                me.apellidos=apellidos
                                me.save()
                            else:
                                return render(request,"panel/Almacenero/modificar/modificar_empleado.html",{
                                    "empleado":me,
                                    "Alerta":"Nombres y Apellidos en uso"
                                })  
                        
                        if username!=me.userid.username:
                            if models.User.objects.filter(username=username).exists():
                                if Solo_letras_numeros(username):
                                    return render(request,"panel/Almacenero/modificar/modificar_empleado.html",{
                                        "empleado":me,
                                        "Alerta":"El nombre de usuario no admite caracteres especiales."
                                    })
                                return render(request,"panel/Almacenero/modificar/modificar_empleado.html",{
                                    "empleado":me,
                                    "Alerta":"Nombre de usuario en uso"
                                })
                            else:
                                me.userid.username=username
                                me.userid.save()
                                me.save()
                        return render(request,"panel/Almacenero/modificar/modificar_empleado.html",{
                            "empleado":me,
                            "Alerta":"Datos de usuario actualizados correctamente"
                        })
                    except Exception as e:
                        return render(request,"panel/Almacenero/empleados.html",{
                            "Alerta":f"ERROR: {e}",
                            "empleados":get_empleados()
                        })  
                return redirect("../../../../../../../../../../")
            #### CRUD PRODUCTO ####
            elif opc=="get_aniadir_producto_almacen":
                return render(request,"panel/Almacenero/annadir.html",{
                    "mostrador":False,
                    "categorias":get_categorias()
                })
            elif opc=="nuevo_producto":
                nombre=str(request.POST.get("nombre")).strip().capitalize()
                cantidad=str(request.POST.get("cantidad")).strip()
                peso=str(request.POST.get("peso")).strip()
                precio=str(request.POST.get("precio")).strip()
                categoria=str(request.POST.get("categoria")).strip().capitalize()
                otra=str(request.POST.get("otra_categoria")).strip().capitalize()
                imagen_producto = request.FILES.get('imagen_producto')
                back={
                    "nombre":nombre,"cantidad":cantidad,"peso":peso,
                    "precio":precio,"categoria":categoria,"otra":otra
                }
                if "" in [nombre,cantidad,peso,precio,categoria] or not imagen_producto:
                    return render(request,"panel/Almacenero/annadir.html",{
                        "mostrador":False,
                        "categorias":get_categorias(),
                        "Alerta":"Todos los campos son obligatorios",
                        "back":back
                    })  
                cat=None
                
                if categoria=="Otra":
                    if otra=="":
                        return render(request,"panel/Almacenero/annadir.html",{
                            "mostrador":False,
                            "categorias":get_categorias(),
                            "Alerta":"Todos los campos son obligatorios",
                            "back":back
                        })
                    if not Solo_Letras_espacio(otra):
                        return render(request,"panel/Almacenero/annadir.html",{
                            "mostrador":False,
                            "categorias":get_categorias(),
                            "Alerta":"La categoria no admite caracteres especiales ni números.",
                            "back":back
                        })
                    cat=add_categoria(otra)
                else:
                    cat=add_categoria(categoria)
                if cat==None:
                    return render(request,"panel/Almacenero/annadir.html",{
                        "mostrador":False,
                        "categorias":get_categorias(),
                        "Alerta":"Error al obtener los datos",
                        "back":back
                    })
                if not validar_imagen(imagen_producto):
                    return render(request,"panel/Almacenero/annadir.html",{
                        "mostrador":False,
                        "categorias":get_categorias(),
                        "Alerta":"Imagen no permitida",
                        "back":back
                    })

                if not Solo_Letras_espacio(nombre):
                    return render(request,"panel/Almacenero/annadir.html",{
                        "mostrador":False,
                        "categorias":get_categorias(),
                        "Alerta":"El nombre del producto no admite caracteres especiales",
                        "back":back
                    })
                if int(cantidad)<=0:
                    return render(request,"panel/Almacenero/annadir.html",{
                        "mostrador":False,
                        "categorias":get_categorias(),
                        "Alerta":"La cantidad tiene que ser mayor que cero",
                        "back":back
                    })

                if float(peso)<=0:
                    return render(request,"panel/Almacenero/annadir.html",{
                        "mostrador":False,
                        "categorias":get_categorias(),
                        "Alerta":"El peso tiene que ser mayor que cero",
                        "back":back
                    })
                if not float(precio)>0:
                    return render(request,"panel/Almacenero/annadir.html",{
                        "mostrador":False,
                        "categorias":get_categorias(),
                        "Alerta":"El precio tiene que ser mayor que cero",
                        "back":back
                    })
                
                fs = FileSystemStorage()
                filename = fs.save(imagen_producto.name, imagen_producto)
                uploaded_file_url = fs.url(filename)
                np=models.Producto(
                    nombre=nombre,categoriaid=cat,cantidad_Almacen=cantidad,
                    cantidad_Mostrador=0,
                    peso=peso,precio=precio,
                    urlimagen=uploaded_file_url
                )
                np.save()
                return render(request,"panel/Almacenero/mostrar.html",{
                    "mostrador":False,
                    "Alerta":"Producto Registrado correctamente",
                    "productos":get_productos("Almacen")
                })
            elif opc=="get_modificar_producto":
                id=request.POST.get("id")
                try:
                    pmod=models.Producto.objects.get(id=id)
                    return render(request,"panel/Almacenero/modificar/modificar_producto.html",{
                        "vv":pmod,
                        "categorias":get_categorias()
                    })
                except Exception:
                    contexto={
                        "mostrador":False,
                        "productos":get_productos("Almacen")
                    }
                    return render(request,"panel/Almacenero/mostrar.html",contexto)
            elif opc=="modificar_producto":
                productoid=request.POST.get("productoid")
                try:
                    producto=models.Producto.objects.get(id=productoid)
                    nombre=str(request.POST.get("nombre")).strip().capitalize()
                    cantidad=str(request.POST.get("cantidad")).strip()
                    peso=str(request.POST.get("peso")).strip()
                    precio=str(request.POST.get("precio")).strip()
                    categoria=str(request.POST.get("categoria")).strip().capitalize()
                    otra=str(request.POST.get("otra_categoria")).strip().capitalize()
                    imagen_producto = request.FILES.get('imagen_producto')
                    
                    if "" in [nombre,cantidad,peso,precio,categoria]:
                        return render(request,"panel/Almacenero/modificar/modificar_producto.html",{
                            "mostrador":False,
                            "categorias":get_categorias(),
                            "Alerta":"Todos los campos son obligatorios",
                            "vv":producto
                        })  
                    
                    cat=None
                    if categoria=="Otra":
                        if otra=="":
                            return render(request,"panel/Almacenero/modificar/modificar_producto.html",{
                                "mostrador":False,
                                "categorias":get_categorias(),
                                "Alerta":"Todos los campos son obligatorios",
                                "vv":producto
                            })
                        if not Solo_Letras_espacio(otra):
                            return render(request,"panel/Almacenero/modificar/modificar_producto.html",{
                                "mostrador":False,
                                "categorias":get_categorias(),
                                "Alerta":"La categoria no admite caracteres especiales ni números.",
                                "back":back
                            })
                        cat=add_categoria(otra)
                    else:
                        cat=add_categoria(categoria)

                    if cat==None:
                        return render(request,"panel/Almacenero/modificar/modificar_producto.html",{
                            "mostrador":False,
                            "categorias":get_categorias(),
                            "Alerta":"Error al obtener los datos",
                            "vv":producto
                        })
                    
                    if imagen_producto:
                        if not validar_imagen(imagen_producto):
                            return render(request,"panel/Almacenero/modificar/modificar_producto.html",{
                                "mostrador":False,
                                "categorias":get_categorias(),
                                "Alerta":"Imagen no permitida",
                                "vv":producto
                            })
                        eliminar_imagen_producto(productoid)


                        fs = FileSystemStorage()
                        filename = fs.save(imagen_producto.name, imagen_producto)
                        uploaded_file_url = fs.url(filename)
                        producto.urlimagen=uploaded_file_url
                    
                    if int(cantidad)<=0:
                        return render(request,"panel/Almacenero/modificar/modificar_producto.html",{
                            "mostrador":False,
                            "categorias":get_categorias(),
                            "Alerta":"La cantidad tiene que ser mayor que cero",
                            "back":back
                        })

                    if float(peso)<=0:
                        return render(request,"panel/Almacenero/modificar/modificar_producto.html",{
                            "mostrador":False,
                            "categorias":get_categorias(),
                            "Alerta":"El peso tiene que ser mayor que cero",
                            "back":back
                        })
                    if not float(precio)>0:
                        return render(request,"panel/Almacenero/modificar/modificar_producto.html",{
                            "mostrador":False,
                            "categorias":get_categorias(),
                            "Alerta":"El precio tiene que ser mayor que cero",
                            "back":back
                        })
                    
                    producto.nombre=nombre
                    producto.categoriaid=cat
                    producto.cantidad_Almacen=cantidad
                    producto.peso=peso
                    producto.precio=precio
                    producto.save()
                    return render(request,"panel/Almacenero/mostrar.html",{
                        "mostrador":False,
                        "Alerta":"Producto actualizado correctamente",
                        "productos":get_productos("Almacen")
                    })
                except Exception as e:
                    contexto={
                        "mostrador":False,
                        "productos":get_productos("Almacen"),
                        "Alerta":f"ERROR: {e}"
                    }
                    return render(request,"panel/Almacenero/mostrar.html",contexto)    
            elif opc=="eliminar_producto":
                id=request.POST.get("id")
                try:
                    pdel=models.Producto.objects.get(id=id)
                    eliminar_imagen_producto(producto_id=pdel.id)
                    pdel.delete()
                    contexto={
                        "mostrador":False,
                        "productos":get_productos("Almacen")
                    }
                    return render(request,"panel/Almacenero/mostrar.html",contexto)

                except Exception as e:
                    contexto={
                        "mostrador":False,
                        "productos":get_productos("Almacen"),
                        "Alerta":f"ERROR: {e}"
                    }
                    return render(request,"panel/Almacenero/mostrar.html",contexto)
            elif opc=="get_inventario_almacen":
                contexto={
                    "mostrador":False,
                    "productos":get_productos("Almacen")
                }
                return render(request,"panel/Almacenero/mostrar.html",contexto)
            elif opc=="get_inventario_mostrador":
                if staf==True:
                    contexto={
                        "mostrador":True,
                        "productos":get_productos("Mostrador")
                    }
                    return render(request,"panel/Almacenero/mostrar.html",contexto)
                else:
                    return render(request,"panel/Mostrador/inventario.html",{
                        "productos":get_productos("Mostrador")
                    })
            elif opc=="entrega_mostrador":
                productoid=request.POST.get("productoid")
                cantidad=int(request.POST.get("cantidad"))
                try:
                    producto=models.Producto.objects.get(id=productoid)
                    if cantidad>int(producto.cantidad_Almacen) or cantidad<0:
                        return render(request,"panel/Almacenero/mostrar.html",{
                            "mostrador":False,
                            "productos":get_productos("Almacen"),
                            "Alerta":"ERROR: CANTIDAD INVALIDA"
                        })    
                    producto.cantidad_Almacen-=cantidad
                    producto.cantidad_Mostrador+=cantidad
                    producto.save()
                    return render(request,"panel/Almacenero/mostrar.html",{
                        "mostrador":False,
                        "productos":get_productos("Almacen"),
                        "Alerta":"Producto entregado al mostrador"
                    })    
                except Exception as e:
                    return render(request,"panel/Almacenero/mostrar.html",{
                        "mostrador":False,
                        "productos":get_productos("Almacen"),
                        "Alerta":f"ERROR: {e}"
                    })
        else:
            return redirect("../../../../admin/login/")





##### ADMIN ####
class Informe(View):
    def get(self,request):
        if request.user.is_authenticated and request.user.is_staff:
            historial=get_historial_informes()
            return render(request,"panel/Almacenero/info.html",{
                "informes":historial
            })
        return redirect("../../../../../../../../../admin/")

    def post(self,request,accion):
        if request.user.is_authenticated and request.user.is_staff:
            informeid=request.POST.get("id")
            try:
                informe=models.Informe_Cierre.objects.get(id=informeid)
                informe.save()
                if accion==0:
                    informe.estado=-1
                    informe.save()
                    detalles=list(models.Detalle_Informe.objects.filter(informeid=informe))
                    for dt in detalles:
                        dt.productoid.cantidad_Mostrador=dt.resto+dt.diferencia
                        dt.productoid.save()
                elif accion==1:
                    perdida=None
                    try:
                        perdida=float(request.POST.get("perdida"))
                    except Exception:
                        perdida=None
                    informe.estado=1
                    informe.perdida=perdida
                    informe.save()
                    detalles=list(models.Detalle_Informe.objects.filter(informeid=informe))
                    for dt in detalles:
                        dt.productoid.cantidad_Almacen+=dt.resto
                        dt.productoid.save()
                return redirect("../../../../../../admin/informes/")
            except Exception as e:
                print(e)
        return redirect("../../../../../../../../../admin/")















#### MOSTRADOS #####

class Ticket_Online(View):
    def post(self,request):
        if request.user.is_authenticated:
            try:
                usuario=models.Usuario.objects.get(userid=request.user,cliente_bool=False)
                tocken=request.POST.get("tocken")
                compra=client_model.Compra.objects.get(codigo=tocken,entregado=0)
                detalles=list(client_model.Detalles_Compra.objects.filter(compraid=compra))
                dd=[]
                total=0
                for d in detalles:
                    dd.append({"detalle":d,"subtotal":d.cantidad*d.productoid.precio})
                    total+=d.cantidad*d.productoid.precio
                return render(request,"panel/Mostrador/ticket.html",{
                    "compra":compra,"detalles":dd,"total":total
                })
            except Exception as e:
                print(e)
        return redirect("../../../../../../../../../admin/")


class Hacer_Entrega(View):
    def get(self,request,codigo):
        if request.user.is_authenticated:
            try:
                usuario=models.Usuario.objects.get(userid=request.user,cliente_bool=False)
                compra=client_model.Compra.objects.get(codigo=codigo,entregado=0)
                compra.entregado=1
                compra.save()
            except Exception as e:
                print(e)
        return redirect("../../../../../../../admin/")


class Historial(View):
    def get(self,request):
        if request.user.is_authenticated:
            try:
                usuario=models.Usuario.objects.get(userid=request.user,cliente_bool=False)
                historial=get_historial_informes(usuario)
                return render(request,"panel/Mostrador/historial.html",{
                    "informes":historial
                })
            except Exception as e:
                print(e)
        return redirect("../../../../../../../admin/")

class Create_Informe(View):
    def get(self,request):
        if request.user.is_authenticated:
            try:
                usuario=models.Usuario.objects.get(userid=request.user,cliente_bool=False)
                return render(request,"panel/Mostrador/nuevo_informe.html",{
                    "productos":get_productos("Mostrador")
                })
            except Exception as e:
                print(e)
        return redirect("../../../../../../../admin/")
    

    def post(self,request):
        if request.user.is_authenticated:
            try:
                usuario=models.Usuario.objects.get(userid=request.user,cliente_bool=False)
                productos_Mostrador=get_productos("Mostrador")
                excedente=[]
                for pp in productos_Mostrador:
                    ex=request.POST.get(str(pp.id))
                    if ex=="":
                        print("Todos los campos son obligatorios")
                        return render(request,"panel/Mostrador/nuevo_informe.html",{
                            "productos":get_productos("Mostrador"),"Alerta":"Todos los campos son obligatorios",
                            "back":request.POST
                        })
                    ex=int(ex)
                    if ex < 0 or ex > pp.cantidad_Mostrador:
                        print("Error: Cantidad excedente invalida.")
                        return render(request,"panel/Mostrador/nuevo_informe.html",{
                            "productos":get_productos("Mostrador"),"Alerta":"Error: Cantidad excedente invalida.",
                            "back":request.POST
                        })
                    excedente.append({"productoid":pp.id,"excedente":ex})
                
                nuevo_informe=models.Informe_Cierre(estado=0,usuarioid=usuario)
                nuevo_informe.save()
                for x in excedente:
                    pr=models.Producto.objects.get(id=x.get('productoid'))
                    detalle=models.Detalle_Informe(informeid=nuevo_informe,productoid=pr,resto=x.get("excedente"),diferencia=pr.cantidad_Mostrador-x.get('excedente'))
                    detalle.save()
                    detalle.productoid.cantidad_Mostrador=0
                    detalle.productoid.save()
                '''
                pedidos=list(client_model.Compra.objects.filter(entregado=0))
                for p in pedidos:
                    p.entregado=-1
                    p.save()
                '''
                return redirect("../../../../../../../../../admin/historial/")
            except Exception as e:
                print(e)
        return redirect("../../../../../../../admin/")


