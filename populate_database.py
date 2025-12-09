#!/usr/bin/env python
"""
Script para poblar la base de datos de ArtStore con datos de prueba
Uso: python manage.py shell < populate_database.py
"""

import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ArtStoreProject.settings')
django.setup()

from django.contrib.auth.models import User
from store.models import *

def crear_superusuario():
    """Crea el superusuario administrador"""
    print("Creando superusuario...")
    
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@artstore.com',
            password='admin123',
            first_name='Administrador',
            last_name='ArtStore'
        )
        print("✓ Superusuario 'admin' creado (contraseña: admin123)")
    else:
        print("✓ Superusuario ya existe")

def crear_usuarios_clientes():
    """Crea usuarios de prueba (clientes)"""
    print("\nCreando usuarios clientes...")
    
    clientes = [
        {'username': 'cliente1', 'email': 'cliente1@artstore.com', 'first_name': 'Ana', 'last_name': 'García'},
        {'username': 'cliente2', 'email': 'cliente2@artstore.com', 'first_name': 'Carlos', 'last_name': 'Rodríguez'},
        {'username': 'cliente3', 'email': 'cliente3@artstore.com', 'first_name': 'María', 'last_name': 'López'},
        {'username': 'artista1', 'email': 'andrea@artstore.com', 'first_name': 'Andrea', 'last_name': 'Montoya'},
        {'username': 'artista2', 'email': 'yahel@artstore.com', 'first_name': 'Yahel', 'last_name': 'Villa'},
    ]
    
    for datos in clientes:
        if not User.objects.filter(username=datos['username']).exists():
            user = User.objects.create_user(
                username=datos['username'],
                email=datos['email'],
                password='cliente123',
                first_name=datos['first_name'],
                last_name=datos['last_name']
            )
            print(f"✓ Usuario '{datos['username']}' creado (contraseña: cliente123)")
        else:
            print(f"✓ Usuario '{datos['username']}' ya existe")

def crear_categorias():
    """Crea categorías de productos"""
    print("\nCreando categorías...")
    
    categorias = [
        {'nombre': 'Pintura al Óleo', 'slug': 'pintura-oleo'},
        {'nombre': 'Pintura Acrílica', 'slug': 'pintura-acrilica'},
        {'nombre': 'Lienzos', 'slug': 'lienzos'},
        {'nombre': 'Pinceles', 'slug': 'pinceles'},
        {'nombre': 'Obras Originales', 'slug': 'obras-originales'},
        {'nombre': 'Réplicas', 'slug': 'replicas'},
        {'nombre': 'Suministros Varios', 'slug': 'suministros-varios'},
    ]
    
    for cat_data in categorias:
        cat, created = Categoria.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={'slug': cat_data['slug']}
        )
        if created:
            print(f"✓ Categoría '{cat.nombre}' creada")
        else:
            print(f"✓ Categoría '{cat.nombre}' ya existe")
    
    return Categoria.objects.all()

