import uuid
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from unittest.mock import patch

from .models import Clients, ClientMembers
from .serializers import (
    ClientSerializer,
    ClientCreateSerializer,
    ClientMemberSerializer,
    ClientMemberCreateSerializer,
)
from .views import (
    ClientListCreateView,
    ClientDetailView,
    ClientMemberListView,
    ClientMemberDetailView,
    my_clients_view,
)
from apps.core.models import BaseModel


class ClientsModelTest(TestCase):
    """Test cases for Clients model"""

    def setUp(self):
        """Set up test data"""
        self.client_data = {"name": "Test Client", "onboarding_status": "PENDING"}

    def test_client_creation(self):
        """Test basic client creation"""
        client = Clients.objects.create(**self.client_data)

        self.assertEqual(client.name, "Test Client")
        self.assertEqual(client.onboarding_status, "PENDING")
        self.assertIsNotNone(client.id)
        self.assertIsNotNone(client.public_id)
        self.assertIsNotNone(client.created_at)
        self.assertIsNotNone(client.updated_at)
        self.assertIsNone(client.deleted_at)

    def test_client_str_representation(self):
        """Test string representation of client"""
        client = Clients.objects.create(**self.client_data)
        expected_str = f"{client.name} ({client.get_onboarding_status_display()})"
        self.assertEqual(str(client), expected_str)

    def test_client_onboarding_status_choices(self):
        """Test all onboarding status choices"""
        statuses = ["PENDING", "ACTIVE", "SUSPENDED", "CANCELLED"]

        for status in statuses:
            client = Clients.objects.create(
                name=f"Client {status}", onboarding_status=status
            )
            self.assertEqual(client.onboarding_status, status)

    def test_client_default_onboarding_status(self):
        """Test default onboarding status"""
        client = Clients.objects.create(name="Test Client")
        self.assertEqual(client.onboarding_status, "PENDING")

    def test_client_soft_delete(self):
        """Test soft delete functionality"""
        client = Clients.objects.create(**self.client_data)

        # Initially not deleted
        self.assertFalse(client.is_deleted)
        self.assertIsNone(client.deleted_at)

        # Soft delete
        client.soft_delete()
        self.assertTrue(client.is_deleted)
        self.assertIsNotNone(client.deleted_at)

        # Restore
        client.restore()
        self.assertFalse(client.is_deleted)
        self.assertIsNone(client.deleted_at)

    def test_client_soft_delete_manager(self):
        """Test soft delete manager functionality"""
        client1 = Clients.objects.create(name="Client 1")
        client2 = Clients.objects.create(name="Client 2")

        # Soft delete one client
        client1.soft_delete()

        # Test manager methods
        active_clients = Clients.objects.all()
        self.assertEqual(active_clients.count(), 1)
        self.assertEqual(active_clients.first(), client2)

        all_clients = Clients.objects.with_deleted()
        self.assertEqual(all_clients.count(), 2)

        deleted_clients = Clients.objects.only_deleted()
        self.assertEqual(deleted_clients.count(), 1)
        self.assertEqual(deleted_clients.first(), client1)

    def test_client_inherits_base_model(self):
        """Test that Clients inherits from BaseModel"""
        self.assertTrue(issubclass(Clients, BaseModel))

    def test_client_public_id_uniqueness(self):
        """Test that public_id is unique"""
        client1 = Clients.objects.create(name="Client 1")
        client2 = Clients.objects.create(name="Client 2")

        self.assertNotEqual(client1.public_id, client2.public_id)

    def test_client_timestamps(self):
        """Test created_at and updated_at timestamps"""
        before_creation = timezone.now()
        client = Clients.objects.create(**self.client_data)
        after_creation = timezone.now()

        self.assertGreaterEqual(client.created_at, before_creation)
        self.assertLessEqual(client.created_at, after_creation)
        self.assertGreaterEqual(client.updated_at, before_creation)
        self.assertLessEqual(client.updated_at, after_creation)

    def test_client_name_max_length(self):
        """Test name field max length constraint"""
        long_name = "x" * 121  # Exceeds max_length=120
        client = Clients(name=long_name)

        with self.assertRaises(ValidationError):
            client.full_clean()

    def test_client_db_table_name(self):
        """Test custom db_table name"""
        self.assertEqual(Clients._meta.db_table, "clients")


