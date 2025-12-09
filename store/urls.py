from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('api/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    
    # Vistas del cliente
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Productos por categoría
    path('productos/<str:tipo>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    
    # Carrito y compras
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('checkout/', views.checkout, name='checkout'),
     path('confirmacion-pedido/<int:pedido_id>/', views.confirmacion_pedido, name='confirmacion_pedido'),
    
    # Otras secciones
    path('artistas/', views.artistas, name='artistas'),
    path('artista/<int:artista_id>/', views.detalle_artista, name='detalle_artista'),
    path('encargos/', views.crear_encargo, name='crear_encargo'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    
    # Panel administrativo
    path('mod/panel/', views.panel_admin, name='panel_admin'),
    
    # CRUD genérico
    path('mod/<str:modelo>/', views.crud_lista, name='crud_lista'),
    path('mod/<str:modelo>/crear/', views.crud_crear, name='crud_crear'),
    path('mod/<str:modelo>/<int:id>/', views.crud_detalle, name='crud_detalle'),
    path('mod/<str:modelo>/<int:id>/editar/', views.crud_editar, name='crud_editar'),
    path('mod/<str:modelo>/<int:id>/eliminar/', views.crud_eliminar, name='crud_eliminar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)