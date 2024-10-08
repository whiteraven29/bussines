from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,Group,Permission
from django.conf import settings
from django.core.exceptions import ValidationError



class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_manager(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self.create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)
    
class Manager(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    groups = models.ManyToManyField(
        Group,
        related_name='manager_set',  # Changed from 'user_set' to 'manager_set'
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='manager_user_permissions',  # Changed from 'user_set' to 'manager_user_permissions'
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )


    def __str__(self):
        return self.email

    def clean(self):
        if not self.email.endswith('@gmail.com'):
            raise ValidationError({'email': 'Only Gmail addresses are allowed.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Branch(models.Model):
    name = models.CharField(max_length=100)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='branches')

    def __str__(self):
        return self.name

