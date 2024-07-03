from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
import uuid
import re

#from p1.settings import EMAIL_HOST_USER,ENVIO_EMAIL
from . import models
from . import correo

from django.views import View
from administracion import models as admin_models
from administracion import views as admin_views

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

def mensaje_verificacion(usuario,tocken):
    mensaje=f'''
    Hola {usuario.nombres}

    Usted se ha registrado en el portal virtual de la
    Pasteleria MY LIFE YALEBIS.
    Para verificar su correo electronico el tocken es el siguiente:
    
    {tocken}

'''
    return mensaje


def get_carrito(user):
    carrito=None
    if user.is_authenticated:
        try:
            cliente=models.Cliente.objects.get(
                usuarioid=admin_models.Usuario.objects.get(userid=user)
            )
            carrito=list(models.Carrito.objects.filter(
                clienteid=cliente
            ))
        except Exception:
            pass
    return carrito

def get_total_mount(carrito):
    total=0
    try:
        for c in carrito:
            total+=c.productoid.precio*c.cantidad
    except Exception:
        return None
    return total


def get_compras(cliente):
    try:
        contexto=[]#<{"",[]}>
        compras=list(models.Compra.objects.filter(clienteid=cliente).order_by('-id'))
        for cp in compras:
            detalles=list(models.Detalles_Compra.objects.filter(compraid=cp))
            dd=[]
            for d in detalles:
                dd.append({"lista":d,"importe":d.productoid.precio * d.cantidad})
            contexto.append({"id":cp.id,"compra":cp,"detalles":dd,"total":get_total_mount(detalles)})
        return contexto
    except Exception as e:
        return print(e)


##//////////////////////////////////////////////////////////////////////////////////////////
##//////////////////////////////////////////////////////////////////////////////////////////
##//////////////////////////////////////////////////////////////////////////////////////////
##//////////////////////////////////////////////////////////////////////////////////////////
##//////////////////////////////////////////////////////////////////////////////////////////
##//////////////////////////////////////////////////////////////////////////////////////////
##//////////////////////////////////////////////////////////////////////////////////////////
##//////////////////////////////////////////////////////////////////////////////////////////

class Index(View):
    def get(self,request):
        carrito=get_carrito(request.user)
        total_mount=get_total_mount(carrito=carrito)
        cant_prod_car=None
        try:
            cant_prod_car=carrito.__len__()
        except Exception:
            pass
        return render(request,'client/home.html',{
            "carrito":carrito,"total":total_mount,"cant_prod_car":cant_prod_car
        })


class Iniciar_Sesion(View):
    def post(self,request):
        if not request.user.is_authenticated:
            username=request.POST.get("username")
            password=request.POST.get("password")
            back={"username":username,"password":password}
            user=User.objects.filter(username=username)
            if(user.exists()):
                user=user.first()
                if(user.check_password(password)):
                    user = authenticate(request,username=user.username, password=password)
                    cliente=None
                    if user is not None:
                        auth_login(request,user)
                    try:
                        us=admin_models.Usuario.objects.get(userid=user)
                        if us.cliente_bool == True:
                            cliente=models.Cliente.objects.get(usuarioid=us,verificado=False)
                            return redirect("../../../../../verificacion/")
                    except Exception:
                        pass
                    return redirect("../../../../../../")
            return render(request,'client/home.html',{
                "Alerta":"Nombre de usuario o contraseña incorrecto","back":back
            })        
        else:
            return redirect("../../../../../../")
        
