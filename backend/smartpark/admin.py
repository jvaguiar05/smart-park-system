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
    site_header = "SmartPark - Painel Administrativo"
    site_title = "SmartPark Admin"
    index_title = "Dashboard do Sistema SmartPark"

    def index(self, request, extra_context=None):
        """
        Dashboard customizado com métricas importantes
        """
        extra_context = extra_context or {}

        # Métricas gerais
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        # Estatísticas de clientes
        total_clients = Clients.objects.count()
        active_clients = Clients.objects.filter(onboarding_status="ACTIVE").count()

        # Estatísticas de estabelecimentos e vagas
        total_establishments = Establishments.objects.count()
        total_lots = Lots.objects.count()
        total_slots = Slots.objects.filter(active=True).count()

        # Status das vagas
        occupied_slots = SlotStatus.objects.filter(status="OCCUPIED").count()
        free_slots = SlotStatus.objects.filter(status="FREE").count()
        occupancy_rate = (occupied_slots / total_slots * 100) if total_slots > 0 else 0

        # Estatísticas de hardware
        total_cameras = Cameras.objects.count()
        active_cameras = Cameras.objects.filter(state="ACTIVE").count()
        online_cameras = Cameras.objects.filter(
            last_seen_at__gte=now - timedelta(minutes=5)
        ).count()

        # Eventos recentes
        events_24h = SlotStatusEvents.objects.filter(received_at__gte=last_24h).count()
        events_7d = SlotStatusEvents.objects.filter(received_at__gte=last_7d).count()

        # Top estabelecimentos por ocupação
        top_establishments = (
            Establishments.objects.annotate(
                total_slots=Count("lots__slots"),
                occupied_slots=Count(
                    "lots__slots__slotstatus",
                    filter=Q(lots__slots__slotstatus__status="OCCUPIED"),
                ),
            )
            .filter(total_slots__gt=0)
            .order_by("-occupied_slots")[:5]
        )

        # Câmeras com problemas
        problematic_cameras = Cameras.objects.filter(
            Q(state="ERROR") | Q(last_seen_at__lt=now - timedelta(hours=1))
        )[:5]

        # Eventos recentes
        recent_events = SlotStatusEvents.objects.select_related(
            "slot__lot__establishment", "client"
        ).order_by("-received_at")[:10]

        extra_context.update(
            {
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
                    "infrastructure": {
                        "establishments": total_establishments,
                        "lots": total_lots,
                        "slots": total_slots,
                    },
                    "occupancy": {
                        "occupied": occupied_slots,
                        "free": free_slots,
                        "rate": occupancy_rate,
                    },
                    "hardware": {
                        "total_cameras": total_cameras,
                        "active_cameras": active_cameras,
                        "online_cameras": online_cameras,
                        "online_percentage": (
                            (online_cameras / total_cameras * 100)
                            if total_cameras > 0
                            else 0
                        ),
                    },
                    "events": {"last_24h": events_24h, "last_7d": events_7d},
                },
                "top_establishments": top_establishments,
                "problematic_cameras": problematic_cameras,
                "recent_events": recent_events,
            }
        )

        return super().index(request, extra_context)


# Registrar o site admin customizado
admin_site = SmartParkAdminSite(name="smartpark_admin")

# Configurações globais do admin
admin.site.site_header = "SmartPark - Painel Administrativo"
admin.site.site_title = "SmartPark Admin"
admin.site.index_title = "Dashboard do Sistema SmartPark"
admin.site.enable_nav_sidebar = True