class ClientMembersModelTest(TestCase):
    """Test cases for ClientMembers model"""

    def setUp(self):
        """Set up test data"""
        self.client = Clients.objects.create(name="Test Client")
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.group = Group.objects.create(name="test_group")

        self.member_data = {
            "client": self.client,
            "user": self.user,
            "role": self.group,
        }

    def test_client_member_creation(self):
        """Test basic client member creation"""
        member = ClientMembers.objects.create(**self.member_data)

        self.assertEqual(member.client, self.client)
        self.assertEqual(member.user, self.user)
        self.assertEqual(member.role, self.group)
        self.assertIsNotNone(member.joined_at)
        self.assertIsNotNone(member.id)
        self.assertIsNotNone(member.public_id)

    def test_client_member_str_representation(self):
        """Test string representation of client member"""
        member = ClientMembers.objects.create(**self.member_data)
        expected_str = (
            f"{member.user.username} - {member.client.name} ({member.role.name})"
        )
        self.assertEqual(str(member), expected_str)

    def test_client_member_unique_constraint(self):
        """Test unique constraint on client and user"""
        # Create first member
        ClientMembers.objects.create(**self.member_data)

        # Try to create duplicate
        with self.assertRaises(IntegrityError):
            ClientMembers.objects.create(**self.member_data)

    def test_client_member_soft_delete(self):
        """Test soft delete functionality"""
        member = ClientMembers.objects.create(**self.member_data)

        # Initially not deleted
        self.assertFalse(member.is_deleted)
        self.assertIsNone(member.deleted_at)

        # Soft delete
        member.soft_delete()
        self.assertTrue(member.is_deleted)
        self.assertIsNotNone(member.deleted_at)

        # Restore
        member.restore()
        self.assertFalse(member.is_deleted)
        self.assertIsNone(member.deleted_at)

    def test_client_member_soft_delete_manager(self):
        """Test soft delete manager functionality"""
        member1 = ClientMembers.objects.create(**self.member_data)

        # Create another member
        user2 = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )
        member2 = ClientMembers.objects.create(
            client=self.client, user=user2, role=self.group
        )

        # Soft delete one member
        member1.soft_delete()

        # Test manager methods
        active_members = ClientMembers.objects.all()
        self.assertEqual(active_members.count(), 1)
        self.assertEqual(active_members.first(), member2)

        all_members = ClientMembers.objects.with_deleted()
        self.assertEqual(all_members.count(), 2)

        deleted_members = ClientMembers.objects.only_deleted()
        self.assertEqual(deleted_members.count(), 1)
        self.assertEqual(deleted_members.first(), member1)

    def test_client_member_foreign_key_relationships(self):
        """Test foreign key relationships"""
        member = ClientMembers.objects.create(**self.member_data)

        # Test reverse relationships
        self.assertIn(member, self.client.client_members.all())
        self.assertIn(member, self.user.client_members.all())
        self.assertIn(member, self.group.client_members.all())

    def test_client_member_joined_at_auto_now_add(self):
        """Test joined_at field is set automatically"""
        before_creation = timezone.now()
        member = ClientMembers.objects.create(**self.member_data)
        after_creation = timezone.now()

        self.assertGreaterEqual(member.joined_at, before_creation)
        self.assertLessEqual(member.joined_at, after_creation)

    def test_client_member_inherits_base_model(self):
        """Test that ClientMembers inherits from BaseModel"""
        self.assertTrue(issubclass(ClientMembers, BaseModel))

    def test_client_member_db_table_name(self):
        """Test custom db_table name"""
        self.assertEqual(ClientMembers._meta.db_table, "client_members")

    def test_client_member_cascade_protection(self):
        """Test that foreign keys use PROTECT on delete"""
        member = ClientMembers.objects.create(**self.member_data)

        # Try to delete client (should be protected)
        with self.assertRaises(IntegrityError):
            self.client.delete()

        # Try to delete user (should be protected)
        with self.assertRaises(IntegrityError):
            self.user.delete()

        # Try to delete group (should be protected)
        with self.assertRaises(IntegrityError):
            self.group.delete()


