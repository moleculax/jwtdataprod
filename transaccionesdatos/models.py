from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Cliente(models.Model):
    """Modelo de cliente (persona que ocupa la habitación)"""

    TIPO_DOCUMENTO = [
        ('dni', 'DNI'),
        ('pasaporte', 'Pasaporte'),
        ('cedula', 'Cédula'),
        ('otros', 'Otros'),
    ]

    nombres = models.CharField(max_length=200, verbose_name="Nombres")
    apellidos = models.CharField(max_length=200, verbose_name="Apellidos")
    tipo_documento = models.CharField(
        max_length=20,
        choices=TIPO_DOCUMENTO,
        default='dni',
        verbose_name="Tipo de documento"
    )
    numero_documento = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número de documento"
    )
    email = models.EmailField(verbose_name="Email")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cliente',
        verbose_name="Usuario (si está registrado)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.numero_documento}"

    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"


class Habitacion(models.Model):
    """Modelo de habitación"""

    TIPOS_HABITACION = [
        ('individual', 'Individual'),
        ('doble_matrimonial', 'Doble matrimonial'),
        ('doble_individual', 'Doble Individual'),
        ('triple', 'Triple'),
        ('cuadruple', 'Cuádruple'),
        ('suite', 'Suite'),
        ('familiar', 'Familiar'),
    ]

    ESTADO_HABITACION = [
        ('disponible', 'Disponible'),
        ('reservada', 'Reservada'),
        ('ocupada', 'Ocupada'),
        ('mantenimiento', 'En mantenimiento'),
    ]

    numero = models.CharField(max_length=10, unique=True, verbose_name="Número")
    tipo = models.CharField(max_length=20, choices=TIPOS_HABITACION, verbose_name="Tipo")
    precio_por_noche = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por noche")
    capacidad = models.PositiveIntegerField(default=1, verbose_name="Capacidad")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_HABITACION,
        default='disponible',
        verbose_name="Estado de la habitación"
    )
    imagen = models.ImageField(upload_to='habitaciones/', blank=True, null=True, verbose_name="Imagen")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.numero} - {self.get_tipo_display()} - {self.get_estado_display()}"

    def esta_ocupada(self, fecha_inicio, fecha_fin):
        """Verifica si la habitación está ocupada en un rango de fechas"""
        reservas_activas = self.reservas.filter(
            estado__in=['pendiente', 'confirmada'],
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio
        )
        return reservas_activas.exists()

    def esta_disponible_para_reservar(self, fecha_inicio, fecha_fin):
        """Verifica si la habitación está disponible para reservar"""
        if self.estado != 'disponible':
            return False
        return not self.esta_ocupada(fecha_inicio, fecha_fin)

    def actualizar_estado(self):
        """Actualiza el estado de la habitación según sus transaccionesdatos activas"""
        from datetime import date
        hoy = date.today()

        # Verificar si hay transaccionesdatos activas (pendientes o confirmadas)
        reservas_activas = self.reservas.filter(
            estado__in=['pendiente', 'confirmada'],
            fecha_fin__gte=hoy
        )

        if reservas_activas.exists():
            self.estado = 'reservada'
        else:
            self.estado = 'disponible'

        self.save(update_fields=['estado'])

    def reservar(self):
        """Cambia el estado de la habitación a reservada"""
        self.estado = 'reservada'
        self.save()

    def ocupar(self):
        """Cambia el estado de la habitación a ocupada"""
        self.estado = 'ocupada'
        self.save()

    def liberar(self):
        """Cambia el estado de la habitación a disponible"""
        self.estado = 'disponible'
        self.save()

    def poner_mantenimiento(self):
        """Cambia el estado de la habitación a mantenimiento"""
        self.estado = 'mantenimiento'
        self.save()

    @classmethod
    def habitaciones_disponibles(cls, fecha_inicio, fecha_fin):
        """Obtiene todas las habitaciones disponibles en un rango de fechas"""
        habitaciones = cls.objects.filter(estado='disponible')
        disponibles = []
        for habitacion in habitaciones:
            if habitacion.esta_disponible_para_reservar(fecha_inicio, fecha_fin):
                disponibles.append(habitacion)
        return disponibles

    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"


class Reserva(models.Model):
    """Modelo de reserva"""

    ESTADOS_RESERVA = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='transaccionesdatos',
        verbose_name="Cliente",
        null=True,
        blank=True
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservas_usuario',
        verbose_name="Usuario que reserva",
        null=True,
        blank=True
    )

    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.CASCADE,
        related_name='transaccionesdatos',
        verbose_name="Habitación",
        null=True,
        blank=True
    )

    fecha_inicio = models.DateField(
        verbose_name="Fecha de inicio",
        null=True,
        blank=True
    )
    fecha_fin = models.DateField(
        verbose_name="Fecha de fin",
        null=True,
        blank=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_RESERVA,
        default='pendiente',
        verbose_name="Estado"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total",
        default=0.00
    )
    notas = models.TextField(blank=True, null=True, verbose_name="Notas")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reserva #{self.id}"

    def calcular_total(self):
        """Calcula el total de la reserva"""
        if not self.fecha_inicio or not self.fecha_fin or not self.habitacion:
            return 0
        dias = (self.fecha_fin - self.fecha_inicio).days
        if dias <= 0:
            return 0
        return dias * self.habitacion.precio_por_noche

    def clean(self):
        """Validaciones"""
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_inicio >= self.fecha_fin:
                raise ValidationError({
                    'fecha_fin': 'La fecha de fin debe ser después de la fecha de inicio'
                })

    def save(self, *args, **kwargs):
        self.total = self.calcular_total()
        super().save(*args, **kwargs)
        # Actualizar estado de la habitación después de guardar
        if self.habitacion:
            self.habitacion.actualizar_estado()

    def delete(self, *args, **kwargs):
        habitacion = self.habitacion
        super().delete(*args, **kwargs)
        # Actualizar estado de la habitación después de eliminar
        if habitacion:
            habitacion.actualizar_estado()

class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-created_at']



class VentaViews(models.Model):
    fecha = models.DateField()
    producto = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    vendedor = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    region = models.CharField(max_length=50)
    cliente = models.CharField(max_length=100)
    metodo_pago = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.producto} - {self.fecha}"

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha']