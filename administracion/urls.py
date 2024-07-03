
from django.urls import path
from . import views


urlpatterns = [
    path('index/',views.Index.as_view()),
    path('',views.Login.as_view()),
    path('login/',views.Login.as_view()),
    path('informes/',views.Informe.as_view()),
    path('informe/<int:accion>',views.Informe.as_view()),

    path('ticket_online/',views.Ticket_Online.as_view()),
    path('hacer_entrega/<str:codigo>/',views.Hacer_Entrega.as_view()),
    path('historial/',views.Historial.as_view()),
    path('nuevo_informe/',views.Create_Informe.as_view()),
]
