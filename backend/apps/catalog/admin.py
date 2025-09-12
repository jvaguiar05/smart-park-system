from django.contrib import admin
from .models import (
    StoreTypes, Establishments, Lots, Slots, SlotTypes, 
    VehicleTypes, SlotStatus, SlotStatusHistory
)


@admin.register(StoreTypes)
class StoreTypesAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Establishments)
class EstablishmentsAdmin(admin.ModelAdmin):
    list_display = ['name', 'client', 'store_type', 'city', 'state']
    list_filter = ['store_type', 'city', 'state', 'created_at']
    search_fields = ['name', 'client__name']


@admin.register(Lots)
class LotsAdmin(admin.ModelAdmin):
    list_display = ['lot_code', 'name', 'establishment', 'client']
    list_filter = ['created_at']
    search_fields = ['lot_code', 'name', 'establishment__name']


@admin.register(Slots)
class SlotsAdmin(admin.ModelAdmin):
    list_display = ['slot_code', 'lot', 'slot_type', 'active']
    list_filter = ['slot_type', 'active', 'created_at']
    search_fields = ['slot_code', 'lot__lot_code']


@admin.register(SlotTypes)
class SlotTypesAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(VehicleTypes)
class VehicleTypesAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(SlotStatus)
class SlotStatusAdmin(admin.ModelAdmin):
    list_display = ['slot', 'status', 'vehicle_type', 'confidence', 'changed_at']
    list_filter = ['status', 'vehicle_type', 'changed_at']
    search_fields = ['slot__slot_code']


@admin.register(SlotStatusHistory)
class SlotStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['slot', 'status', 'vehicle_type', 'recorded_at']
    list_filter = ['status', 'vehicle_type', 'recorded_at']
    search_fields = ['slot__slot_code']