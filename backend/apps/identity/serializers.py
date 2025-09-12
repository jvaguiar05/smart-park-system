from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import Users, People, Roles, UserRoles, RefreshTokens
from apps.tenants.models import ClientMembers
from apps.core.serializers import BaseModelSerializer, SoftDeleteSerializerMixin


class PeopleSerializer(BaseModelSerializer, SoftDeleteSerializerMixin):
    class Meta(BaseModelSerializer.Meta):
        model = People
        fields = BaseModelSerializer.Meta.fields + ['name', 'email']


class UserSerializer(BaseModelSerializer, SoftDeleteSerializerMixin):
    person = PeopleSerializer(read_only=True)
    roles = serializers.SerializerMethodField()
    client_memberships = serializers.SerializerMethodField()

    class Meta(BaseModelSerializer.Meta):
        model = Users
        fields = BaseModelSerializer.Meta.fields + [
            'person', 'is_active', 'roles', 'client_memberships'
        ]

    def get_roles(self, obj):
        return [ur.role.name for ur in obj.user_roles.all()]

    def get_client_memberships(self, obj):
        memberships = ClientMembers.objects.filter(user=obj).select_related('client', 'role')
        return [
            {
                'client_id': membership.client.id,
                'client_name': membership.client.name,
                'role': membership.role.name,
                'joined_at': membership.joined_at
            }
            for membership in memberships
        ]


class UserRegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=80)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem")
        return attrs

    def validate_email(self, value):
        if People.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso")
        return value

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = Users.objects.create_user(
            email=validated_data['email'],
            password=password,
            name=validated_data['name']
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Adicionar claims customizados
        token['user_id'] = user.id
        token['email'] = user.person.email
        token['name'] = user.person.name
        
        # Adicionar roles
        roles = [ur.role.name for ur in user.user_roles.all()]
        token['roles'] = roles
        
        # Adicionar client_id se for client_admin
        if 'client_admin' in roles:
            client_membership = ClientMembers.objects.filter(
                user=user, 
                role__name='client_admin'
            ).first()
            if client_membership:
                token['client_id'] = client_membership.client.id
        
        return token

    def validate(self, attrs):
        # Usar email em vez de username
        email = attrs.get('email') or attrs.get('username')
        password = attrs.get('password')
        
        if email and password:
            try:
                user = Users.objects.get(person__email=email)
                if not user.check_password(password):
                    raise serializers.ValidationError('Credenciais inválidas')
                if not user.is_active:
                    raise serializers.ValidationError('Conta desativada')
                
                attrs['user'] = user
                return attrs
            except Users.DoesNotExist:
                raise serializers.ValidationError('Credenciais inválidas')
        else:
            raise serializers.ValidationError('Email e senha são obrigatórios')


class RoleSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Roles
        fields = BaseModelSerializer.Meta.fields + ['name']


class UserRoleSerializer(BaseModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.IntegerField(write_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = UserRoles
        fields = BaseModelSerializer.Meta.fields + ['role', 'role_id', 'assigned_at']


class RefreshTokenSerializer(BaseModelSerializer, SoftDeleteSerializerMixin):
    class Meta(BaseModelSerializer.Meta):
        model = RefreshTokens
        fields = BaseModelSerializer.Meta.fields + [
            'expires_at', 'fingerprint', 'ip', 'user_agent'
        ]
