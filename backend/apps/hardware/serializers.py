from rest_framework import serializers
from .models import ApiKeys, Cameras, CameraHeartbeats
from apps.core.serializers import (
    BaseModelSerializer,
    TenantModelSerializer,
    SoftDeleteSerializerMixin,
)


class ApiKeySerializer(TenantModelSerializer, SoftDeleteSerializerMixin):
    class Meta(TenantModelSerializer.Meta):
        model = ApiKeys
        fields = TenantModelSerializer.Meta.fields + ["name", "key_id", "enabled"]


class ApiKeyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKeys
        fields = ["name"]

    def create(self, validated_data):
        # Gerar key_id e hmac_secret
        import secrets
        import hashlib

        key_id = secrets.token_urlsafe(32)
        hmac_secret = secrets.token_urlsafe(64)
        hmac_secret_hash = hashlib.sha256(hmac_secret.encode()).hexdigest()

        return ApiKeys.objects.create(
            client=validated_data["client"],
            name=validated_data["name"],
            key_id=key_id,
            hmac_secret_hash=hmac_secret_hash,
        )


class CameraSerializer(TenantModelSerializer, SoftDeleteSerializerMixin):
    api_key = ApiKeySerializer(read_only=True)
    api_key_id = serializers.IntegerField(write_only=True)
    establishment = serializers.SerializerMethodField()
    lot = serializers.SerializerMethodField()

    class Meta(TenantModelSerializer.Meta):
        model = Cameras
        fields = TenantModelSerializer.Meta.fields + [
            "camera_code",
            "api_key",
            "api_key_id",
            "establishment",
            "lot",
            "state",
            "last_seen_at",
        ]

    def get_establishment(self, obj):
        if obj.establishment:
            return {"id": obj.establishment.id, "name": obj.establishment.name}
        return None

    def get_lot(self, obj):
        if obj.lot:
            return {
                "id": obj.lot.id,
                "lot_code": obj.lot.lot_code,
                "name": obj.lot.name,
            }
        return None


class CameraCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cameras
        fields = ["camera_code", "api_key_id", "establishment_id", "lot_id", "state"]

    def create(self, validated_data):
        user_client = self.context["request"].user.client_members.first()
        if user_client:
            validated_data["client"] = user_client.client

        return super().create(validated_data)


class CameraHeartbeatSerializer(BaseModelSerializer, SoftDeleteSerializerMixin):
    class Meta(BaseModelSerializer.Meta):
        model = CameraHeartbeats
        fields = BaseModelSerializer.Meta.fields + [
            "camera",
            "received_at",
            "payload_json",
        ]

    def create(self, validated_data):
        from django.utils import timezone

        validated_data["received_at"] = timezone.now()
        return super().create(validated_data)


class CameraHeartbeatCreateSerializer(serializers.Serializer):
    camera_id = serializers.IntegerField()
    payload_json = serializers.JSONField(required=False)

    def validate_camera_id(self, value):
        try:
            camera = Cameras.objects.get(id=value)
            # Verificar se a câmera pertence ao cliente do usuário
            user_clients = self.context["request"].user.client_members.values_list(
                "client_id", flat=True
            )
            if camera.client_id not in user_clients:
                raise serializers.ValidationError("Câmera não encontrada")
            return value
        except Cameras.DoesNotExist:
            raise serializers.ValidationError("Câmera não encontrada")

    def create(self, validated_data):
        from django.utils import timezone

        camera = Cameras.objects.get(id=validated_data["camera_id"])

        # Atualizar last_seen_at da câmera
        camera.last_seen_at = timezone.now()
        camera.save()

        return CameraHeartbeats.objects.create(
            camera=camera, payload_json=validated_data.get("payload_json")
        )
