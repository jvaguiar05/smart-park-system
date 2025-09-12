from django.contrib import admin
from .models import SlotStatusEvents


@admin.register(SlotStatusEvents)
class SlotStatusEventsAdmin(admin.ModelAdmin):
    list_display = [
        'event_id', 'event_type', 'slot', 'client', 'occurred_at', 'received_at'
    ]
    list_filter = ['event_type', 'occurred_at', 'received_at']
    search_fields = ['event_id', 'slot__slot_code', 'client__name']