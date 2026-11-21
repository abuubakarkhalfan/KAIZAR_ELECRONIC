from django.db import models
from django.urls import reverse
import uuid

class Product(models.Model):
    brand = models.CharField(max_length=80)
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    price = models.PositiveBigIntegerField(help_text="Bei kwa TZS")
    image = models.ImageField(upload_to="products/%Y/%m/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand} {self.name}"

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Inasubiri malipo"
        PAID = "paid", "Imelipiwa"
        CANCELLED = "cancelled", "Imeghairiwa"

    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer_name = models.CharField(max_length=140)
    phone = models.CharField(max_length=24)
    delivery_area = models.CharField(max_length=240)
    payment_method = models.CharField(max_length=40)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer_name} · {self.reference}"

    @property
    def total(self):
        return sum(item.line_total for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=180)
    quantity = models.PositiveIntegerField()
    unit_price = models.PositiveBigIntegerField()

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"
