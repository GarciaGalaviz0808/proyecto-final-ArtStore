# views.py - VERSION COMPLETA CON USUARIOS
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from decimal import Decimal
import json
from django import forms
from django.utils.timezone import now
from datetime import timedelta

from .models import *
from .forms import *
from functools import wraps

# ========== FUNCIONES AUXILIARES ==========

def es_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

def solo_cliente(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
            messages.warning(request, 'Los administradores no pueden realizar compras.')
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# ========== VISTAS DEL CLIENTE ==========

def index(request):
    productos_destacados = Producto.objects.filter(destacado=True, activo=True)[:6]
    categorias = Categoria.objects.all()
    artistas_destacados = Artista.objects.filter(activo=True).order_by('?')[:2]
    
    context = {
        'productos_destacados': productos_destacados,
        'categorias': categorias,
        'seccion': 'inicio',
        'artistas_destacados': artistas_destacados,
    }
    return render(request, 'cliente/index.html', context)

def productos_por_categoria(request, tipo):
    tipo_map = {
        'oleos': 'oleo',
        'acrilicos': 'acrilico',
        'lienzos': 'lienzo',
        'pinceles': 'pincel',
        'obras': 'original',
        'replicas': 'replica',
        'suministros': 'suministro',
    }
    
    tipo_producto = tipo_map.get(tipo, tipo)
    productos = Producto.objects.filter(tipo=tipo_producto, activo=True)
    
    context = {
        'productos': productos,
        'tipo': tipo,
        'seccion': 'suministros' if tipo in ['oleos', 'acrilicos', 'lienzos', 'pinceles', 'suministros'] else tipo,
    }
    return render(request, 'cliente/productos/listar_producto.html', context)

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    form = AgregarAlCarritoForm()
    
    # Calcular precios con IVA
    precio_sin_iva = producto.precio
    iva = precio_sin_iva * Decimal('0.16')
    precio_con_iva = precio_sin_iva + iva
    
    context = {
        'producto': producto,
        'form': form,
        'precio_sin_iva': precio_sin_iva,
        'iva': iva,
        'precio_con_iva': precio_con_iva,
    }
    return render(request, 'cliente/productos/detalle_producto.html', context)

@login_required
def agregar_al_carrito(request, producto_id):
    if request.user.is_staff or request.user.is_superuser:
        messages.warning(request, 'Los administradores no pueden realizar compras.')
        return redirect('index')
        
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id, activo=True)
        form = AgregarAlCarritoForm(request.POST)
        
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']
            
            # Obtener o crear carrito del usuario
            carrito, created = Carrito.objects.get_or_create(usuario=request.user)
            
            # Verificar si el producto ya está en el carrito
            item, item_created = ItemCarrito.objects.get_or_create(
                carrito=carrito,
                producto=producto,
                defaults={'cantidad': cantidad}
            )
            
            if not item_created:
                item.cantidad += cantidad
                item.save()
            
            messages.success(request, f'¡{producto.nombre} agregado al carrito!')
        else:
            messages.error(request, 'Cantidad inválida.')
    
    return redirect('detalle_producto', producto_id=producto_id)

@login_required
def ver_carrito(request):
    if request.user.is_staff or request.user.is_superuser:
        messages.warning(request, 'Los administradores no pueden realizar compras.')
        return redirect('index')
        
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'actualizar':
            for item in carrito.items.all():
                nueva_cantidad = request.POST.get(f'cantidad_{item.id}')
                if nueva_cantidad and nueva_cantidad.isdigit():
                    nueva_cantidad = int(nueva_cantidad)
                    if nueva_cantidad <= item.producto.stock and nueva_cantidad > 0:
                        item.cantidad = nueva_cantidad
                        item.save()
            messages.success(request, 'Carrito actualizado.')
            
        elif action == 'eliminar':
            item_id = request.POST.get('item_id')
            if item_id:
                item = get_object_or_404(ItemCarrito, id=item_id, carrito=carrito)
                item.delete()
                messages.success(request, 'Producto eliminado del carrito.')
        
        return HttpResponseRedirect(request.path_info)
    
    # Calcular totales con IVA
    subtotal = carrito.total
    iva = subtotal * Decimal('0.16')
    total = subtotal + iva
    
    context = {
        'carrito': carrito,
        'subtotal': subtotal,
        'iva': iva,
        'total': total,
    }
    return render(request, 'cliente/compra/carrito.html', context)

