from django.contrib import admin
from .models import Product, Order, OrderItem, Transaction

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status',)
    actions = ['mark_completed']

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_completed.short_description = "Mark selected orders as completed"

admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Transaction)
