from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Clients, ClientMembers
from .serializers import (
    ClientSerializer, ClientCreateSerializer, 
    ClientMemberSerializer, ClientMemberCreateSerializer
)
from apps.core.permissions import IsAdminUser, IsClientAdminForClient
from apps.core.views import BaseViewSetMixin, SoftDeleteViewSetMixin, SearchMixin, PaginationMixin


class ClientListCreateView(
    SoftDeleteViewSetMixin, 
    SearchMixin, 
    PaginationMixin,
    generics.ListCreateAPIView
):
    queryset = Clients.objects.all()
    permission_classes = [IsAdminUser]
    search_fields = ['name', 'onboarding_status']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClientCreateSerializer
        return ClientSerializer


class ClientDetailView(
    SoftDeleteViewSetMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    queryset = Clients.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAdminUser]


class ClientMemberListView(
    BaseViewSetMixin,
    SearchMixin,
    PaginationMixin,
    generics.ListCreateAPIView
):
    serializer_class = ClientMemberSerializer
    permission_classes = [IsClientAdminForClient]
    search_fields = ['user__person__name', 'user__person__email', 'role__name']

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return ClientMembers.objects.filter(client_id=client_id)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClientMemberCreateSerializer
        return ClientMemberSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['client_id'] = self.kwargs['client_id']
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client_member = serializer.save()
        
        # Retornar o objeto criado com serializer de leitura
        read_serializer = ClientMemberSerializer(client_member)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class ClientMemberDetailView(
    BaseViewSetMixin,
    generics.RetrieveDestroyAPIView
):
    serializer_class = ClientMemberSerializer
    permission_classes = [IsClientAdminForClient]

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return ClientMembers.objects.filter(client_id=client_id)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_clients_view(request):
    """Listar clientes do usuário logado"""
    user_clients = ClientMembers.objects.filter(
        user=request.user
    ).select_related('client', 'role')
    
    clients_data = []
    for membership in user_clients:
        clients_data.append({
            'id': membership.client.id,
            'name': membership.client.name,
            'onboarding_status': membership.client.onboarding_status,
            'role': membership.role.name,
            'joined_at': membership.joined_at
        })
    
    return Response(clients_data)