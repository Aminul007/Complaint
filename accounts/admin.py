from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.
from .models import User


class UserAdmin(admin.ModelAdmin):

    list_display = ('username', 'email', 'is_staff', 'is_ministry_incharge', 'is_uno', 'is_public_user')


admin.site.register(User, UserAdmin)
