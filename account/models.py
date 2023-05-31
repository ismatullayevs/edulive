from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, User
from django.db import models

from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True."
            )
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True."
            )

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, blank=True, null=True)

    email = models.EmailField(unique=True)
    phone_number = models.CharField(_('phone_number'), unique=True, max_length=20)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='user/images/', blank=True)

    # father name
    father_name = models.CharField(_('father_name'), max_length=100, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['phone_number']

    objects = CustomUserManager()

    def get_full_name(self):
        return f"{self.last_name} {self.first_name}  {self.father_name}"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Students(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.PROTECT, related_name='students',
                                related_query_name='students')
    pasport = models.FileField('pasport', upload_to='students/pasport/', blank=True)
    selfi_pasport = models.FileField('selfipasport', upload_to='students/pasport/', blank=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def get_full_name(self):
        return f"{self.user.last_name} {self.user.first_name}"

    def __str__(self):
        return f"{self.user}"


class Teachers(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.PROTECT)
    bio = models.TextField(blank=True)

    # skills = models.ManyToManyField('Skills', blank=True)
    # socials = models.ManyToManyField('Socials', blank=True, verbose_name='ijtimoiy tarmoqlar')
    grade = models.CharField(max_length=100, blank=True)
