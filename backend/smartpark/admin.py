from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.tenants.models import Clients, ClientMembers
from apps.catalog.models import Establishments, Lots, Slots, SlotStatus
from apps.hardware.models import Cameras, ApiKeys
from apps.events.models import SlotStatusEvents


class SmartParkAdminSite(AdminSite):
    """
    AdminSite customizado para administradores do sistema SmartPark.

    Este admin é exclusivo para superusuários e membros da equipe,
    oferecendo acesso completo ao sistema e funcionalidades avançadas.
    """

    site_header = "🏗️ SmartPark - Admin Backoffice"
    site_title = "SmartPark Admin"
    index_title = "Central de Controle e Monitoramento"

    def has_permission(self, request):
        """
        Restringe acesso apenas para superusuários e staff.
        """
        return request.user.is_active and (
            request.user.is_superuser or request.user.is_staff
        )

    def login(self, request, extra_context=None):
        """
        Adiciona contexto específico para a página de login do admin.
        """
        extra_context = extra_context or {}
        extra_context.update(
            {
                "title": "SmartPark - Admin Login",
                "site_name": "SmartPark Admin Backoffice",
                "admin_type": "admin",
            }
        )
        return super().login(request, extra_context)

    def index(self, request, extra_context=None):
        """
        Dashboard principal com estatísticas e métricas do sistema.
        """
        extra_context = extra_context or {}

        # Importações para estatísticas básicas
        from apps.tenants.models import Clients
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        # Estatísticas básicas de clientes
        total_clients = Clients.objects.count()
        active_clients = Clients.objects.filter(onboarding_status="ACTIVE").count()

        extra_context.update(
            {
                "admin_type": "admin_backoffice",
                "user_role": "Administrador do Sistema",
                "dashboard_stats": {
                    "clients": {
                        "total": total_clients,
                        "active": active_clients,
                        "active_percentage": (
                            (active_clients / total_clients * 100)
                            if total_clients > 0
                            else 0
                        ),
                    },
                    "system": {
                        "status": "online",
                        "version": "1.0.0",
                        "uptime": "Running",
                    },
                },
            }
        )

        return super().index(request, extra_context)


# Registrar o site admin customizado
admin_site = SmartParkAdminSite(name="smartpark_admin")

# Configurações globais do admin padrão (para fallback)
admin.site.site_header = "🏗️ SmartPark - Admin Backoffice"
admin.site.site_title = "SmartPark Admin"
admin.site.index_title = "Central de Controle e Monitoramento"
admin.site.enable_nav_sidebar = True
