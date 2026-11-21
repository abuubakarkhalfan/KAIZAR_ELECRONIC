from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:product_id>/", views.update_cart, name="update_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("receipt/<uuid:reference>/", views.receipt, name="receipt"),
    path("receipt/<uuid:reference>/cancel/", views.cancel_order, name="cancel_order"),
    path("staff/login/", views.staff_login, name="staff_login"),
    path("staff/logout/", views.staff_logout, name="staff_logout"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
    path("staff/products/new/", views.product_create, name="product_create"),
    path("staff/products/<int:product_id>/toggle/",views.product_toggle,name="product_toggle",),
    path("staff/orders/<uuid:reference>/paid/", views.mark_paid, name="mark_paid"),
    path("language/<str:language>/", views.switch_language, name="switch_language"),
    path("receipt/<uuid:reference>/payment-reference/",views.submit_payment_reference,name="submit_payment_reference", ),
]