@login_required
def checkout(request):
    if request.user.is_staff or request.user.is_superuser:
        messages.warning(request, 'Los administradores no pueden realizar compras.')
        return redirect('index')
        
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    
    if carrito.cantidad_items == 0:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('ver_carrito')
    
    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago')
        direccion = request.POST.get('direccion')
        notas = request.POST.get('notas', '')
        
        if not metodo_pago or not direccion:
            messages.error(request, 'Por favor completa todos los campos requeridos.')
            return redirect('checkout')
        
        # Calcular totales
        subtotal = carrito.total
        iva = subtotal * Decimal('0.16')
        total = subtotal + iva
        
        # Crear pedido
        pedido = Pedido.objects.create(
            usuario=request.user,
            metodo_pago=metodo_pago,
            subtotal=subtotal,
            iva=iva,
            total=total,
            direccion_envio=direccion,
            notas=notas,
        )
        
        # Crear items del pedido
        for item in carrito.items.all():
            ItemPedido.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio,
                subtotal=item.subtotal,
            )
            # Reducir stock
            item.producto.stock -= item.cantidad
            item.producto.save()
        
        # Vaciar carrito
        carrito.items.all().delete()
        
        messages.success(request, f'¡Pedido #{pedido.numero_pedido} realizado con éxito!')
        return redirect('confirmacion_pedido', pedido_id=pedido.id)
    
    # Calcular totales para el checkout
    subtotal = carrito.total
    iva = subtotal * Decimal('0.16')
    total = subtotal + iva
    
    context = {
        'carrito': carrito,
        'subtotal': subtotal,
        'iva': iva,
        'total': total,
        'metodos_pago': Pedido.METODO_PAGO_CHOICES,
    }
    return render(request, 'cliente/compra/checkout.html', context)

def artistas(request):
    artistas_list = Artista.objects.filter(activo=True)
    context = {
        'artistas': artistas_list,
        'seccion': 'artistas',
    }
    return render(request, 'cliente/productos/artistas.html', context)

@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    context = {
        'pedido': pedido,
        'seccion': 'mis_pedidos',
    }
    return render(request, 'cliente/compra/detalle_pedido.html', context)

@login_required
def crear_encargo(request):
    if request.user.is_staff or request.user.is_superuser:
        messages.warning(request, 'Los administradores no pueden realizar compras.')
        return redirect('index')
        
    if request.method == 'POST':
        form = EncargoForm(request.POST)
        if form.is_valid():
            encargo = form.save(commit=False)
            encargo.cliente = request.user
            encargo.save()
            messages.success(request, '¡Tu encargo ha sido enviado! Te contactaremos pronto.')
            return redirect('index')
    else:
        form = EncargoForm()
    
    artistas_list = Artista.objects.filter(activo=True)
    context = {
        'form': form,
        'artistas': artistas_list,
        'seccion': 'encargos',
    }
    return render(request, 'cliente/productos/encargos.html', context)

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.first_name}! Tu cuenta ha sido creada.')
            return redirect('index')
    else:
        form = RegistroForm()
    
    context = {'form': form}
    return render(request, 'cliente/registration/register.html', context)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo {user.first_name}!')
                
                # Redirigir según tipo de usuario
                if user.is_staff or user.is_superuser:
                    return redirect('panel_admin')
                return redirect('index')
    else:
        form = LoginForm()
    
    context = {'form': form}
    return render(request, 'cliente/registration/login.html', context)

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return render(request, 'cliente/registration/logout.html')

# ========== VISTAS DEL ADMINISTRADOR ==========

