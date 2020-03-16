from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import Node, Partner, Order
# Register your models here.

class OrderAdmin(admin.ModelAdmin):
	list_display = ['store', 'complete', 'assigned_to']

admin.site.register(Node)
admin.site.register(Partner)
admin.site.register(Order, OrderAdmin)