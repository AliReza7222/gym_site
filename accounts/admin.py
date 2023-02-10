from django.contrib import admin
from .models import MyUser


@admin.register(MyUser)
class AdminPanelMyUser(admin.ModelAdmin):
    list_filter = [
        'username',
    ]
    fields = [
        ('username', 'password', 'type_user'),
        'email',
        ('first_name', 'last_name'),
        ('is_active', 'is_staff', 'is_superuser'),
        'groups',
        'user_permissions'
    ]
    filter_horizontal = ['groups', 'user_permissions']
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_editable = ['is_staff', 'is_active']
