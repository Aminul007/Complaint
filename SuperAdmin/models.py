from django.conf import settings
from django.contrib import auth
from django.db import models
from django.urls import reverse


class District(models.Model):
    district = models.CharField(max_length=200)

    def __str__(self):
        return self.district


class PoliceStation(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    police_station = models.CharField(max_length=200)
    email = models.EmailField()

    def __str__(self):
        return self.police_station


class Ministry(models.Model):
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ministry_name = models.CharField(max_length=100, verbose_name='Ministry Name')
    minister_name = models.CharField(max_length=100, verbose_name='Minister Name')
    email = models.EmailField(verbose_name='Email')

    def __str__(self):
        return str(self.ministry_name)
