from django.contrib import admin
from .models import Clients, ClientMembers


@admin.register(Clients)
class ClientsAdmin(admin.ModelAdmin):
    list_display = ['name', 'onboarding_status', 'created_at']
    list_filter = ['onboarding_status', 'created_at']
    search_fields = ['name']


@admin.register(ClientMembers)
class ClientMembersAdmin(admin.ModelAdmin):
    list_display = ['client', 'user', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['client__name', 'user__person__name']