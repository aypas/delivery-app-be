from django.contrib import admin

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from authentication.models import CustomUser
from authentication.forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
	add_form = CustomUserCreationForm
	add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': '__all__'}
        ),
    )


# Register your models here.
admin.site.register(CustomUser)
