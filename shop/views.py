from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count, F
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import CheckoutForm, ProductForm
from .models import Order, OrderItem, Product

WHATSAPP_NUMBER = "255612660381"

def _cart(request):
    return request.session.get("cart", {})

def _cart_rows(request):
    rows, total = [], 0
    cart = _cart(request)
    for key, quantity in cart.items():
        try:
            product = Product.objects.get(pk=int(key), is_active=True)
            quantity = max(1, int(quantity))
        except (Product.DoesNotExist, ValueError, TypeError):
            continue
        line_total = product.price * quantity
        rows.append({"product": product, "quantity": quantity, "line_total": line_total})
        total += line_total
    return rows, total

def home(request):
    products = Product.objects.filter(is_active=True)
    rows, _ = _cart_rows(request)
    return render(request, "shop/home.html", {"products": products, "cart_count": sum(row["quantity"] for row in rows), "whatsapp_number": WHATSAPP_NUMBER})

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    try:
        quantity = max(1, min(50, int(request.POST.get("quantity", "1"))))
    except ValueError:
        quantity = 1
    cart = _cart(request).copy()
    cart[str(product.pk)] = min(50, int(cart.get(str(product.pk), 0)) + quantity)
    request.session["cart"] = cart
    messages.success(request, "Simu imeongezwa kwenye oda yako.")
    return redirect("home")

def cart_view(request):
    rows, total = _cart_rows(request)
    return render(request, "shop/cart.html", {"rows": rows, "total": total})

@require_POST
def update_cart(request, product_id):
    cart = _cart(request).copy()
    key = str(product_id)
    if request.POST.get("action") == "remove":
        cart.pop(key, None)
    else:
        try:
            quantity = int(request.POST.get("quantity", "1"))
            if quantity < 1:
                cart.pop(key, None)
            else:
                cart[key] = min(50, quantity)
        except ValueError:
            pass
    request.session["cart"] = cart
    return redirect("cart")

def checkout(request):
    rows, total = _cart_rows(request)
    if not rows:
        messages.info(request, "Kikapu chako bado hakina simu.")
        return redirect("home")
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        order = Order.objects.create(**form.cleaned_data)
        OrderItem.objects.bulk_create([
            OrderItem(order=order, product=row["product"], product_name=str(row["product"]), quantity=row["quantity"], unit_price=row["product"].price)
            for row in rows
        ])
        request.session["cart"] = {}
        return redirect("receipt", reference=order.reference)
    return render(request, "shop/checkout.html", {"form": form, "rows": rows, "total": total})

def receipt(request, reference):
    order = get_object_or_404(Order.objects.prefetch_related("items"), reference=reference)
    return render(request, "shop/receipt.html", {"order": order, "whatsapp_number": WHATSAPP_NUMBER})

@require_POST
def cancel_order(request, reference):
    order = get_object_or_404(Order, reference=reference)
    if order.status == Order.Status.PENDING:
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])
        messages.success(request, "Oda yako imeghairiwa kwa kuwa bado haijalipiwa.")
    else:
        messages.error(request, "Oda hii haiwezi kughairiwa hapa; tayari imelipiwa au imeghairiwa.")
    return redirect("receipt", reference=order.reference)

def staff_only(view):
    return user_passes_test(lambda user: user.is_authenticated and user.is_staff, login_url="staff_login")(view)

@staff_only
def staff_dashboard(request):
    paid_orders = Order.objects.filter(status=Order.Status.PAID)
    total_sales = paid_orders.aggregate(amount=Sum(F("items__quantity") * F("items__unit_price")))['amount'] or 0
    units_sold = OrderItem.objects.filter(order__status=Order.Status.PAID).aggregate(amount=Sum("quantity"))["amount"] or 0
    products = Product.objects.all()
    orders = Order.objects.prefetch_related("items").all()[:50]
    return render(request, "shop/dashboard.html", {"orders": orders, "products": products, "total_sales": total_sales, "paid_count": paid_orders.count(), "units_sold": units_sold})

@staff_only
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Bidhaa imeongezwa dukani.")
        return redirect("staff_dashboard")
    return render(request, "shop/product_form.html", {"form": form})

@staff_only
@require_POST
def product_toggle(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.is_active = not product.is_active
    product.save(update_fields=["is_active"])
    return redirect("staff_dashboard")

@staff_only
@require_POST
def mark_paid(request, reference):
    order = get_object_or_404(Order, reference=reference)
    if order.status == Order.Status.PENDING:
        order.status = Order.Status.PAID
        order.save(update_fields=["status"])
        messages.success(request, "Malipo yamethibitishwa na mauzo yameongezwa kwenye ripoti.")
    return redirect("staff_dashboard")

def staff_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("staff_dashboard")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if user.is_staff:
            login(request, user)
            return redirect("staff_dashboard")
        form.add_error(None, "Login hii ni ya wafanyakazi wa duka pekee.")
    return render(request, "shop/login.html", {"form": form})

@require_POST
def staff_logout(request):
    logout(request)
    return redirect("home")

def switch_language(request, language):
    request.session["store_language"] = "en" if language == "en" else "sw"
    return redirect(request.META.get("HTTP_REFERER", "home"))