@login_required
@user_passes_test(es_admin)
def panel_admin(request):
    estadisticas = {
        'total_productos': Producto.objects.count(),
        'total_pedidos': Pedido.objects.count(),
        'total_usuarios': User.objects.count(),
        'total_encargos': EncargoPersonalizado.objects.count(),
        'pedidos_pendientes': Pedido.objects.filter(estado='pendiente').count(),
    }
    
    pedidos_recientes = Pedido.objects.all().order_by('-fecha_pedido')[:5]
    productos_bajo_stock = Producto.objects.filter(stock__lt=5)[:5]
    
    # Agregar contextos adicionales para los templates
    context = {
        'estadisticas': estadisticas,
        'pedidos_recientes': pedidos_recientes,
        'productos_bajo_stock': productos_bajo_stock,
        'pedidos_pendientes': estadisticas['pedidos_pendientes'],
        'encargos_pendientes': EncargoPersonalizado.objects.filter(estado='pendiente').count(),
    }
    return render(request, 'admin/panel/panel.html', context)

# CRUD Genérico Reutilizable
# CRUD Genérico Reutilizable
@login_required
@user_passes_test(es_admin)
def crud_lista(request, modelo):
    # Diccionario de modelos permitidos
    modelos_permitidos = {
        'productos': Producto,
        'artistas': Artista,
        'categorias': Categoria,
        'pedidos': Pedido,
        'encargos': EncargoPersonalizado,
        'usuarios': User,
    }
    
    if modelo not in modelos_permitidos:
        messages.error(request, 'Modelo no válido')
        return redirect('panel_admin')
    
    Model = modelos_permitidos[modelo]
    
    # Obtener todos los objetos del modelo
    objetos = Model.objects.all().order_by('-id')
    
    # Filtros especiales por modelo
    if modelo == 'productos':
        # Filtro por stock bajo si se solicita
        if request.GET.get('stock') == 'bajo':
            objetos = objetos.filter(stock__lt=5)
        
        # Estadísticas
        stats = {
            'activos': Producto.objects.filter(activo=True).count(),
            'destacados': Producto.objects.filter(destacado=True, activo=True).count(),
        }
    elif modelo == 'pedidos':
        # Filtro por estado
        estado = request.GET.get('estado')
        if estado:
            objetos = objetos.filter(estado=estado)
        
        # Estadísticas
        stats = {
            'pendientes': Pedido.objects.filter(estado='pendiente').count(),
        }
        
        # Calcular total de ventas
        total_ventas = Pedido.objects.filter(estado='entregado').aggregate(
            total=Sum('total')
        )['total'] or 0
    elif modelo == 'usuarios':
        # Filtrar por tipo de usuario si se solicita
        user_type = request.GET.get('type')
        if user_type == 'staff':
            objetos = objetos.filter(is_staff=True)
        elif user_type == 'superuser':
            objetos = objetos.filter(is_superuser=True)
        elif user_type == 'clientes':
            objetos = objetos.filter(is_staff=False, is_superuser=False)
        
        stats = {
            'total': User.objects.count(),
            'staff': User.objects.filter(is_staff=True).count(),
            'superusers': User.objects.filter(is_superuser=True).count(),
            'clientes': User.objects.filter(is_staff=False, is_superuser=False).count(),
        }
        total_ventas = 0
    else:
        stats = {}
        total_ventas = 0
    
    # Paginación
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    
    paginator = Paginator(objetos, page_size)
    try:
        objetos_paginados = paginator.page(page)
    except PageNotAnInteger:
        objetos_paginados = paginator.page(1)
    except EmptyPage:
        objetos_paginados = paginator.page(paginator.num_pages)
    
    estado_choices = None
    if modelo == 'pedidos':
        estado_choices = Pedido.ESTADO_CHOICES
    
    context = {
        'modelo': modelo,
        'objetos': objetos_paginados,
        'titulo': modelo.capitalize(),
        'total_ventas': total_ventas if modelo == 'pedidos' else None,
        'stats': stats,
        'estado_choices': estado_choices,
        'titulo_formateado': Model._meta.verbose_name_plural.title() if hasattr(Model._meta, 'verbose_name_plural') else modelo.capitalize(),
    }
    
    return render(request, 'admin/crud/lista.html', context)

