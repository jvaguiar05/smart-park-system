from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from apps.core.models import BaseModel, SoftDeleteManager


class People(BaseModel):
    name = models.CharField(max_length=80)
    email = models.CharField(max_length=255, unique=True)

    objects = SoftDeleteManager()

    class Meta:
        db_table = "people"

    def __str__(self):
        return f"{self.name} ({self.email})"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        
        email = self.normalize_email(email)
        person = People.objects.create(
            email=email,
            name=extra_fields.get('name', ''),
        )
        
        user = self.model(
            person=person,
            password_hash=password,  # Será hasheado no save()
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        user = self.create_user(email, password, **extra_fields)
        return user


class Users(BaseModel, AbstractBaseUser):
    person = models.OneToOneField(
        "People",
        on_delete=models.PROTECT,
        db_column="person_id",
        related_name="user",
    )
    password_hash = models.TextField()
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'person__email'
    REQUIRED_FIELDS = ['person__name']

    class Meta:
        db_table = "users"

    def __str__(self):
        return f"{self.person.name} ({self.person.email})"

    @property
    def email(self):
        return self.person.email

    @property
    def name(self):
        return self.person.name


class Roles(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40, unique=True)

    class Meta:
        db_table = "roles"

    def __str__(self):
        return self.name


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

    def __str__(self):
        return f"{self.user.person.name} - {self.role.name}"


class RefreshTokens(BaseModel):
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

    objects = SoftDeleteManager()

    class Meta:
        db_table = "refresh_tokens"
        indexes = [
            models.Index(fields=["user"], name="ix_refresh_tokens_user"),
        ]

    def __str__(self):
        return f"Refresh token for {self.user.person.email}"