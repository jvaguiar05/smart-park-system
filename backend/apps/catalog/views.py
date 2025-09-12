from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import (
    StoreTypes, Establishments, Lots, Slots, SlotTypes, 
    VehicleTypes, SlotStatus, SlotStatusHistory
)
from .serializers import (
    StoreTypeSerializer, EstablishmentSerializer, LotSerializer,
    SlotSerializer, SlotTypeSerializer, VehicleTypeSerializer,
    SlotStatusSerializer, SlotStatusHistorySerializer, SlotStatusUpdateSerializer
)
from apps.core.permissions import IsClientAdminForClient, IsClientMember
from apps.core.views import (
    TenantViewSetMixin, BaseViewSetMixin, SearchMixin, 
    PaginationMixin, FilterByClientMixin
)


class StoreTypeListView(
    BaseViewSetMixin,
    SearchMixin,
    PaginationMixin,
    generics.ListAPIView
):
    queryset = StoreTypes.objects.all()
    serializer_class = StoreTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name']


class EstablishmentListCreateView(
    TenantViewSetMixin,
    SearchMixin,
    PaginationMixin,
    generics.ListCreateAPIView
):
    serializer_class = EstablishmentSerializer
    permission_classes = [IsClientMember]
    search_fields = ['name', 'address', 'city', 'state']


class EstablishmentDetailView(
    TenantViewSetMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = EstablishmentSerializer
    permission_classes = [IsClientAdminForClient]


class LotListCreateView(
    TenantViewSetMixin,
    SearchMixin,
    PaginationMixin,
    generics.ListCreateAPIView
):
    serializer_class = LotSerializer
    permission_classes = [IsClientMember]
    search_fields = ['lot_code', 'name']


class LotDetailView(
    TenantViewSetMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = LotSerializer
    permission_classes = [IsClientAdminForClient]


class SlotListCreateView(
    TenantViewSetMixin,
    SearchMixin,
    PaginationMixin,
    generics.ListCreateAPIView
):
    serializer_class = SlotSerializer
    permission_classes = [IsClientMember]
    search_fields = ['slot_code']

    def get_queryset(self):
        lot_id = self.kwargs['lot_id']
        return super().get_queryset().filter(lot_id=lot_id)

    def perform_create(self, serializer):
        lot_id = self.kwargs['lot_id']
        lot = get_object_or_404(Lots, id=lot_id)
        # O TenantViewSetMixin já define o client
        serializer.save(lot=lot)


class SlotDetailView(
    TenantViewSetMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = SlotSerializer
    permission_classes = [IsClientAdminForClient]


class SlotTypeListView(
    BaseViewSetMixin,
    SearchMixin,
    PaginationMixin,
    generics.ListAPIView
):
    queryset = SlotTypes.objects.all()
    serializer_class = SlotTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name']


class VehicleTypeListView(
    BaseViewSetMixin,
    SearchMixin,
    PaginationMixin,
    generics.ListAPIView
):
    queryset = VehicleTypes.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name']


class SlotStatusDetailView(
    FilterByClientMixin,
    generics.RetrieveUpdateAPIView
):
    serializer_class = SlotStatusSerializer
    permission_classes = [IsClientMember]

    def update(self, request, *args, **kwargs):
        slot_status = self.get_object()
        serializer = SlotStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Atualizar o status
            slot_status.status = serializer.validated_data['status']
            slot_status.changed_at = timezone.now()
            
            if 'vehicle_type_id' in serializer.validated_data:
                vehicle_type_id = serializer.validated_data['vehicle_type_id']
                if vehicle_type_id:
                    slot_status.vehicle_type_id = vehicle_type_id
                else:
                    slot_status.vehicle_type = None
            
            if 'confidence' in serializer.validated_data:
                slot_status.confidence = serializer.validated_data['confidence']
            
            slot_status.save()
            
            # Criar entrada no histórico
            SlotStatusHistory.objects.create(
                slot=slot_status.slot,
                status=slot_status.status,
                vehicle_type=slot_status.vehicle_type,
                confidence=slot_status.confidence
            )
            
            return Response(SlotStatusSerializer(slot_status).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SlotStatusHistoryListView(
    FilterByClientMixin,
    SearchMixin,
    PaginationMixin,
    generics.ListAPIView
):
    serializer_class = SlotStatusHistorySerializer
    permission_classes = [IsClientMember]
    search_fields = ['status', 'event_id']

    def get_queryset(self):
        slot_id = self.kwargs['slot_id']
        return super().get_queryset().filter(
            slot_id=slot_id
        ).order_by('-recorded_at')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_establishments_view(request):
    """Endpoint público para listar estabelecimentos"""
    establishments = Establishments.objects.filter(
        client__onboarding_status='ACTIVE'
    ).select_related('store_type', 'client')
    
    data = []
    for establishment in establishments:
        data.append({
            'id': establishment.id,
            'name': establishment.name,
            'store_type': establishment.store_type.name if establishment.store_type else None,
            'address': establishment.address,
            'city': establishment.city,
            'state': establishment.state,
            'lat': establishment.lat,
            'lng': establishment.lng
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_slot_status_view(request, establishment_id):
    """Endpoint público para status das vagas de um estabelecimento"""
    establishment = get_object_or_404(Establishments, id=establishment_id)
    
    lots = Lots.objects.filter(establishment=establishment)
    slots = Slots.objects.filter(
        lot__in=lots, 
        active=True
    ).select_related('lot', 'current_status', 'current_status__vehicle_type')
    
    data = []
    for slot in slots:
        status_data = None
        if hasattr(slot, 'current_status'):
            status_obj = slot.current_status.first()
            if status_obj:
                status_data = {
                    'status': status_obj.status,
                    'vehicle_type': status_obj.vehicle_type.name if status_obj.vehicle_type else None,
                    'confidence': status_obj.confidence,
                    'changed_at': status_obj.changed_at
                }
        
        data.append({
            'id': slot.id,
            'slot_code': slot.slot_code,
            'lot_code': slot.lot.lot_code,
            'status': status_data
        })
    
    return Response(data)