@login_required
@user_passes_test(es_admin)
def crud_detalle(request, modelo, id):
    modelos = {
        'productos': Producto,
        'artistas': Artista,
        'categorias': Categoria,
        'pedidos': Pedido,
        'encargos': EncargoPersonalizado,
        'usuarios': User,
    }
    
    if modelo not in modelos:
        messages.error(request, 'Modelo no válido')
        return redirect('panel_admin')
    
    Model = modelos[modelo]
    objeto = get_object_or_404(Model, id=id)
    
    context = {
        'modelo': modelo,
        'objeto': objeto,
        'titulo': f'Detalle de {modelo[:-1]}',
        'historial_models': ['pedidos', 'encargos'],
    }
    
    # Datos adicionales para usuarios
    if modelo == 'usuarios':
        from django.utils.timezone import now
        from datetime import timedelta
        
        pedidos_count = Pedido.objects.filter(usuario=objeto).count()
        encargos_count = EncargoPersonalizado.objects.filter(cliente=objeto).count()
        
        # Calcular días registrado
        dias_registro = (now().date() - objeto.date_joined.date()).days
        
        # Calcular total gastado
        total_gastado = Pedido.objects.filter(
            usuario=objeto, 
            estado='entregado'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        context.update({
            'pedidos_count': pedidos_count,
            'encargos_count': encargos_count,
            'dias_registro': dias_registro,
            'total_gastado': total_gastado,
        })
    
    return render(request, 'admin/crud/detalle.html', context)

@login_required
@user_passes_test(es_admin)
def crud_crear(request, modelo):
    # Diccionario de formularios por modelo
    forms_dict = {
        'productos': ProductoForm,
        'artistas': ArtistaForm,
        'categorias': CategoriaForm,
        'encargos': EncargoForm,
        'pedidos': None,  # Los pedidos no se crean manualmente
        'usuarios': None,  # Los usuarios no se crean aquí (se usa registro normal)
    }
    
    if modelo not in forms_dict or forms_dict[modelo] is None:
        messages.error(request, 'No se puede crear este tipo de registro manualmente')
        return redirect('crud_lista', modelo=modelo)
    
    FormClass = forms_dict[modelo]
    
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'{modelo[:-1].capitalize()} creado exitosamente.')
                return redirect('crud_lista', modelo=modelo)
            except Exception as e:
                messages.error(request, f'Error al crear: {str(e)}')
    else:
        form = FormClass()
    
    # Configuración de campos por paso
    field_config = {
        'productos': {
            'basic': ['nombre', 'tipo', 'categoria', 'imagen'],
            'detail': ['descripcion', 'precio', 'stock', 'artista'],
            'config': ['destacado', 'activo']
        },
        'artistas': {
            'basic': ['nombre', 'especialidad', 'foto'],
            'detail': ['biografia'],
            'config': ['activo']
        },
        'categorias': {
            'basic': ['nombre', 'slug'],
            'detail': [],
            'config': []
        },
        'encargos': {
            'basic': ['tipo_obra', 'artista_preferido'],
            'detail': ['descripcion', 'dimensiones', 'presupuesto_maximo', 'fecha_entrega_estimada'],
            'config': []
        }
    }
    
    config_campos = field_config.get(modelo, {})
    
    context = {
        'modelo': modelo,
        'form': form,
        'titulo': f'Crear {modelo[:-1]}',
        'basic_fields': config_campos.get('basic', []),
        'detail_fields': config_campos.get('detail', []),
        'config_fields': config_campos.get('config', []),
    }
    return render(request, 'admin/crud/crear.html', context)

