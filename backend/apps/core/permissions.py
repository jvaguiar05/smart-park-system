from rest_framework import permissions
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404


class BasePermission(permissions.BasePermission):
    """
    Classe base para permissões customizadas
    """
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True


class IsAdminUser(BasePermission):
    """
    Permite acesso apenas para usuários admin
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.groups.filter(name='admin').exists()
        )


class IsClientAdmin(BasePermission):
    """
    Permite acesso para client admins
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.groups.filter(name='client_admin').exists()
        )


class IsAppUser(BasePermission):
    """
    Permite acesso para usuários do app
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.groups.filter(name='app_user').exists()
        )


class IsClientAdminOrAdmin(BasePermission):
    """
    Permite acesso para client admins ou admins
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        user_groups = request.user.groups.values_list('name', flat=True)
        return 'admin' in user_groups or 'client_admin' in user_groups


class IsOwnerOrAdmin(BasePermission):
    """
    Permite acesso para o dono do objeto ou admin
    """
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Admin tem acesso a tudo
        if request.user.groups.filter(name='admin').exists():
            return True
        
        # Verifica se é o dono do objeto
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        if hasattr(obj, 'created_by') and obj.created_by == request.user:
            return True
        
        return False


class IsClientMember(BasePermission):
    """
    Permite acesso para membros de clientes
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Admin tem acesso a tudo
        if request.user.groups.filter(name='admin').exists():
            return True
        
        # Verifica se é membro de algum cliente
        return request.user.client_members.exists()


class IsClientAdminForClient(BasePermission):
    """
    Permite acesso para client admins do cliente específico
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Admin tem acesso a tudo
        if request.user.groups.filter(name='admin').exists():
            return True
        
        # Verifica se é client admin
        if not request.user.groups.filter(name='client_admin').exists():
            return False
        
        # Para views que precisam de client_id específico
        client_id = view.kwargs.get('client_id')
        if client_id:
            return request.user.client_members.filter(
                client_id=client_id,
                role__name='client_admin'
            ).exists()
        
        return True


class IsOwnerOrClientAdmin(BasePermission):
    """
    Permite acesso para o dono ou client admin do cliente
    """
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Admin tem acesso a tudo
        if request.user.groups.filter(name='admin').exists():
            return True
        
        # Verifica se é o dono do objeto
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Verifica se é client admin do cliente do objeto
        if hasattr(obj, 'client'):
            return request.user.client_members.filter(
                client=obj.client,
                role__name='client_admin'
            ).exists()
        
        return False


class ReadOnlyOrAdmin(BasePermission):
    """
    Permite leitura para usuários autenticados, escrita apenas para admins
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.groups.filter(name='admin').exists()


class IsActiveUser(BasePermission):
    """
    Permite acesso apenas para usuários ativos
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_active
        )
