from ast import Sub
from django.contrib.admin import register, ModelAdmin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser,SubscribeModel
from .forms import CustomUserCreationForm, CustomUserChangeForm


@register(CustomUser)
class UserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = (
        'id', 'email', 'username', 'first_name', 'last_name', 'is_blocked',
        'is_superuser',
    )
    list_filter = (
        'email', 'username', 'is_blocked', 'is_superuser',
    )
    fieldsets = (
        ('Данные пользователя', {'fields': (
            'email', 'username', 'first_name', 'last_name', 'password',
        )}),
        ('Права доступа', {'fields': ('is_blocked', 'is_superuser',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name', 'password1',
                'password2', 'is_blocked', 'is_superuser',
            )
        }),
    )
    list_display_links = ('id', 'email')
    search_fields = ('email', 'username', 'first_name', 'last_name',)
    ordering = ('id', 'email', 'username',)


@register(SubscribeModel)
class SubscribeAdmin(ModelAdmin):
    list_display = ('id', 'author', 'follower')
    list_filter = ('author',)
    list_display_links = ('id', 'author')
    search_fields = ('id', 'author', 'follower')
    ordering = ('id',)
