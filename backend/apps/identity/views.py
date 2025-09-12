from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import hashlib
import secrets

from .models import Users, Roles, RefreshTokens
from .serializers import (
    UserSerializer, UserRegistrationSerializer, CustomTokenObtainPairSerializer,
    RoleSerializer, UserRoleSerializer, RefreshTokenSerializer
)
from apps.core.views import BaseViewSetMixin, SoftDeleteViewSetMixin
from apps.core.permissions import IsAdminUser, IsClientAdmin, IsAppUser

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(generics.CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Criar token de acesso
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def me_view(request):
    """Endpoint para obter e atualizar dados do usuário logado"""
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Endpoint para logout (invalidar refresh token)"""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({'message': 'Logout realizado com sucesso'})
    except Exception as e:
        return Response(
            {'error': 'Token inválido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class RoleListView(BaseViewSetMixin, generics.ListAPIView):
    queryset = Roles.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserRoleListCreateView(BaseViewSetMixin, generics.ListCreateAPIView):
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserRoles.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserRoleDetailView(BaseViewSetMixin, generics.RetrieveDestroyAPIView):
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserRoles.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def refresh_tokens_view(request):
    """Listar refresh tokens do usuário"""
    tokens = RefreshTokens.objects.filter(
        user=request.user,
        revoked_at__isnull=True,
        expires_at__gt=timezone.now()
    ).order_by('-created_at')
    
    serializer = RefreshTokenSerializer(tokens, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def revoke_refresh_token_view(request):
    """Revogar um refresh token específico"""
    token_id = request.data.get('token_id')
    if not token_id:
        return Response(
            {'error': 'token_id é obrigatório'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        token = RefreshTokens.objects.get(
            id=token_id,
            user=request.user,
            revoked_at__isnull=True
        )
        token.revoked_at = timezone.now()
        token.save()
        
        return Response({'message': 'Token revogado com sucesso'})
    except RefreshTokens.DoesNotExist:
        return Response(
            {'error': 'Token não encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )