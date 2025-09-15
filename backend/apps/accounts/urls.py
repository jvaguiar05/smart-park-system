from django.urls import path
from .views import (
    # Authentication views
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    # User management views
    CreateAppUserView,
    UserProfileView,
    UpdateUserProfileView,
    ChangePasswordView,
    DeactivateUserView,
    # User search views
    UserSearchView,
    # Utility views
    check_username_availability,
    check_email_availability,
)

urlpatterns = [
    # ==================== AUTHENTICATION ENDPOINTS ====================
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    # ==================== USER REGISTRATION ====================
    path("auth/register/", CreateAppUserView.as_view(), name="register"),
    # ==================== USER PROFILE MANAGEMENT ====================
    path("me/", UserProfileView.as_view(), name="user_profile"),
    path("me/update/", UpdateUserProfileView.as_view(), name="update_profile"),
    path("me/change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("me/deactivate/", DeactivateUserView.as_view(), name="deactivate_account"),
    # ==================== USER SEARCH ====================
    path("users/search/", UserSearchView.as_view(), name="user_search"),
    # ==================== UTILITY ENDPOINTS ====================
    path("utils/check-username/", check_username_availability, name="check_username"),
    path("utils/check-email/", check_email_availability, name="check_email"),
]
