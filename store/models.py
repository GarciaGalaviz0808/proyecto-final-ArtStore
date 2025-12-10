from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import uuid

# Modelo existente para Categoria...
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

# Modelo existente para Artista...
class Artista(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='artista')
    nombre = models.CharField(max_length=200)
    biografia = models.TextField()
    especialidad = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='artistas/', null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

# NUEVO MODELO PARA PERFIL DE USUARIO
class PerfilUsuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('cliente', 'Cliente'),
        ('artista', 'Artista'),
        ('admin', 'Administrador'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES, default='cliente')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    notificaciones_activas = models.BooleanField(default=True)
    newsletter = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'
        ordering = ['usuario__username']
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
    
    @property
    def nombre_completo(self):
        return f"{self.usuario.first_name} {self.usuario.last_name}".strip() or self.usuario.username
    
    @property
    def email(self):
        return self.usuario.email
    
    @property
    def es_artista(self):
        return hasattr(self.usuario, 'artista') and self.usuario.artista.activo

# Modelo existente para Producto...
class Producto(models.Model):
    TIPO_CHOICES = [
        ('oleo', 'Óleos'),
        ('acrilico', 'Acrílicos'),
        ('lienzo', 'Lienzos'),
        ('pincel', 'Pinceles'),
        ('original', 'Obra Original'),
        ('replica', 'Réplica'),
        ('suministro', 'Suministro'),
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    artista = models.ForeignKey(Artista, on_delete=models.SET_NULL, null=True, blank=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    destacado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

# Modelo existente para Carrito...
class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrito')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def cantidad_items(self):
        return sum(item.cantidad for item in self.items.all())
    
    def __str__(self):
        return f"Carrito de {self.usuario.username}"

# Modelo existente para ItemCarrito...
class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad
    
    class Meta:
        unique_together = ['carrito', 'producto']
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

# Modelo existente para Pedido...
class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta_credito', 'Tarjeta de Crédito'),
        ('tarjeta_debito', 'Tarjeta de Débito'),
        ('paypal', 'PayPal'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    numero_pedido = models.CharField(max_length=20, unique=True, default=uuid.uuid4().hex[:10].upper())
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    direccion_envio = models.TextField()
    notas = models.TextField(blank=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_pedido']
    
    def __str__(self):
        return f"Pedido {self.numero_pedido} - {self.usuario.username}"

# Modelo existente para ItemPedido...
class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

# Modelo existente para EncargoPersonalizado...
class EncargoPersonalizado(models.Model):
    TIPO_OBRA_CHOICES = [
        ('retrato', 'Retrato'),
        ('paisaje', 'Paisaje'),
        ('abstracto', 'Arte Abstracto'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='encargos')
    tipo_obra = models.CharField(max_length=20, choices=TIPO_OBRA_CHOICES)
    descripcion = models.TextField()
    artista_preferido = models.ForeignKey(Artista, on_delete=models.SET_NULL, null=True, blank=True)
    dimensiones = models.CharField(max_length=100, blank=True)
    fecha_entrega_estimada = models.DateField(null=True, blank=True)
    presupuesto_maximo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"Encargo de {self.cliente.username} - {self.get_tipo_obra_display()}"