from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone
from datetime import timedelta
import uuid
from django_countries.fields import CountryField
from django.conf import settings

class EmailVerificationToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"Token for {self.user.username}"





# def user_directory_path(instance, filename):
#     return f'user_{instance.id}/{filename}'

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    country = CountryField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True, default='default.jpg')

    def __str__(self):
        return self.username
