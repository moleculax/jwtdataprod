from rest_framework import serializers
from .models import Cliente, Habitacion, Reserva


class ClienteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Cliente
        fields = [
            'id', 'nombres', 'apellidos', 'nombre_completo',
            'tipo_documento', 'numero_documento', 'email',
            'telefono', 'usuario'
        ]


class HabitacionSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Habitacion
        fields = [
            'id', 'numero', 'tipo', 'tipo_display',
            'precio_por_noche', 'capacidad', 'descripcion',
            'estado', 'estado_display', 'imagen'
        ]


class ReservaSerializer(serializers.ModelSerializer):
    cliente_detalle = ClienteSerializer(source='cliente', read_only=True)
    habitacion_detalle = HabitacionSerializer(source='habitacion', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    dias = serializers.SerializerMethodField()

    class Meta:
        model = Reserva
        fields = [
            'id', 'cliente', 'cliente_detalle', 'usuario', 'usuario_nombre',
            'habitacion', 'habitacion_detalle', 'fecha_inicio', 'fecha_fin',
            'dias', 'total', 'estado', 'notas', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'usuario',  # ✅ EL USUARIO NO SE PUEDE MODIFICAR
            'total',
            'created_at',
            'updated_at'
        ]

    def get_dias(self, obj):
        if obj.fecha_inicio and obj.fecha_fin:
            return (obj.fecha_fin - obj.fecha_inicio).days
        return 0

    def validate(self, data):
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        habitacion = data.get('habitacion')

        if not fecha_inicio or not fecha_fin or not habitacion:
            return data

        if fecha_inicio >= fecha_fin:
            raise serializers.ValidationError(
                "La fecha de fin debe ser después de la fecha de inicio"
            )

        if habitacion.estado != 'disponible':
            raise serializers.ValidationError(
                "La habitación no está disponible para reservar"
            )

        reservas_existentes = Reserva.objects.filter(
            habitacion=habitacion,
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio,
            estado__in=['pendiente', 'confirmada']
        )
        if self.instance:
            reservas_existentes = reservas_existentes.exclude(id=self.instance.id)

        if reservas_existentes.exists():
            raise serializers.ValidationError(
                "La habitación ya está reservada en esas fechas"
            )

        return data