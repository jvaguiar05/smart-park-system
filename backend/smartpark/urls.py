from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema


# Custom JWT Views com tags do Swagger
class CustomTokenObtainPairView(TokenObtainPairView):
    @extend_schema(
        summary="Login - Obtain JWT token",
        description="Authenticate user and obtain access/refresh tokens",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    @extend_schema(
        summary="Refresh JWT token",
        description="Refresh access token using refresh token",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth (JWT)
    path(
        "api/auth/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/auth/token/refresh/",
        CustomTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    # OpenAPI/Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    # Apps do projeto
    path("api/core/", include("apps.core.urls")),
    path("api/tenants/", include("apps.tenants.urls")),
    path("api/catalog/", include("apps.catalog.urls")),
    path("api/hardware/", include("apps.hardware.urls")),
    path("api/events/", include("apps.events.urls")),
]