class Register(View):
    def post(self,request):
        if not request.user.is_authenticated:
            nombre=str(request.POST.get("nombre")).strip().title()
            apellidos=str(request.POST.get("apellidos")).strip().title()
            username=str(request.POST.get("username")).strip().lower()
            email=str(request.POST.get("email")).strip()
            direccion=str(request.POST.get("direccion")).strip()
            password1=request.POST.get("password1")
            password2=request.POST.get("password2")
            back_register={
                "nombre":apellidos,"apellidos":apellidos,"username":username,
                "email":email,"password1":password1,"password2":password2,
                "direccion":direccion
            }
            if "" in [nombre,apellidos,username,email,password1,password2,direccion]:
                return render(request,'client/home.html',{
                    "Alerta":"Todos los campos son obligatorios",
                    "back_register":back_register
                })
            if admin_models.Usuario.objects.filter(nombres=nombre,apellidos=apellidos).exists():
                return render(request,'client/home.html',{
                    "Alerta":"Nombres y apellidos en uso",
                    "back_register":back_register
                })
            
            if not Solo_Letras_espacio(nombre):
                return render(request,'client/home.html',{
                    "Alerta":"El nombre no acepta numeros ni caracteres especiales",
                    "back_register":back_register
                })
            
            if not Solo_Letras_espacio(apellidos):
                return render(request,'client/home.html',{
                    "Alerta":"El apellido no acepta numeros ni caracteres especiales",
                    "back_register":back_register
                })
            
            if not Solo_letras_numeros(username):
                return render(request,'client/home.html',{
                    "Alerta":"El nombre de usuario no admite caracteres especiales",
                    "back_register":back_register
                })


            if User.objects.filter(email=email).exists():
                return render(request,'client/home.html',{
                    "Alerta":"Correo electronico en uso",
                    "back_register":back_register
                })

            if not formato_correo(email):
                return render(request,'client/home.html',{
                    "Alerta":"Formato de Correo electronico incorrecto",
                    "back_register":back_register
                })

            if User.objects.filter(username=username).exists():
                return render(request,'client/home.html',{
                    "Alerta":"Nombre de usuario en uso",
                    "back_register":back_register
                })
            
            vpass=validar_password(password1=password1,password2=password2)
            if vpass!="OK":
                return render(request,'client/home.html',{
                    "Alerta":vpass,
                    "back_register":back_register
                })
            nu=User(username=username,email=email)
            nu.set_password(password1)
            nu.save()
            nuu=admin_models.Usuario(userid=nu,nombres=nombre,apellidos=apellidos,cliente_bool=True)
            nuu.save()
            nc=models.Cliente(verificado=False,direccion=direccion,usuarioid=nuu)
            nc.save()
            user = authenticate(request,username=username, password=password1)
            if user is not None:
                auth_login(request,user)
                return redirect("../../../../../../verificacion/")
        else:
            return redirect("../../../../../../")

class Logout(View):
    def get(self,request):
        if request.user.is_authenticated:
            logout(request=request)
        return redirect("../../../../../")

class verificacion_correo(View):
    def get(self,request):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return render(request,"client/verificacion/verificacion.html")
            try:
                cliente=models.Cliente.objects.get(
                    usuarioid=admin_models.Usuario.objects.get(userid=request.user),
                    verificado=False
                )
                tocken=str(uuid.uuid4())
                i=tocken.find('-')
                tocken=tocken[:i]
                print(tocken)
                cliente.tocken=tocken                        
                cliente.save()
                correo.enviar_correo(s=mensaje_verificacion(cliente.usuarioid,tocken=tocken),email=cliente.usuarioid.userid.email,tema="[MY LIFE YALEBIS] CONFIRMACION DE CORREO")
                return render(request,"client/verificacion/verificacion.html")
            except Exception as e:
                return redirect("../../../../../../../")
        else:
            return redirect("../../../../../../../")

    def post(self,request):
        if request.user.is_authenticated:
            tocken=str(request.POST.get("tocken")).strip()
            try:
                cliente=models.Cliente.objects.get(
                    usuarioid=admin_models.Usuario.objects.get(userid=request.user),
                    verificado=False
                )
                if tocken==cliente.tocken:
                    cliente.verificado=True
                    cliente.tocken=None
                    cliente.save()
                    return redirect("../../../../../../")
                else:
                    return render(request,"client/verificacion/verificacion.html",{
                        "Alerta":"Tocken incorrecto"
                    })
            except Exception:
                pass
        return redirect("../../../../../")