@login_required
@user_passes_test(es_admin)
def crud_editar(request, modelo, id):
    # Diccionario de modelos
    modelos_dict = {
        'productos': Producto,
        'artistas': Artista,
        'categorias': Categoria,
        'encargos': EncargoPersonalizado,
        'pedidos': Pedido,
        'usuarios': User,
    }
    
    # Diccionario de formularios
    forms_dict = {
        'productos': ProductoForm,
        'artistas': ArtistaForm,
        'categorias': CategoriaForm,
        'encargos': EncargoForm,
        'pedidos': None,
        'usuarios': None,
    }
    
    if modelo not in modelos_dict or modelo not in forms_dict:
        messages.error(request, 'Modelo no válido')
        return redirect('panel_admin')
    
    Model = modelos_dict[modelo]
    objeto = get_object_or_404(Model, id=id)
    
    # Para usuarios, usar un formulario especial
    if modelo == 'usuarios':
        class UserEditForm(forms.ModelForm):
            class Meta:
                model = User
                fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']
                widgets = {
                    'username': forms.TextInput(attrs={'class': 'form-control'}),
                    'email': forms.EmailInput(attrs={'class': 'form-control'}),
                    'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                    'last_name': forms.TextInput(attrs={'class': 'form-control'}),
                }
        
        FormClass = UserEditForm
    elif modelo == 'pedidos':
        class PedidoForm(forms.ModelForm):
            class Meta:
                model = Pedido
                fields = ['estado', 'metodo_pago', 'direccion_envio', 'notas']
                widgets = {
                    'direccion_envio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
                    'notas': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
                }
        
        FormClass = PedidoForm
    else:
        FormClass = forms_dict[modelo]
    
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=objeto)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'{modelo[:-1].capitalize()} actualizado exitosamente.')
                return redirect('crud_lista', modelo=modelo)
            except Exception as e:
                messages.error(request, f'Error al actualizar: {str(e)}')
    else:
        form = FormClass(instance=objeto)
    
    context = {
        'modelo': modelo,
        'form': form,
        'objeto': objeto,
        'titulo': f'Editar {modelo[:-1]}',
        'archive_models': ['productos', 'artistas', 'encargos', 'usuarios'],
    }
    
    # Añadir choices para pedidos si es necesario
    if modelo == 'pedidos':
        # NO necesitas importar Pedido aquí, ya está importado al principio del archivo
        context['status_choices'] = Pedido.ESTADO_CHOICES
    
    return render(request, 'admin/crud/editar.html', context)

