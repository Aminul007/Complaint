from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image
from django.contrib.auth.models import User
from SuperAdmin.models import Ministry, District, PoliceStation


class Activation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)


class User(AbstractUser):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    ministry_name = models.ForeignKey(Ministry, on_delete=models.CASCADE, blank=True, null=True,
                                      verbose_name='Ministry Name')
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    police_station = models.ForeignKey(PoliceStation, on_delete=models.CASCADE)
    is_ministry_incharge = models.BooleanField(default=False)
    is_uno = models.BooleanField(default=False)
    is_public_user = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=12, null=True, blank=True)
    address = models.CharField(max_length=120, null=True, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