def crear_artistas():
    """Crea artistas para los productos"""
    print("\nCreando artistas...")
    
    # Primero asegurar que los usuarios artistas existen
    usuarios_artistas = [
        {'username': 'artista1', 'email': 'andrea@artstore.com', 'first_name': 'Andrea', 'last_name': 'Montoya'},
        {'username': 'artista2', 'email': 'yahel@artstore.com', 'first_name': 'Yahel', 'last_name': 'Villa'},
        {'username': 'davinci', 'email': 'davinci@artstore.com', 'first_name': 'Leonardo', 'last_name': 'da Vinci'},
        {'username': 'vangogh', 'email': 'vangogh@artstore.com', 'first_name': 'Vincent', 'last_name': 'van Gogh'},
    ]
    
    for datos in usuarios_artistas:
        if not User.objects.filter(username=datos['username']).exists():
            User.objects.create_user(
                username=datos['username'],
                email=datos['email'],
                password='artista123',
                first_name=datos['first_name'],
                last_name=datos['last_name']
            )
            print(f"✓ Usuario artista '{datos['username']}' creado")
    
    artistas = [
        {
            'usuario': User.objects.get(username='artista1'),
            'nombre': 'Andrea Montoya',
            'biografia': 'Especialista en arte abstracto y técnica mixta. Graduada de la Escuela de Bellas Artes con más de 10 años de experiencia en exposiciones internacionales.',
            'especialidad': 'Arte Abstracto y Técnica Mixta',
            'activo': True
        },
        {
            'usuario': User.objects.get(username='artista2'),
            'nombre': 'Yahel Villa',
            'biografia': 'Pintor realista especializado en paisajes naturales. Su obra captura la esencia de la naturaleza mexicana con un estilo único y detallado.',
            'especialidad': 'Pintura Realista de Paisajes',
            'activo': True
        },
        {
            'usuario': User.objects.get(username='davinci'),
            'nombre': 'Leonardo da Vinci',
            'biografia': 'Artista renacentista italiano, uno de los mayores genios de la historia del arte. Creador de obras maestras como La Mona Lisa y La Última Cena.',
            'especialidad': 'Renacimiento Italiano',
            'activo': True
        },
        {
            'usuario': User.objects.get(username='vangogh'),
            'nombre': 'Vincent van Gogh',
            'biografia': 'Pintor postimpresionista neerlandés. Conocido por su uso vibrante del color y pinceladas expresivas. Autor de La Noche Estrellada.',
            'especialidad': 'Postimpresionismo',
            'activo': True
        }
    ]
    
    artistas_objetos = []
    for artista_data in artistas:
        # Verificar si ya existe un artista con este usuario
        artista, created = Artista.objects.get_or_create(
            usuario=artista_data['usuario'],
            defaults={
                'nombre': artista_data['nombre'],
                'biografia': artista_data['biografia'],
                'especialidad': artista_data['especialidad'],
                'activo': artista_data['activo']
            }
        )
        if created:
            print(f"✓ Artista '{artista.nombre}' creado")
        else:
            # Si ya existe, actualizar los datos
            artista.nombre = artista_data['nombre']
            artista.biografia = artista_data['biografia']
            artista.especialidad = artista_data['especialidad']
            artista.activo = artista_data['activo']
            artista.save()
            print(f"✓ Artista '{artista.nombre}' actualizado")
        artistas_objetos.append(artista)
    
    return artistas_objetos

