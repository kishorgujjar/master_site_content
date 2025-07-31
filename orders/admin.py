from django.contrib import admin
from .models import Payment, Order, OrderProduct


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'user', 'quantity', 'product_price', 'ordered', 'created_at')
    list_filter = ('ordered', 'product__product_name', 'user__username')
    search_fields = ('order__order_number', 'product__product_name', 'user__username')
    filter_horizontal = ('variations',)  # For color & size (ManyToMany)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'email', 'phone', 'order_total', 'status', 'is_ordered', 'created_at')
    list_filter = ('status', 'is_ordered', 'created_at')
    search_fields = ('order_number', 'first_name', 'last_name', 'email', 'phone')
    inlines = [OrderProductInline]

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'payment_method', 'amount_paid', 'status', 'created_at')
    list_filter = ('payment_method', 'status')
    search_fields = ('payment_id', 'user__username')

# Register models
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
