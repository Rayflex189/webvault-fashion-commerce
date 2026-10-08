from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_detail, name='cart'),
    path('cart/add/<int:variant_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:variant_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:variant_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
]
