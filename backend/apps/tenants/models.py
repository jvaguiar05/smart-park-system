from django.db import models
from apps.core.models import BaseModel, SoftDeleteManager


class Clients(BaseModel):
    ONBOARDING_STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('ACTIVE', 'Ativo'),
        ('SUSPENDED', 'Suspenso'),
        ('CANCELLED', 'Cancelado'),
    ]

    name = models.CharField(max_length=120)
    onboarding_status = models.CharField(
        max_length=32, 
        choices=ONBOARDING_STATUS_CHOICES,
        default="PENDING"
    )

    objects = SoftDeleteManager()

    class Meta:
        db_table = "clients"
        indexes = [
            models.Index(fields=["name"], name="ix_clients_name"),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_onboarding_status_display()})"


class ClientMembers(BaseModel):
    client = models.ForeignKey(
        "Clients",
        on_delete=models.PROTECT,
        db_column="client_id",
        related_name="client_members",
    )
    user = models.ForeignKey(
        "identity.Users",
        on_delete=models.PROTECT,
        db_column="user_id",
        related_name="client_members",
    )
    role = models.ForeignKey(
        "identity.Roles",
        on_delete=models.PROTECT,
        db_column="role_id",
        related_name="client_members",
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    objects = SoftDeleteManager()

    class Meta:
        db_table = "client_members"
        constraints = [
            models.UniqueConstraint(
                fields=["client", "user"], name="uq_client_members_client_user"
            ),
        ]

    def __str__(self):
        return f"{self.user.person.name} - {self.client.name} ({self.role.name})"