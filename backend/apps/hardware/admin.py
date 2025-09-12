from django.contrib import admin
from .models import ApiKeys, Cameras, CameraHeartbeats


@admin.register(ApiKeys)
class ApiKeysAdmin(admin.ModelAdmin):
    list_display = ['name', 'key_id', 'client', 'enabled', 'created_at']
    list_filter = ['enabled', 'created_at']
    search_fields = ['name', 'key_id', 'client__name']


@admin.register(Cameras)
class CamerasAdmin(admin.ModelAdmin):
    list_display = ['camera_code', 'client', 'establishment', 'lot', 'state', 'last_seen_at']
    list_filter = ['state', 'created_at', 'last_seen_at']
    search_fields = ['camera_code', 'client__name']


@admin.register(CameraHeartbeats)
class CameraHeartbeatsAdmin(admin.ModelAdmin):
    list_display = ['camera', 'received_at']
    list_filter = ['received_at']
    search_fields = ['camera__camera_code']