def crear_productos(categorias, artistas):
    """Crea productos de prueba para todas las categorías"""
    print("\nCreando productos...")
    
    productos_data = [
        # ÓLEOS
        {
            'nombre': 'Set de Óleos Primarios Profesionales',
            'descripcion': 'Set completo de 12 tubos de óleo de alta calidad. Pigmentos puros que garantizan colores vibrantes y duraderos. Ideal para artistas profesionales.',
            'precio': Decimal('120.00'),
            'stock': 25,
            'tipo': 'oleo',
            'categoria': categorias.get(slug='pintura-oleo'),
            'artista': None,
            'destacado': True,
            'activo': True
        },
        {
            'nombre': 'Óleos Profesionales 24 Colores',
            'descripcion': 'Colección premium de 24 colores al óleo. Incluye todos los tonos básicos y especiales para crear cualquier paleta. Alta resistencia a la luz.',
            'precio': Decimal('380.00'),
            'stock': 15,
            'tipo': 'oleo',
            'categoria': categorias.get(slug='pintura-oleo'),
            'artista': None,
            'destacado': True,
            'activo': True
        },
        {
            'nombre': 'Óleos para Estudiantes - Set Básico',
            'descripcion': 'Set económico perfecto para estudiantes. 8 colores básicos de buena calidad a un precio accesible.',
            'precio': Decimal('65.00'),
            'stock': 40,
            'tipo': 'oleo',
            'categoria': categorias.get(slug='pintura-oleo'),
            'artista': None,
            'destacado': False,
            'activo': True
        },
        
        # ACRÍLICOS
        {
            'nombre': 'Set Acrílicos Básicos 12 Colores',
            'descripcion': 'Set de 12 colores acrílicos de secado rápido. Perfecto para principiantes y proyectos escolares.',
            'precio': Decimal('210.00'),
            'stock': 30,
            'tipo': 'acrilico',
            'categoria': categorias.get(slug='pintura-acrilica'),
            'artista': None,
            'destacado': True,
            'activo': True
        },
        {
            'nombre': 'Acrílicos Metálicos Premium',
            'descripcion': 'Set exclusivo de 8 colores acrílicos metálicos. Efectos brillantes y profesionales para obras especiales.',
            'precio': Decimal('365.00'),
            'stock': 18,
            'tipo': 'acrilico',
            'categoria': categorias.get(slug='pintura-acrilica'),
            'artista': None,
            'destacado': False,
            'activo': True
        },
        {
            'nombre': 'Acrílicos Fluorescentes 6 Colores',
            'descripcion': 'Colores acrílicos fluorescentes que brillan bajo luz UV. Ideal para arte urbano y obras contemporáneas.',
            'precio': Decimal('280.00'),
            'stock': 22,
            'tipo': 'acrilico',
            'categoria': categorias.get(slug='pintura-acrilica'),
            'artista': None,
            'destacado': False,
            'activo': True
        },
        
        # LIENZOS
        {
            'nombre': 'Lienzo 40x50 cm - Algodón Premium',
            'descripcion': 'Lienzo de algodón de primera calidad. Tensado en marco de pino. Listo para pintar al óleo o acrílico.',
            'precio': Decimal('95.00'),
            'stock': 50,
            'tipo': 'lienzo',
            'categoria': categorias.get(slug='lienzos'),
            'artista': None,
            'destacado': True,
            'activo': True
        },
        {
            'nombre': 'Pack de 3 Lienzos (30x40, 40x50, 50x70)',
            'descripcion': 'Pack económico con 3 lienzos de diferentes tamaños. Perfecto para practicar o crear una serie de obras.',
            'precio': Decimal('579.00'),
            'stock': 20,
            'tipo': 'lienzo',
            'categoria': categorias.get(slug='lienzos'),
            'artista': None,
            'destacado': False,
            'activo': True
        },
        {
            'nombre': 'Lienzo Grande 100x150 cm Profesional',
            'descripcion': 'Lienzo profesional de gran formato. Estructura reforzada para obras monumentales.',
            'precio': Decimal('1200.00'),
            'stock': 8,
            'tipo': 'lienzo',
            'categoria': categorias.get(slug='lienzos'),
            'artista': None,
            'destacado': True,
            'activo': True
        },
        
        # PINCELES
        {
            'nombre': 'Set de Pinceles Redondos 8 Piezas',
            'descripcion': 'Set completo de pinceles redondos en 8 tamaños diferentes. Cerdas sintéticas de alta calidad.',
            'precio': Decimal('290.00'),
            'stock': 35,
            'tipo': 'pincel',
            'categoria': categorias.get(slug='pinceles'),
            'artista': None,
            'destacado': True,
            'activo': True
        },
        {
            'nombre': 'Pinceles Sintéticos Premium 12 Unidades',
            'descripcion': 'Colección premium de pinceles sintéticos. Incluye variedad de formas y tamaños para todas las técnicas.',
            'precio': Decimal('678.00'),
            'stock': 25,
            'tipo': 'pincel',
            'categoria': categorias.get(slug='pinceles'),
            'artista': None,
            'destacado': False,
            'activo': True
        },
        {
            'nombre': 'Set Pinceles para Acuarela 6 Piezas',
            'descripcion': 'Pinceles especializados para acuarela. Pelo de marta kolinsky para máxima absorción y precisión.',
            'precio': Decimal('420.00'),
            'stock': 18,
            'tipo': 'pincel',
            'categoria': categorias.get(slug='pinceles'),
            'artista': None,
            'destacado': False,
            'activo': True
        },
        
        # OBRAS ORIGINALES
        {
            'nombre': 'La Torre Eiffel al Atardecer',
            'descripcion': 'Pintura original al óleo que captura la belleza de la Torre Eiffil al atardecer. Obra única firmada por el artista.',
            'precio': Decimal('850.00'),
            'stock': 1,
            'tipo': 'original',
            'categoria': categorias.get(slug='obras-originales'),
            'artista': artistas[0],  # Andrea Montoya
            'destacado': True,
            'activo': True
        },
        {
            'nombre': 'Mujer Vestida de Azul',
            'descripcion': 'Retrato original en técnica mixta. Obra abstracta que explora la feminidad y la melancolía.',
            'precio': Decimal('1200.00'),
            'stock': 1,
            'tipo': 'original',
            'categoria': categorias.get(slug='obras-originales'),
            'artista': artistas[0],
            'destacado': True,
            'activo': True
        },
        {
            'nombre': 'Gatito Bebé - Realismo',
            'descripcion': 'Pintura realista de un gatito bebé. Detalles perfectos que capturan la ternura del animal.',
            'precio': Decimal('777.00'),
            'stock': 1,
            'tipo': 'original',
            'categoria': categorias.get(slug='obras-originales'),
            'artista': artistas[1],  # Yahel Villa
            'destacado': False,
            'activo': True
        },
        {
            'nombre': 'Paisaje Montañoso en Otoño',
            'descripcion': 'Obra original que muestra la belleza de las montañas durante el otoño. Colores vibrantes y texturas ricas.',
            'precio': Decimal('950.00'),
            'stock': 1,
            'tipo': 'original',
            'categoria': categorias.get(slug='obras-originales'),
            'artista': artistas[1],
            'destacado': True,
            'activo': True
        },
        
        # RÉPLICAS
        {
            'nombre': 'La Noche Estrellada - Van Gogh',
            'descripcion': 'Réplica detallada de la obra maestra de Van Gogh. Pintada a mano por artistas especializados.',
            'precio': Decimal('450.00'),
            'stock': 3,
            'tipo': 'replica',
            'categoria': categorias.get(slug='replicas'),
            'artista': artistas[3],  # Van Gogh
            'destacado': True,
            'activo': True
        },
        {
            'nombre': 'La Mona Lisa - Leonardo da Vinci',
            'descripcion': 'Reproducción en óleo de la famosa Mona Lisa. Detalles cuidadosamente replicados.',
            'precio': Decimal('600.00'),
            'stock': 2,
            'tipo': 'replica',
            'categoria': categorias.get(slug='replicas'),
            'artista': artistas[2],  # Da Vinci
            'destacado': True,
            'activo': True
        },
        {
            'nombre': 'Los Girasoles - Van Gogh',
            'descripcion': 'Réplica de la famosa serie de girasoles de Van Gogh. Colores vibrantes y pinceladas expresivas.',
            'precio': Decimal('380.00'),
            'stock': 4,
            'tipo': 'replica',
            'categoria': categorias.get(slug='replicas'),
            'artista': artistas[3],
            'destacado': False,
            'activo': True
        },
        
        # SUMINISTROS VARIOS
        {
            'nombre': 'Kit Iniciación Arte - 25 Piezas',
            'descripcion': 'Kit completo para principiantes. Incluye pinturas, pinceles, lienzos y paleta.',
            'precio': Decimal('299.00'),
            'stock': 15,
            'tipo': 'suministro',
            'categoria': categorias.get(slug='suministros-varios'),
            'artista': None,
            'destacado': True,
            'activo': True
        },
        {
            'nombre': 'Caballete de Estudio Profesional',
            'descripcion': 'Caballete robusto de madera para estudio. Ajustable en altura e inclinación.',
            'precio': Decimal('450.00'),
            'stock': 12,
            'tipo': 'suministro',
            'categoria': categorias.get(slug='suministros-varios'),
            'artista': None,
            'destacado': False,
            'activo': True
        },
        {
            'nombre': 'Set Paletas Mezcladoras 5 Unidades',
            'descripcion': 'Set de 5 paletas de plástico para mezclar colores. Fáciles de limpiar y reutilizar.',
            'precio': Decimal('85.00'),
            'stock': 40,
            'tipo': 'suministro',
            'categoria': categorias.get(slug='suministros-varios'),
            'artista': None,
            'destacado': False,
            'activo': True
        }
    ]
    
    productos_creados = 0
    for prod_data in productos_data:
        # Verificar si el producto ya existe
        if not Producto.objects.filter(nombre=prod_data['nombre']).exists():
            producto = Producto.objects.create(**prod_data)
            productos_creados += 1
            print(f"✓ Producto '{producto.nombre}' creado")
        else:
            print(f"✓ Producto '{prod_data['nombre']}' ya existe")
    
    print(f"\nTotal productos creados: {productos_creados}")
    return Producto.objects.count()

