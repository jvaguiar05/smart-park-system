from rest_framework import viewsets
from . import models
from . import serializers
from rest_framework import permissions


# Permissão padrão: autenticado para escrita, leitura aberta no MVP (ajuste depois)
class DefaultPermission(permissions.IsAuthenticatedOrReadOnly):
    pass


class PeopleViewSet(viewsets.ModelViewSet):
    queryset = models.People.objects.all().order_by("-id")
    serializer_class = serializers.PeopleSerializer
    permission_classes = [DefaultPermission]


class UsersViewSet(viewsets.ModelViewSet):
    queryset = models.Users.objects.all().order_by("-id")
    serializer_class = serializers.UsersSerializer
    permission_classes = [DefaultPermission]


class RolesViewSet(viewsets.ModelViewSet):
    queryset = models.Roles.objects.all().order_by("-id")
    serializer_class = serializers.RolesSerializer
    permission_classes = [DefaultPermission]


class UserRolesViewSet(viewsets.ModelViewSet):
    queryset = models.UserRoles.objects.all().order_by("-id")
    serializer_class = serializers.UserRolesSerializer
    permission_classes = [DefaultPermission]


class EstablishmentsViewSet(viewsets.ModelViewSet):
    queryset = models.Establishments.objects.all().order_by("-id")
    serializer_class = serializers.EstablishmentsSerializer
    permission_classes = [DefaultPermission]


class SlotsViewSet(viewsets.ModelViewSet):
    queryset = models.Slots.objects.all().order_by("-id")
    serializer_class = serializers.SlotsSerializer
    permission_classes = [DefaultPermission]


class SlotStatusViewSet(viewsets.ModelViewSet):
    queryset = models.SlotStatus.objects.all().order_by("-id")
    serializer_class = serializers.SlotStatusSerializer
    permission_classes = [DefaultPermission]


class ApiKeysViewSet(viewsets.ModelViewSet):
    queryset = models.ApiKeys.objects.all().order_by("-id")
    serializer_class = serializers.ApiKeysSerializer
    permission_classes = [DefaultPermission]


class CamerasViewSet(viewsets.ModelViewSet):
    queryset = models.Cameras.objects.all().order_by("-id")
    serializer_class = serializers.CamerasSerializer
    permission_classes = [DefaultPermission]


class RefreshTokensViewSet(viewsets.ModelViewSet):
    queryset = models.RefreshTokens.objects.all().order_by("-id")
    serializer_class = serializers.RefreshTokensSerializer
    permission_classes = [DefaultPermission]


class ClientsViewSet(viewsets.ModelViewSet):
    queryset = models.Clients.objects.all().order_by("-id")
    serializer_class = serializers.ClientsSerializer
    permission_classes = [DefaultPermission]


class ClientMembersViewSet(viewsets.ModelViewSet):
    queryset = models.ClientMembers.objects.all().order_by("-id")
    serializer_class = serializers.ClientMembersSerializer
    permission_classes = [DefaultPermission]


class StoreTypesViewSet(viewsets.ModelViewSet):
    queryset = models.StoreTypes.objects.all().order_by("-id")
    serializer_class = serializers.StoreTypesSerializer
    permission_classes = [DefaultPermission]


class LotsViewSet(viewsets.ModelViewSet):
    queryset = models.Lots.objects.all().order_by("-id")
    serializer_class = serializers.LotsSerializer
    permission_classes = [DefaultPermission]


class SlotTypesViewSet(viewsets.ModelViewSet):
    queryset = models.SlotTypes.objects.all().order_by("-id")
    serializer_class = serializers.SlotTypesSerializer
    permission_classes = [DefaultPermission]


class VehicleTypesViewSet(viewsets.ModelViewSet):
    queryset = models.VehicleTypes.objects.all().order_by("-id")
    serializer_class = serializers.VehicleTypesSerializer
    permission_classes = [DefaultPermission]


class SlotStatusHistoryViewSet(viewsets.ModelViewSet):
    queryset = models.SlotStatusHistory.objects.all().order_by("-id")
    serializer_class = serializers.SlotStatusHistorySerializer
    permission_classes = [DefaultPermission]


class CameraHeartbeatsViewSet(viewsets.ModelViewSet):
    queryset = models.CameraHeartbeats.objects.all().order_by("-id")
    serializer_class = serializers.CameraHeartbeatsSerializer
    permission_classes = [DefaultPermission]


class SlotStatusEventsViewSet(viewsets.ModelViewSet):
    queryset = models.SlotStatusEvents.objects.all().order_by("-id")
    serializer_class = serializers.SlotStatusEventsSerializer
    permission_classes = [DefaultPermission]