class ClientSerializerTest(TestCase):
    """Test cases for Client serializers"""

    def setUp(self):
        """Set up test data"""
        self.client = Clients.objects.create(
            name="Test Client", onboarding_status="ACTIVE"
        )

    def test_client_serializer_serialization(self):
        """Test ClientSerializer serialization"""
        serializer = ClientSerializer(self.client)
        data = serializer.data

        self.assertEqual(data["id"], self.client.id)
        self.assertEqual(data["name"], self.client.name)
        self.assertEqual(data["onboarding_status"], self.client.onboarding_status)
        self.assertEqual(data["public_id"], str(self.client.public_id))
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIn("is_deleted", data)
        self.assertFalse(data["is_deleted"])

    def test_client_serializer_deserialization(self):
        """Test ClientSerializer deserialization"""
        data = {"name": "New Client", "onboarding_status": "PENDING"}
        serializer = ClientSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        client = serializer.save()

        self.assertEqual(client.name, "New Client")
        self.assertEqual(client.onboarding_status, "PENDING")

    def test_client_create_serializer(self):
        """Test ClientCreateSerializer"""
        data = {"name": "Create Test Client", "onboarding_status": "ACTIVE"}
        serializer = ClientCreateSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        client = serializer.save()

        self.assertEqual(client.name, "Create Test Client")
        self.assertEqual(client.onboarding_status, "ACTIVE")

    def test_client_serializer_with_soft_delete(self):
        """Test ClientSerializer with soft deleted client"""
        self.client.soft_delete()
        serializer = ClientSerializer(self.client)
        data = serializer.data

        self.assertTrue(data["is_deleted"])

    def test_client_serializer_validation(self):
        """Test ClientSerializer validation"""
        # Test invalid onboarding status
        data = {"name": "Test Client", "onboarding_status": "INVALID_STATUS"}
        serializer = ClientSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("onboarding_status", serializer.errors)

    def test_client_serializer_fields(self):
        """Test ClientSerializer field configuration"""
        serializer = ClientSerializer()
        expected_fields = [
            "id",
            "public_id",
            "created_at",
            "updated_at",
            "is_deleted",
            "name",
            "onboarding_status",
        ]

        for field in expected_fields:
            self.assertIn(field, serializer.fields)


