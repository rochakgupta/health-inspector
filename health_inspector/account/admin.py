from django.contrib import admin

# Register your models here.

from .models import CustomUser, Doctor, Parent, Child

@admin.register(CustomUser, Doctor, Parent, Child)
class ActivateUserAdmin(admin.ModelAdmin):
    pass