def crear_carritos_usuarios():
    """Crea carritos para todos los usuarios"""
    print("\nCreando carritos para usuarios...")
    
    usuarios_sin_carrito = User.objects.filter(carrito__isnull=True)
    for usuario in usuarios_sin_carrito:
        Carrito.objects.create(usuario=usuario)
        print(f"✓ Carrito creado para usuario '{usuario.username}'")
    
    print(f"Total carritos creados: {usuarios_sin_carrito.count()}")

def crear_pedidos_prueba():
    """Crea pedidos de prueba"""
    print("\nCreando pedidos de prueba...")
    
    # Obtener clientes y productos
    cliente1 = User.objects.get(username='cliente1')
    cliente2 = User.objects.get(username='cliente2')
    
    productos = Producto.objects.filter(activo=True, stock__gt=0)
    
    if productos.count() < 3:
        print("✗ No hay suficientes productos para crear pedidos")
        return
    
    # Pedido 1 - Cliente 1 (Entregado)
    try:
        pedido1 = Pedido.objects.create(
            usuario=cliente1,
            metodo_pago='tarjeta_credito',
            subtotal=Decimal('450.00'),
            iva=Decimal('72.00'),
            total=Decimal('522.00'),
            direccion_envio='Calle Principal 123, Colonia Centro, CDMX',
            estado='entregado',
            fecha_pedido=datetime.now() - timedelta(days=10)
        )
        
        # Agregar items al pedido
        ItemPedido.objects.create(
            pedido=pedido1,
            producto=productos[0],
            cantidad=1,
            precio_unitario=productos[0].precio,
            subtotal=productos[0].precio * 1
        )
        
        print(f"✓ Pedido #{pedido1.numero_pedido} creado (entregado)")
    except Exception as e:
        print(f"✗ Error creando pedido 1: {e}")
    
    # Pedido 2 - Cliente 1 (Enviado)
    try:
        pedido2 = Pedido.objects.create(
            usuario=cliente1,
            metodo_pago='paypal',
            subtotal=Decimal('850.00'),
            iva=Decimal('136.00'),
            total=Decimal('986.00'),
            direccion_envio='Avenida Reforma 456, Polanco, CDMX',
            estado='enviado',
            fecha_pedido=datetime.now() - timedelta(days=3)
        )
        
        ItemPedido.objects.create(
            pedido=pedido2,
            producto=productos[1],
            cantidad=2,
            precio_unitario=productos[1].precio,
            subtotal=productos[1].precio * 2
        )
        
        print(f"✓ Pedido #{pedido2.numero_pedido} creado (enviado)")
    except Exception as e:
        print(f"✗ Error creando pedido 2: {e}")
    
    # Pedido 3 - Cliente 2 (Pendiente)
    try:
        pedido3 = Pedido.objects.create(
            usuario=cliente2,
            metodo_pago='efectivo',
            subtotal=Decimal('1200.00'),
            iva=Decimal('192.00'),
            total=Decimal('1392.00'),
            direccion_envio='Calle Jardín 789, Del Valle, CDMX',
            estado='pendiente',
            fecha_pedido=datetime.now() - timedelta(days=1)
        )
        
        ItemPedido.objects.create(
            pedido=pedido3,
            producto=productos[2],
            cantidad=1,
            precio_unitario=productos[2].precio,
            subtotal=productos[2].precio * 1
        )
        
        ItemPedido.objects.create(
            pedido=pedido3,
            producto=productos[3],
            cantidad=1,
            precio_unitario=productos[3].precio,
            subtotal=productos[3].precio * 1
        )
        
        print(f"✓ Pedido #{pedido3.numero_pedido} creado (pendiente)")
    except Exception as e:
        print(f"✗ Error creando pedido 3: {e}")
    
    print(f"Total pedidos creados: {Pedido.objects.count()}")

