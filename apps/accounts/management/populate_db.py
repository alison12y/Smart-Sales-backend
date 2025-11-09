from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from random import choice, randint, uniform
from decimal import Decimal
from datetime import timedelta, date

from apps.customers.models import Cliente
from apps.catalog.models import Categoria, Producto, Garantia
from apps.sales.models import Venta, DetalleVenta, Pago
from apps.marketing.models import Promocion, ProductoPromocion
from apps.reporting.models import Reporte, ModeloEntrenado, PrediccionVenta
from apps.security.models import Bitacora


class Command(BaseCommand):
    help = "Pobla toda la base de datos con datos coherentes."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING(" Iniciando poblado completo de base de datos..."))

        # ===========================
        #  Usuarios
        # ===========================
        usuarios_data = [
            ("admin", "admin123", "ana.admin@gmail.com", True, True),
            ("analista", "analista123", "marta.analista@gmail.com", True, False),
            ("carlos", "cliente123", "carlosr@gmail.com", False, False),
            ("andrea", "cliente123", "andrea@gmail.com", False, False),
            ("luis", "cliente123", "luis@gmail.com", False, False),
        ]

        users = []
        for username, password, email, staff, superuser in usuarios_data:
            user, created = User.objects.get_or_create(username=username, defaults={
                "email": email,
                "is_staff": staff,
                "is_superuser": superuser
            })
            if created:
                user.set_password(password)
                user.save()
            users.append(user)
        self.stdout.write(self.style.SUCCESS("Usuarios creados correctamente."))

        # ===========================
        #  Clientes
        # ===========================
        clientes_data = [
            (users[2], "8456321", "75550000", "Av. Grigotá #320", "Santa Cruz"),
            (users[3], "7485962", "75660123", "Calle Aroma #15", "Cochabamba"),
            (users[4], "9214578", "77780456", "Av. Busch #450", "La Paz"),
        ]

        clientes = []
        for user, ci, tel, dirc, ciudad in clientes_data:
            c, _ = Cliente.objects.get_or_create(
                user=user,
                defaults={"ci_nit": ci, "telefono": tel, "direccion": dirc, "ciudad": ciudad}
            )
            clientes.append(c)
        self.stdout.write(self.style.SUCCESS("Clientes creados correctamente."))

        # ===========================
        #  Categorías
        # ===========================
        categorias_nombres = [
            ("Electrodomésticos", "Aparatos eléctricos para el hogar."),
            ("Tecnología", "Dispositivos tecnológicos."),
            ("Muebles", "Mobiliario de interior."),
            ("Audio", "Equipos de sonido."),
            ("Cocina", "Equipos de cocina y accesorios.")
        ]
        categorias = []
        for nombre, desc in categorias_nombres:
            cat, _ = Categoria.objects.get_or_create(nombre=nombre, descripcion=desc)
            categorias.append(cat)
        self.stdout.write(self.style.SUCCESS("Categorías creadas correctamente."))

        # ===========================
        #  Productos
        # ===========================
        productos_info = [
            ("Refrigerador LG 350L", "Refrigerador eficiente A+", "LG", "FF350", 4500),
            ("Smart TV Samsung 55\"", "Televisor UHD 4K WiFi", "Samsung", "UHD55", 3800),
            ("Lavadora Mabe 18Kg", "Alta eficiencia, 3 ciclos", "Mabe", "LM18", 2500),
            ("Silla de oficina Ergonómica", "Con soporte lumbar", "Genérico", "CH300", 950),
            ("Set de ollas Tramontina", "Acero inoxidable 8 piezas", "Tramontina", "COOK8", 790),
            ("Notebook HP Pavilion", "Core i7, 16GB RAM, SSD 512GB", "HP", "PAV16", 7200),
            ("Auriculares Sony WH-1000XM5", "Noise Cancelling, Bluetooth", "Sony", "WH1000XM5", 2100),
            ("Microondas Samsung 30L", "Descongelamiento rápido", "Samsung", "MW30", 1200),
            ("Mesa de comedor 6p", "Madera de roble", "MobelHome", "MC6", 3400),
            ("Horno eléctrico Oster", "Capacidad 60L", "Oster", "O60L", 980),
        ]

        productos = []
        for i, info in enumerate(productos_info):
            nombre, desc, marca, modelo, precio = info
            cat = categorias[i % len(categorias)]
            p, _ = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "descripcion": desc,
                    "marca": marca,
                    "modelo": modelo,
                    "precio": Decimal(precio),
                    "stock": randint(5, 20),
                    "categoria": cat,
                    "imagen_url": f"img/{modelo}.png"
                }
            )
            productos.append(p)
        self.stdout.write(self.style.SUCCESS("Productos creados correctamente."))

        # ===========================
        #  Ventas, Detalles y Pagos
        # ===========================
        for i in range(5):
            cliente = choice(clientes)
            productos_seleccionados = [choice(productos) for _ in range(2)]
            total = sum(p.precio for p in productos_seleccionados)

            venta = Venta.objects.create(
                id_cliente=cliente,
                fecha_venta=timezone.now() - timedelta(days=randint(1, 30)),
                metodo_pago="Transferencia",
                total=total,
                estado_venta="Completada"
            )

            for p in productos_seleccionados:
                DetalleVenta.objects.create(
                    id_venta=venta,
                    id_producto=p,
                    cantidad=randint(1, 3),
                    precio_unitario=p.precio
                )

            Pago.objects.create(
                id_venta=venta,
                metodo="Transferencia",
                monto=total,
                fecha_pago=timezone.now(),
                estado_pago="Pagado"
            )
        self.stdout.write(self.style.SUCCESS("Ventas, detalles y pagos creados correctamente."))

        # ===========================
        #  Promociones
        # ===========================
        promociones_info = [
            ("Verano Tech", "15% en tecnología", 15),
            ("Cocina Feliz", "10% en artículos de cocina", 10),
            ("Muebles Plus", "20% en muebles seleccionados", 20)
        ]
        for titulo, desc, descu in promociones_info:
            promo = Promocion.objects.create(
                titulo=titulo,
                descripcion=desc,
                descuento_porcentaje=descu,
                fecha_inicio=date(2025, 11, 1),
                fecha_fin=date(2025, 12, 31),
                estado="activa"
            )
            ProductoPromocion.objects.create(id_producto=choice(productos), id_promocion=promo)
        self.stdout.write(self.style.SUCCESS("Promociones creadas correctamente."))

        # ===========================
        #  Modelos IA y Predicciones
        # ===========================
        modelos = []
        for nombre in ["Predicción Ventas LG", "Predicción Ventas Samsung"]:
            modelo = ModeloEntrenado.objects.create(
                nombre_modelo=nombre,
                tipo_modelo="Regresión Lineal",
                version="1.0",
                ruta_serializacion=f"/modelos/{nombre.replace(' ', '_').lower()}.pkl",
                dataset_usado="ventas_2024.csv"
            )
            modelos.append(modelo)

        for _ in range(10):
            PrediccionVenta.objects.create(
                id_producto=choice(productos),
                id_modelo=choice(modelos),
                fecha_prediccion=date.today() + timedelta(days=randint(1, 90)),
                ventas_estimadas=Decimal(uniform(5, 25)),
                periodo="Mensual",
                precision_modelo=Decimal(uniform(80, 98)),
                fecha_entrenamiento=date.today() - timedelta(days=30)
            )
        self.stdout.write(self.style.SUCCESS("Modelos y predicciones IA creados correctamente."))

        # ===========================
        #  Reportes
        # ===========================
        Reporte.objects.create(
            tipo_reporte="Ventas mensuales",
            formato="PDF",
            generado_por=users[1],
            descripcion="Reporte mensual consolidado de ventas",
            ruta_archivo="/reportes/ventas_noviembre.pdf"
        )
        Reporte.objects.create(
            tipo_reporte="Productos más vendidos",
            formato="XLSX",
            generado_por=users[1],
            descripcion="Listado de los productos más vendidos",
            ruta_archivo="/reportes/top_productos.xlsx"
        )
        Reporte.objects.create(
            tipo_reporte="Predicciones IA",
            formato="CSV",
            generado_por=users[1],
            descripcion="Proyecciones de ventas próximas",
            ruta_archivo="/reportes/predicciones_ia.csv"
        )

        # ===========================
        # 9️⃣ Bitácora
        # ===========================
        acciones = [
            ("Login", "Inicio de sesión administrador"),
            ("Compra", "Cliente realizó una compra"),
            ("Generar Reporte", "Analista generó reporte de ventas"),
        ]
        for accion, desc in acciones:
            Bitacora.objects.create(
                usuario=choice(users),
                accion=accion,
                descripcion=desc,
                fecha_accion=timezone.now() - timedelta(days=randint(0, 10))
            )

        self.stdout.write(self.style.SUCCESS(" Poblado completo exitoso."))