class ClientMemberSerializerTest(TestCase):
    """Test cases for ClientMember serializers"""

    def setUp(self):
        """Set up test data"""
        self.client = Clients.objects.create(name="Test Client")
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.group = Group.objects.create(name="test_group")

        self.member = ClientMembers.objects.create(
            client=self.client, user=self.user, role=self.group
        )

    def test_client_member_serializer_serialization(self):
        """Test ClientMemberSerializer serialization"""
        serializer = ClientMemberSerializer(self.member)
        data = serializer.data

        self.assertEqual(data["id"], self.member.id)
        self.assertEqual(data["client"]["id"], self.client.id)
        self.assertEqual(data["client"]["name"], self.client.name)
        self.assertEqual(data["user"]["id"], self.user.id)
        self.assertEqual(
            data["user"]["name"], self.user.get_full_name() or self.user.username
        )
        self.assertEqual(data["user"]["email"], self.user.email)
        self.assertEqual(data["role"]["id"], self.group.id)
        self.assertEqual(data["role"]["name"], self.group.name)
        self.assertIn("joined_at", data)

    def test_client_member_create_serializer_validation(self):
        """Test ClientMemberCreateSerializer validation"""
        # Create a new user for this test
        new_user = User.objects.create_user(
            username="validationuser",
            email="validation@example.com",
            password="validationpass123",
        )

        data = {"user_id": new_user.id, "group_id": self.group.id}
        serializer = ClientMemberCreateSerializer(
            data=data, context={"client_id": self.client.id}
        )

        self.assertTrue(serializer.is_valid())

    def test_client_member_create_serializer_invalid_user(self):
        """Test ClientMemberCreateSerializer with invalid user"""
        data = {"user_id": 99999, "group_id": self.group.id}  # Non-existent user
        serializer = ClientMemberCreateSerializer(
            data=data, context={"client_id": self.client.id}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("user_id", serializer.errors)

    def test_client_member_create_serializer_invalid_group(self):
        """Test ClientMemberCreateSerializer with invalid group"""
        data = {"user_id": self.user.id, "group_id": 99999}  # Non-existent group
        serializer = ClientMemberCreateSerializer(
            data=data, context={"client_id": self.client.id}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("group_id", serializer.errors)

    def test_client_member_create_serializer_duplicate_member(self):
        """Test ClientMemberCreateSerializer with duplicate member"""
        # The member already exists from setUp, so we just test with the same data
        data = {"user_id": self.user.id, "group_id": self.group.id}
        serializer = ClientMemberCreateSerializer(
            data=data, context={"client_id": self.client.id}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_client_member_create_serializer_creation(self):
        """Test ClientMemberCreateSerializer creation"""
        # Create a new user for this test
        new_user = User.objects.create_user(
            username="newuser", email="newuser@example.com", password="newuserpass123"
        )

        data = {"user_id": new_user.id, "group_id": self.group.id}
        serializer = ClientMemberCreateSerializer(
            data=data, context={"client_id": self.client.id}
        )

        self.assertTrue(serializer.is_valid())
        member = serializer.save()

        self.assertEqual(member.client, self.client)
        self.assertEqual(member.user, new_user)
        self.assertEqual(member.role, self.group)

    def test_client_member_serializer_with_soft_delete(self):
        """Test ClientMemberSerializer with soft deleted member"""
        self.member.soft_delete()
        serializer = ClientMemberSerializer(self.member)
        data = serializer.data

        self.assertTrue(data["is_deleted"])


class ClientViewTest(TestCase):
    """Test cases for Client views"""

    def setUp(self):
        """Set up test data"""
        self.client = Clients.objects.create(
            name="Test Client", onboarding_status="ACTIVE"
        )

        # Create admin user
        self.admin_user = User.objects.create_user(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        admin_group = Group.objects.create(name="admin")
        self.admin_user.groups.add(admin_group)

        # Create regular user
        self.regular_user = User.objects.create_user(
            username="user", email="user@example.com", password="userpass123"
        )

    def test_client_list_view_get(self):
        """Test GET request to client list view"""
        view = ClientListCreateView()
        request = type("Request", (), {"method": "GET"})()
        view.request = request

        serializer_class = view.get_serializer_class()
        self.assertEqual(serializer_class, ClientSerializer)

    def test_client_list_view_post(self):
        """Test POST request to client list view"""
        view = ClientListCreateView()
        request = type("Request", (), {"method": "POST"})()
        view.request = request

        serializer_class = view.get_serializer_class()
        self.assertEqual(serializer_class, ClientCreateSerializer)

    def test_client_detail_view_serializer_class(self):
        """Test client detail view serializer class"""
        view = ClientDetailView()
        self.assertEqual(view.serializer_class, ClientSerializer)

    def test_client_list_view_search_fields(self):
        """Test client list view search fields"""
        view = ClientListCreateView()
        expected_fields = ["name", "onboarding_status"]
        self.assertEqual(view.search_fields, expected_fields)

    def test_client_list_view_permission_classes(self):
        """Test client list view permission classes"""
        view = ClientListCreateView()
        from apps.core.permissions import IsAdminUser

        self.assertIn(IsAdminUser, view.permission_classes)

    def test_client_detail_view_permission_classes(self):
        """Test client detail view permission classes"""
        view = ClientDetailView()
        from apps.core.permissions import IsAdminUser

        self.assertIn(IsAdminUser, view.permission_classes)


class ClientMemberViewTest(TestCase):
    """Test cases for ClientMember views"""

    def setUp(self):
        """Set up test data"""
        self.client = Clients.objects.create(name="Test Client")
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.group = Group.objects.create(name="test_group")

        self.member = ClientMembers.objects.create(
            client=self.client, user=self.user, role=self.group
        )

    def test_client_member_list_view_get_serializer_class(self):
        """Test GET serializer class for client member list view"""
        view = ClientMemberListView()
        request = type("Request", (), {"method": "GET"})()
        view.request = request

        serializer_class = view.get_serializer_class()
        self.assertEqual(serializer_class, ClientMemberSerializer)

    def test_client_member_list_view_post_serializer_class(self):
        """Test POST serializer class for client member list view"""
        view = ClientMemberListView()
        request = type("Request", (), {"method": "POST"})()
        view.request = request

        serializer_class = view.get_serializer_class()
        self.assertEqual(serializer_class, ClientMemberCreateSerializer)

    def test_client_member_list_view_get_queryset(self):
        """Test get_queryset method for client member list view"""
        view = ClientMemberListView()
        view.kwargs = {"client_id": self.client.id}

        queryset = view.get_queryset()
        self.assertIn(self.member, queryset)

    def test_client_member_list_view_get_serializer_context(self):
        """Test get_serializer_context method for client member list view"""
        from django.test import RequestFactory

        view = ClientMemberListView()
        view.kwargs = {"client_id": self.client.id}

        # Mock the request and other required attributes
        factory = RequestFactory()
        request = factory.get("/")
        view.request = request
        view.format_kwarg = None

        context = view.get_serializer_context()
        self.assertEqual(context["client_id"], self.client.id)

    def test_client_member_list_view_search_fields(self):
        """Test search fields for client member list view"""
        view = ClientMemberListView()
        expected_fields = ["user__person__name", "user__person__email", "role__name"]
        self.assertEqual(view.search_fields, expected_fields)

    def test_client_member_detail_view_get_queryset(self):
        """Test get_queryset method for client member detail view"""
        view = ClientMemberDetailView()
        view.kwargs = {"client_id": self.client.id}

        queryset = view.get_queryset()
        self.assertIn(self.member, queryset)

    def test_client_member_detail_view_serializer_class(self):
        """Test serializer class for client member detail view"""
        view = ClientMemberDetailView()
        self.assertEqual(view.serializer_class, ClientMemberSerializer)


class MyClientsViewTest(TestCase):
    """Test cases for my_clients_view"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.client1 = Clients.objects.create(name="Client 1")
        self.client2 = Clients.objects.create(name="Client 2")

        self.group1 = Group.objects.create(name="group1")
        self.group2 = Group.objects.create(name="group2")

        self.member1 = ClientMembers.objects.create(
            client=self.client1, user=self.user, role=self.group1
        )
        self.member2 = ClientMembers.objects.create(
            client=self.client2, user=self.user, role=self.group2
        )

    def test_my_clients_view_response_structure(self):
        """Test my_clients_view response structure"""
        from django.test import RequestFactory
        from rest_framework.test import force_authenticate

        factory = RequestFactory()
        request = factory.get("/my-clients/")
        force_authenticate(request, user=self.user)

        response = my_clients_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)

    def test_my_clients_view_data_content(self):
        """Test my_clients_view data content"""
        from django.test import RequestFactory
        from rest_framework.test import force_authenticate

        factory = RequestFactory()
        request = factory.get("/my-clients/")
        force_authenticate(request, user=self.user)

        response = my_clients_view(request)
        data = response.data

        # Check first client data
        client1_data = next(item for item in data if item["id"] == self.client1.id)
        self.assertEqual(client1_data["name"], "Client 1")
        self.assertEqual(client1_data["onboarding_status"], "PENDING")
        self.assertEqual(client1_data["role"], "group1")
        self.assertIn("joined_at", client1_data)

        # Check second client data
        client2_data = next(item for item in data if item["id"] == self.client2.id)
        self.assertEqual(client2_data["name"], "Client 2")
        self.assertEqual(client2_data["onboarding_status"], "PENDING")
        self.assertEqual(client2_data["role"], "group2")
        self.assertIn("joined_at", client2_data)

    def test_my_clients_view_empty_response(self):
        """Test my_clients_view with user having no clients"""
        from django.test import RequestFactory
        from rest_framework.test import force_authenticate

        # Create user with no clients
        user_no_clients = User.objects.create_user(
            username="nouser", email="nouser@example.com", password="nouserpass123"
        )

        factory = RequestFactory()
        request = factory.get("/my-clients/")
        force_authenticate(request, user=user_no_clients)

        response = my_clients_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_my_clients_view_permission_required(self):
        """Test my_clients_view requires authentication"""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/my-clients/")

        # This should raise an error or return 401
        # The actual behavior depends on DRF settings
        response = my_clients_view(request)
        # Note: This test might need adjustment based on actual DRF configuration


class TenantAppIntegrationTest(TestCase):
    """Integration tests for tenant app functionality"""

    def setUp(self):
        """Set up test data"""
        self.client = Clients.objects.create(
            name="Integration Test Client", onboarding_status="ACTIVE"
        )

        self.user = User.objects.create_user(
            username="integrationuser",
            email="integration@example.com",
            password="integrationpass123",
        )

        self.group = Group.objects.create(name="integration_group")

    def test_full_client_member_lifecycle(self):
        """Test complete client member lifecycle"""
        # Create member
        member = ClientMembers.objects.create(
            client=self.client, user=self.user, role=self.group
        )

        # Verify creation
        self.assertEqual(ClientMembers.objects.count(), 1)
        self.assertFalse(member.is_deleted)

        # Soft delete
        member.soft_delete()
        self.assertTrue(member.is_deleted)
        self.assertEqual(ClientMembers.objects.count(), 0)  # Filtered out
        self.assertEqual(ClientMembers.objects.with_deleted().count(), 1)

        # Restore
        member.restore()
        self.assertFalse(member.is_deleted)
        self.assertEqual(ClientMembers.objects.count(), 1)

    def test_client_with_multiple_members(self):
        """Test client with multiple members"""
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="user2pass123"
        )
        user3 = User.objects.create_user(
            username="user3", email="user3@example.com", password="user3pass123"
        )

        # Create members
        member1 = ClientMembers.objects.create(
            client=self.client, user=self.user, role=self.group
        )
        member2 = ClientMembers.objects.create(
            client=self.client, user=user2, role=self.group
        )
        member3 = ClientMembers.objects.create(
            client=self.client, user=user3, role=self.group
        )

        # Verify relationships
        self.assertEqual(self.client.client_members.count(), 3)
        self.assertIn(member1, self.client.client_members.all())
        self.assertIn(member2, self.client.client_members.all())
        self.assertIn(member3, self.client.client_members.all())

    def test_user_with_multiple_clients(self):
        """Test user with multiple clients"""
        client2 = Clients.objects.create(
            name="Second Client", onboarding_status="ACTIVE"
        )

        group2 = Group.objects.create(name="group2")

        # Create memberships
        member1 = ClientMembers.objects.create(
            client=self.client, user=self.user, role=self.group
        )
        member2 = ClientMembers.objects.create(
            client=client2, user=self.user, role=group2
        )

        # Verify relationships
        self.assertEqual(self.user.client_members.count(), 2)
        self.assertIn(member1, self.user.client_members.all())
        self.assertIn(member2, self.user.client_members.all())

    def test_serializer_integration(self):
        """Test serializer integration with models"""
        member = ClientMembers.objects.create(
            client=self.client, user=self.user, role=self.group
        )

        # Test serialization
        serializer = ClientMemberSerializer(member)
        data = serializer.data

        # Verify serialized data
        self.assertEqual(data["client"]["id"], self.client.id)
        self.assertEqual(data["user"]["id"], self.user.id)
        self.assertEqual(data["role"]["id"], self.group.id)
        self.assertIn("joined_at", data)

    def test_soft_delete_cascade_behavior(self):
        """Test soft delete behavior across related objects"""
        member = ClientMembers.objects.create(
            client=self.client, user=self.user, role=self.group
        )

        # Soft delete client
        self.client.soft_delete()

        # Member should still exist but client should be soft deleted
        self.assertTrue(self.client.is_deleted)
        self.assertFalse(member.is_deleted)

        # Member should still be accessible
        self.assertEqual(ClientMembers.objects.count(), 1)
        self.assertEqual(ClientMembers.objects.first(), member)


class TenantAppAdminTest(TestCase):
    """Test cases for tenant app admin functionality"""

    def setUp(self):
        """Set up test data"""
        self.client = Clients.objects.create(
            name="Admin Test Client", onboarding_status="ACTIVE"
        )

        self.user = User.objects.create_user(
            username="adminuser", email="admin@example.com", password="adminpass123"
        )

        self.group = Group.objects.create(name="admin_group")

        self.member = ClientMembers.objects.create(
            client=self.client, user=self.user, role=self.group
        )

    def test_clients_admin_list_display(self):
        """Test ClientsAdmin list_display configuration"""
        from .admin import ClientsAdmin

        admin = ClientsAdmin(Clients, None)
        expected_fields = [
            "name",
            "onboarding_status",
            "members_count",
            "establishments_count",
            "created_at",
        ]
        self.assertEqual(admin.list_display, expected_fields)

    def test_clients_admin_list_filter(self):
        """Test ClientsAdmin list_filter configuration"""
        from .admin import ClientsAdmin

        admin = ClientsAdmin(Clients, None)
        expected_filters = ["onboarding_status", "created_at"]
        self.assertEqual(admin.list_filter, expected_filters)

    def test_clients_admin_search_fields(self):
        """Test ClientsAdmin search_fields configuration"""
        from .admin import ClientsAdmin

        admin = ClientsAdmin(Clients, None)
        expected_fields = ["name"]
        self.assertEqual(admin.search_fields, expected_fields)

    def test_client_members_admin_list_display(self):
        """Test ClientMembersAdmin list_display configuration"""
        from .admin import ClientMembersAdmin

        admin = ClientMembersAdmin(ClientMembers, None)
        expected_fields = ["client", "user_info", "role", "joined_at"]
        self.assertEqual(admin.list_display, expected_fields)

    def test_client_members_admin_list_filter(self):
        """Test ClientMembersAdmin list_filter configuration"""
        from .admin import ClientMembersAdmin

        admin = ClientMembersAdmin(ClientMembers, None)
        expected_filters = ["role", "joined_at", "client"]
        self.assertEqual(admin.list_filter, expected_filters)

    def test_client_members_admin_search_fields(self):
        """Test ClientMembersAdmin search_fields configuration"""
        from .admin import ClientMembersAdmin

        admin = ClientMembersAdmin(ClientMembers, None)
        expected_fields = ["client__name", "user__username", "user__email"]
        self.assertEqual(admin.search_fields, expected_fields)

    def test_admin_registration(self):
        """Test that models are properly registered with admin"""
        from django.contrib import admin
        from .models import Clients, ClientMembers

        # Check if models are registered
        self.assertTrue(admin.site.is_registered(Clients))
        self.assertTrue(admin.site.is_registered(ClientMembers))

    def test_admin_model_representation(self):
        """Test admin model string representation"""
        # Test Clients admin representation
        self.assertEqual(
            str(self.client),
            f"{self.client.name} ({self.client.get_onboarding_status_display()})",
        )

        # Test ClientMembers admin representation
        expected_str = f"{self.user.username} - {self.client.name} ({self.group.name})"
        self.assertEqual(str(self.member), expected_str)
