from django.contrib import admin
from django.utils.html import format_html
from .models import Cliente, Habitacion, Reserva


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'numero_documento', 'email', 'telefono')
    list_filter = ('tipo_documento',)
    search_fields = ('nombres', 'apellidos', 'numero_documento', 'email')


@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    # ✅ CORREGIDO: cambiar esta_disponible por estado
    list_display = ('numero', 'tipo', 'precio_por_noche', 'capacidad', 'estado', 'imagen_preview')
    list_filter = ('tipo', 'estado')  # ✅ CORREGIDO
    search_fields = ('numero', 'descripcion')
    list_editable = ('precio_por_noche', 'estado')  # ✅ CORREGIDO

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" />', obj.imagen.url)
        return "Sin imagen"
    imagen_preview.short_description = 'Imagen'


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'usuario', 'habitacion', 'fecha_inicio', 'fecha_fin', 'total', 'estado')
    list_filter = ('estado', 'fecha_inicio', 'fecha_fin')
    search_fields = ('cliente__nombres', 'cliente__apellidos', 'usuario__username', 'habitacion__numero')
    list_editable = ('estado',)
    readonly_fields = ('total', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    date_hierarchy = 'fecha_inicio'
    fieldsets = (
        ('Cliente y habitación', {
            'fields': ('cliente', 'usuario', 'habitacion')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Precio y estado', {
            'fields': ('total', 'estado', 'notas')
        }),
        ('Información del sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )