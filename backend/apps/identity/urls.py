from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'identity'

urlpatterns = [
    # Autenticação
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # Usuário
    path('me/', views.me_view, name='me'),
    
    # Roles
    path('roles/', views.RoleListView.as_view(), name='role-list'),
    path('user-roles/', views.UserRoleListCreateView.as_view(), name='user-role-list'),
    path('user-roles/<int:pk>/', views.UserRoleDetailView.as_view(), name='user-role-detail'),
    
    # Refresh Tokens
    path('refresh-tokens/', views.refresh_tokens_view, name='refresh-tokens'),
    path('refresh-tokens/revoke/', views.revoke_refresh_token_view, name='revoke-refresh-token'),
]