@login_required
@user_passes_test(es_admin)
def crud_eliminar(request, modelo, id):
    modelos = {
        'productos': Producto,
        'artistas': Artista,
        'categorias': Categoria,
        'encargos': EncargoPersonalizado,
        'pedidos': Pedido,
        'usuarios': User,
    }
    
    if modelo not in modelos:
        messages.error(request, 'Modelo no válido')
        return redirect('panel_admin')
    
    Model = modelos[modelo]
    objeto = get_object_or_404(Model, id=id)
    
    # Prevenir que un administrador se elimine a sí mismo
    if modelo == 'usuarios' and objeto.id == request.user.id:
        messages.error(request, 'No puedes eliminar tu propio usuario.')
        return redirect('crud_detalle', modelo=modelo, id=id)
    
    # Prevenir eliminar el último superusuario
    if modelo == 'usuarios' and objeto.is_superuser:
        superusers_count = User.objects.filter(is_superuser=True).count()
        if superusers_count <= 1:
            messages.error(request, 'No se puede eliminar el último superusuario del sistema.')
            return redirect('crud_detalle', modelo=modelo, id=id)
    
    if request.method == 'POST':
        try:
            # Para usuarios, también eliminar el perfil de artista si existe
            if modelo == 'usuarios' and hasattr(objeto, 'artista'):
                objeto.artista.delete()
            
            # Para usuarios, también eliminar el carrito si existe
            if modelo == 'usuarios' and hasattr(objeto, 'carrito'):
                objeto.carrito.delete()
            
            objeto.delete()
            messages.success(request, f'{modelo[:-1].capitalize()} eliminado exitosamente.')
            return redirect('crud_lista', modelo=modelo)
        except Exception as e:
            messages.error(request, f'Error al eliminar: {str(e)}')
            return redirect('crud_detalle', modelo=modelo, id=id)
    
    # Obtener dependencias para mostrar advertencia
    dependencies = []
    
    if modelo == 'usuarios':
        pedidos_count = Pedido.objects.filter(usuario=objeto).count()
        if pedidos_count > 0:
            dependencies.append(f'{pedidos_count} pedido(s) asociado(s)')
        
        encargos_count = EncargoPersonalizado.objects.filter(cliente=objeto).count()
        if encargos_count > 0:
            dependencies.append(f'{encargos_count} encargo(s) asociado(s)')
        
        # Verificar si es artista
        if hasattr(objeto, 'artista'):
            dependencies.append(f'1 perfil de artista asociado')
            
        # Verificar si tiene carrito
        if hasattr(objeto, 'carrito'):
            dependencies.append(f'1 carrito de compras asociado')
    
    elif modelo == 'artistas':
        productos_count = Producto.objects.filter(artista=objeto).count()
        if productos_count > 0:
            dependencies.append(f'{productos_count} producto(s) asociado(s)')
        
        encargos_count = EncargoPersonalizado.objects.filter(artista_preferido=objeto).count()
        if encargos_count > 0:
            dependencies.append(f'{encargos_count} encargo(s) como artista preferido')
    
    elif modelo == 'categorias':
        productos_count = Producto.objects.filter(categoria=objeto).count()
        if productos_count > 0:
            dependencies.append(f'{productos_count} producto(s) asociado(s)')
    
    elif modelo == 'pedidos':
        items_count = objeto.items.count()
        if items_count > 0:
            dependencies.append(f'{items_count} item(s) de pedido asociado(s)')
    
    elif modelo == 'encargos':
        # No hay dependencias directas para encargos
        pass
    
    elif modelo == 'productos':
        carritos_count = ItemCarrito.objects.filter(producto=objeto).count()
        if carritos_count > 0:
            dependencies.append(f'{carritos_count} carrito(s) con este producto')
        
        pedidos_count = ItemPedido.objects.filter(producto=objeto).count()
        if pedidos_count > 0:
            dependencies.append(f'{pedidos_count} pedido(s) con este producto')
    
    context = {
        'modelo': modelo,
        'objeto': objeto,
        'titulo': f'Eliminar {modelo[:-1]}',
        'dependencies': dependencies,
        'archive_models': ['productos', 'artistas', 'encargos', 'usuarios'],
    }
    
    # Añadir estadísticas para usuarios
    if modelo == 'usuarios':
        pedidos_count = Pedido.objects.filter(usuario=objeto).count()
        encargos_count = EncargoPersonalizado.objects.filter(cliente=objeto).count()
        dias_registro = (now().date() - objeto.date_joined.date()).days
        total_gastado = Pedido.objects.filter(
            usuario=objeto, 
            estado='entregado'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        context.update({
            'pedidos_count': pedidos_count,
            'encargos_count': encargos_count,
            'dias_registro': dias_registro,
            'total_gastado': total_gastado,
        })
    
    return render(request, 'admin/crud/eliminar.html', context)

# ========== VISTAS ADICIONALES ==========

@login_required
def confirmacion_pedido(request, pedido_id):
    """Página de confirmación después de hacer un pedido"""
    if request.user.is_staff or request.user.is_superuser:
        messages.warning(request, 'Los administradores no pueden realizar compras.')
        return redirect('index')
        
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    context = {
        'pedido': pedido,
    }
    return render(request, 'cliente/compra/confirmacion.html', context)

@login_required
def mis_pedidos(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('panel_admin')
        
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(pedidos, 10)
    
    try:
        pedidos_paginados = paginator.page(page)
    except PageNotAnInteger:
        pedidos_paginados = paginator.page(1)
    except EmptyPage:
        pedidos_paginados = paginator.page(paginator.num_pages)
    
    context = {
        'pedidos': pedidos_paginados,
        'seccion': 'mis_pedidos',
    }
    return render(request, 'cliente/compra/mis_pedidos.html', context)

def detalle_artista(request, artista_id):
    artista = get_object_or_404(Artista, id=artista_id, activo=True)
    
    # Obtener productos del artista
    productos = Producto.objects.filter(artista=artista, activo=True)[:6]
    
    context = {
        'artista': artista,
        'productos': productos,
        'seccion': 'artistas',
    }
    return render(request, 'cliente/productos/detalle_artista.html', context)

# ========== API PARA AJAX ==========

@login_required
@user_passes_test(es_admin)
def api_dashboard_stats(request):
    """API para obtener estadísticas del dashboard (AJAX)"""
    stats = {
        'total_productos': Producto.objects.count(),
        'total_pedidos': Pedido.objects.count(),
        'total_usuarios': User.objects.count(),
        'total_encargos': EncargoPersonalizado.objects.count(),
        'pedidos_pendientes': Pedido.objects.filter(estado='pendiente').count(),
        'stock_bajo': Producto.objects.filter(stock__lt=5).count(),
    }
    return JsonResponse(stats)