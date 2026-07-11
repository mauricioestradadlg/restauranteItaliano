

from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("menu/", views.menu, name="menu"),
    path("nosotros/", views.nosotros, name="nosotros"),
    path("sucursales/", views.sucursales, name="sucursales"),
    path("contacto/", views.contacto, name="contacto"),
    path("trabajo/", views.trabajo, name="trabajo"),
]
