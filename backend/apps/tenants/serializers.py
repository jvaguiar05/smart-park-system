from rest_framework import serializers
from .models import Clients, ClientMembers
from apps.identity.models import Users, Roles
from apps.core.serializers import BaseModelSerializer, SoftDeleteSerializerMixin


class ClientSerializer(BaseModelSerializer, SoftDeleteSerializerMixin):
    class Meta(BaseModelSerializer.Meta):
        model = Clients
        fields = BaseModelSerializer.Meta.fields + ['name', 'onboarding_status']


class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clients
        fields = ['name', 'onboarding_status']

    def create(self, validated_data):
        # Apenas admin pode criar clientes
        return super().create(validated_data)


class ClientMemberSerializer(BaseModelSerializer, SoftDeleteSerializerMixin):
    user = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()

    class Meta(BaseModelSerializer.Meta):
        model = ClientMembers
        fields = BaseModelSerializer.Meta.fields + [
            'client', 'user', 'role', 'joined_at'
        ]

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'name': obj.user.person.name,
            'email': obj.user.person.email
        }

    def get_role(self, obj):
        return {
            'id': obj.role.id,
            'name': obj.role.name
        }

    def get_client(self, obj):
        return {
            'id': obj.client.id,
            'name': obj.client.name
        }


class ClientMemberCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role_id = serializers.IntegerField()

    def validate_user_id(self, value):
        try:
            user = Users.objects.get(id=value)
            return value
        except Users.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado")

    def validate_role_id(self, value):
        try:
            role = Roles.objects.get(id=value)
            return value
        except Roles.DoesNotExist:
            raise serializers.ValidationError("Role não encontrada")

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        role_id = attrs.get('role_id')
        client_id = self.context.get('client_id')

        # Verificar se o usuário já é membro deste cliente
        if ClientMembers.objects.filter(
            client_id=client_id, 
            user_id=user_id
        ).exists():
            raise serializers.ValidationError(
                "Este usuário já é membro deste cliente"
            )

        return attrs

    def create(self, validated_data):
        client_id = self.context.get('client_id')
        return ClientMembers.objects.create(
            client_id=client_id,
            user_id=validated_data['user_id'],
            role_id=validated_data['role_id']
        )
