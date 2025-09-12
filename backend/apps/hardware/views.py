from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import ApiKeys, Cameras, CameraHeartbeats
from .serializers import (
    ApiKeySerializer, ApiKeyCreateSerializer, CameraSerializer, 
    CameraCreateSerializer, CameraHeartbeatSerializer, CameraHeartbeatCreateSerializer
)
from apps.core.permissions import IsClientAdminForClient, IsClientMember
from apps.core.views import (
    TenantViewSetMixin, BaseViewSetMixin, SearchMixin, 
    PaginationMixin, FilterByClientMixin
)


class ApiKeyListCreateView(
    TenantViewSetMixin,
    SearchMixin,
    PaginationMixin,
    generics.ListCreateAPIView
):
    serializer_class = ApiKeySerializer
    permission_classes = [IsClientMember]
    search_fields = ['name', 'key_id']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ApiKeyCreateSerializer
        return ApiKeySerializer


class ApiKeyDetailView(
    TenantViewSetMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = ApiKeySerializer
    permission_classes = [IsClientAdminForClient]


class CameraListCreateView(
    TenantViewSetMixin,
    SearchMixin,
    PaginationMixin,
    generics.ListCreateAPIView
):
    serializer_class = CameraSerializer
    permission_classes = [IsClientMember]
    search_fields = ['camera_code', 'state']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CameraCreateSerializer
        return CameraSerializer


class CameraDetailView(
    TenantViewSetMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = CameraSerializer
    permission_classes = [IsClientAdminForClient]


class CameraHeartbeatCreateView(generics.CreateAPIView):
    serializer_class = CameraHeartbeatCreateSerializer
    permission_classes = [permissions.AllowAny]  # Hardware pode enviar heartbeats

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        heartbeat = serializer.save()
        
        # Retornar com serializer de leitura
        read_serializer = CameraHeartbeatSerializer(heartbeat)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class CameraHeartbeatListView(
    FilterByClientMixin,
    SearchMixin,
    PaginationMixin,
    generics.ListAPIView
):
    serializer_class = CameraHeartbeatSerializer
    permission_classes = [IsClientMember]
    search_fields = ['payload_json']

    def get_queryset(self):
        camera_id = self.kwargs['camera_id']
        return super().get_queryset().filter(
            camera_id=camera_id
        ).order_by('-received_at')


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def slot_status_event_view(request):
    """Endpoint para receber eventos de status de vagas do hardware"""
    # TODO: Implementar validação de API Key e HMAC
    # Por enquanto, aceitar qualquer requisição
    
    try:
        slot_id = request.data.get('slot_id')
        status = request.data.get('status')
        vehicle_type_id = request.data.get('vehicle_type_id')
        confidence = request.data.get('confidence')
        
        if not slot_id or not status:
            return Response(
                {'error': 'slot_id e status são obrigatórios'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar a vaga
        slot = get_object_or_404(Slots, id=slot_id)
        
        # Atualizar ou criar status
        slot_status, created = SlotStatus.objects.get_or_create(
            slot=slot,
            defaults={
                'status': status,
                'vehicle_type_id': vehicle_type_id,
                'confidence': confidence
            }
        )
        
        if not created:
            # Atualizar status existente
            slot_status.status = status
            slot_status.vehicle_type_id = vehicle_type_id
            slot_status.confidence = confidence
            slot_status.changed_at = timezone.now()
            slot_status.save()
        
        # Criar entrada no histórico
        SlotStatusHistory.objects.create(
            slot=slot,
            status=status,
            vehicle_type_id=vehicle_type_id,
            confidence=confidence
        )
        
        return Response({
            'message': 'Status atualizado com sucesso',
            'slot_id': slot_id,
            'status': status
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )