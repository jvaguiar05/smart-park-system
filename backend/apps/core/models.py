from django.db import models
import uuid


class People(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=80)
    email = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "people"


class Users(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False)
    person = models.OneToOneField(
        "People",
        on_delete=models.PROTECT,
        db_column="person_id",
        related_name="user",
    )

    password_hash = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "users"


class Roles(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40, unique=True)

    class Meta:
        db_table = "roles"


class UserRoles(models.Model):
    user = models.ForeignKey(
        "Users",
        on_delete=models.PROTECT,
        db_column="user_id",
        related_name="user_roles",
    )
    role = models.ForeignKey(
        "Roles",
        on_delete=models.PROTECT,
        db_column="role_id",
        related_name="user_roles",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_roles"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "role"], name="uq_user_roles_user_role"
            ),
        ]


class Establishments(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        "Clients",
        on_delete=models.PROTECT,
        db_column="client_id",
        related_name="establishments",
    )
    name = models.CharField(max_length=120)
    store_type = models.ForeignKey(
        "StoreTypes",
        on_delete=models.PROTECT,
        db_column="store_type_id",
        null=True,
        blank=True,
        related_name="establishments",
    )
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "establishments"
        constraints = [
            models.UniqueConstraint(
                fields=["client", "name"], name="uq_establishments_client_name"
            ),
        ]
        indexes = [
            models.Index(fields=["store_type"], name="ix_establishments_store_type"),
        ]


class Slots(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        "Clients", on_delete=models.PROTECT, db_column="client_id", related_name="slots"
    )
    lot = models.ForeignKey(
        "Lots", on_delete=models.PROTECT, db_column="lot_id", related_name="slots"
    )
    slot_code = models.CharField(max_length=10)
    slot_type = models.ForeignKey(
        "SlotTypes",
        on_delete=models.PROTECT,
        db_column="slot_type_id",
        related_name="slots",
    )
    polygon_json = models.JSONField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "slots"
        constraints = [
            models.UniqueConstraint(
                fields=["lot", "slot_code"], name="uq_slots_lot_code"
            ),
        ]


