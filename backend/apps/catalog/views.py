from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import (
    StoreTypes,
    Establishments,
    Lots,
    Slots,
    SlotTypes,
    VehicleTypes,
    SlotStatus,
    SlotStatusHistory,
)
from .serializers import (
    StoreTypeSerializer,
    EstablishmentSerializer,
    LotSerializer,
    SlotSerializer,
    SlotTypeSerializer,
    VehicleTypeSerializer,
    SlotStatusSerializer,
    SlotStatusHistorySerializer,
    SlotStatusUpdateSerializer,
)
from apps.core.permissions import IsClientAdminForClient, IsClientMember
from apps.core.views import (
    TenantViewSetMixin,
    BaseViewSetMixin,
    SearchMixin,
    PaginationMixin,
    FilterByClientMixin,
)


def apply_search_filter(view_instance, queryset):
    """Helper function to apply search filtering to a queryset"""
    search_term = view_instance.request.query_params.get("search")
    if (
        search_term
        and hasattr(view_instance, "search_fields")
        and view_instance.search_fields
    ):
        search_filters = None
        for field in view_instance.search_fields:
            field_filter = Q(**{f"{field}__icontains": search_term})
            if search_filters is None:
                search_filters = field_filter
            else:
                search_filters |= field_filter
        if search_filters:
            queryset = queryset.filter(search_filters)
    return queryset


@extend_schema(
    summary="List store types",
    description="Retrieve list of available store types",
    tags=["Catalog - Types"],
)
class StoreTypeListView(
    BaseViewSetMixin, SearchMixin, PaginationMixin, generics.ListAPIView
):
    queryset = StoreTypes.objects.all()
    serializer_class = StoreTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["name"]

    def get_queryset(self):
        """Override to ensure SearchMixin is called"""
        queryset = self.queryset._clone()
        search_term = self.request.query_params.get("search")

        if search_term and self.search_fields:
            from django.db.models import Q

            search_filters = None
            for field in self.search_fields:
                field_filter = Q(**{f"{field}__icontains": search_term})
                if search_filters is None:
                    search_filters = field_filter
                else:
                    search_filters |= field_filter

            if search_filters:
                queryset = queryset.filter(search_filters)

        return queryset


@extend_schema_view(
    get=extend_schema(
        summary="List establishments",
        description="Retrieve paginated list of establishments for client",
        tags=["Tenants - Establishments"],
    ),
    post=extend_schema(
        summary="Create establishment",
        description="Create a new establishment for client",
        tags=["Tenants - Establishments"],
    ),
)
class EstablishmentListCreateView(
    TenantViewSetMixin, SearchMixin, PaginationMixin, generics.ListCreateAPIView
):
    serializer_class = EstablishmentSerializer
    permission_classes = [IsClientMember]
    search_fields = ["name", "address", "city", "state"]

    def get_queryset(self):
        """Override to ensure SearchMixin is called"""
        queryset = super().get_queryset()
        return apply_search_filter(self, queryset)


@extend_schema_view(
    get=extend_schema(
        summary="Get establishment details",
        description="Retrieve details of a specific establishment",
        tags=["Tenants - Establishments"],
    ),
    put=extend_schema(
        summary="Update establishment",
        description="Update establishment information",
        tags=["Tenants - Establishments"],
    ),
    patch=extend_schema(
        summary="Partially update establishment",
        description="Partially update establishment information",
        tags=["Tenants - Establishments"],
    ),
    delete=extend_schema(
        summary="Delete establishment",
        description="Delete an establishment",
        tags=["Tenants - Establishments"],
    ),
)
class EstablishmentDetailView(
    TenantViewSetMixin, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = EstablishmentSerializer
    permission_classes = [IsClientAdminForClient]


@extend_schema_view(
    get=extend_schema(
        summary="List lots",
        description="Retrieve paginated list of lots for establishment",
        tags=["Tenants - Lots"],
    ),
    post=extend_schema(
        summary="Create lot",
        description="Create a new lot for establishment",
        tags=["Tenants - Lots"],
    ),
)
class LotListCreateView(
    TenantViewSetMixin, SearchMixin, PaginationMixin, generics.ListCreateAPIView
):
    serializer_class = LotSerializer
    permission_classes = [IsClientMember]
    search_fields = ["lot_code", "name"]

    def get_queryset(self):
        """Override to ensure SearchMixin is called"""
        queryset = super().get_queryset()
        return apply_search_filter(self, queryset)


@extend_schema_view(
    get=extend_schema(
        summary="Get lot details",
        description="Retrieve details of a specific lot",
        tags=["Tenants - Lots"],
    ),
    put=extend_schema(
        summary="Update lot",
        description="Update lot information",
        tags=["Tenants - Lots"],
    ),
    patch=extend_schema(
        summary="Partially update lot",
        description="Partially update lot information",
        tags=["Tenants - Lots"],
    ),
    delete=extend_schema(
        summary="Delete lot", description="Delete a lot", tags=["Tenants - Lots"]
    ),
)
class LotDetailView(TenantViewSetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LotSerializer
    permission_classes = [IsClientAdminForClient]


@extend_schema_view(
    get=extend_schema(
        summary="List slots in lot",
        description="Retrieve paginated list of slots for a specific lot",
        tags=["Tenants - Slots"],
    ),
    post=extend_schema(
        summary="Create slot",
        description="Create a new slot in the lot",
        tags=["Tenants - Slots"],
    ),
)
class SlotListCreateView(
    TenantViewSetMixin, SearchMixin, PaginationMixin, generics.ListCreateAPIView
):
    serializer_class = SlotSerializer
    permission_classes = [IsClientMember]
    search_fields = ["slot_code"]

    def get_queryset(self):
        """Override to ensure SearchMixin is called and filter by lot"""
        if getattr(self, "swagger_fake_view", False):
            return Slots.objects.none()
        lot_id = self.kwargs["lot_id"]
        queryset = super().get_queryset().filter(lot_id=lot_id)
        return apply_search_filter(self, queryset)

    def perform_create(self, serializer):
        lot_id = self.kwargs["lot_id"]
        lot = get_object_or_404(Lots, id=lot_id)
        # O TenantViewSetMixin já define o client
        serializer.save(lot=lot)


@extend_schema_view(
    get=extend_schema(
        summary="Get slot details",
        description="Retrieve details of a specific slot",
        tags=["Tenants - Slots"],
    ),
    put=extend_schema(
        summary="Update slot",
        description="Update slot information",
        tags=["Tenants - Slots"],
    ),
    patch=extend_schema(
        summary="Partially update slot",
        description="Partially update slot information",
        tags=["Tenants - Slots"],
    ),
    delete=extend_schema(
        summary="Delete slot", description="Delete a slot", tags=["Tenants - Slots"]
    ),
)
class SlotDetailView(TenantViewSetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SlotSerializer
    permission_classes = [IsClientAdminForClient]


@extend_schema(
    summary="List slot types",
    description="Retrieve list of available slot types",
    tags=["Catalog - Types"],
)
class SlotTypeListView(
    BaseViewSetMixin, SearchMixin, PaginationMixin, generics.ListAPIView
):
    queryset = SlotTypes.objects.all()
    serializer_class = SlotTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["name"]

    def get_queryset(self):
        """Override to ensure SearchMixin is called"""
        queryset = self.queryset._clone()
        return apply_search_filter(self, queryset)


@extend_schema(
    summary="List vehicle types",
    description="Retrieve list of available vehicle types",
    tags=["Catalog - Types"],
)
class VehicleTypeListView(
    BaseViewSetMixin, SearchMixin, PaginationMixin, generics.ListAPIView
):
    queryset = VehicleTypes.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["name"]

    def get_queryset(self):
        """Override to ensure SearchMixin is called"""
        queryset = self.queryset._clone()
        return apply_search_filter(self, queryset)


@extend_schema_view(
    get=extend_schema(
        summary="Get slot status",
        description="Retrieve current status of a specific slot",
        tags=["Tenants - Slot Status"],
    ),
    put=extend_schema(
        summary="Update slot status",
        description="Update the current status of a slot",
        tags=["Tenants - Slot Status"],
    ),
    patch=extend_schema(
        summary="Partially update slot status",
        description="Partially update slot status information",
        tags=["Tenants - Slot Status"],
    ),
)
class SlotStatusDetailView(generics.RetrieveUpdateAPIView):
    queryset = SlotStatus.objects.all()
    serializer_class = SlotStatusSerializer
    permission_classes = [IsClientMember]

    def get_queryset(self):
        # Filter SlotStatus by client through slot->lot->establishment->client relationship
        user_clients = [
            membership.client.id
            for membership in self.request.user.client_members.all()
        ]
        return self.queryset.filter(
            slot__lot__establishment__client__id__in=user_clients
        )

    def update(self, request, *args, **kwargs):
        slot_status = self.get_object()
        serializer = SlotStatusUpdateSerializer(data=request.data)

        if serializer.is_valid():
            # Atualizar o status
            slot_status.status = serializer.validated_data["status"]
            slot_status.changed_at = timezone.now()

            if "vehicle_type_id" in serializer.validated_data:
                vehicle_type_id = serializer.validated_data["vehicle_type_id"]
                if vehicle_type_id:
                    slot_status.vehicle_type_id = vehicle_type_id
                else:
                    slot_status.vehicle_type = None

            if "confidence" in serializer.validated_data:
                slot_status.confidence = serializer.validated_data["confidence"]

            slot_status.save()

            # Criar entrada no histórico
            SlotStatusHistory.objects.create(
                slot=slot_status.slot,
                status=slot_status.status,
                vehicle_type=slot_status.vehicle_type,
                confidence=slot_status.confidence,
            )

            return Response(SlotStatusSerializer(slot_status).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="List slot status history",
    description="Retrieve paginated history of status changes for a specific slot",
    tags=["Tenants - Slot Status History"],
)
class SlotStatusHistoryListView(SearchMixin, PaginationMixin, generics.ListAPIView):
    queryset = SlotStatusHistory.objects.all()
    serializer_class = SlotStatusHistorySerializer
    permission_classes = [IsClientMember]
    search_fields = ["status", "event_id"]

    def get_queryset(self):
        """Override to ensure SearchMixin is called and filter by client and slot"""
        slot_id = self.kwargs["slot_id"]
        # Filter SlotStatusHistory by client through slot->lot->establishment->client relationship
        user_clients = [
            membership.client.id
            for membership in self.request.user.client_members.all()
        ]
        queryset = (
            super()
            .get_queryset()
            .filter(
                slot_id=slot_id, slot__lot__establishment__client__id__in=user_clients
            )
            .order_by("-recorded_at")
        )
        return apply_search_filter(self, queryset)


@extend_schema(
    tags=["Catalog - Public"],
    summary="List public establishments",
    description="Public endpoint to list active establishments",
    responses={
        200: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "store_type": {"type": "string", "nullable": True},
                    "address": {"type": "string"},
                    "city": {"type": "string"},
                    "state": {"type": "string"},
                    "lat": {"type": "number", "format": "float"},
                    "lng": {"type": "number", "format": "float"},
                },
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def public_establishments_view(request):
    """Endpoint público para listar estabelecimentos"""
    establishments = Establishments.objects.filter(
        client__onboarding_status="ACTIVE"
    ).select_related("store_type", "client")

    data = []
    for establishment in establishments:
        data.append(
            {
                "id": establishment.id,
                "name": establishment.name,
                "store_type": (
                    establishment.store_type.name if establishment.store_type else None
                ),
                "address": establishment.address,
                "city": establishment.city,
                "state": establishment.state,
                "lat": establishment.lat,
                "lng": establishment.lng,
            }
        )

    return Response(data)


@extend_schema(
    tags=["Catalog - Public"],
    summary="Status of slots for an establishment",
    description="Public endpoint to check slot statuses for a specific establishment",
    responses={
        200: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "slot_code": {"type": "string"},
                    "lot_code": {"type": "string"},
                    "status": {
                        "type": "object",
                        "nullable": True,
                        "properties": {
                            "status": {"type": "string"},
                            "vehicle_type": {"type": "string", "nullable": True},
                            "confidence": {"type": "number", "format": "float"},
                            "changed_at": {"type": "string", "format": "date-time"},
                        },
                    },
                },
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def public_slot_status_view(request, establishment_id):
    """Endpoint público para status das vagas de um estabelecimento"""
    establishment = get_object_or_404(Establishments, id=establishment_id)

    lots = Lots.objects.filter(establishment=establishment)
    slots = (
        Slots.objects.filter(lot__in=lots, active=True)
        .select_related("lot")
        .prefetch_related("current_status", "current_status__vehicle_type")
    )

    data = []
    for slot in slots:
        status_data = None
        if hasattr(slot, "current_status"):
            status_obj = slot.current_status.first()
            if status_obj:
                status_data = {
                    "status": status_obj.status,
                    "vehicle_type": (
                        status_obj.vehicle_type.name
                        if status_obj.vehicle_type
                        else None
                    ),
                    "confidence": status_obj.confidence,
                    "changed_at": status_obj.changed_at,
                }

        data.append(
            {
                "id": slot.id,
                "slot_code": slot.slot_code,
                "lot_code": slot.lot.lot_code,
                "status": status_data,
            }
        )

    return Response(data)
