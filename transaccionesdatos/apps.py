# ============================================
# ARCHIVO: transaccionesdatos/apps.py
# ============================================
from django.apps import AppConfig


class ReservasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transaccionesdatos'
    verbose_name = 'Gestión de Reservas'
