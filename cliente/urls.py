
from django.urls import path
from . import views

urlpatterns = [
    path('',views.Index.as_view()),
    path('login/',views.Iniciar_Sesion.as_view()),
    path('verificacion/',views.verificacion_correo.as_view()),
    path('logout/',views.Logout.as_view()),
    path('registro/',views.Register.as_view()),
    path('catalogo/',views.Catalogo.as_view()),
    path('compras/',views.Compras.as_view()),
    
    path('carrito/',views.Carrito.as_view()),
    path('agregar_carrito/<int:productoid>/',views.Agregar_Carrito.as_view()),
    path('set_carrito/<int:carritoid>/',views.Modificar_Carrito.as_view()),
    path('quitar_carrito/<int:carritoid>/',views.Eliminar_Carrito.as_view()),
    path('efectuar_compra/',views.Efectuar_Compra.as_view()),

    path('perfil/',views.Perfil.as_view()),
    path('cambiar_clave/',views.Cambiar_Clave.as_view()),
]
