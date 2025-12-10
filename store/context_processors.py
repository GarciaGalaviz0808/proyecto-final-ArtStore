from .models import Carrito

def carrito_context(request):
    if request.user.is_authenticated:
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            cantidad_items = carrito.cantidad_items
            total_carrito = carrito.total
        except Carrito.DoesNotExist:
            cantidad_items = 0
            total_carrito = 0
    else:
        cantidad_items = 0
        total_carrito = 0
    
    return {
        'cantidad_carrito': cantidad_items,
        'total_carrito': total_carrito,
    }