class Catalogo(View):
    def get(self,request):
        productos=admin_views.get_productos("Mostrador")

        carrito=get_carrito(request.user)
        total_mount=get_total_mount(carrito=carrito)
        cant_prod_car=None
        try:
            cant_prod_car=carrito.__len__()
        except Exception:
            pass
        return render(request,"client/catalogo/catalogo.html",{
            "productos":productos,
            "tamanio":productos.__len__(),
            "carrito":carrito,"total":total_mount,"cant_prod_car":cant_prod_car
        })

    def post(self,request):
        busqueda=str(request.POST.get("busqueda")).strip().lower()
        pr=admin_views.get_productos("Mostrador")
        productos=[]
        for pp in pr:
            if busqueda in str(pp.nombre).lower():
                productos.append(pp)

        carrito=get_carrito(request.user)
        total_mount=get_total_mount(carrito=carrito)
        cant_prod_car=None
        try:
            cant_prod_car=carrito.__len__()
        except Exception:
            pass
        return render(request,"client/catalogo/catalogo.html",{
            "productos":productos,
            "tamanio":productos.__len__(),
            "carrito":carrito,"total":total_mount,"cant_prod_car":cant_prod_car,
            "busqueda":True
        })



class Compras(View):
    def get(self,request):
        if request.user.is_authenticated:
            carrito=get_carrito(request.user)
            total_mount=get_total_mount(carrito=carrito)
            cant_prod_car=None
            try:
                cant_prod_car=carrito.__len__()
            except Exception:
                pass
            compras=None
            try:
                cliente=models.Cliente.objects.get(usuarioid=admin_models.Usuario.objects.get(userid=request.user))
                compras=get_compras(cliente)
            except Exception:
                pass
            return render(request,"client/Cliente/compra.html",{
                "carrito":carrito,"total":total_mount,"cant_prod_car":cant_prod_car,
                "compras":compras,
            })
        return redirect("../../../../../../")




class Carrito(View):
    def get(self,request):
        if request.user.is_authenticated:
            carrito=get_carrito(request.user)
            total_mount=get_total_mount(carrito=carrito)
            cant_prod_car=None
            try:
                cant_prod_car=carrito.__len__()
            except Exception:
                pass
            return render(request,"client/Cliente/carrito.html",{
                "carrito":carrito,"total":total_mount,"cant_prod_car":cant_prod_car
            })
        else:
            return redirect("../../../../../../")

class Agregar_Carrito(View):
    def get(self,request,productoid):
        if request.user.is_authenticated:
            try:
                producto=admin_models.Producto.objects.get(id=productoid)
                us=admin_models.Usuario.objects.get(userid=request.user)
                cliente=models.Cliente.objects.get(usuarioid=us)
                if cliente.verificado==True:
                    if not models.Carrito.objects.filter(productoid=producto,clienteid=cliente).exists():
                        npc=models.Carrito(clienteid=cliente,productoid=producto,cantidad=1)
                        npc.save()
                else:
                    return redirect("../../../../../verificacion/")
            except Exception:
                pass
        
        return redirect("../../../../../../catalogo/")
class Modificar_Carrito(View):
    def post(self,request,carritoid):
        if request.user.is_authenticated:
            try:
                cantidad=int(request.POST.get('cantidad'))
                usu=admin_models.Usuario.objects.get(userid=request.user)
                cliente=models.Cliente.objects.get(usuarioid=usu)
                if cliente.verificado==False:
                    return redirect("../../../../../../verificacion/")
                carrito=models.Carrito.objects.get(id=carritoid,clienteid=cliente)
                if cantidad>0 and cantidad<=carrito.productoid.cantidad_Mostrador:
                    carrito.cantidad=cantidad
                    carrito.save()
            except Exception as e:
                print(e)
            return redirect("../../../../../carrito/")
class Eliminar_Carrito(View):
    def get(self,request,carritoid):
        if request.user.is_authenticated:
            cliente=models.Cliente.objects.get(
                usuarioid=admin_models.Usuario.objects.get(userid=request.user)
            )
            if cliente.verificado==False:
                return redirect("../../../../../../verificacion/")
            carrito=models.Carrito.objects.get(clienteid=cliente,id=carritoid)
            carrito.delete()
            return redirect("../../../../../carrito/")
        else:
            return render("../../../../../../../")

