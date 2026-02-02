from django.contrib import admin
from .models import Order, ServiceProvider

# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_name', 'address', 'message', 'created_at', 'message', 'amount', 'payment_id', 'payment_status')
admin.site.register(ServiceProvider)