def crear_encargos_prueba():
    """Crea encargos personalizados de prueba"""
    print("\nCreando encargos de prueba...")
    
    cliente1 = User.objects.get(username='cliente1')
    artista1 = Artista.objects.get(nombre='Andrea Montoya')
    
    # Encargo 1 - Pendiente
    encargo1 = EncargoPersonalizado.objects.create(
        cliente=cliente1,
        tipo_obra='retrato',
        descripcion='Retrato familiar en estilo realista. Familia de 4 personas en un jardín. Preferiblemente en óleo.',
        artista_preferido=artista1,
        dimensiones='80x100 cm',
        presupuesto_maximo=Decimal('1500.00'),
        estado='pendiente'
    )
    print(f"✓ Encargo #{encargo1.id} creado (pendiente)")
    
    # Encargo 2 - En Proceso
    encargo2 = EncargoPersonalizado.objects.create(
        cliente=cliente1,
        tipo_obra='paisaje',
        descripcion='Paisaje marino al atardecer. Con acantilados y el mar en calma. Técnica mixta.',
        dimensiones='60x90 cm',
        presupuesto_maximo=Decimal('1200.00'),
        estado='en_proceso',
        fecha_solicitud=datetime.now() - timedelta(days=15)
    )
    print(f"✓ Encargo #{encargo2.id} creado (en proceso)")
    
    # Encargo 3 - Completado
    encargo3 = EncargoPersonalizado.objects.create(
        cliente=cliente1,
        tipo_obra='abstracto',
        descripcion='Obra abstracta con colores cálidos (rojos, naranjas, amarillos). Que transmita energía y pasión.',
        artista_preferido=artista1,
        dimensiones='100x120 cm',
        estado='completado',
        fecha_solicitud=datetime.now() - timedelta(days=30),
        fecha_actualizacion=datetime.now() - timedelta(days=5)
    )
    print(f"✓ Encargo #{encargo3.id} creado (completado)")
    
    print(f"Total encargos creados: {EncargoPersonalizado.objects.count()}")