class SlotStatus(models.Model):
    id = models.BigAutoField(primary_key=True)
    slot = models.ForeignKey(
        "Slots",
        on_delete=models.PROTECT,
        db_column="slot_id",
        related_name="current_status",
    )
    status = models.CharField(max_length=16)
    vehicle_type = models.ForeignKey(
        "VehicleTypes",
        on_delete=models.PROTECT,
        db_column="vehicle_type_id",
        null=True,
        blank=True,
        related_name="slot_statuses",
    )
    confidence = models.DecimalField(
        max_digits=4, decimal_places=3, null=True, blank=True
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "slot_status"
        constraints = [
            models.UniqueConstraint(
                fields=["slot"], name="uq_slot_status_slot"
            ),  # 1-para-1 com “estado atual”
        ]


class ApiKeys(models.Model):
    id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(
        "Clients",
        on_delete=models.PROTECT,
        db_column="client_id",
        related_name="api_keys",
    )
    name = models.CharField(max_length=100)
    key_id = models.CharField(max_length=64, unique=True)
    hmac_secret_hash = models.TextField()
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "api_keys"


class Cameras(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        "Clients",
        on_delete=models.PROTECT,
        db_column="client_id",
        related_name="cameras",
    )
    establishment = models.ForeignKey(
        "Establishments",
        on_delete=models.PROTECT,
        db_column="establishment_id",
        null=True,
        blank=True,
        related_name="cameras",
    )
    lot = models.ForeignKey(
        "Lots",
        on_delete=models.PROTECT,
        db_column="lot_id",
        null=True,
        blank=True,
        related_name="cameras",
    )
    camera_code = models.CharField(max_length=50)
    api_key = models.ForeignKey(
        "ApiKeys",
        on_delete=models.PROTECT,
        db_column="api_key_id",
        related_name="cameras",
    )
    state = models.CharField(max_length=16, default="UNASSIGNED")
    last_seen_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cameras"
        constraints = [
            models.UniqueConstraint(
                fields=["client", "camera_code"], name="uq_cameras_client_code"
            ),
        ]


class RefreshTokens(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        "Users",
        on_delete=models.PROTECT,
        db_column="user_id",
        related_name="refresh_tokens",
    )
    token_hash = models.TextField()
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    fingerprint = models.TextField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "refresh_tokens"
        indexes = [
            models.Index(fields=["user"], name="ix_refresh_tokens_user"),
        ]


class Clients(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    onboarding_status = models.CharField(max_length=32, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "clients"
        indexes = [
            models.Index(fields=["name"], name="ix_clients_name"),
        ]


class ClientMembers(models.Model):
    client = models.ForeignKey(
        "Clients",
        on_delete=models.PROTECT,
        db_column="client_id",
        related_name="client_members",
    )
    user = models.ForeignKey(
        "Users",
        on_delete=models.PROTECT,
        db_column="user_id",
        related_name="client_members",
    )
    role = models.ForeignKey(
        "Roles",
        on_delete=models.PROTECT,
        db_column="role_id",
        related_name="client_members",
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "client_members"
        constraints = [
            models.UniqueConstraint(
                fields=["client", "user"], name="uq_client_members_client_user"
            ),
        ]


class StoreTypes(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "store_types"


class Lots(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        "Clients", on_delete=models.PROTECT, db_column="client_id", related_name="lots"
    )
    establishment = models.ForeignKey(
        "Establishments",
        on_delete=models.PROTECT,
        db_column="establishment_id",
        related_name="lots",
    )
    lot_code = models.CharField(max_length=50)
    name = models.CharField(max_length=120, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "lots"
        constraints = [
            models.UniqueConstraint(
                fields=["client", "lot_code"], name="uq_lots_client_code"
            ),
        ]


class SlotTypes(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = "slot_types"


class VehicleTypes(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = "vehicle_types"


class SlotStatusHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    slot = models.ForeignKey(
        "Slots",
        on_delete=models.PROTECT,
        db_column="slot_id",
        related_name="status_history",
    )
    status = models.CharField(max_length=16)
    vehicle_type = models.ForeignKey(
        "VehicleTypes",
        on_delete=models.PROTECT,
        db_column="vehicle_type_id",
        null=True,
        blank=True,
        related_name="slot_status_history",
    )
    confidence = models.DecimalField(
        max_digits=4, decimal_places=3, null=True, blank=True
    )
    event_id = models.UUIDField(null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "slot_status_history"
        indexes = [
            models.Index(
                fields=["slot", "recorded_at"], name="ix_slot_hist_slot_rec_at"
            ),
        ]


class CameraHeartbeats(models.Model):
    id = models.BigAutoField(primary_key=True)
    camera = models.ForeignKey(
        "Cameras",
        on_delete=models.PROTECT,
        db_column="camera_id",
        related_name="heartbeats",
    )
    received_at = models.DateTimeField(auto_now_add=True)
    payload_json = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "camera_heartbeats"
        indexes = [
            models.Index(
                fields=["camera", "received_at"], name="ix_cam_heartbeats_cam_rec_at"
            ),
        ]


class SlotStatusEvents(models.Model):
    id = models.BigAutoField(primary_key=True)
    event_id = models.UUIDField(unique=True)
    event_type = models.CharField(max_length=50)
    occurred_at = models.DateTimeField()
    client = models.ForeignKey(
        "Clients",
        on_delete=models.PROTECT,
        db_column="client_id",
        related_name="slot_status_events",
    )
    lot = models.ForeignKey(
        "Lots",
        on_delete=models.PROTECT,
        db_column="lot_id",
        related_name="slot_status_events",
    )
    camera = models.ForeignKey(
        "Cameras",
        on_delete=models.PROTECT,
        db_column="camera_id",
        null=True,
        blank=True,
        related_name="slot_status_events",
    )
    sequence = models.BigIntegerField(null=True, blank=True)
    slot = models.ForeignKey(
        "Slots",
        on_delete=models.PROTECT,
        db_column="slot_id",
        related_name="slot_status_events",
    )
    prev_status = models.CharField(max_length=16, null=True, blank=True)
    prev_vehicle = models.ForeignKey(
        "VehicleTypes",
        on_delete=models.PROTECT,
        db_column="prev_vehicle_id",
        null=True,
        blank=True,
        related_name="prev_slot_status_events",
    )
    curr_status = models.CharField(max_length=16)
    curr_vehicle = models.ForeignKey(
        "VehicleTypes",
        on_delete=models.PROTECT,
        db_column="curr_vehicle_id",
        null=True,
        blank=True,
        related_name="curr_slot_status_events",
    )
    confidence = models.DecimalField(
        max_digits=4, decimal_places=3, null=True, blank=True
    )
    source_model = models.CharField(max_length=60, null=True, blank=True)
    source_version = models.CharField(max_length=30, null=True, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "slot_status_events"
        indexes = [
            models.Index(
                fields=["slot", "occurred_at"], name="ix_slot_sts_events_occ_at"
            ),
        ]