class Efectuar_Compra(View):
    def get(self,request):
        if request.user.is_authenticated:
            try:
                usuario=admin_models.Usuario.objects.get(userid=request.user)
                cliente=models.Cliente.objects.get(usuarioid=usuario)
                if cliente.verificado == False:
                    return redirect("../../../../../verificacion/")
                carrito=list(models.Carrito.objects.filter(clienteid=cliente))
                compra=None
                for cc in carrito:
                    if cc.cantidad<=cc.productoid.cantidad_Mostrador:
                        cc.productoid.cantidad_Mostrador-=cc.cantidad
                        cc.productoid.save()
                        if compra==None:
                            tocken=str(uuid.uuid1())
                            compra=models.Compra(clienteid=cliente,entregado=0,codigo=tocken)
                            compra.save()
                        detalle=models.Detalles_Compra(compraid=compra,productoid=cc.productoid,cantidad=cc.cantidad)
                        detalle.save()
                        cc.delete()
            except Exception as e:
                print(e)
            return redirect("../../../../../../compras/")
        else:
            return redirect("../../../../../../../")


class Perfil(View):
    def get(self,request):
        if request.user.is_authenticated:
            carrito=get_carrito(request.user)
            total_mount=get_total_mount(carrito=carrito)
            cant_prod_car=None
            try:
                cant_prod_car=carrito.__len__()
            except Exception:
                pass
            return render(request,"client/Cliente/perfil.html",{
                "carrito":carrito,"total":total_mount,"cant_prod_car":cant_prod_car
            })
        else:
            return redirect("../../../../../../")

    def post(self,request):
        if request.user.is_authenticated:
            username=str(request.POST.get("username")).strip().lower()
            u=User.objects.get(id=request.user.id)
            m=None
            if User.objects.filter(username=username).exists():
                m="El nombre de usuario esta en uso"
            else:
                u.username=username
                u.save()
            return redirect("../../../../perfil/")
        else:
            return redirect("../../../../../../")
        


class Cambiar_Clave(View):
    def post(self,request):
        if request.user.is_authenticated:
            password0=request.POST.get("password0")
            password1=request.POST.get("password1")
            password2=request.POST.get("password2")
            print(request.POST)
            if(request.user.check_password(password0)):
                v=validar_password(password1=password1,password2=password2)
                if v!="OK":
                    carrito=get_carrito(request.user)
                    total_mount=get_total_mount(carrito=carrito)
                    cant_prod_car=None
                    try:
                        cant_prod_car=carrito.__len__()
                    except Exception:
                        pass
                    return render(request,"client/Cliente/perfil.html",{
                        "carrito":carrito,"total":total_mount,"cant_prod_car":cant_prod_car,
                        "Alerta":v
                    })
                request.user.set_password(password1)
                request.user.save()
                user = authenticate(request,username=request.user.username, password=password1)
                if user is not None:
                    auth_login(request,user)
                carrito=get_carrito(request.user)
                total_mount=get_total_mount(carrito=carrito)
                cant_prod_car=None
                try:
                    cant_prod_car=carrito.__len__()
                except Exception:
                    pass
                return render(request,"client/Cliente/perfil.html",{
                    "carrito":carrito,"total":total_mount,"cant_prod_car":cant_prod_car,
                    "Alerta":"Contraseña actualizada correctamente"
                })
            carrito=get_carrito(request.user)
            total_mount=get_total_mount(carrito=carrito)
            cant_prod_car=None
            try:
                cant_prod_car=carrito.__len__()
            except Exception:
                pass
            return render(request,"client/Cliente/perfil.html",{
                "carrito":carrito,"total":total_mount,"cant_prod_car":cant_prod_car,
                "Alerta":"Contraseña actual incorrecta"
            })
        else:
            return redirect("../../../../../../")