def crear_items_carrito_prueba():
    """Crea items en carritos de prueba"""
    print("\nCreando items en carritos de prueba...")
    
    cliente1 = User.objects.get(username='cliente1')
    productos = Producto.objects.filter(activo=True, stock__gt=0)[:3]
    
    try:
        carrito = Carrito.objects.get(usuario=cliente1)
        
        # Limpiar carrito existente
        carrito.items.all().delete()
        
        # Agregar productos al carrito
        for i, producto in enumerate(productos, 1):
            ItemCarrito.objects.create(
                carrito=carrito,
                producto=producto,
                cantidad=i  # 1, 2, 3 unidades
            )
            print(f"✓ Producto '{producto.nombre}' agregado al carrito ({i} unidades)")
        
        print(f"Total items en carrito: {carrito.items.count()}")
        print(f"Subtotal carrito: ${carrito.total}")
        
    except Exception as e:
        print(f"✗ Error creando items en carrito: {e}")

def main():
    """Función principal que ejecuta todo el proceso"""
    print("=" * 60)
    print("POBLANDO BASE DE DATOS ARTSTORE")
    print("=" * 60)
    
    try:
        # 1. Crear superusuario
        crear_superusuario()
        
        # 2. Crear usuarios clientes y artistas
        crear_usuarios_clientes()
        
        # 3. Crear categorías
        categorias = crear_categorias()
        
        # 4. Crear artistas
        artistas = crear_artistas()
        
        # 5. Crear productos
        total_productos = crear_productos(categorias, artistas)
        
        # 6. Crear carritos para usuarios
        crear_carritos_usuarios()
        
        # 7. Crear pedidos de prueba
        crear_pedidos_prueba()
        
        # 8. Crear encargos de prueba
        crear_encargos_prueba()
        
        # 9. Crear items en carrito de prueba
        crear_items_carrito_prueba()
        
        print("\n" + "=" * 60)
        print("POBLACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        
        # Mostrar resumen
        print(f"\nRESUMEN:")
        print(f"- Usuarios: {User.objects.count()}")
        print(f"- Categorías: {Categoria.objects.count()}")
        print(f"- Artistas: {Artista.objects.count()}")
        print(f"- Productos: {total_productos}")
        print(f"- Pedidos: {Pedido.objects.count()}")
        print(f"- Encargos: {EncargoPersonalizado.objects.count()}")
        print(f"- Carritos: {Carrito.objects.count()}")
        
        print(f"\nCREDENCIALES DE ACCESO:")
        print(f"- Admin: usuario='admin', contraseña='admin123'")
        print(f"- Cliente: usuario='cliente1', contraseña='cliente123'")
        print(f"- Artista: usuario='artista1', contraseña='cliente123'")
        
        print(f"\nURLS IMPORTANTES:")
        print(f"- Sitio principal: http://localhost:8000/")
        print(f"- Panel admin: http://localhost:8000/admin/panel/")
        print(f"- Admin Django: http://localhost:8000/admin/ (usar credenciales Django)")
        
    except Exception as e:
        print(f"\n✗ ERROR durante la población: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()