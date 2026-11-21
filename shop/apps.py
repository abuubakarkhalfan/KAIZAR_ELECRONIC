from django.apps import AppConfig

class ShopConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shop"
    verbose_name = "Duka la Kaizar"

    def ready(self):
        from . import site_admin  # noqa: F401
