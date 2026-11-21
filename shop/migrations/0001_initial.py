from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Order", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("reference", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
            ("customer_name", models.CharField(max_length=140)), ("phone", models.CharField(max_length=24)),
            ("delivery_area", models.CharField(max_length=240)), ("payment_method", models.CharField(max_length=40)),
            ("status", models.CharField(choices=[("pending", "Inasubiri malipo"), ("paid", "Imelipiwa"), ("cancelled", "Imeghairiwa")], default="pending", max_length=16)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ], options={"ordering": ["-created_at"]}),
        migrations.CreateModel(name="Product", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("brand", models.CharField(max_length=80)), ("name", models.CharField(max_length=140)),
            ("description", models.TextField(blank=True)), ("price", models.PositiveBigIntegerField(help_text="Bei kwa TZS")),
            ("image", models.ImageField(blank=True, null=True, upload_to="products/%Y/%m/")),
            ("is_active", models.BooleanField(default=True)), ("created_at", models.DateTimeField(auto_now_add=True)),
        ], options={"ordering": ["-created_at"]}),
        migrations.CreateModel(name="OrderItem", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("product_name", models.CharField(max_length=180)), ("quantity", models.PositiveIntegerField()),
            ("unit_price", models.PositiveBigIntegerField()),
            ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="shop.order")),
            ("product", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="shop.product")),
        ]),
    ]
