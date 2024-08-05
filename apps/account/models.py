from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from apps.core import validators
from apps.account import managers
from apps.core.mixin import mixin_model
from apps.core import managers as soft_delete_manager
from django.utils.translation import gettext_lazy as _


class User(mixin_model.TimestampsStatusFlagMixin, AbstractBaseUser, PermissionsMixin):
    """
    Custom user model representing users in the system.
    Inherits from mixin.TimestampsStatusFlagMixin for timestamps and status flags,
    AbstractBaseUser for a custom user model, and PermissionsMixin for permissions.
    """

    """
    Fields for user information
    """
    username = models.CharField(
        max_length=100, unique=True,
        validators=[validators.UsernameValidator()], verbose_name=_('Username')
    )
    email = models.EmailField(
        max_length=100, unique=True,
        validators=[validators.EmailValidator()], verbose_name=_('Email')
    )
    phone_number = models.CharField(
        max_length=11, unique=True,
        validators=[validators.PhoneNumberMobileValidator()], verbose_name=_('Phone Number')
    )

    """
    Boolean fields for user permissions and status
    """
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    """
    Specify the field to be used as the unique identifier for the user
    """
    USERNAME_FIELD = "phone_number"

    """
    Fields required when creating a user
    """
    REQUIRED_FIELDS = ['username', 'email']

    """
    Custom managers
    """
    objects = managers.UserManager()
    soft_delete = soft_delete_manager.DeleteManager()

    def __str__(self):
        """
        String representation of the user object
        """
        return f'{self.username} - {self.phone_number}'

    class Meta:
        """
        Meta information about the model
        """
        ordering = ('-update_time', '-create_time', 'is_deleted')
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = [
            models.UniqueConstraint(fields=['username', 'email'], name='unique_username_email')
        ]
        indexes = [
            models.Index(fields=['username', 'phone_number'], name='index_username_phone_number')
        ]
