from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as AuthUser

from . import models


# Define an inline admin descriptor for the custom User model
class UserInline(admin.StackedInline):
    model = models.User  # Refers to your custom User model
    can_delete = False
    verbose_name_plural = "user"


# Define a new User admin that includes the inline for the custom User model
class UserAdmin(BaseUserAdmin):
    inlines = [UserInline]


# Unregister the default User model and register the customized UserAdmin
admin.site.unregister(AuthUser)
admin.site.register(models.User)
admin.site.register(AuthUser, UserAdmin)
