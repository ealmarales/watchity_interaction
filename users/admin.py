from django.contrib import admin

from users import models

# Register your models here.
from users.models import InteractionUser


@admin.register(InteractionUser)
class UserAdmin(admin.ModelAdmin):
    pass