from django.contrib import admin
from .models import People, Users, Roles, UserRoles, RefreshTokens


@admin.register(People)
class PeopleAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    search_fields = ['name', 'email']
    list_filter = ['created_at']


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['person', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['person__name', 'person__email']


@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(UserRoles)
class UserRolesAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'assigned_at']
    list_filter = ['role', 'assigned_at']


@admin.register(RefreshTokens)
class RefreshTokensAdmin(admin.ModelAdmin):
    list_display = ['user', 'expires_at', 'revoked_at', 'created_at']
    list_filter = ['expires_at', 'revoked_at', 'created_at']