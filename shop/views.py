from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CheckoutForm, ProductForm
from .models import Order, OrderItem, Product
from .notifications import (
    notify_order_received,
    notify_payment_confirmed,
    notify_payment_reference,
)

WHATSAPP_NUMBER = "255612660381"


def _cart(request):
    """Rudisha kikapu kilichohifadhiwa kwenye session ya mteja."""
    return request.session.get("cart", {})


def _cart_rows(request):
    """Pata bidhaa za kikapu na hesabu jumla ya bei."""
    rows = []
    total = 0

    for product_id, raw_quantity in _cart(request).items():
        try:
            product = Product.objects.get(
                pk=int(product_id),
                is_active=True,
            )
            quantity = max(1, min(50, int(raw_quantity)))
        except (Product.DoesNotExist, TypeError, ValueError):
            continue

        line_total = product.price * quantity

        rows.append(
            {
                "product": product,
                "quantity": quantity,
                "line_total": line_total,
            }
        )

        total += line_total

    return rows, total


def home(request):
    products = Product.objects.filter(is_active=True)
    cart_rows, _ = _cart_rows(request)
    cart_count = sum(row["quantity"] for row in cart_rows)

    return render(
        request,
        "shop/home.html",
        {
            "products": products,
            "cart_count": cart_count,
            "whatsapp_number": WHATSAPP_NUMBER,
        },
    )


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(
        Product,
        pk=product_id,
        is_active=True,
    )

    try:
        quantity = max(
            1,
            min(50, int(request.POST.get("quantity", "1"))),
        )
    except (TypeError, ValueError):
        quantity = 1

    cart = _cart(request).copy()
    key = str(product.pk)
    current_quantity = int(cart.get(key, 0))
    cart[key] = min(50, current_quantity + quantity)
    request.session["cart"] = cart

    messages.success(request, "Simu imeongezwa kwenye oda yako.")
    return redirect("home")


def cart_view(request):
    rows, total = _cart_rows(request)

    return render(
        request,
        "shop/cart.html",
        {
            "rows": rows,
            "total": total,
        },
    )


@require_POST
def update_cart(request, product_id):
    cart = _cart(request).copy()
    key = str(product_id)

    if request.POST.get("action") == "remove":
        cart.pop(key, None)
    else:
        try:
            quantity = int(request.POST.get("quantity", "1"))
        except (TypeError, ValueError):
            quantity = 1

        if quantity < 1:
            cart.pop(key, None)
        else:
            cart[key] = min(50, quantity)

    request.session["cart"] = cart
    return redirect("cart")


def checkout(request):
    rows, total = _cart_rows(request)

    if not rows:
        messages.info(request, "Kikapu chako bado hakina simu.")
        return redirect("home")

    form = CheckoutForm(request.POST or None)

    if request.session.get("store_language") == "en":
        form.fields["customer_name"].label = "Full name"
        form.fields["phone"].label = "Phone number"
        form.fields["delivery_area"].label = "Delivery area"
        form.fields["payment_method"].label = "Payment method"
        form.fields["payment_method"].choices = [
            ("HaloPesa", "HaloPesa (manual payment)"),
            ("Cash", "Cash on delivery"),
        ]

    if request.method == "POST" and form.is_valid():
        order = Order.objects.create(**form.cleaned_data)

        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    product=row["product"],
                    product_name=str(row["product"]),
                    quantity=row["quantity"],
                    unit_price=row["product"].price,
                )
                for row in rows
            ]
        )

        receipt_url = request.build_absolute_uri(f"/receipt/{order.reference}/")

        notify_order_received(order, receipt_url)
        request.session["cart"] = {}

        return redirect("receipt", reference=order.reference)

    return render(
        request,
        "shop/checkout.html",
        {
            "form": form,
            "rows": rows,
            "total": total,
        },
    )


