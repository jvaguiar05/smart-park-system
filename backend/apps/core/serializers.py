from rest_framework import serializers
from . import models


class PeopleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.People
        fields = "__all__"


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Users
        fields = "__all__"


class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Roles
        fields = "__all__"


class UserRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserRoles
        fields = "__all__"


class EstablishmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Establishments
        fields = "__all__"


class SlotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Slots
        fields = "__all__"


class SlotStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SlotStatus
        fields = "__all__"


class ApiKeysSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApiKeys
        fields = "__all__"


class CamerasSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cameras
        fields = "__all__"


class RefreshTokensSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RefreshTokens
        fields = "__all__"


class ClientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Clients
        fields = "__all__"


class ClientMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClientMembers
        fields = "__all__"


class StoreTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StoreTypes
        fields = "__all__"


class LotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lots
        fields = "__all__"


class SlotTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SlotTypes
        fields = "__all__"


class VehicleTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.VehicleTypes
        fields = "__all__"


class SlotStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SlotStatusHistory
        fields = "__all__"


class CameraHeartbeatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CameraHeartbeats
        fields = "__all__"


class SlotStatusEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SlotStatusEvents
        fields = "__all__"
