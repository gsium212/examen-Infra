from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_ordenes, name='lista_ordenes'),
    path('ordenes/nueva/', views.crear_orden, name='crear_orden'),
    path('ordenes/<int:oid>/editar/', views.editar_orden, name='editar_orden'),
    path('ordenes/<int:oid>/eliminar/', views.eliminar_orden, name='eliminar_orden'),
    path('ordenes/<int:oid>/detalles/', views.lista_detalles, name='lista_detalles'),
    path('ordenes/<int:oid>/detalles/nuevo/', views.crear_detalle, name='crear_detalle'),
    path('ordenes/<int:oid>/detalles/<int:did>/editar/', views.editar_detalle, name='editar_detalle'),
    path('ordenes/<int:oid>/detalles/<int:did>/eliminar/', views.eliminar_detalle, name='eliminar_detalle'),
]