@require_POST
def submit_payment_reference(request, reference):
    order = get_object_or_404(Order, reference=reference)
    transaction_reference = request.POST.get(
        "payment_reference",
        "",
    ).strip()

    if (
        order.status == Order.Status.PENDING
        and order.payment_method == "HaloPesa"
        and transaction_reference
    ):
        order.payment_reference = transaction_reference[:80]
        order.save(update_fields=["payment_reference"])

        notify_payment_reference(order)

        messages.success(
            request,
            "Namba ya muamala imetumwa. Duka litakagua malipo.",
        )
    else:
        messages.error(
            request,
            "Weka namba ya muamala halali wakati oda inasubiri malipo.",
        )

    return redirect("receipt", reference=order.reference)


def receipt(request, reference):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        reference=reference,
    )

    return render(
        request,
        "shop/receipt.html",
        {
            "order": order,
            "whatsapp_number": WHATSAPP_NUMBER,
        },
    )


@require_POST
def cancel_order(request, reference):
    order = get_object_or_404(Order, reference=reference)

    if order.status == Order.Status.PENDING:
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])

        messages.success(
            request,
            "Oda yako imeghairiwa kwa kuwa bado haijalipiwa.",
        )
    else:
        messages.error(
            request,
            "Oda hii haiwezi kughairiwa; imelipiwa au imeghairiwa tayari.",
        )

    return redirect("receipt", reference=order.reference)


def staff_only(view):
    """Ruhusu wafanyakazi walioingia kwenye akaunti pekee."""
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_staff,
        login_url="staff_login",
    )(view)


@staff_only
def staff_dashboard(request):
    paid_orders = Order.objects.filter(
        status=Order.Status.PAID,
    )

    sales = (
        paid_orders.aggregate(
            amount=Sum(F("items__quantity") * F("items__unit_price"))
        )["amount"]
        or 0
    )

    units_sold = (
        OrderItem.objects.filter(
            order__status=Order.Status.PAID,
        ).aggregate(
            amount=Sum("quantity"),
        )["amount"]
        or 0
    )

    products = Product.objects.all()
    orders = Order.objects.prefetch_related("items").all()[:50]

    return render(
        request,
        "shop/dashboard.html",
        {
            "orders": orders,
            "products": products,
            "total_sales": sales,
            "paid_count": paid_orders.count(),
            "units_sold": units_sold,
        },
    )


@staff_only
def product_create(request):
    form = ProductForm(
        request.POST or None,
        request.FILES or None,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Bidhaa imeongezwa dukani.")
        return redirect("staff_dashboard")

    return render(
        request,
        "shop/product_form.html",
        {
            "form": form,
        },
    )


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

    if order.status != Order.Status.PENDING:
        messages.error(
            request,
            "Oda hii haisubiri tena malipo.",
        )
        return redirect("staff_dashboard")

    if order.payment_method == "HaloPesa" and not order.payment_reference:
        messages.error(
            request,
            "Mteja aweke namba ya muamala ya HaloPesa kwanza.",
        )
        return redirect("staff_dashboard")

    # Kagua malipo kwenye akaunti ya HaloPesa kabla ya kuthibitisha.
    order.status = Order.Status.PAID
    order.save(update_fields=["status"])

    notify_payment_confirmed(order)

    messages.success(
        request,
        "Malipo yamethibitishwa na mauzo yameongezwa kwenye ripoti.",
    )

    return redirect("staff_dashboard")


def staff_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("staff_dashboard")

    form = AuthenticationForm(
        request,
        data=request.POST or None,
    )

    if request.method == "POST" and form.is_valid():
        user = form.get_user()

        if user.is_staff:
            login(request, user)
            return redirect("staff_dashboard")

        form.add_error(
            None,
            "Login hii ni ya wafanyakazi wa duka pekee.",
        )

    return render(
        request,
        "shop/login.html",
        {
            "form": form,
        },
    )


@require_POST
def staff_logout(request):
    logout(request)
    return redirect("home")


def switch_language(request, language):
    request.session["store_language"] = "en" if language == "en" else "sw"

    return redirect(request.META.get("HTTP_REFERER", "home"))
