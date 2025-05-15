from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('base/', views.base, name='base'),
    path('collection/', views.collection, name='collection'),
    path('product_filter/', views.product_filter, name='product_filter'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('new/', views.new, name='new'),
    path('wishiist/', views.wishlist, name='wishlist'),
    path('myorders/', views.my_orders, name='myorders'),
    path('cart/', views.cart, name='cart'),
    path('search/', views.search, name='search'),
    path('razorpay-checkout/', views.razorpay_checkout, name='razorpay_checkout'),
    path('razorpay-payment-success/', views.razorpay_payment_success, name='razorpay_payment_success'),
    # --- generic patterns must be last ---
    path('<str:category>/', views.product_list, name='product_list'),
    path('<str:category>/<slug:slug>/', views.product_detail, name='product_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)