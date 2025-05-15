from django.urls import path
from shop import views as home_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'users'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('profile/new-orders/', views.new_orders, name='new_orders'),
    path('profile/order-history/', views.order_history, name='order_history'),
    path('profile/transactions/', views.transactions, name='transactions'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('profile/add-address/', views.add_address, name='add_address'),
    path('profile/delete-address/<int:id>/', views.delete_address, name='delete_address'),
    path('profile/edit-address/<int:id>/', views.edit_address, name='edit_address'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)