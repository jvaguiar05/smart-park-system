from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path("admin/", admin.site.urls),
    # OpenAPI/Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    # Apps do projeto
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/core/", include("apps.core.urls")),
    path("api/tenants/", include("apps.tenants.urls")),
    path("api/catalog/", include("apps.catalog.urls")),
    path("api/hardware/", include("apps.hardware.urls")),
    path("api/events/", include("apps.events.urls")),
]
