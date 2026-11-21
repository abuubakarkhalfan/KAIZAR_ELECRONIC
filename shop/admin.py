from django.contrib import admin
from .models import Order, OrderItem, Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("brand", "name", "price", "is_active", "created_at")
    list_filter = ("brand", "is_active")
    search_fields = ("brand", "name")

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "quantity", "unit_price")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "customer_name", "phone", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("customer_name", "phone", "reference")
    inlines = [OrderItemInline]
