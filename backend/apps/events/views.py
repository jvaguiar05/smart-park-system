from rest_framework import generics, permissions
from .models import SlotStatusEvents
from .serializers import SlotStatusEventSerializer, SlotStatusEventCreateSerializer
from apps.core.permissions import IsClientMember
from apps.core.views import (
    TenantViewSetMixin, BaseViewSetMixin, SearchMixin, 
    PaginationMixin, FilterByClientMixin
)


class SlotStatusEventListCreateView(
    TenantViewSetMixin,
    SearchMixin,
    PaginationMixin,
    generics.ListCreateAPIView
):
    serializer_class = SlotStatusEventSerializer
    permission_classes = [IsClientMember]
    search_fields = ['event_type', 'slot__slot_code', 'lot__lot_code']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SlotStatusEventCreateSerializer
        return SlotStatusEventSerializer


class SlotStatusEventDetailView(
    TenantViewSetMixin,
    generics.RetrieveAPIView
):
    serializer_class = SlotStatusEventSerializer
    permission_classes = [IsClientMember]